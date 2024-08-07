const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    baseUrl: "https://main-portal.dev.paig.ai",
    viewportHeight: 768,
    viewportWidth: 1424
  }
});
