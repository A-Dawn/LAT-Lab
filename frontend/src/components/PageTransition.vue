<template>
  <transition 
    :name="effectiveTransitionName" 
    mode="out-in"
    @before-enter="onBeforeEnter"
    @enter="onEnter"
    @after-enter="onAfterEnter"
    @before-leave="onBeforeLeave"
    @leave="onLeave"
    @after-leave="onAfterLeave"
  >
    <div 
      :key="route.path" 
      class="page-transition-wrapper"
      :class="wrapperClasses"
    >
      <!-- 毛玻璃背景 -->
      <div 
        v-if="hasGlassBackground" 
        class="glass-background"
        :class="glassBackgroundClasses"
      ></div>
      
      <!-- 页面内容 -->
      <div class="page-content">
        <slot />
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  transitionType: {
    type: String,
    default: 'fade'
  },
  duration: {
    type: Number,
    default: 300
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const prefersReducedMotion = ref(false)
const isAnimating = ref(false)

// 检测用户是否偏好减少动画
onMounted(() => {
  if (typeof window !== 'undefined') {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    prefersReducedMotion.value = mediaQuery.matches
    mediaQuery.addEventListener('change', (e) => {
      prefersReducedMotion.value = e.matches
    })
  }
})

// 判断是否使用毛玻璃背景的动画
const hasGlassBackground = computed(() => {
  const transitionName = effectiveTransitionName.value
  return transitionName && transitionName.startsWith('glass-')
})

// 毛玻璃背景的CSS类
const glassBackgroundClasses = computed(() => {
  const transitionName = effectiveTransitionName.value
  if (!transitionName) return ''
  
  // 根据主题添加特殊类
  const theme = document.documentElement.getAttribute('data-theme') || 'light'
  if (theme === 'neon' && transitionName.includes('ripple')) {
    return 'neon-glass-ripple'
  }
  
  return ''
})

// 包装器的CSS类
const wrapperClasses = computed(() => {
  const classes = ['page-transition-wrapper']
  
  if (hasGlassBackground.value) {
    classes.push('glass-transition')
  }
  
  return classes
})

const effectiveTransitionName = computed(() => {
  if (props.disabled || prefersReducedMotion.value) {
    return 'no-transition'
  }
  return route.meta?.transition || props.transitionType
})

// 性能优化的动画钩子
const onBeforeEnter = (el) => {
  isAnimating.value = true
  // 启用硬件加速
  el.style.willChange = 'transform, opacity'
  el.style.setProperty('--transition-duration', `${props.duration}ms`)
  
  // 为毛玻璃动画添加特殊处理
  if (hasGlassBackground.value) {
    const glassBg = el.querySelector('.glass-background')
    if (glassBg) {
      glassBg.style.willChange = 'transform, opacity'
    }
  }
}

const onEnter = (el, done) => {
  // 确保动画使用当前主题色和最新的CSS变量
  nextTick(() => {
    // 添加页面加载完成动画
    el.classList.add('page-loaded')
    done()
  })
}

const onAfterEnter = (el) => {
  // 清理性能优化属性
  el.style.willChange = 'auto'
  if (hasGlassBackground.value) {
    const glassBg = el.querySelector('.glass-background')
    if (glassBg) {
      glassBg.style.willChange = 'auto'
    }
  }
  isAnimating.value = false
}

const onBeforeLeave = (el) => {
  isAnimating.value = true
  el.style.willChange = 'transform, opacity'
  el.style.setProperty('--transition-duration', `${props.duration}ms`)
  
  if (hasGlassBackground.value) {
    const glassBg = el.querySelector('.glass-background')
    if (glassBg) {
      glassBg.style.willChange = 'transform, opacity'
    }
  }
}

const onLeave = (el, done) => {
  nextTick(() => {
    done()
  })
}

const onAfterLeave = (el) => {
  el.style.willChange = 'auto'
  if (hasGlassBackground.value) {
    const glassBg = el.querySelector('.glass-background')
    if (glassBg) {
      glassBg.style.willChange = 'auto'
    }
  }
  isAnimating.value = false
}

// 暴露动画状态给父组件
defineExpose({
  isAnimating
})
</script>

<style scoped>
/* 页面过渡包装器 */
.page-transition-wrapper {
  position: relative;
  min-height: 60vh;
  overflow: hidden;
}

.page-transition-wrapper.glass-transition {
  position: relative;
}

.page-transition-wrapper.glass-transition .page-content {
  position: relative;
  z-index: 1;
}

/* 毛玻璃背景样式 */
.glass-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
}

/* 页面内容容器 */
.page-content {
  position: relative;
  z-index: 1;
}

/* 使用新的动画系统 - 与主题完美对接 */
.no-transition-enter-active, .no-transition-leave-active {
  transition: none !important;
}
.no-transition-enter-from, .no-transition-leave-to {
  opacity: 1 !important;
  transform: none !important;
}

/* 所有动画现在使用新的动画系统，与主题色完美对接 */

/* 彩色波纹动画 - 使用主题色 */
.ripple-enter-active {
  position: relative;
  overflow: hidden;
  transition: all var(--transition-duration, 500ms) ease;
}

.ripple-enter-active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at center,
    var(--primary-color, #4c84ff) 0%,
    var(--secondary-color, #6366f1) 30%,
    transparent 70%
  );
  transform: scale(0);
  opacity: 0.8;
  animation: rippleExpand var(--transition-duration, 500ms) ease-out;
  z-index: -1;
}

@keyframes rippleExpand {
  0% {
    transform: scale(0);
    opacity: 0.8;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.ripple-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.ripple-leave-active {
  transition: all var(--transition-duration, 300ms) ease;
}

.ripple-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

/* 上升动画 - 带主题色阴影，性能优化版本 */
.rise-enter-active, .rise-leave-active {
  transition: transform var(--transition-duration, 400ms) cubic-bezier(0.25, 0.8, 0.25, 1),
              opacity var(--transition-duration, 400ms) ease,
              box-shadow var(--transition-duration, 400ms) ease;
  backface-visibility: hidden;
  transform: translateZ(0);
}

.rise-enter-from {
  transform: translateY(50px) translateZ(0);
  opacity: 0;
  box-shadow: 0 10px 30px rgba(var(--primary-color-rgb, 76, 132, 255), 0.3);
}

.rise-leave-to {
  transform: translateY(-50px) translateZ(0);
  opacity: 0;
  box-shadow: 0 -10px 30px rgba(var(--primary-color-rgb, 76, 132, 255), 0.2);
}

/* 旋转动画 - 性能优化版本 */
.rotate-enter-active, .rotate-leave-active {
  transition: transform var(--transition-duration, 500ms) cubic-bezier(0.25, 0.8, 0.25, 1),
              opacity var(--transition-duration, 500ms) ease;
  backface-visibility: hidden;
  transform-style: preserve-3d;
  perspective: 1000px;
}

.rotate-enter-from {
  transform: rotateY(90deg) scale(0.8) translateZ(0);
  opacity: 0;
  transform-origin: center;
}

.rotate-leave-to {
  transform: rotateY(-90deg) scale(0.8) translateZ(0);
  opacity: 0;
  transform-origin: center;
}

/* 折叠动画 */
.fold-enter-active, .fold-leave-active {
  transition: all var(--transition-duration, 400ms) cubic-bezier(0.25, 0.8, 0.25, 1);
}

.fold-enter-from {
  transform: rotateX(-90deg);
  opacity: 0;
  transform-origin: center top;
}

.fold-leave-to {
  transform: rotateX(90deg);
  opacity: 0;
  transform-origin: center bottom;
}

/* 弹性动画 - 带主题色 */
.bounce-enter-active {
  animation: bounceIn var(--transition-duration, 600ms) cubic-bezier(0.25, 0.8, 0.25, 1);
}

.bounce-leave-active {
  animation: bounceOut var(--transition-duration, 400ms) ease-in;
}

@keyframes bounceIn {
  0% {
    transform: scale(0.3);
    opacity: 0;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
    box-shadow: 0 0 20px rgba(var(--primary-color-rgb, 76, 132, 255), 0.4);
  }
  70% {
    transform: scale(0.95);
    opacity: 0.9;
  }
  100% {
    transform: scale(1);
    opacity: 1;
    box-shadow: 0 0 10px rgba(var(--primary-color-rgb, 76, 132, 255), 0.2);
  }
}

@keyframes bounceOut {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
  100% {
    transform: scale(0);
    opacity: 0;
  }
}

/* 渐变背景动画 */
.gradient-enter-active {
  position: relative;
  transition: all var(--transition-duration, 500ms) ease;
}

.gradient-enter-active::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    var(--primary-color, #4c84ff) 0%,
    var(--secondary-color, #6366f1) 50%,
    var(--accent-color, #8b5cf6) 100%
  );
  opacity: 0;
  z-index: -1;
  animation: gradientFade var(--transition-duration, 500ms) ease-out;
}

@keyframes gradientFade {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 0.1;
  }
  100% {
    opacity: 0;
  }
}

.gradient-enter-from {
  opacity: 0;
  transform: scale(0.98);
}

.gradient-leave-active {
  transition: all var(--transition-duration, 300ms) ease;
}

.gradient-leave-to {
  opacity: 0;
  transform: scale(1.02);
}

/* 毛玻璃动画样式 */
.glass-transition {
  position: relative;
}

.glass-transition .page-content {
  position: relative;
  z-index: 1;
}

/* 霓虹主题特殊处理 */
.neon-glass-ripple {
  box-shadow: 0 0 30px rgba(var(--primary-color-rgb), 0.3);
}
</style>
