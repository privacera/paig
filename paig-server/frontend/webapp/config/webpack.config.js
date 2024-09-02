const common = require('./webpack.common');
const { merge } = require('webpack-merge');

const envs = {
	development: 'dev',
	production: 'prod'
};
/* eslint-disable global-require,import/no-dynamic-require */
const env = envs[process.env.NODE_ENV || 'development'];
const envConfig = require(`./webpack.${env}.js`);
module.exports = merge(common, envConfig);