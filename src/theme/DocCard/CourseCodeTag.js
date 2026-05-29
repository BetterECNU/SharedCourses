import React from 'react';
import Link from '@docusaurus/Link';
import styles from './CourseCodeTag.module.css';

/**
 * 课程代码标签组件
 * 用于显示课程编号和 Plus 跳转入口
 */
export default function CourseCodeTag({ code, linkable = true }) {
  if (!code) {
    return null;
  }

  const plusHref = `https://plus.myecnu.org/#/course?id=${encodeURIComponent(code)}`;
  const plusIcon = (
    <svg
      className={styles.plusIconSvg}
      viewBox="0 0 16 16"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M8 3.25v9.5M3.25 8h9.5" />
    </svg>
  );
  const Wrapper = linkable ? Link : 'span';
  const wrapperProps = linkable
    ? {
      href: plusHref,
      title: '点击前往 Plus 查看开课情况',
      'aria-label': '跳转到 Plus',
    }
    : {};

  return (
    <Wrapper className={styles.courseCodeLink} {...wrapperProps}>
      <span className={styles.courseCodeTag}>
        <span className={styles.courseCodeText}>{code}</span>
      </span>
      {linkable && <span className={styles.plusIconWrapper}>
        {plusIcon}
      </span>}
    </Wrapper>
  );
}
