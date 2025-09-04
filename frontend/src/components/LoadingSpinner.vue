<template>
  <div class="loading-container" :class="containerClass">
    <!-- 半透明灰白色背景 -->
    <div class="loading-background"></div>
    
    <!-- 加载动画内容 -->
    <div class="loading-content">
      <!-- 根据类型显示不同的加载器 -->
      <div v-if="type === 'spinner'" class="loading-spinner"></div>
      <div v-else-if="type === 'gradient'" class="loading-gradient"></div>
      <div v-else-if="type === 'pulse'" class="loading-pulse"></div>
      <div v-else-if="type === 'wave'" class="loading-wave">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
      </div>
      
      <!-- 加载文本 -->
      <div v-if="text" class="loading-text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  // 加载器类型
  type: {
    type: String,
    default: 'spinner',
    validator: (value) => ['spinner', 'gradient', 'pulse', 'wave'].includes(value)
  },
  // 加载文本
  text: {
    type: String,
    default: ''
  },
  // 容器大小
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})

const currentTheme = ref('light')

// 检测当前主题
onMounted(() => {
  const detectTheme = () => {
    const htmlTheme = document.documentElement.getAttribute('data-theme')
    if (htmlTheme) {
      currentTheme.value = htmlTheme
    } else {
      // 检测系统主题偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      currentTheme.value = prefersDark ? 'dark' : 'light'
    }
  }
  
  detectTheme()
  
  // 监听主题变化
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
        detectTheme()
      }
    })
  })
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
  })
  
  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', detectTheme)
})

// 容器CSS类
const containerClass = computed(() => {
  const classes = ['loading-container']
  classes.push(`size-${props.size}`)
  classes.push(`theme-${currentTheme.value}`)
  return classes
})
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  position: relative;
  width: 100%;
}

.loading-container.size-small {
  min-height: 100px;
}

.loading-container.size-large {
  min-height: 300px;
}

/* 半透明灰白色背景 */
.loading-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(128, 128, 128, 0.3);
  z-index: -1;
}

/* 加载内容 */
.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  z-index: 1;
}

/* 加载文本 */
.loading-text {
  color: #666;
  font-size: 1rem;
  font-weight: 500;
  text-align: center;
  max-width: 200px;
}

/* 主题色旋转加载器 */
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e0e0e0;
  border-top: 3px solid #4c84ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 渐变加载器 */
.loading-gradient {
  width: 50px;
  height: 50px;
  background: conic-gradient(
    from 0deg,
    #4c84ff 0deg,
    #6366f1 120deg,
    #8b5cf6 240deg,
    #4c84ff 360deg
  );
  border-radius: 50%;
  animation: gradientSpin 1.5s linear infinite;
  position: relative;
}

.loading-gradient::before {
  content: '';
  position: absolute;
  top: 5px;
  left: 5px;
  right: 5px;
  bottom: 5px;
  background: #ffffff;
  border-radius: 50%;
}

@keyframes gradientSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 脉冲加载器 */
.loading-pulse {
  width: 40px;
  height: 40px;
  background: #4c84ff;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 波浪加载器 */
.loading-wave {
  display: flex;
  gap: 4px;
}

.loading-wave span {
  width: 4px;
  height: 20px;
  background: #4c84ff;
  border-radius: 2px;
  animation: wave 1.2s ease-in-out infinite;
}

.loading-wave span:nth-child(1) { animation-delay: 0s; }
.loading-wave span:nth-child(2) { animation-delay: 0.1s; }
.loading-wave span:nth-child(3) { animation-delay: 0.2s; }
.loading-wave span:nth-child(4) { animation-delay: 0.3s; }

@keyframes wave {
  0%, 40%, 100% {
    transform: scaleY(0.4);
  }
  20% {
    transform: scaleY(1);
  }
}

/* 尺寸调整 */
.loading-container.size-small .loading-spinner {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.loading-container.size-small .loading-gradient {
  width: 30px;
  height: 30px;
}

.loading-container.size-small .loading-gradient::before {
  top: 3px;
  left: 3px;
  right: 3px;
  bottom: 3px;
}

.loading-container.size-small .loading-pulse {
  width: 24px;
  height: 24px;
}

.loading-container.size-small .loading-wave span {
  width: 3px;
  height: 16px;
}

.loading-container.size-small .loading-text {
  font-size: 0.9rem;
}

.loading-container.size-large .loading-spinner {
  width: 60px;
  height: 60px;
  border-width: 4px;
}

.loading-container.size-large .loading-gradient {
  width: 80px;
  height: 80px;
}

.loading-container.size-large .loading-gradient::before {
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
}

.loading-container.size-large .loading-pulse {
  width: 60px;
  height: 60px;
}

.loading-container.size-large .loading-wave span {
  width: 6px;
  height: 30px;
}

.loading-container.size-large .loading-text {
  font-size: 1.2rem;
}

/* 主题特定样式 */
.loading-container.theme-dark .loading-text {
  color: rgba(255, 255, 255, 0.8);
}

.loading-container.theme-dark .loading-background {
  background: rgba(64, 64, 64, 0.4);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .loading-container {
    min-height: 150px;
  }
  
  .loading-container.size-large {
    min-height: 200px;
  }
}

/* 自动播放动画 */
.loading-container {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 