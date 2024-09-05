const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const commonPaths = require('./paths');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const autoprefixer = require('autoprefixer');

let env = process.env.NODE_ENV || '';
let outputPath = commonPaths.outputPath;

module.exports = {
  mode: 'production',
  output: {
    filename: `${commonPaths.jsFolder}/[name].[fullhash].js`,
    path: outputPath,
    chunkFilename: `${commonPaths.jsFolder}/[name].[chunkhash].js`,
  },
  module: {
    rules: [{
      //test: /\.(css|scss)$/,
      test: /\.(css)$/,
      use: [{
          loader: MiniCssExtractPlugin.loader,
          options: {
            // you can specify a publicPath here
            // by default it use publicPath in webpackOptions.output
            publicPath: '../../'
          }
        },
        'css-loader', {
          loader: 'postcss-loader',
          options: {
            sourceMap: true,
            plugins: [
              autoprefixer({
                browsers: ['last 2 versions']
              })
            ]
          }
        }
      ]
    }]
  },
  plugins: [
    new CleanWebpackPlugin([outputPath.split('/').pop()], {
      root: commonPaths.root,
    }),
    new CopyWebpackPlugin({
      patterns: [{
        from: commonPaths.commonAppImagesPath,
        to: 'static/images'
      }, {
        from: commonPaths.appImagesPath,
        to: 'static/images'
      }]
    }),
    new MiniCssExtractPlugin({
      //filename: `${commonPaths.cssFolder}/[name].css`,
      filename: `${commonPaths.cssFolder}/style.css`,
      chunkFilename: `${commonPaths.cssFolder}/[id].css`,
    })
  ],
  optimization: {
    minimize: true,
    //noEmitOnErrors: true,
    minimizer: [
      new TerserPlugin({
        parallel: true,
        terserOptions: {
          sourceMap: false,
          ecma: 6,
          compress: true,
          keep_fnames: true,
          //ie8: true,
          //safari10: true,
          mangle: {
            keep_fnames: true,
            //safari10: true
          },
          output: {
            comments: false
          },
          compress: {
            dead_code: true,
            drop_console: true
          }
        }
      })
    ],
    splitChunks: {
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    }
  }
  //devtool: 'source-map',
};
