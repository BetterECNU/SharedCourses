const fs = require('fs');
const path = require('path');

/**
 * Simple YAML frontmatter parser.
 * Handles top-level string values in YAML frontmatter.
 */
function parseFrontmatter(content) {
  // 去除 UTF-8 BOM（部分编辑器会在文件开头插入 \uFEFF）
  const clean = content.charCodeAt(0) === 0xfeff ? content.slice(1) : content;
  const match = clean.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  const fm = {};
  for (const line of match[1].split('\n')) {
    const idx = line.indexOf(':');
    if (idx > 0) {
      const key = line.substring(0, idx).trim();
      let value = line.substring(idx + 1).trim();
      // Strip quotes
      value = value.replace(/^["']|["']$/g, '');
      fm[key] = value;
    }
  }
  return fm;
}

module.exports = function courseCodePlugin(context) {
  const docsDir = path.join(context.siteDir, 'docs');

  return {
    name: 'course-code',

    getPathsToWatch() {
      // 确保 docs 目录变更时重新执行 loadContent
      return [docsDir];
    },

    async loadContent() {
      const mapping = {};

      function scanDir(dir) {
        let entries;
        try {
          entries = fs.readdirSync(dir, { withFileTypes: true });
        } catch {
          return;
        }
        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);
          if (entry.isDirectory()) {
            scanDir(fullPath);
          } else if (entry.name.endsWith('.md') || entry.name.endsWith('.mdx') || entry.name.endsWith('.MD')) {
            try {
              const content = fs.readFileSync(fullPath, 'utf-8');
              const fm = parseFrontmatter(content);
              if (fm.course_code) {
                // Compute docId matching Docusaurus convention:
                // [relative-dir]/[filename-without-ext]
                // E.g. undergraduate/软件工程学院/线性代数/README
                const relPath = path.relative(docsDir, fullPath).replace(/\\/g, '/');
                const sourceDirName = path.posix.dirname(relPath);
                const baseName = path.posix.basename(relPath, path.posix.extname(relPath));
                const docId = sourceDirName === '.'
                  ? baseName
                  : sourceDirName + '/' + baseName;
                mapping[docId] = fm.course_code;
              }
            } catch {
              // Skip files we can't read
            }
          }
        }
      }

      scanDir(docsDir);
      return mapping;
    },

    async contentLoaded({ content, actions }) {
      actions.setGlobalData(content);
    },
  };
};
