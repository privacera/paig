module.exports = {
    "sourceType": "unambiguous",
    "presets": [
        "airbnb",
        "@babel/preset-env",
        "@babel/preset-react"
    ],
    "plugins": [
        "@babel/plugin-transform-runtime",
        ["@babel/plugin-proposal-decorators", { "legacy": true }],
        "@babel/plugin-syntax-dynamic-import",
        "@babel/plugin-proposal-class-properties",
        "@babel/plugin-proposal-export-namespace-from",
        "@babel/plugin-proposal-throw-expressions",
        "@babel/transform-flow-strip-types",
        "@babel/plugin-transform-modules-commonjs",
        "@babel/plugin-transform-react-constant-elements",
        "transform-es2015-spread",
        "react-hot-loader/babel",
        "transform-async-to-generator",
        ["module:babel-root-slash-import", {
            "rootPathSuffix": "./app"
        }]
    ]
}