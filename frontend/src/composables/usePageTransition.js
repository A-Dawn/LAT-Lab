import { computed, watch, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'

/**
 * 页面切换动画的组合式函数
 * 支持根据路由选择动画类型并响应主题色变化
 * 包含性能优化和可访问性支持
 */
export function usePageTransition() {
  const route = useRoute()
  const store = useStore()
  const prefersReducedMotion = ref(false)
  const isSlowDevice = ref(false)
  const userPreferences = ref({
    enableAnimations: true,
    animationSpeed: 'normal' // 'slow', 'normal', 'fast'
  })

  // 检测设备性能和用户偏好
  onMounted(() => {
    if (typeof window !== 'undefined') {
      // 检测用户是否偏好减少动画
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      prefersReducedMotion.value = mediaQuery.matches
      mediaQuery.addEventListener('change', (e) => {
        prefersReducedMotion.value = e.matches
      })

      // 检测设备性能（简单的启发式检测）
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
      if (connection) {
        isSlowDevice.value = connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g'
      }

      // 检测硬件并发数（低核心数可能意味着较低性能）
      if (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2) {
        isSlowDevice.value = true
      }

      // 从 localStorage 加载用户偏好
      const savedPrefs = localStorage.getItem('pageTransitionPreferences')
      if (savedPrefs) {
        try {
          Object.assign(userPreferences.value, JSON.parse(savedPrefs))
        } catch (e) {
          console.warn('无法解析用户动画偏好设置')
        }
      }
    }
  })

  // 动画类型映射表 - 针对不同路由优化，与主题系统完美对接
  const transitionMap = {
    // 主页 - 使用渐变动画
    '/': 'gradient',
    // 文章相关页面 - 使用上升动画
    '/articles': 'rise',
    '/article': 'rise',
    '/write': 'rise',
    // 用户相关页面 - 使用滑动动画
    '/login': 'slide',
    '/register': 'slide',
    '/profile': 'slide',
    // 管理员页面 - 使用缩放动画
    '/admin': 'scale',
    // 插件相关页面 - 使用旋转动画
    '/plugins': 'rotate',
    '/marketplace': 'rotate',
    // 开发工具页面 - 使用弹性动画
    '/dev-tools': 'bounce',
    // 其他页面 - 使用波纹动画
    '/about': 'ripple',
    '/contact': 'ripple',
    // 特殊页面 - 使用主题特定动画
    '/verify-email': 'fade'
  }

  // 动画速度映射
  const speedMap = {
    'slow': 500,
    'normal': 300,
    'fast': 200
  }

  // 获取优化后的动画类型
  const getOptimizedTransition = (baseTransition) => {
    // 如果用户偏好减少动画或设备性能低，使用简单动画
    if (prefersReducedMotion.value || !userPreferences.value.enableAnimations) {
      return 'no-transition'
    }
    
    if (isSlowDevice.value) {
      // 在低性能设备上使用简单动画
      const simpleTransitions = ['fade', 'slide']
      return simpleTransitions.includes(baseTransition) ? baseTransition : 'fade'
    }
    
    return baseTransition
  }

  // 当前动画类型
  const currentTransition = computed(() => {
    const path = route.path
    let baseTransition = 'fade'
    
    // 先检查精确匹配
    if (transitionMap[path]) {
      baseTransition = transitionMap[path]
    } else {
      // 再检查模糊匹配
      for (const [routePath, transitionType] of Object.entries(transitionMap)) {
        if (path.startsWith(routePath) && routePath !== '/') {
          baseTransition = transitionType
          break
        }
      }
    }
    
    return getOptimizedTransition(baseTransition)
  })

  // 动画持续时间
  const transitionDuration = computed(() => {
    const baseSpeed = speedMap[userPreferences.value.animationSpeed] || 300
    
    // 在低性能设备上减少动画时间
    if (isSlowDevice.value) {
      return Math.min(baseSpeed, 200)
    }
    
    return baseSpeed
  })

  // 保存用户偏好
  const saveUserPreferences = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('pageTransitionPreferences', JSON.stringify(userPreferences.value))
    }
  }

  // 更新用户偏好
  const updatePreferences = (newPrefs) => {
    Object.assign(userPreferences.value, newPrefs)
    saveUserPreferences()
  }

  return {
    currentTransition,
    transitionDuration,
    prefersReducedMotion,
    isSlowDevice,
    userPreferences,
    updatePreferences,
    // 暴露一些工具方法供组件使用
    setCustomTransition: (transitionType) => {
      // 可以用于临时覆盖默认动画
      console.log('设置自定义加载及动画:', transitionType)
    },
    // 获取优化建议
    getPerformanceInfo: () => ({
      prefersReducedMotion: prefersReducedMotion.value,
      isSlowDevice: isSlowDevice.value,
      currentTransition: currentTransition.value,
      duration: transitionDuration.value
    })
  }
}

// 主题色动画工具
export function useThemeTransition() {
  const themeColors = ref({
    primary: '#4c84ff',
    secondary: '#6366f1', 
    accent: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444'
  })

  // 更新CSS自定义属性
  const updateThemeColors = (newColors) => {
    const root = document.documentElement
    
    Object.entries(newColors).forEach(([key, value]) => {
      root.style.setProperty(`--${key}-color`, value)
      
      // 提取RGB值用于透明度效果
      const rgb = hexToRgb(value)
      if (rgb) {
        root.style.setProperty(`--${key}-color-rgb`, `${rgb.r}, ${rgb.g}, ${rgb.b}`)
      }
    })
    
    themeColors.value = { ...themeColors.value, ...newColors }
  }

  // 颜色转换工具
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }

  // 生成渐变色
  const createGradient = (color1, color2, direction = '135deg') => {
    return `linear-gradient(${direction}, ${color1}, ${color2})`
  }

  // 主题切换动画
  const animateThemeChange = (newTheme) => {
    const root = document.documentElement
    
    // 添加过渡类
    root.classList.add('theme-transitioning')
    
    // 更新主题
    updateThemeColors(newTheme)
    
    // 移除过渡类
    setTimeout(() => {
      root.classList.remove('theme-transitioning')
    }, 300)
  }

  return {
    themeColors: computed(() => themeColors.value),
    updateThemeColors,
    createGradient,
    animateThemeChange,
    hexToRgb
  }
}
