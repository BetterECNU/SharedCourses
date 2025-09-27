import React from 'react';
import clsx from 'clsx';
import { useWindowSize } from '@docusaurus/theme-common';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import DocItemPaginator from '@theme/DocItem/Paginator';
import DocVersionBanner from '@theme/DocVersionBanner';
import DocVersionBadge from '@theme/DocVersionBadge';
import DocItemFooter from '@theme/DocItem/Footer';
import DocItemTOCMobile from '@theme/DocItem/TOC/Mobile';
import DocItemTOCDesktop from '@theme/DocItem/TOC/Desktop';
import DocItemContent from '@theme/DocItem/Content';
import DocBreadcrumbs from '@theme/DocBreadcrumbs';
import ContentVisibility from '@theme/ContentVisibility';
import styles from './styles.module.css';
import Giscus from '@giscus/react';
/**
 * Decide if the toc should be rendered, on mobile or desktop viewports
 */
function useDocTOC() {
    const { frontMatter, toc } = useDoc();
    const windowSize = useWindowSize();
    const hidden = frontMatter.hide_table_of_contents;
    const canRender = !hidden && toc.length > 0;
    const mobile = canRender ? <DocItemTOCMobile /> : undefined;
    const desktop =
        canRender && (windowSize === 'desktop' || windowSize === 'ssr') ? (
            <DocItemTOCDesktop />
        ) : undefined;
    return {
        hidden,
        mobile,
        desktop,
    };
}
export default function DocItemLayout({ children }) {
    const docTOC = useDocTOC();
    const { metadata } = useDoc();
    const { hide_comment: hideComment } = metadata.frontMatter;
    return (
        <div className="row">
            <div className={clsx('col', !docTOC.hidden && styles.docItemCol)}>
                <ContentVisibility metadata={metadata} />
                <DocVersionBanner />
                <div className={styles.docItemContainer}>
                    <article>
                        <DocBreadcrumbs />
                        <DocVersionBadge />
                        {docTOC.mobile}
                        <DocItemContent>{children}</DocItemContent>
                        <DocItemFooter />
                    </article>
                    <DocItemPaginator />
                </div>
                {!hideComment && <div className={styles.commentsContainer}>
                    <Giscus
                        id="comments"
                        repo="betterecnu/sharedcourses"
                        repoId='R_kgDOMR1oyA'
                        category='General'
                        categoryId='DIC_kwDOMR1oyM4CvymM'
                        mapping="pathname"
                        strict='1'
                        term="Welcome to discuss!"
                        reactionsEnabled='1'
                        emitMetadata='0'
                        inputPosition='top'
                        theme='preferred_color_scheme'
                        lang='zh-CN'
                    />
                </div>}
            </div>
            {docTOC.desktop && <div className="col col--3">{docTOC.desktop}</div>}
        </div>
    );
}
