export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: false },
  modules: ["@nuxt/ui-pro", "@nuxt/eslint", "@pinia/nuxt"],
  css: ["~/assets/css/main.css"],
  ui: {
    colorMode: false,
  },
  runtimeConfig: {
    proxyUrl: process.env.PROXY_URL || "http://localhost:8000/"
  },
});