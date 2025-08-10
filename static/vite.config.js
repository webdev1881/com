import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// ES импорт нашего изолятора
import vueStyleIsolator from './postcss-vue-isolator.mjs'

export default defineConfig({
  plugins: [vue()],

  build: {
    outDir: 'dist',
    emptyOutDir: true,
    lib: {
      entry: resolve(__dirname, 'src/vue/main.js'),
      name: 'VueOdooApp',
      fileName: 'js/vue-app',
      formats: ['iife']
    },
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'css/vue-app.css';
          }
          return assetInfo.name;
        },
        globals: { vue: 'Vue' },
        extend: true
      }
    },
    cssCodeSplit: false,
  },

  css: {
    postcss: {
      plugins: [
        // Упрощенный изолятор стилей
        vueStyleIsolator({
          selector: '.vue-isolated-app',
          // убираем опцию specificity - используем встроенную логику
        })
      ]
    }
  },

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/vue'),
    }
  },

  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
    '__VUE_OPTIONS_API__': true,
    '__VUE_PROD_DEVTOOLS__': false
  }
})