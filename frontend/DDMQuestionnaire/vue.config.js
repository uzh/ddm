const BundleTracker = require('webpack-bundle-tracker');
const path = require('path');

const pages = {
    'ddm_questionnaire_frontend': {
        entry: './src/questionnaire.ts',
        chunks: ['chunk-vendors']
    }
}

module.exports = {
    pages: pages,
    filenameHashing: false,
    runtimeCompiler: true,
    publicPath: '/static/ddm_core/frontend/questionnaire',
    outputDir: path.resolve('../../ddm/core/static/ddm_core/frontend/questionnaire'),

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
            __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
          })
          return definitions
        })

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
                path: '../../ddm/core/static/ddm_core/frontend/questionnaire',
                relativePath: true
            }]);

        config.resolve.alias
            .set('@questionnaire', path.resolve(__dirname, './src'))
            .set('__STATIC__', 'static');
    },

    pluginOptions: {
      i18n: {
        locale: 'en',
        fallbackLocale: 'en',
        localeDir: 'locales',
        enableLegacy: true,
        compositionOnly: false,
        runtimeOnly: false,
        fullInstall: true,
      }
    }
};
