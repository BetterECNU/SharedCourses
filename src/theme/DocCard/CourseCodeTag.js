import React from 'react';
import styles from './CourseCodeTag.module.css';

/**
 * 课程代码标签组件
 * 用于显示课程编号
 */
export default function CourseCodeTag({ code }) {
    if (!code) {
        return null;
    }

    return (
        <span className={styles.courseCodeTag}>
            {code}
        </span>
    );
}
