// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'ECNU·课栈',
  tagline: '华东师范大学课程共享计划',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://myecnu.org',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'BetterECNU', // Usually your GitHub org/user name.
  projectName: 'SharedCourses', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  plugins: [
    './plugins/course-code',
  ],

  themes: [
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
      {
        hashed: true,
        language: ["en", "zh"],
        explicitSearchResultPath: true
      },
    ],
    '@docusaurus/theme-mermaid',
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/BetterECNU/SharedCourses/tree/main',
        },
        blog: false,
        theme: {
          customCss: [
            require.resolve('katex/dist/katex.min.css'),
            './src/css/custom.css',
          ],
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'ECNU·课栈',
        logo: {
          alt: 'ECNU·课栈 Logo',
          src: 'img/logo.svg',
        },
        items: [
          { to: '/docs/', label: '课栈', position: 'left' },
          { to: '/docs/undergraduate/', label: '本科生院', position: 'left' },
          { to: '/docs/postgraduate/', label: '研究生院', position: 'left' },

          {
            href: 'https://github.com/BetterECNU/SharedCourses',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      metadata: [
        { name: 'keywords', content: 'ECNU, 华师大, 华东师范大学, 课程共享, 复习资料' },
      ],
      footer: {
        style: 'dark',
        links: [
          {
            title: '课程',
            items: [
              {
                label: '本科生院',
                to: '/docs/undergraduate/',
              },
              {
                label: '研究生院',
                to: '/docs/postgraduate/',
              },
            ],
          },
          {
            title: '社区',
            items: [
              {
                label: 'QQ 群聊',
                href: 'https://qm.qq.com/q/ARnu9JwBfq',
              },

            ],
          },
          {
            title: '更多',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/BetterECNU/SharedCourses',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} ECNU·课栈. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
  // 以下部分为启用mermaid支持
  // 具体信息请参考http://docusaurus.io/docs/next/markdown-features/diagrams
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },
};

export default config;
