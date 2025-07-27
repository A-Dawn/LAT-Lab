import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 导入全局样式
import './assets/styles.css'
import './style.css'

// 导入主题样式
import './assets/theme-light.css'
import './assets/theme-dark.css'
import './assets/theme-neon.css'

import { installContentStyles } from './utils/content-styles'

/**
 * 在应用渲染前初始化主题
 * 从本地存储中获取主题设置并应用到页面
 */
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  
  // 设置HTML元素的data-theme属性
  document.documentElement.setAttribute('data-theme', savedTheme);
  
  // 移除所有可能的主题类
  document.documentElement.classList.remove('theme-light', 'theme-dark', 'theme-neon');
  
  // 添加当前主题类
  document.documentElement.classList.add(`theme-${savedTheme}`);
  
  // 设置元数据，用于PWA
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    // 根据主题设置不同的主题色
    const themeColors = {
      light: '#4361ee', // 浅色主题的主色
      dark: '#1e293b',  // 深色主题的背景色
      neon: '#030613'   // 霓虹主题的背景色
    };
    metaThemeColor.setAttribute('content', themeColors[savedTheme] || themeColors.light);
    }
}

// 初始化主题
initTheme();

// 创建Vue应用
const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err);
  console.info('错误组件:', vm);
  console.info('错误信息:', info);
  
  // 错误上报逻辑可以在这里添加
}

// 为开发调试提供全局访问
if (import.meta.env.DEV) {
  window.__APP__ = app;
}

/**
 * 初始化应用
 * 检查用户登录状态，加载插件扩展
 */
const initApp = async () => {
  // 使用路由和状态管理
  app.use(router);
  app.use(store);
  
  // 安装内容样式
  installContentStyles(app)
  
  // 如果本地存储中有token，尝试获取用户信息
  if (localStorage.getItem('token')) {
    console.log('发现token，尝试获取用户信息');
    try {
      await store.dispatch('fetchCurrentUser');
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 如果获取失败，清除token
      localStorage.removeItem('token');
    }
  } else {
    console.log('未找到token，用户未登录');
  }
  
  // 加载插件扩展
  try {
    // 始终加载插件扩展，但有些功能可能只对管理员可见
    await store.dispatch('loadPluginExtensions');
  } catch (error) {
    console.error('加载插件扩展失败:', error);
  }
  
  // 挂载应用
  app.mount('#app');
  
  console.log('LAT-LAB已启动 🚀');
}

// 启动应用
initApp();

// 安全性注释
/**
 * 安全使用注意事项：
 * 1. v-html指令存在XSS风险，必须配合sanitizeHtml等净化函数使用
 * 2. 导入utils/sanitize.js中的净化函数来处理不可信HTML
 * 3. 对于用户输入内容，应使用strictSanitizeHtml函数进行更严格的过滤
 * 4. 对于Markdown渲染内容，应使用sanitizeMarkdown函数
 */
