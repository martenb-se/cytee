const path = require("path");
const webpack = require("webpack");
const HTMLWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  mode: 'development',
  entry: path.join(__dirname, 'src/index.jsx'),
  output: {
    filename: "bundle.js",
    path: path.resolve("dist"),
    publicPath: "/",
  },
  module: {
    rules:[
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: "babel-loader"
      },
      {
        test: /\.html$/,
        use: "html-loader"
      },
      /*Choose only one of the following two: if you're using 
      plain CSS, use the first one, and if you're using a
      preprocessor, in this case SASS, use the second one*/
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.scss$/,
        use:[
          "style-loader",
          "css-loader",
          "sass-loader"
        ],
      },
    ], 
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'dist')
    },
    historyApiFallback: true,
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000',
      '/sock': {
        target: 'ws://localhost:5000',
        ws: true},
      // TODO: Only used for testing, remove later.
      '/test-socket': 'http://localhost:5000'
    },
  },
  resolve: {
    // allows us to do absolute imports from "src"
    modules: [path.join(__dirname, 'src'), 'node_modules'],
    extensions: ['*', '.js', '.jsx'],
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new HTMLWebpackPlugin({
      template: path.join(__dirname, 'src/index.html'),
      favicon: path.join(__dirname, 'src/favicon.ico'),
    })
  ]
}
