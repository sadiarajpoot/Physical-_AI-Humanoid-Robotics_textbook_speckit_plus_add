// @ts-check
// `@type` JSDoc annotations allow IDEs and type-checking tools to autocomplete
// and validate function arguments and return values, enhancing code quality.

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'An Interactive Book for AI and Computer Science Students',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-username.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub Pages, this is usually '/<project-name>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'your-username', // Usually your GitHub org/user name.
  projectName: 'grok', // Usually your repo name.
  trailingSlash: false,
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: '/docs', // Serve docs at /docs instead of root
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/your-username/your-project-name/tree/main/docs',
        },
        blog: false, // Disable blog
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themes: [
    // ... Your other themes.
  ],

  plugins: [
    // Plugin to add the chatbot to the site
    async function myPlugin(context, options) {
      return {
        name: 'docusaurus-plugin-chatbot',
        configureWebpack(config, isServer, utils) {
          return {
            resolve: {
              fallback: {
                path: require.resolve('path-browserify'),
              },
            },
          };
        },
        loadContent: async function () {
          // This method is called during the content load phase.
          // You can fetch remote content here.
          return {};
        },
        contentLoaded: async function ({ content, actions }) {
          const { setGlobalData } = actions;
          setGlobalData({
            chatbotEnabled: true,
          });
        },
      };
    },
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        style: 'dark',
        title: 'Physical AI & Humanoid Robotics',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: '📖 Book',
          },
          {
            href: 'https://github.com/your-username/your-project-name',
            label: '🐙 GitHub',
            position: 'right',
          },
        ],
      },
      prism: {
        theme: require('prism-react-renderer').themes.vsLight, // Changed to a more modern theme
        darkTheme: require('prism-react-renderer').themes.vsDark,
        additionalLanguages: ['python', 'bash', 'json', 'yaml', 'docker'], // Added more languages
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      announcementBar: {
        id: 'announcement-bar',
        content:
          '📘 <strong>Welcome to Physical AI & Humanoid Robotics!</strong> Ask our AI assistant anything about the book content using the chat widget in the bottom-right corner.',
        backgroundColor: '#667eea',
        textColor: '#ffffff',
        isCloseable: true,
      },
    }),
};

module.exports = config;