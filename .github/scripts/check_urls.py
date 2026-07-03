#!/usr/bin/env python3
"""Scan the repository for URLs and check whether they are reachable.

The script walks the working tree (skipping VCS data, dependencies and build
output), extracts http(s) URLs from every text file via a regex, performs
concurrent HEAD/GET requests, and prints a categorized report. It exits with a
non-zero status when any URL is broken so it can gate CI.
"""

from __future__ import annotations

import argparse
import os
import re
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Iterable
from urllib import error, request
from urllib.parse import quote, urlsplit, urlunsplit

# --- Configuration -----------------------------------------------------------

# Directories that should never be scanned.
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".docusaurus",
    ".cache-loader",
    "node_modules",
    "build",
    ".idea",
    ".vscode",
    "__pycache__",
}

# File extensions we treat as text. Binary files are skipped entirely.
DEFAULT_INCLUDE_EXT = {
    ".md", ".mdx", ".markdown",
    ".yml", ".yaml",
    ".json",
    ".html", ".htm",
    ".js", ".jsx", ".ts", ".tsx",
    ".py", ".rb", ".go", ".rs",
    ".txt", ".rst",
    ".css", ".scss",
    ".xml", ".svg",
    ".toml", ".ini", ".cfg",
}

# Regex that matches http(s) URLs. The negated character class stops at common
# delimiters (whitespace, angle/quote/backtick, square bracket) so we don't
# capture surrounding markup. Note that ')' is intentionally NOT excluded:
# parentheses are valid URL characters (Wikipedia, "(3rd).pdf", etc.) and
# Markdown link syntax wraps URLs as ](url) — the trailing ')' from the wrapper
# is stripped after matching by balancing parenthesis counts (see below).
URL_REGEX = re.compile(r"https://[^\s<>\"'`\]]+|http://[^\s<>\"'`\]]+")

# Characters that frequently trail a URL in prose/markdown but are not part of
# the URL itself. We strip them from the tail of each match. Note: ')' is NOT
# included here — parentheses are valid URL characters, and Markdown's link
# wrapper `](url)` is handled separately by balancing paren counts below.
TRAILING_PUNCT = ".,;:!?]}'\""

def normalize_url(url: str) -> str:
    """Percent-encode any non-ASCII characters in *url*.

    ``urllib`` only speaks ASCII at the wire level, so a URL containing CJK
    characters (e.g. a Chinese path segment) must be quoted before it is sent.
    Components that are already percent-encoded are preserved (``%`` is in the
    safe set), and URL-structural characters are kept verbatim.
    """
    parts = urlsplit(url)
    # Each component gets its own safe set so we don't accidentally re-encode
    # characters that have structural meaning in that component.
    safe_path = "/%:@+$,;&=()"
    safe_query = "/%:@+$,;&=()*!?"
    safe_fragment = "/%:@+$,;&=()*!?"
    quoted = parts._replace(
        path=quote(parts.path, safe=safe_path),
        query=quote(parts.query, safe=safe_query),
        fragment=quote(parts.fragment, safe=safe_fragment),
    )
    return urlunsplit(quoted)


# Hosts that are valid placeholders and should not be probed.
SKIP_HOSTS = {
    "localhost",
    "127.0.0.1",
    "example.com",
    "example.org",
    "example.net",
    "schema.org",
    "fonts.gstatic.com",
}

DEFAULT_TIMEOUT = 15
DEFAULT_WORKERS = 16
USER_AGENT = "sharedcourses-url-checker/1.0 (+https://github.com/BetterECNU/SharedCourses)"


# --- Data model --------------------------------------------------------------

@dataclass(frozen=True)
class UrlResult:
    url: str
    status: int | None
    ok: bool
    note: str = ""
    sources: set[str] = field(default_factory=set)


# --- Scanning ----------------------------------------------------------------

def iter_text_files(root: str, exclude_dirs: set[str], include_ext: set[str]) -> Iterable[str]:
    """Yield paths of text files under *root* that match the filters."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in place so os.walk skips them.
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in include_ext:
                yield os.path.join(dirpath, name)


def find_urls_in_file(path: str, regex: re.Pattern[str]) -> dict[str, set[str]]:
    """Return {url: {relative_paths}} for every URL found in *path*."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
    except OSError:
        return {}

    url_to_sources: dict[str, set[str]] = {}
    for match in regex.findall(content):
        url = match.rstrip(TRAILING_PUNCT)
        # Drop trailing closing parens that were part of markdown link syntax.
        while url.endswith(")") and url.count("(") < url.count(")"):
            url = url[:-1]
        if not url:
            continue
        url_to_sources.setdefault(url, set()).add(path)
    return url_to_sources


def collect_urls(root: str, exclude_dirs: set[str], include_ext: set[str]) -> dict[str, set[str]]:
    """Walk the tree and aggregate every URL with the files it appears in."""
    aggregated: dict[str, set[str]] = {}
    files_scanned = 0
    for file_path in iter_text_files(root, exclude_dirs, include_ext):
        files_scanned += 1
        for url, sources in find_urls_in_file(file_path, URL_REGEX).items():
            aggregated.setdefault(url, set()).update(sources)
    return aggregated, files_scanned


# --- Probing -----------------------------------------------------------------

def check_url(url: str, timeout: float) -> UrlResult:
    """Probe *url* with a HEAD request, falling back to GET on failure."""
    # Filter placeholder hosts without importing urllib.parse for every URL.
    host = url.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0].lower()
    if host in SKIP_HOSTS or host.endswith(".local"):
        return UrlResult(url=url, status=None, ok=True, note="skipped (placeholder host)")

    headers = {"User-Agent": USER_AGENT}
    # URLs with non-ASCII path segments (e.g. CJK characters) must be quoted
    # before being handed to urllib, otherwise the underlying socket layer
    # raises a UnicodeEncodeError on the host component.
    request_url = normalize_url(url)
    for method in ("HEAD", "GET"):
        try:
            req = request.Request(request_url, headers=headers, method=method)
            with request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", resp.getcode())
                if 200 <= status < 400:
                    return UrlResult(url=url, status=status, ok=True, note=f"{method} OK")
        except error.HTTPError as exc:
            # Some servers reject HEAD (405). Try GET before giving up.
            if method == "HEAD" and exc.code in (405, 403, 400):
                continue
            return UrlResult(url=url, status=exc.code, ok=False,
                             note=f"{method} HTTPError {exc.code}")
        except error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            return UrlResult(url=url, status=None, ok=False, note=f"{method} URLError: {reason}")
        except (socket.timeout, TimeoutError) as exc:
            return UrlResult(url=url, status=None, ok=False,
                             note=f"{method} timeout after {timeout}s")
        except Exception as exc:  # noqa: BLE001 — we want every probe to return a result
            return UrlResult(url=url, status=None, ok=False,
                             note=f"{method} error: {type(exc).__name__}: {exc}")
    return UrlResult(url=url, status=None, ok=False, note="exhausted HEAD/GET")


def probe_all(urls: Iterable[str], timeout: float, workers: int) -> list[UrlResult]:
    """Probe every URL concurrently, preserving the input order in the output."""
    url_list = list(urls)
    results: dict[str, UrlResult] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check_url, url, timeout): url for url in url_list}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                results[url] = fut.result()
            except Exception as exc:  # noqa: BLE001
                results[url] = UrlResult(url=url, status=None, ok=False,
                                         note=f"executor error: {type(exc).__name__}: {exc}")
    return [results[url] for url in url_list]


# --- Reporting ---------------------------------------------------------------

def format_report(results: list[UrlResult], files_scanned: int, sources: dict[str, set[str]]) -> str:
    total = len(results)
    ok = [r for r in results if r.ok]
    broken = [r for r in results if not r.ok]
    skipped = [r for r in ok if r.note.startswith("skipped")]

    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("URL Check Report")
    lines.append("=" * 72)
    lines.append(f"Files scanned : {files_scanned}")
    lines.append(f"Unique URLs   : {total}")
    lines.append(f"OK            : {len(ok) - len(skipped)}")
    lines.append(f"Skipped       : {len(skipped)}")
    lines.append(f"Broken        : {len(broken)}")
    lines.append("")

    if broken:
        lines.append("-" * 72)
        lines.append("Broken URLs")
        lines.append("-" * 72)
        for r in broken:
            lines.append(f"[{r.status or '---'}] {r.url}")
            lines.append(f"      note : {r.note}")
            sample = sorted(sources.get(r.url, set()))[:3]
            if sample:
                shown = " , ".join(os.path.relpath(p) for p in sample)
                more = len(sources.get(r.url, set())) - len(sample)
                suffix = f" (+{more} more)" if more > 0 else ""
                lines.append(f"      in   : {shown}{suffix}")
        lines.append("")

    if skipped:
        lines.append("-" * 72)
        lines.append("Skipped (placeholder hosts)")
        lines.append("-" * 72)
        for r in skipped:
            lines.append(f"  {r.url}")
        lines.append("")

    lines.append("=" * 72)
    if broken:
        lines.append(f"Result: FAIL — {len(broken)} broken URL(s) found.")
    else:
        lines.append(f"Result: PASS — all {len(ok) - len(skipped)} reachable URL(s) OK.")
    lines.append("=" * 72)
    return "\n".join(lines)


def write_step_summary(results: list[UrlResult], files_scanned: int,
                       sources: dict[str, set[str]]) -> None:
    """Append a Markdown summary to GITHUB_STEP_SUMMARY if running in CI."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    total = len(results)
    ok = [r for r in results if r.ok and not r.note.startswith("skipped")]
    skipped = [r for r in results if r.note.startswith("skipped")]
    broken = [r for r in results if not r.ok]

    out = ["### 🔗 URL Check", ""]
    out.append(f"- Files scanned: **{files_scanned}**")
    out.append(f"- Unique URLs: **{total}**")
    out.append(f"- OK: **{len(ok)}** | Skipped: {len(skipped)} | Broken: **{len(broken)}**")
    out.append("")
    if broken:
        out.append("#### ❌ Broken URLs")
        out.append("")
        out.append("| Status | URL | Note | File(s) |")
        out.append("| --- | --- | --- | --- |")
        for r in broken:
            srcs = ", ".join(
                f"`{os.path.relpath(p)}`" for p in sorted(sources.get(r.url, set()))[:2]
            )
            note = r.note.replace("|", "\\|")
            out.append(f"| {r.status or '—'} | {r.url} | {note} | {srcs} |")
        out.append("")
    else:
        out.append("✅ No broken URLs detected.")
        out.append("")
    try:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(out))
    except OSError:
        pass


# --- Entry point -------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".", help="Repository root to scan (default: .)")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Per-request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                   help=f"Concurrent workers (default: {DEFAULT_WORKERS})")
    p.add_argument("--allow-fail", action="store_true",
                   help="Exit 0 even when broken URLs are found (still report them).")
    p.add_argument("--only", action="append", default=None,
                   help="Limit scan to these comma-separated globs/paths (repeatable).")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = os.path.abspath(args.root)
    exclude = set(DEFAULT_EXCLUDE_DIRS)
    include = set(DEFAULT_INCLUDE_EXT)

    if args.only:
        # When --only is given, scan just those paths but keep the same filters.
        urls: dict[str, set[str]] = {}
        files_scanned = 0
        for target in args.only:
            for t in target.split(","):
                t = t.strip()
                if not t:
                    continue
                full = os.path.join(root, t) if not os.path.isabs(t) else t
                if os.path.isdir(full):
                    for fp in iter_text_files(full, exclude, include):
                        files_scanned += 1
                        for url, srcs in find_urls_in_file(fp, URL_REGEX).items():
                            urls.setdefault(url, set()).update(srcs)
                elif os.path.isfile(full):
                    files_scanned += 1
                    for url, srcs in find_urls_in_file(full, URL_REGEX).items():
                        urls.setdefault(url, set()).update(srcs)
    else:
        urls, files_scanned = collect_urls(root, exclude, include)

    if not urls:
        print("No URLs found in the scanned files.")
        return 0

    print(f"Found {len(urls)} unique URL(s) across {files_scanned} file(s). "
          f"Probing with {args.workers} workers (timeout {args.timeout}s)...\n")
    results = probe_all(urls.keys(), args.timeout, args.workers)

    print(format_report(results, files_scanned, urls))
    write_step_summary(results, files_scanned, urls)

    broken = [r for r in results if not r.ok]
    if broken and not args.allow_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
