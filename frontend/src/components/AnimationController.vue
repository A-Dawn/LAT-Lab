<template>
  <div class="animation-controller">
    <!-- 动画性能监控面板 -->
    <div v-if="showDebugPanel" class="animation-debug-panel">
      <h4>动画性能监控</h4>
      <div class="debug-info">
        <p><strong>当前动画:</strong> {{ currentTransition }}</p>
        <p><strong>动画时长:</strong> {{ transitionDuration }}ms</p>
        <p><strong>设备性能:</strong> {{ isSlowDevice ? '低' : '正常' }}</p>
        <p><strong>减少动画偏好:</strong> {{ prefersReducedMotion ? '是' : '否' }}</p>
        <p><strong>当前主题:</strong> {{ currentTheme }}</p>
      </div>
      <div class="debug-controls">
        <button @click="toggleAnimations" class="debug-btn">
          {{ userPreferences.enableAnimations ? '禁用动画' : '启用动画' }}
        </button>
        <button @click="cycleAnimationSpeed" class="debug-btn">
          速度: {{ userPreferences.animationSpeed }}
        </button>
      </div>
    </div>

    <!-- 动画设置按钮 -->
    <button 
      v-if="showDebugButton"
      @click="toggleDebugPanel" 
      class="animation-debug-toggle"
      :title="showDebugPanel ? '隐藏动画设置' : '显示动画设置'"
    >
      🎬
    </button>

    <!-- 动画性能指示器 -->
    <div v-if="showPerformanceIndicator" class="performance-indicator">
      <div class="indicator-dot" :class="{ 'low-performance': isSlowDevice }"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { usePageTransition } from '../composables/usePageTransition'

const props = defineProps({
  showDebugButton: {
    type: Boolean,
    default: false
  },
  showPerformanceIndicator: {
    type: Boolean,
    default: true
  }
})

const store = useStore()
const showDebugPanel = ref(false)

const {
  currentTransition,
  transitionDuration,
  prefersReducedMotion,
  isSlowDevice,
  userPreferences,
  updatePreferences
} = usePageTransition()

// 当前主题
const currentTheme = computed(() => {
  const html = document.documentElement
  return html.getAttribute('data-theme') || 'light'
})

// 切换调试面板
const toggleDebugPanel = () => {
  showDebugPanel.value = !showDebugPanel.value
}

// 切换动画启用状态
const toggleAnimations = () => {
  updatePreferences({
    enableAnimations: !userPreferences.value.enableAnimations
  })
}

// 循环切换动画速度
const cycleAnimationSpeed = () => {
  const speeds = ['slow', 'normal', 'fast']
  const currentIndex = speeds.indexOf(userPreferences.value.animationSpeed)
  const nextIndex = (currentIndex + 1) % speeds.length
  updatePreferences({
    animationSpeed: speeds[nextIndex]
  })
}

// 监听主题变化，更新动画变量
watch(currentTheme, (newTheme) => {
  // 主题切换时添加过渡效果
  const html = document.documentElement
  html.classList.add('theme-transitioning')
  
  setTimeout(() => {
    html.classList.remove('theme-transitioning')
  }, 300)
})

// 性能监控
const performanceMetrics = ref({
  frameRate: 60,
  animationCount: 0,
  lastUpdate: Date.now()
})

// 监控动画性能
const monitorPerformance = () => {
  if (typeof window !== 'undefined' && 'requestAnimationFrame' in window) {
    let lastTime = performance.now()
    let frameCount = 0
    
    const measureFrameRate = (currentTime) => {
      frameCount++
      
      if (currentTime - lastTime >= 1000) {
        performanceMetrics.value.frameRate = frameCount
        frameCount = 0
        lastTime = currentTime
      }
      
      requestAnimationFrame(measureFrameRate)
    }
    
    requestAnimationFrame(measureFrameRate)
  }
}

onMounted(() => {
  monitorPerformance()
  
  // 在开发环境中显示调试按钮
  if (import.meta.env.DEV) {
    showDebugPanel.value = true
  }
})

// 暴露方法给父组件
defineExpose({
  toggleDebugPanel,
  toggleAnimations,
  cycleAnimationSpeed,
  performanceMetrics: computed(() => performanceMetrics.value)
})
</script>

<style scoped>
.animation-controller {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  pointer-events: none;
}

.animation-debug-panel {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--card-shadow);
  backdrop-filter: blur(10px);
  pointer-events: auto;
  min-width: 280px;
  max-width: 320px;
}

.animation-debug-panel h4 {
  margin: 0 0 15px 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.debug-info p {
  margin: 8px 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.debug-info strong {
  color: var(--text-primary);
}

.debug-controls {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.debug-btn {
  background: var(--button-bg);
  border: 1px solid var(--border-color);
  color: var(--button-text);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  pointer-events: auto;
}

.debug-btn:hover {
  background: var(--button-bg-hover);
  transform: translateY(-1px);
}

.animation-debug-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  box-shadow: var(--card-shadow);
  transition: all 0.3s ease;
  pointer-events: auto;
  z-index: 10001;
}

.animation-debug-toggle:hover {
  transform: scale(1.1);
  box-shadow: var(--card-shadow-hover);
}

.performance-indicator {
  position: fixed;
  top: 70px;
  right: 20px;
  pointer-events: auto;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--success-color);
  box-shadow: 0 0 8px rgba(var(--success-color-rgb), 0.5);
  animation: pulse 2s ease-in-out infinite;
}

.indicator-dot.low-performance {
  background: var(--warning-color);
  box-shadow: 0 0 8px rgba(var(--warning-color-rgb), 0.5);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

/* 主题特定样式 */
[data-theme="neon"] .animation-debug-panel {
  background: rgba(13, 16, 44, 0.9);
  border-color: var(--primary-color);
  box-shadow: 0 0 20px rgba(var(--primary-color-rgb), 0.2);
}

[data-theme="neon"] .animation-debug-toggle {
  background: var(--primary-color);
  box-shadow: 0 0 15px rgba(var(--primary-color-rgb), 0.4);
}

[data-theme="neon"] .debug-btn {
  background: rgba(var(--primary-color-rgb), 0.1);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

[data-theme="neon"] .debug-btn:hover {
  background: rgba(var(--primary-color-rgb), 0.2);
  box-shadow: 0 0 10px rgba(var(--primary-color-rgb), 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .animation-controller {
    top: 10px;
    right: 10px;
  }
  
  .animation-debug-panel {
    min-width: 250px;
    max-width: 280px;
    padding: 15px;
  }
  
  .debug-controls {
    flex-direction: column;
  }
  
  .debug-btn {
    width: 100%;
  }
}
</style> 