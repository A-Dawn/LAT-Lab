import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 导入全局样式
import './assets/styles.css'
import './style.css'
import './assets/animations.css'

// 导入主题样式 - 确保在Docker环境中也能正常工作
import './assets/theme-light.css'
import './assets/theme-dark.css'
import './assets/theme-neon.css'

import { installContentStyles } from './utils/content-styles'
import './utils/toast'
import devToolsStyleLoader from './utils/devToolsStyleLoader'
import syncDevToolsLoader from './utils/syncDevToolsLoader'

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
  
  // 在Docker生产环境中，确保主题样式被正确应用
  if (import.meta.env.PROD) {
    console.log('生产环境：应用主题:', savedTheme);
    // 强制重新计算CSS变量
    document.documentElement.style.setProperty('--force-theme-update', Date.now());
  }
}

initTheme();

// 同步加载开发工具配置（在Vue挂载前）
syncDevToolsLoader.init();

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
    
    // 动态提取所有CSS变量的函数
    function extractAllCssVariables(doc) {
      const rootStyles = getComputedStyle(doc.documentElement);
      const cssVariables = [];
      const variableSet = new Set();
      
      // 方法1: 从样式表中提取所有CSS变量定义（最可靠的方法）
      try {
        const allRules = Array.from(doc.styleSheets || [])
          .flatMap(sheet => {
            try {
              return Array.from(sheet.cssRules || sheet.rules || []);
            } catch (e) {
              // 跨域样式表可能无法访问
              return [];
            }
          });
        
        allRules.forEach(rule => {
          // 处理普通规则（如:root, html等）
          if (rule.style) {
            for (let i = 0; i < rule.style.length; i++) {
              const property = rule.style[i];
              if (property.startsWith('--')) {
                variableSet.add(property);
              }
            }
          }
          // 处理 @media 规则中的变量
          if (rule.cssRules) {
            Array.from(rule.cssRules).forEach(mediaRule => {
              if (mediaRule.style) {
                for (let i = 0; i < mediaRule.style.length; i++) {
                  const property = mediaRule.style[i];
                  if (property.startsWith('--')) {
                    variableSet.add(property);
                  }
                }
              }
            });
          }
          // 处理 @supports 规则中的变量
          if (rule.type === CSSRule.SUPPORTS_RULE && rule.cssRules) {
            Array.from(rule.cssRules).forEach(supportsRule => {
              if (supportsRule.style) {
                for (let i = 0; i < supportsRule.style.length; i++) {
                  const property = supportsRule.style[i];
                  if (property.startsWith('--')) {
                    variableSet.add(property);
                  }
                }
              }
            });
          }
        });
      } catch (error) {
        console.warn('从样式表提取CSS变量时出错:', error);
      }
      
      // 方法2: 从documentElement的内联样式中提取
      try {
        const rootElement = doc.documentElement;
        if (rootElement.style) {
          for (let i = 0; i < rootElement.style.length; i++) {
            const property = rootElement.style[i];
            if (property.startsWith('--')) {
              variableSet.add(property);
            }
          }
        }
      } catch (error) {
        console.warn('从根元素内联样式提取CSS变量时出错:', error);
      }
      
      // 方法3: 从所有元素的computedStyle中提取使用的变量
      // 遍历所有元素，查找使用var()的CSS变量
      try {
        const allElements = doc.querySelectorAll('*');
        allElements.forEach(el => {
          const styles = getComputedStyle(el);
          // 检查所有CSS属性（不仅仅是常见的几个）
          // 通过遍历style对象来获取所有属性
          for (let i = 0; i < styles.length; i++) {
            const prop = styles[i];
            try {
              const value = styles.getPropertyValue(prop);
              if (value && value.includes('var(')) {
                // 提取var()中的变量名（支持嵌套var()）
                const varMatches = value.match(/var\((--[^,)]+)/g);
                if (varMatches) {
                  varMatches.forEach(match => {
                    const varName = match.replace(/var\(|\)/g, '').trim();
                    if (varName.startsWith('--')) {
                      variableSet.add(varName);
                    }
                  });
                }
              }
            } catch (e) {
              // 忽略无法访问的属性
            }
          }
        });
      } catch (error) {
        console.warn('从元素样式提取CSS变量时出错:', error);
      }
      
      // 将Set转换为数组并获取值
      variableSet.forEach(varName => {
        try {
        const value = rootStyles.getPropertyValue(varName).trim();
        if (value) {
          cssVariables.push({
            name: varName,
            value: value,
            originalValue: value,
              type: varName.includes('color') || varName.includes('Color') ? 'color' : 'text'
          });
        }
        } catch (error) {
          // 忽略无法获取的变量
        }
      });
      
      // 按变量名排序
      cssVariables.sort((a, b) => a.name.localeCompare(b.name));
      
      console.log('提取到', cssVariables.length, '个CSS变量');
      return cssVariables;
    }
    
    // 添加辅助函数到全局作用域
    window.extractElementsForDevTools = function() {
      // CSS变量 - 使用动态提取
      const cssVariables = extractAllCssVariables(document);
      
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
  
  // 检查访客模式状态
  const guestMode = localStorage.getItem('guest_mode') === 'true'
  if (guestMode) {
    store.commit('setGuestMode', true)
  }
  
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
  
  // 初始化开发工具样式加载器（立即启动，不延迟）
  try {
    // 异步加载最新配置（在后台更新，不影响首次渲染）
    devToolsStyleLoader.init().catch(error => {
      console.error('开发工具样式加载器初始化失败:', error);
    });
  } catch (error) {
    console.error('开发工具样式加载器初始化失败:', error);
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
