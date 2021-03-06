module.exports = {
  siteMetadata: {
    title: 'Notify docs',
  },
  plugins: [
    'gatsby-plugin-react-helmet',
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: 'Notify docs',
        short_name: 'Notify docs',
        start_url: '/',
        background_color: '#0b0c0c',
        theme_color: '#0b0c0c',
        display: 'minimal-ui',
        icon: 'src/images/favicon.png', // This path is relative to the root of the site.
      },
    },
    {
      resolve: `gatsby-plugin-google-analytics`,
      options: {
        trackingId: 'UA-61222473-21',
        // Puts tracking script in the head instead of the body
        head: false,
        // Setting this parameter is also optional
        respectDNT: true,
        // Avoids sending pageview hits from custom paths
        exclude: [],
        siteSpeedSampleRate: 100,
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `data`,
        path: `${__dirname}/src/code-examples/`,
      },
    },
    {
      resolve: 'gatsby-source-filesystem',
      options: {
        name: 'markdown-content',
        path: `${__dirname}/src/content/`,
      },
    },
    {
      resolve: `gatsby-transformer-code-samples`,
      options: {
        name: `data`,
      },
    },
    {
      resolve: `gatsby-mdx`,
      options: {
        gatsbyRemarkPlugins: [
          {
            resolve: 'gatsby-remark-autolink-headers',
            options: {
              icon: false,
            },
            // this is deprecated but gatbsy-mdx is terrible. it even
            // documents using options, but the code looks for pluginOptions
            get pluginOptions() {
              return this.options
            },
          },
        ],
      },
    },
    {
      resolve: 'mdx-pages',
      options: {
        layout: `${__dirname}/src/mdx-layout.js`,
        name: 'markdown-content',
      },
    },
    'gatsby-plugin-styled-components',
    'gatsby-plugin-offline',
  ],
}
