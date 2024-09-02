const webpack = require('webpack');
const commonPaths = require('./paths');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");

let env = process.env.NODE_ENV || '';
let entryPath = commonPaths.entryPath;
let outputPath = commonPaths.outputPath;

module.exports = {
  entry: {
    bundle: ['babel-polyfill', entryPath],
    //vendor: ['react', 'react-dom', 'react-router' ]
  },
  module: {
    rules: [{
        test: /\.(js|jsx)$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        options: {
          presets: ['@babel/preset-env', '@babel/preset-react'],
          plugins: ['@babel/transform-runtime', '@babel/proposal-class-properties']
        }
      },
      /*{
        test: require.resolve("pdfmake"),
        use: "imports-loader?this=>window"
      },*/
      {
        test: /\.(png|jpg|jpeg|gif|svg)$/,
        use: [{
          loader: 'file-loader',
          options: {
            outputPath: commonPaths.imagesFolder
          }
        }]
      }, {
        test: /\.(woff|woff2|ttf|eot)(\?v=\d+\.\d+\.\d+)?$/,
        use: [{
          loader: 'file-loader',
          options: {
            outputPath: commonPaths.fontsFolder
          }
        }]
      },
      //{include: /\.json$/, loaders: ["json-loader"]},
      {
        test: /\.html$/,
        use: [{
          loader: "html-loader",
          options: {
            minimize: false
          }
        }]
      }
    ],
  },
  resolve: {
    modules: ['node_modules', commonPaths.scriptPath, commonPaths.testPath],
    extensions: ['.*', '.js', '.jsx', '.es6'],
    alias: {
      'react-dom': '@hot-loader/react-dom'
    }
  },
  plugins: [
    new webpack.ProgressPlugin(),
    new HtmlWebpackPlugin({
      template: commonPaths.indexPath,
      filename: `${outputPath}/index.html`
    }),
    new CopyPlugin({
      patterns: [
        { from: commonPaths.loginHtmlPath, to: `${outputPath}/login.html` }
      ],
    })
  ],
  performance: {
    maxAssetSize: 2000000,
    assetFilter: function(assetFilename) {
      // Function predicate that provides asset filenames
      return assetFilename.endsWith('.css') || assetFilename.endsWith('.jsx');
    }
  }
};