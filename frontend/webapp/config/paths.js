const path = require('path');

module.exports = {
  root: path.resolve(__dirname, '../'),
  entryPath: path.resolve(__dirname, '../app/main'),
  outputPath: path.resolve(__dirname, '../public'),
  commonAppImagesPath: path.resolve(__dirname, '../app/common-ui/images'),
  appImagesPath: path.resolve(__dirname, '../app/images'),
  scriptPath: path.resolve(__dirname, '../app'),
  testPath: path.resolve(__dirname, '../test'),
  indexPath: path.resolve(__dirname, '../index.html'),
  loginHtmlPath: path.resolve(__dirname, '../login.html'),
  imagesFolder: 'static/images',
  fontsFolder: 'styles/fonts',
  cssFolder: 'static/styles/css',
  jsFolder: 'static/js',
  host: '0.0.0.0', //'localhost',
  port: process.env.PORT || 9090,
  accountId: '',
  target: 'host:port',
  auth: 'user:password',
  cookie: 'key=value'
};