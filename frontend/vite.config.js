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
        __DEV__: JSON.stringify(process.env.NODE_ENV === 'development' || process.env.VITE_ENABLE_DEV_TOOLS === 'true')
  },
  build: {
    // 降低chunk大小警告限制，促进更好的代码分割
    chunkSizeWarningLimit: 400,
    // 确保主题文件被正确复制
    assetsDir: 'assets',
    // 生产构建优化配置
    rollupOptions: {
      // 已移除devTools排除逻辑
      input: {
        main: path.resolve(__dirname, 'index.html')
      },
      output: {
        // 确保主题文件被正确输出
        assetFileNames: (assetInfo) => {
          // 主题文件保持原文件名
          if (assetInfo.name && assetInfo.name.includes('theme-')) {
            return 'assets/[name][extname]'
          }
          // 其他资源文件
          return 'assets/[name]-[hash][extname]'
        },
        // 确保CSS文件被正确合并
        manualChunks: undefined, // 禁用手动分块，让Vite自动处理CSS
        // 其他配置保持不变...
      }
    },
    // 在生产构建时移除 console 日志（包括开发工具相关的日志）
    terserOptions: {
      compress: {
            drop_console: process.env.NODE_ENV === 'production' && process.env.VITE_ENABLE_DEV_TOOLS !== 'true',
            drop_debugger: process.env.NODE_ENV === 'production' && process.env.VITE_ENABLE_DEV_TOOLS !== 'true',
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
