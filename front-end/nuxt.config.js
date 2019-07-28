export default {
  mode: 'universal',
<<<<<<< HEAD
  router: {
    middleware: ['auth']
  },
=======
  /*
  router: {
    middleware: ['auth']
  },
  */
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
  /*
   ** Headers of the page
   */
  head: {
    title: process.env.npm_package_name || '',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      {
        hid: 'description',
        name: 'description',
        content: process.env.npm_package_description || ''
      }
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }]
  },
  /*
   ** Customize the progress-bar color
   */
  loading: { color: 'green' },
  /*
   ** Global CSS
   */
  css: [],
  /*
   ** Plugins to load before mounting the App
   */
  plugins: [],
  /*
   ** Nuxt.js modules
   */
  modules: [
<<<<<<< HEAD
    'semantic-ui-vue/nuxt',
    '@nuxtjs/axios',
    '@nuxtjs/pwa',
    '@nuxtjs/auth'
=======
    // Doc: https://bootstrap-vue.js.org/docs/
    'bootstrap-vue/nuxt',
    // Doc: https://axios.nuxtjs.org/usage
    '@nuxtjs/axios',
    '@nuxtjs/pwa'
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
    // '@nuxtjs/eslint-module'
  ],
  /*
   ** Axios module configuration
   ** See https://axios.nuxtjs.org/options
   */
<<<<<<< HEAD
  axios: {
    baseURL: 'http://localhost:8000'
=======
  axios: {},
  env: {
    HOST_URL: process.env.HOST_URL || 'http://127.0.0.1:5000'
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
  },
  auth: {
    strategies: {
      local: {
        endpoints: {
          login: { url: '/login', method: 'post', propertyName: 'token' },
<<<<<<< HEAD
          logout: { url: '/logout', method: 'post' },
          user: { url: '/user', method: 'get', propertyName: false }
        },
        tokenRequired: true,
        tokenType: 'token'
      }
    },
    redirect: {
      login: '/login',
      logout: '/login',
      callback: '/login',
      home: '/'
=======
          // logout: { url: '/api/auth/logout', method: 'post' },
          user: { url: '/user', method: 'get', propertyName: false }
        }
        // tokenRequired: true,
        // tokenType: 'bearer'
      }
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
    }
  },
  /*
   ** Build configuration
   */
  build: {
    /*
     ** You can extend webpack config here
     */
    extend(config, ctx) {}
  }
}
