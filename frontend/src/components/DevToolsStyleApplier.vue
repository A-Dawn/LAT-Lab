<template>
  <div :class="['style-transition', { 'is-loaded': isLoaded }]">
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'

const store = useStore()
const route = useRoute()
const isLoaded = ref(false)

// 等待DOM元素出现的辅助函数
const waitForElements = async (selectors, timeout = 3000) => {
  const startTime = Date.now()
  
  while (Date.now() - startTime < timeout) {
    let allFound = true
    
    for (const selector of selectors) {
      if (document.querySelectorAll(selector).length === 0) {
        allFound = false
        break
      }
    }
    
    if (allFound) {
      return true
    }
    
    // 等待50ms后重试
    await new Promise(resolve => setTimeout(resolve, 50))
  }
  
  return false
}

// Apply styles to the document with DOM waiting
const applyStyles = async (config) => {
  if (!config) return

  // 收集所有需要等待的选择器
  const selectorsToWait = []
  
  if (config.texts && config.texts.length > 0) {
    config.texts.forEach(text => {
      if (text.currentValue !== text.originalValue) {
        selectorsToWait.push(text.selector)
      }
    })
  }
  
  if (config.layouts && config.layouts.length > 0) {
    config.layouts.forEach(layout => {
      if (layout.currentValue !== layout.originalValue) {
        selectorsToWait.push(layout.selector)
      }
    })
  }

  // 如果有需要等待的选择器，先等待DOM元素出现
  if (selectorsToWait.length > 0) {
    await waitForElements(selectorsToWait)
  }

  // Apply CSS variables
  if (config.styles && config.styles.length > 0) {
    config.styles.forEach(style => {
      if (style.value !== style.originalValue) {
        document.documentElement.style.setProperty(style.name, style.value)
      }
    })
  }

  // Apply text changes
  if (config.texts && config.texts.length > 0) {
    config.texts.forEach(text => {
      if (text.currentValue !== text.originalValue) {
        const elements = document.querySelectorAll(text.selector)
        elements.forEach(el => {
          el.textContent = text.currentValue
        })
      }
    })
  }

  // Apply layout changes
  if (config.layouts && config.layouts.length > 0) {
    config.layouts.forEach(layout => {
      if (layout.currentValue !== layout.originalValue) {
        const elements = document.querySelectorAll(layout.selector)
        elements.forEach(el => {
          el.style[layout.property] = layout.currentValue
        })
      }
    })
  }
}

// Load cached styles from localStorage
const loadCachedStyles = (page) => {
  try {
    const cachedData = localStorage.getItem('devToolsStyles')
    if (cachedData) {
      const parsedData = JSON.parse(cachedData)
      // Check if data is expired (e.g., 1 hour)
      const isExpired = Date.now() - (parsedData.timestamp || 0) > 3600000
      if (!isExpired && (parsedData[page] || parsedData.current)) {
        return parsedData[page] || parsedData.current
      }
    }
  } catch (e) {
    console.error('Failed to load cached styles:', e)
  }
  return null
}

// Save styles to localStorage
const cacheStyles = (page, config) => {
  try {
    const cachedData = JSON.parse(localStorage.getItem('devToolsStyles') || '{}')
    cachedData[page] = config
    cachedData.timestamp = Date.now()
    localStorage.setItem('devToolsStyles', JSON.stringify(cachedData))
  } catch (e) {
    console.error('Failed to cache styles:', e)
  }
}

// 获取缓存的样式
const getCachedStyles = (page) => {
  try {
    const cachedData = JSON.parse(localStorage.getItem('devToolsStyles') || '{}')
    // 检查缓存是否过期（1小时）
    if (cachedData.timestamp && (Date.now() - cachedData.timestamp) < 3600000) {
      return cachedData[page]
    }
    return null
  } catch (e) {
    console.error('F ailed to get cached styles:', e)
    return null
  }
}

// Load and apply styles for a given page
const loadAndApplyStyles = async (page, forceReload = false, updateCacheOnly = false) => {
  try {
    // 检查devTools模块是否已加载
    if (!store.hasModule('devTools')) {
      isLoaded.value = true
      return false
    }
    
    // 从缓存加载
    const cached = getCachedStyles(page)
    
    // 如果强制重新加载或者没有缓存，则从服务器加载
    if (forceReload || !cached) {
      let pageData = {}
      
      try {
        // 尝试加载保存的更改
        const result = await store.dispatch('devTools/loadSavedChanges', { 
          force: forceReload 
        })
        
        // 从返回的页面数据中获取当前页面的配置
        pageData = result || {}
        
      } catch (error) {
        console.warn('Failed to load saved changes from devTools module:', error)
        // 即使加载失败，也继续使用空配置
        pageData = {}
      }
      
      // 获取当前页面的配置 - 从page_data字段中查找
      const pageConfig = (pageData.page_data && pageData.page_data[page]) || {
        styles: [],
        texts: [],
        layouts: []
      }
      
      // 应用样式（除非是仅更新缓存）
      if (!updateCacheOnly) {
        // 等待DOM渲染完成后再应用样式
        await nextTick()
        await applyStyles(pageConfig)
      }
      
      // 更新缓存
      cacheStyles(page, pageConfig)
    } else if (!updateCacheOnly) {
      // 使用缓存的样式
      // 等待DOM渲染完成后再应用缓存的样式
      await nextTick()
      await applyStyles(cached)
    }
    
    // 如果是当前页面，确保加载状态更新
    if (page === route.path && !updateCacheOnly) {
      isLoaded.value = true
    }
    
    return true
  } catch (error) {
    console.error('Failed to load and apply dev tools styles:', error)
    isLoaded.value = true // 确保UI不会卡在加载状态
    return false
  }
}


// 初始加载
onMounted(() => {
  // 初始加载样式
  loadAndApplyStyles(route.path, true)
})

// Watch for route changes
watch(() => route.path, async (newPath) => {
  // 当路由变化时，为新页面加载并应用样式
  await loadAndApplyStyles(newPath, true)
}, { immediate: true })
</script>

<style scoped>
.style-transition {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.style-transition.is-loaded {
  opacity: 1;
}
</style>
