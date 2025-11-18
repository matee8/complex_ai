// webpack.config.js (frontend フォルダ直下)

const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  // 1. エントリーポイント（Reactアプリの起動ファイル）
  // 以前 'index.js' だったものを 'index.tsx' に変更
  entry: './src/index.tsx',

  // 2. 出力設定
  output: {
    path: path.resolve(__dirname, 'build'), // ビルドファイルの出力先
    filename: 'bundle.js',
    publicPath: '/',
  },

  // 3. モジュール解決（最重要！）
  // どのファイルをインポート可能にするかの設定
  resolve: {
    extensions: [
      // ↓↓↓ この .ts と .tsx が必要です ↓↓↓
      '.ts',
      '.tsx', 
      '.js', 
      '.jsx', 
      '.json'
    ],
  },

  // 4. ローダー設定（最重要！）
  // TypeScript ファイルをJavaScriptに変換するためのルール
  module: {
    rules: [
      {
        // .ts または .tsx ファイルを...
        test: /\.(ts|tsx)$/,
        // 'ts-loader' または 'babel-loader' で処理する
        // （あなたのプロジェクトで 'ts-loader' を使っているか確認してください）
        use: 'ts-loader', 
        exclude: /node_modules/,
      },
      {
        // (babel-loader を使っている場合)
        // Babel で .js, .jsx, .ts, .tsx を処理する設定例
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-env',
              '@babel/preset-react',
              '@babel/preset-typescript', // ← TypeScript用プリセット
            ],
          },
        },
      },
      {
        // CSSローダーなど (省略)
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      // 他のローダー...
    ],
  },

  // 5. プラグイン
  plugins: [
    // public/index.html をテンプレートにする
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],

  // 6. 開発サーバーの設定
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    compress: true,
    port: 3000,
    historyApiFallback: true, // React Router などで 404 にならないため
  },
};