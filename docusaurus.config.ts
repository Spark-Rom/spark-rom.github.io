import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'SparkOS Blog',
  tagline: 'Release announcements, changelogs, and project updates',
  favicon: 'favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://spark-os.live',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  organizationName: 'Spark-Rom',
  projectName: 'SparkOSWebsite',

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: false,
        pages: false,
        blog: {
          routeBasePath: '/',
          blogTitle: 'SparkOS Release Blog',
          blogDescription: 'Official SparkOS release announcements and updates',
          postsPerPage: 12,
          showReadingTime: true,
          blogSidebarTitle: 'Recent posts',
          blogSidebarCount: 10,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl:
            'https://github.com/Spark-Rom/SparkOSWebsite/tree/main/sparkblog/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/logo.svg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'SparkOS Blog',
      logo: {
        alt: 'SparkOS Logo',
        src: 'img/logo.svg',
        srcDark: 'img/logo-dark.svg',
      },
      items: [
        {to: '/', label: 'Releases', position: 'left'},
        {to: '/tags/release', label: 'Release Notes', position: 'left'},
        {
          href: 'https://github.com/Spark-Rom',
          label: 'GitHub',
          position: 'right',
        },
        {
          href: 'https://spark-os.live',
          label: 'Main Website',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Blog',
          items: [
            {
              label: 'All posts',
              to: '/',
            },
            {
              label: 'Release notes',
              to: '/tags/release',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Telegram Community',
              href: 'https://t.me/SparkOSCommunity',
            },
            {
              label: 'Telegram Channel',
              href: 'https://t.me/SparkOSChannel',
            },
            {
              label: 'GitHub Organization',
              href: 'https://github.com/Spark-Rom',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Main Website',
              href: 'https://spark-os.live',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/Spark-Rom/SparkOSWebsite',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} SparkOS. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,

  headTags: [
    {
      tagName: 'link',
      attributes: {
        rel: 'icon',
        type: 'image/png',
        sizes: '32x32',
        href: '/favicon-32x32.png',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'icon',
        type: 'image/png',
        sizes: '16x16',
        href: '/favicon-16x16.png',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'shortcut icon',
        href: '/favicon.ico',
      },
    },
  ],
};

export default config;
