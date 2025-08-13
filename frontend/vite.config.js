import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  define: {
    // 确保环境变量在构建时被正确替换
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development')
  },
  build: {
    // 降低chunk大小警告限制，促进更好的代码分割
    chunkSizeWarningLimit: 400,
    // 生产构建优化配置
    rollupOptions: {
      external: (id) => {
        // 在生产构建时排除开发工具相关模块
        if (process.env.NODE_ENV === 'production') {
          return id.includes('DevTools') || id.includes('devTools') || id.includes('dev-tools')
        }
        return false
      },
      output: {
        manualChunks: (id) => {
          // 将开发工具相关代码分离到独立的 chunk 中，便于在生产环境下完全移除
          if (id.includes('DevTools') || id.includes('devTools')) {
            return 'dev-tools'
          }
          
          // 将 node_modules 中的第三方库进行细粒度分离
          if (id.includes('node_modules')) {
            // Vue 核心
            if (id.includes('vue/dist') || id.includes('@vue/shared') || id.includes('@vue/reactivity')) {
              return 'vue-core'
            }
            // Vue 路由
            if (id.includes('vue-router')) {
              return 'vue-router'
            }
            // Vuex 状态管理
            if (id.includes('vuex')) {
              return 'vuex'
            }
            // 代码高亮库（通常较大）
            if (id.includes('highlight.js')) {
              return 'highlight'
            }
            // Markdown解析器
            if (id.includes('marked')) {
              return 'marked'
            }
            // HTTP客户端
            if (id.includes('axios')) {
              return 'axios'
            }
            // HTML清理库
            if (id.includes('dompurify')) {
              return 'dompurify'
            }
            // UI 组件库和样式
            if (id.includes('element-plus') || id.includes('ant-design') || id.includes('bootstrap')) {
              return 'ui-vendor'
            }
            // 工具库
            if (id.includes('lodash') || id.includes('moment') || id.includes('dayjs')) {
              return 'utils-vendor'
            }
            // 编辑器相关
            if (id.includes('monaco') || id.includes('codemirror') || id.includes('ace')) {
              return 'editor-vendor'
            }
            // 其他第三方库
            return 'vendor'
          }
          
          // 管理员相关页面分离
          if (id.includes('/views/admin/')) {
            return 'admin'
          }
          
          // 组件分离
          if (id.includes('/components/')) {
            return 'components'
          }
          
          // 服务和工具分离
          if (id.includes('/services/') || id.includes('/utils/')) {
            return 'services'
          }
        }
      }
    },
    // 在生产构建时移除 console 日志（包括开发工具相关的日志）
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: process.env.NODE_ENV === 'production',
        // 移除开发环境相关的死代码
        dead_code: true,
        unused: true
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('代理请求错误', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('发送请求到:', proxyReq.path);
          });
        }
      },
      '/uploads': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    },
    host: '0.0.0.0',  // 允许外部访问
    port: 5173        // 明确指定端口
  }
})
