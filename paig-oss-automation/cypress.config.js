const { defineConfig } = require("cypress");
const registerReportPortalPlugin = require('@reportportal/agent-js-cypress/lib/plugin');

const defaultConfig = {
  "invalidCred": {
    "username": "abcUser",
    "password": "abcUser1",
    "firstname": "inval@#$%^&*(",
    "lastname": "inval@#$%^&*("
  },
  "register": {
    "registeredUser": {
      "firstname": "Cypress",
      "lastname": "User",
      "username": "cypressuser",
      "email": "cypressuser@bigbiz.us"
    },
    "newuser": {
      "firstname": "cypress",
      "lastname": "user",
      "username": "cypressuser",
      "email": "cypressuser@bigbiz.us"
    },
    "longUserNames": {
      "firstname": "cypressUserWithLongFirstName",
      "lastname": "cypressUserWithLongLastName"
    }
  }
}

module.exports = defineConfig({
//  reporter: 'cypress-multi-reporters',
//  reporterOptions: {
//    configFile: 'reporter_config.json'
//  },
  defaultCommandTimeout: 20000,
  pageLoadTimeout: 100000,
  e2e: {
    setupNodeEvents(on, config) {
      const environmentName = config.env.environmentName || 'local';
      const environmentFilename = `./${environmentName}.settings.json`;

      const settings = require(environmentFilename);
      if (settings.baseUrl) {
        config.baseUrl = settings.baseUrl;
      }
      console.log('loaded settings for environment %s, env url: %s', environmentName, config.baseUrl);

      if (settings) {
        config.env = {
          ...config.env,
          ...defaultConfig,
          ...settings.env,
        }
      }

      registerReportPortalPlugin(on, config);

      // implement node event listeners here
      return config;
    },
    testIsolation: false,
    viewportHeight: 768,
    viewportWidth: 1400
  },

  component: {
    devServer: {
      framework: "react",
      bundler: "vite",
    }
  }
});
