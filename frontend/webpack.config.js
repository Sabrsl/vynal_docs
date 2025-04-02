const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');
const webpack = require('webpack');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    mode: isProduction ? 'production' : 'development',
    entry: './src/index.js',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProduction ? '[name].[contenthash].js' : 'bundle.js',
      publicPath: '/',
      clean: true
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env', '@babel/preset-react'],
              plugins: [!isProduction && 'react-refresh/babel'].filter(Boolean),
            },
          },
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif)$/i,
          type: 'asset/resource',
        },
      ],
    },
    resolve: {
      extensions: ['.js', '.jsx'],
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: './public/index.html',
        favicon: './public/favicon.ico',
        templateParameters: {
          PUBLIC_URL: ''
        },
        minify: isProduction ? {
          removeComments: true,
          collapseWhitespace: true,
          removeRedundantAttributes: true,
          useShortDoctype: true,
          removeEmptyAttributes: true,
          removeStyleLinkTypeAttributes: true,
          keepClosingSlash: true,
          minifyJS: true,
          minifyCSS: true,
          minifyURLs: true,
        } : false
      }),
      !isProduction && new ReactRefreshWebpackPlugin(),
      new webpack.DefinePlugin({
        'process.env': JSON.stringify({
          ...process.env,
          NODE_ENV: isProduction ? 'production' : 'development',
          REACT_APP_API_URL: isProduction 
            ? 'https://api.vynaldocs.com'
            : (process.env.REACT_APP_API_URL || 'http://localhost:5000')
        }),
      }),
    ].filter(Boolean),
    devServer: {
      hot: true,
      historyApiFallback: true,
      port: 3003,
    },
    performance: {
      hints: false
    },
    devtool: isProduction ? false : 'eval-source-map',
  };
}; 