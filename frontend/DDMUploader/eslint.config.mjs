import js from '@eslint/js'
import typescript from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'
import vue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import globals from 'globals'

export default [
  js.configs.recommended,
  ...vue.configs['flat/recommended'],

  {
    ignores: ['node_modules/**', 'dist/**', '*.config.js', 'vue.config.js']
  },

  {
    files: ['**/*.{js,ts,vue}'],

    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        extraFileExtensions: ['.vue']
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021
      }
    },

    plugins: {
      vue,
      '@typescript-eslint': typescript
    },

    rules: {
      ...typescript.configs.recommended.rules,
    }
  }
]