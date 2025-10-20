import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import {
    useDocById,
    findFirstSidebarItemLink,
} from '@docusaurus/plugin-content-docs/client';
import { usePluralForm } from '@docusaurus/theme-common';
import isInternalUrl from '@docusaurus/isInternalUrl';
import { translate } from '@docusaurus/Translate';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import CourseCodeTag from './CourseCodeTag';
function useCategoryItemsPlural() {
    const { selectMessage } = usePluralForm();
    return (count) =>
        selectMessage(
            count,
            translate(
                {
                    message: '1 item|{count} items',
                    id: 'theme.docs.DocCard.categoryDescription.plurals',
                    description:
                        'The default description for a category card in the generated index about how many items this category includes',
                },
                { count },
            ),
        );
}
function CardContainer({ className, href, children }) {
    return (
        <Link
            href={href}
            className={clsx('card padding--lg', styles.cardContainer, className)}>
            {children}
        </Link>
    );
}
function CardLayout({ className, href, icon, title, description }) {
    // 检查是否以"课程代码:"开头
    const courseCodePrefix = '课程代码:';
    let courseCode = null;
    let displayDescription = description;

    if (description && description.startsWith(courseCodePrefix)) {
        courseCode = description.substring(courseCodePrefix.length).trim();
        displayDescription = null; // 不显示原始描述
    }

    return (
        <CardContainer href={href} className={className}>
            <Heading
                as="h2"
                className={clsx('text--truncate', styles.cardTitle)}
                title={title}>
                {icon} {title}
            </Heading>
            {displayDescription && (
                <p
                    className={clsx('text--truncate', styles.cardDescription)}
                    title={displayDescription}>
                    {displayDescription}
                </p>
            )}
            {courseCode && <CourseCodeTag code={courseCode} />}
        </CardContainer>
    );
}
function CardCategory({ item }) {
    const href = findFirstSidebarItemLink(item);
    const categoryItemsPlural = useCategoryItemsPlural();
    // Unexpected: categories that don't have a link have been filtered upfront
    if (!href) {
        return null;
    }
    const ReadMeSubfix = href.endsWith('/') ? 'README' : '/README';
    const docId = href.substring(6) + ReadMeSubfix;
    let doc;
    try {
        doc = useDocById(docId ?? undefined);
    } catch (e) {
        doc = null;
    }
    console.log(item.description, doc?.description);
    return (
        <CardLayout
            className={item.className}
            href={href}
            icon="🗃️"
            title={item.label}
            description={item.description ?? doc?.description ?? categoryItemsPlural(item.items.length)}
        />
    );
}
function CardLink({ item }) {
    const icon = isInternalUrl(item.href) ? '📄️' : '🔗';
    const doc = useDocById(item.docId ?? undefined);
    return (
        <CardLayout
            className={item.className}
            href={item.href}
            icon={icon}
            title={item.label}
            description={item.description ?? doc?.description}
        />
    );
}
export default function DocCard({ item }) {
    switch (item.type) {
        case 'link':
            return <CardLink item={item} />;
        case 'category':
            return <CardCategory item={item} />;
        default:
            throw new Error(`unknown item type ${JSON.stringify(item)}`);
    }
}
