import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers';
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  // Electron 应用需要使用相对路径
  base: mode === 'production' ? './' : '/',
  plugins: [
    vue(),
    AutoImport({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false, // css in js
        }),
        ElementPlusResolver({
          importStyle: false, // 禁用自动导入样式，手动导入
        })],
    }),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false, // css in js
        }),
        ElementPlusResolver({
          importStyle: false, // 禁用自动导入样式，手动导入
        })],
    }),
  ],
  server: {
    hmr: {
      host: 'localhost',
      overlay: false
    },
    host: 'localhost',
    port: 5173
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 全局scss变量和mixins
        additionalData: `
          @use "@/styles/variables.scss" as *;
          @use "@/styles/mixins.scss" as *;
        `,
        // 使用现代API
        api: 'modern-compiler'
      }
    }
  },
  define: {
    // 定义环境变量
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(process.env.VITE_API_BASE_URL || 'http://localhost:8080/api'),
  },
  build: {
    // 生产构建优化
    outDir: 'dist',
    assetsDir: 'assets',
    // Electron 需要 sourcemap 用于调试
    sourcemap: mode === 'development',
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['ant-design-vue', 'element-plus'],
          'vendor-utils': ['axios', 'crypto-js']
        }
      }
    }
  }
}))
