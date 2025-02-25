const { defineConfig } = require("cypress");

module.exports = defineConfig({
  defaultCommandTimeout: 20000,
  pageLoadTimeout: 100000,
  e2e: {
    setupNodeEvents(on, config) {

        const environmentName = config.env.environmentName || 'local';
        const environmentFilename = `./cypress/fixtures/${environmentName}.settings.json`;

        const settings = require(environmentFilename);
        if (settings.baseUrl) {
          config.baseUrl = settings.baseUrl;
        }
        console.log('loaded settings for environment %s, env url: %s', environmentName, config.baseUrl);

        if (settings) {
          config.env = {
            ...config.env,
            ...settings.env,
          }
        }
        console.log('config', config)

        // implement node event listeners here
        return config;
    },
    viewportHeight: 768,
    viewportWidth: 1424,
    testIsolation: false
  }
});
