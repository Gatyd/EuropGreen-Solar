export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: process.env.NODE_ENV === 'development' },
  modules: ["@nuxt/eslint", "@nuxt/icon", "@nuxt/ui-pro", "@pinia/nuxt"],
  css: ["~/assets/css/main.css"],
  ui: {
    colorMode: false,
  },
  runtimeConfig: {
    proxyUrl: process.env.PROXY_URL || "http://localhost:8000/"
  },
});