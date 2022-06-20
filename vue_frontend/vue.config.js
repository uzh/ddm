const BundleTracker = require("webpack-bundle-tracker");
const path = require('path');

const pages = {
    'vue_uploader': {
        entry: './src/uploader.js',
        chunks: ['chunk-vendors']
    },
    'vue_questionnaire': {
        entry: './src/questionnaire.js',
        chunks: ['chunk-vendors']
    }
}

module.exports = {
    pages: pages,
    filenameHashing: false,
    productionSourceMap: false,
    publicPath: process.env.NODE_ENV === 'production'
        ? '/static/ddm/vue/'
        : '/static/ddm/vue/',
    outputDir: path.resolve('../ddm/static/ddm/vue'),

    chainWebpack: config => {

        config.optimization
            .splitChunks({
                cacheGroups: {
                    vendor: {
                        test: /[\\/]node_modules[\\/]/,
                        name: "chunk-vendors",
                        chunks: "all",
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
                filename: '../ddm/static/ddm/vue/webpack-stats.json',
                path: '../ddm/static/ddm/vue',
                relativePath: true
            }]);

        config.resolve.alias
            .set('__STATIC__', 'static')

        config.devServer
            .public('http://localhost:8080')
            .host('localhost')
            .port(8080)
            .hotOnly(true)
            .watchOptions({poll: 1000})
            .https(false)
            .headers({"Access-Control-Allow-Origin": ["*"]})

    }
};
