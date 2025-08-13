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
import './utils/toast'

function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  
  document.documentElement.setAttribute('data-theme', savedTheme);
  document.documentElement.classList.remove('theme-light', 'theme-dark', 'theme-neon');
  document.documentElement.classList.add(`theme-${savedTheme}`);
  
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    const themeColors = {
      light: '#4361ee',
      dark: '#1e293b',
      neon: '#030613'
    };
    metaThemeColor.setAttribute('content', themeColors[savedTheme] || themeColors.light);
    }
}

initTheme();

const app = createApp(App)

app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err);
  console.info('错误组件:', vm);
  console.info('错误信息:', info);
}

// 为开发调试提供全局访问
if (import.meta.env.DEV) {
  window.__APP__ = app;
  
  // 检查是否是从开发工具中加载的页面
  const urlParams = new URLSearchParams(window.location.search);
  const isInDevTools = urlParams.get('devtools') === 'true';
  
  if (isInDevTools) {
    console.log('页面在开发工具中加载，启用跨域通信');
    
    // 添加辅助函数到全局作用域
    window.extractElementsForDevTools = function() {
      // CSS变量
      const rootStyles = getComputedStyle(document.documentElement);
      const cssVariables = [];
      
      // 主题颜色变量
      const themeVars = [
        '--primary-color', '--secondary-color', '--accent-color',
        '--bg-primary', '--bg-secondary', '--bg-elevated', '--bg-hover',
        '--text-primary', '--text-secondary', '--text-tertiary',
        '--border-color', '--card-bg', '--card-shadow',
        '--input-bg', '--input-border', '--input-text'
      ];
      
      themeVars.forEach(varName => {
        const value = rootStyles.getPropertyValue(varName).trim();
        if (value) {
          cssVariables.push({
            name: varName,
            value: value,
            originalValue: value,
            type: varName.includes('color') ? 'color' : 'text'
          });
        }
      });
      
      // 文本元素
      const textElements = [];
      
      // 查找标题元素
      document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((el, index) => {
        if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
          textElements.push({
            id: `heading-${index}`,
            selector: getUniqueSelector(el),
            description: `标题: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
            currentValue: el.textContent,
            originalValue: el.textContent
          });
        }
      });
      
      // 查找段落元素
      document.querySelectorAll('p').forEach((el, index) => {
        if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
          textElements.push({
            id: `paragraph-${index}`,
            selector: getUniqueSelector(el),
            description: `段落: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
            currentValue: el.textContent,
            originalValue: el.textContent
          });
        }
      });
      
      // 查找按钮文本
      document.querySelectorAll('button, .btn, .button').forEach((el, index) => {
        if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
          textElements.push({
            id: `button-${index}`,
            selector: getUniqueSelector(el),
            description: `按钮: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
            currentValue: el.textContent,
            originalValue: el.textContent
          });
        }
      });
      
      // 查找标签文本
      document.querySelectorAll('label').forEach((el, index) => {
        if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
          textElements.push({
            id: `label-${index}`,
            selector: getUniqueSelector(el),
            description: `标签: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
            currentValue: el.textContent,
            originalValue: el.textContent
          });
        }
      });
      
      // 布局元素
      const layoutElements = [];
      
      // 查找容器元素
      document.querySelectorAll('.container, .card, .section, .panel, main, section, article, aside').forEach((el, index) => {
        const styles = getComputedStyle(el);
        
        // 宽度
        layoutElements.push({
          id: `width-${index}`,
          selector: getUniqueSelector(el),
          property: 'width',
          description: `宽度: ${getUniqueSelector(el).split(' ')[0]}`,
          currentValue: styles.width,
          originalValue: styles.width,
          unit: 'px',
          min: 100,
          max: 2000
        });
        
        // 内边距
        layoutElements.push({
          id: `padding-${index}`,
          selector: getUniqueSelector(el),
          property: 'padding',
          description: `内边距: ${getUniqueSelector(el).split(' ')[0]}`,
          currentValue: styles.padding,
          originalValue: styles.padding,
          unit: 'px',
          min: 0,
          max: 100
        });
        
        // 外边距
        layoutElements.push({
          id: `margin-${index}`,
          selector: getUniqueSelector(el),
          property: 'margin',
          description: `外边距: ${getUniqueSelector(el).split(' ')[0]}`,
          currentValue: styles.margin,
          originalValue: styles.margin,
          unit: 'px',
          min: 0,
          max: 100
        });
        
        // 边框圆角
        layoutElements.push({
          id: `border-radius-${index}`,
          selector: getUniqueSelector(el),
          property: 'border-radius',
          description: `边框圆角: ${getUniqueSelector(el).split(' ')[0]}`,
          currentValue: styles.borderRadius,
          originalValue: styles.borderRadius,
          unit: 'px',
          min: 0,
          max: 50
        });
      });
      
      return {
        cssVariables,
        textElements,
        layoutElements
      };
    };
    
    // 生成元素的唯一选择器
    window.getUniqueSelector = function(el) {
      // 简单实现，实际项目中可能需要更复杂的算法
      if (el.id) {
        return `#${el.id}`;
      }
      
      if (el.className) {
        const classes = el.className.split(' ')
          .filter(c => c && !c.startsWith('v-'))
          .join('.');
        if (classes) {
          return `.${classes}`;
        }
      }
      
      // 如果没有ID或类，使用标签名和索引
      const siblings = Array.from(el.parentNode.children);
      const tagName = el.tagName.toLowerCase();
      const index = siblings.filter(sibling => sibling.tagName.toLowerCase() === tagName)
        .indexOf(el) + 1;
      
      return `${tagName}:nth-of-type(${index})`;
    };
    
    // 监听来自父窗口的消息
    window.addEventListener('message', (event) => {
      // 验证消息来源
      if (event.origin !== window.location.origin) return;
      
      const { action, payload } = event.data;
      
      if (action === 'extract-elements') {
        // 提取元素并回传
        if (typeof window.extractElementsForDevTools === 'function') {
          const elements = window.extractElementsForDevTools();
          window.parent.postMessage({
            action: 'elements-extracted',
            payload: elements
          }, '*');
        }
      } else if (action === 'update-style') {
        // 更新CSS变量
        document.documentElement.style.setProperty(payload.name, payload.value);
      } else if (action === 'update-text') {
        // 更新文本内容
        const element = document.querySelector(payload.selector);
        if (element) element.textContent = payload.value;
      } else if (action === 'update-layout') {
        // 更新布局属性
        const elements = document.querySelectorAll(payload.selector);
        elements.forEach(el => {
          el.style[payload.property] = payload.value;
        });
      }
    });
    
    // 通知父窗口iframe已准备好
    if (window.parent !== window) {
      window.parent.postMessage({
        action: 'iframe-ready',
        payload: { url: window.location.href }
      }, '*');
    }
  }
}

const initApp = async () => {
  app.use(router);
  app.use(store);
  
  installContentStyles(app)
  
  if (localStorage.getItem('token')) {
    console.log('发现token，尝试获取用户信息');
    try {
      await store.dispatch('fetchCurrentUser');
    } catch (error) {
      console.error('获取用户信息失败:', error);
      localStorage.removeItem('token');
    }
  } else {
    console.log('未找到token，用户未登录');
  }
  
  try {
    await store.dispatch('loadPluginExtensions');
  } catch (error) {
    console.error('加载插件扩展失败:', error);
  }
  
  app.mount('#app');
  
  console.log('LAT-LAB已启动 🚀');
}

initApp();

// 安全性注释
/**
 * 安全使用注意事项：
 * 1. v-html指令存在XSS风险，必须配合sanitizeHtml等净化函数使用
 * 2. 导入utils/sanitize.js中的净化函数来处理不可信HTML
 * 3. 对于用户输入内容，应使用strictSanitizeHtml函数进行更严格的过滤
 * 4. 对于Markdown渲染内容，应使用sanitizeMarkdown函数
 */
