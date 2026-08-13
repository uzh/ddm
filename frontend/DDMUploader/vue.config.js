const BundleTracker = require('webpack-bundle-tracker');
const VueI18nPlugin = require('@intlify/unplugin-vue-i18n/webpack');
const path = require('path');

const pages = {
  'ddm_uploader_frontend': {
    entry: './src/main.ts',
    chunks: ['chunk-vendors']
  }
}

const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  pages: pages,
  filenameHashing: false,
  runtimeCompiler: false,
  publicPath: '/static/ddm_core/frontend/uploader',
  outputDir: path.resolve('../../ddm/core/static/ddm_core/frontend/uploader'),

  configureWebpack: {
    plugins: [
      VueI18nPlugin({
        include: [path.resolve(__dirname, './src/locales/**')],
        runtimeOnly: true,
      }),
    ],
  },

  devServer: {
    hot: false,
    devMiddleware: {
      writeToDisk: true, // Write files to disk in dev mode, so Django can serve the assets
    }
  },

  chainWebpack: config => {
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0], {
        __VUE_OPTIONS_API__: 'true',
        __VUE_PROD_DEVTOOLS__: 'false',
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
        // @intlify/unplugin-vue-i18n's own webpack DefinePlugin call doesn't set these
        // (verified via `vue-cli-service inspect`), so without this vue-i18n falls
        // back to its default of JIT-compiling messages at runtime (needs eval).
        __INTLIFY_JIT_COMPILATION__: 'false',
        __INTLIFY_DROP_MESSAGE_COMPILER__: 'true',
      })
      return definitions
    })

    config
      .plugin('copy-locales')
      .use(CopyWebpackPlugin, [{
        patterns: [
          {
            from: path.resolve(__dirname, 'src/locales'),
            to: 'locale',
            globOptions: {
              ignore: ['**/*.js']
            }
          }
        ]
      }]);

    config.optimization
      .splitChunks({
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'chunk-vendors',
            chunks: 'all',
            priority: 1
          },
        },
      });

    Object.keys(pages).forEach(page => {
      config.plugins.delete(`html-${page}`);
      config.plugins.delete(`preload-${page}`);
      config.plugins.delete(`prefetch-${page}`);
    })

    config
      .plugin('BundleTracker')
      .use(BundleTracker, [{
        filename: 'webpack-stats.json',
        path: '../../ddm/core/static/ddm_core/frontend/uploader',
        relativePath: true
      }]);

    config.resolve.alias
      .set('@uploader', path.resolve(__dirname, './src'))
      .set('__STATIC__', 'static')
      // @intlify/unplugin-vue-i18n's own alias injection (via its internal
      // webpack(compiler) hook) doesn't reliably land in vue-cli-service's
      // resolved config (verified via `vue-cli-service inspect` — no
      // vue-i18n entry appears in resolve.alias), so set it explicitly here
      // instead, the same way the other aliases above are set.
      .set('vue-i18n$', 'vue-i18n/dist/vue-i18n.runtime.esm-bundler.js');
  },
};
