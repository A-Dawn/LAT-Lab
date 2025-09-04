<template>
  <div class="theme-switch">
    <button 
      class="theme-option" 
      :class="{ 'active': currentTheme === 'light' }" 
      @click="setTheme('light')" 
      title="浅色主题"
    >
      <span class="theme-icon light-icon">☀️</span>
    </button>
    
    <button 
      class="theme-option" 
      :class="{ 'active': currentTheme === 'dark' }" 
      @click="setTheme('dark')" 
      title="深色主题"
    >
      <span class="theme-icon dark-icon">🌙</span>
    </button>
    
    <button 
      class="theme-option" 
      :class="{ 'active': currentTheme === 'neon' }" 
      @click="setTheme('neon')" 
      title="霓虹主题"
    >
      <span class="theme-icon neon-icon">🌈</span>
    </button>
  </div>
</template>

<script>
export default {
  name: 'ThemeSwitch',
  data() {
    return {
      currentTheme: localStorage.getItem('theme') || 'light',
      themeTransitionStyle: null
    };
  },
  mounted() {
    this.applyTheme(this.currentTheme);
    
    // 创建过渡样式元素
    this.createTransitionStyle();
    
    // 处理系统主题变化
    this.setupSystemThemeListener();
  },
  methods: {
    setTheme(theme) {
      // 如果是相同主题则不切换
      if (this.currentTheme === theme) return;
      
      // 先禁用过渡效果
      this.disableTransitions();
      
      // 应用新主题
      this.currentTheme = theme;
      localStorage.setItem('theme', theme);
      this.applyTheme(theme);
      
      // 稍后恢复过渡效果
      setTimeout(() => {
        this.enableTransitions();
      }, 50);
    },
    applyTheme(theme) {
      // 移除所有主题类名，添加新的主题类名
      document.documentElement.classList.remove('theme-light', 'theme-dark', 'theme-neon');
      document.documentElement.classList.add(`theme-${theme}`);
      
      // 设置 data-theme 属性
      document.documentElement.setAttribute('data-theme', theme);
      
      // 在Docker生产环境中，主题样式已经打包，不需要动态加载CSS文件
      if (import.meta.env.PROD) {
        console.log('生产环境：主题样式已打包，无需动态加载');
        // 触发自定义事件，通知应用主题已更改
        this.$emit('theme-changed', theme);
        return;
      }
      
      // 开发环境：动态加载CSS主题文件
      const cssFiles = ['theme-light.css', 'theme-dark.css', 'theme-neon.css'];
      cssFiles.forEach(file => {
        const linkId = `theme-${file.replace('.css', '')}`;
        let linkElement = document.getElementById(linkId);
        
        if (!linkElement) {
          linkElement = document.createElement('link');
          linkElement.id = linkId;
          linkElement.rel = 'stylesheet';
          // 修复路径问题：在开发环境中使用正确的路径
          const basePath = '/src/assets/';
          linkElement.href = basePath + file;
          document.head.appendChild(linkElement);
        }
        
        // 激活当前主题的CSS，禁用其他主题的CSS
        if (file === `theme-${theme}.css`) {
          linkElement.disabled = false;
        } else {
          linkElement.disabled = true;
        }
      });
      
      // 触发自定义事件，通知应用主题已更改
      this.$emit('theme-changed', theme);
    },
    
    // 创建过渡样式元素
    createTransitionStyle() {
      this.themeTransitionStyle = document.createElement('style');
      this.themeTransitionStyle.innerHTML = `
        * {
          transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease !important;
        }
      `;
      document.head.appendChild(this.themeTransitionStyle);
    },
    
    // 禁用过渡效果
    disableTransitions() {
      if (this.themeTransitionStyle) {
        this.themeTransitionStyle.remove();
      }
    },
    
    // 启用过渡效果
    enableTransitions() {
      if (this.themeTransitionStyle) {
        document.head.appendChild(this.themeTransitionStyle);
      } else {
        this.createTransitionStyle();
      }
    },
    
    // 设置系统主题监听
    setupSystemThemeListener() {
      // 如果用户未手动设置主题，则使用系统的主题模式
      if (!localStorage.getItem('theme')) {
        const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        const handleSystemThemeChange = (e) => {
          const systemTheme = e.matches ? 'dark' : 'light';
          this.setTheme(systemTheme);
        };
        
        // 添加系统主题变化的监听器
        if (darkModeMediaQuery.addEventListener) {
          darkModeMediaQuery.addEventListener('change', handleSystemThemeChange);
        } else if (darkModeMediaQuery.addListener) {
          // 兼容旧版浏览器
          darkModeMediaQuery.addListener(handleSystemThemeChange);
        }
        
        // 初始化时检查系统主题
        if (darkModeMediaQuery.matches) {
          this.setTheme('dark');
        }
      }
    }
  }
}
</script>

<style scoped>
.theme-switch {
  display: flex;
  gap: 10px;
  background-color: var(--card-bg);
  border-radius: 40px;
  padding: 4px;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.theme-option {
  background: none;
  border: none;
  cursor: pointer;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  padding: 0;
  position: relative;
  overflow: hidden;
}

.theme-option:hover {
  transform: scale(1.1);
  background-color: var(--hover-color);
}

.theme-option.active {
  background-color: var(--primary-color);
}

.theme-option.active .theme-icon {
  color: white;
  animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.theme-icon {
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

@keyframes pop {
  0% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  70% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 特殊处理霓虹主题的按钮 */
:root[data-theme="neon"] .theme-switch {
  border-color: var(--border-color);
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}

:root[data-theme="neon"] .theme-option.active {
  box-shadow: 0 0 8px rgba(var(--primary-rgb), 0.4);
}

/* 添加各个主题的独特样式 */
.theme-option .light-icon {
  color: #ffa000; /* 保持固定的主题识别颜色 */
}

.theme-option .dark-icon {
  color: #5870cb; /* 保持固定的主题识别颜色 */
}

.theme-option .neon-icon {
  color: #f900e3; /* 保持固定的主题识别颜色 */
}

/* 响应式调整 */
@media (max-width: 768px) {
  .theme-switch {
    gap: 5px;
    padding: 3px;
  }
  
  .theme-option {
    width: 30px;
    height: 30px;
  }
  
  .theme-icon {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .theme-switch {
    gap: 2px;
    padding: 2px;
  }
  
  .theme-option {
    width: 28px;
    height: 28px;
  }
  
  .theme-icon {
    font-size: 0.95rem;
  }
}
</style> 