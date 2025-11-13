/**
 * 同步开发工具配置加载器
 * 在Vue应用挂载前同步读取localStorage缓存并立即应用
 * 用于消除首次渲染时的闪烁问题
 */

class SyncDevToolsLoader {
  constructor() {
    this.textMap = new Map()
    this.isInitialized = false
  }

  /**
   * 初始化：同步加载缓存配置
   */
  init() {
    if (this.isInitialized) return
    
    try {
      console.log('同步加载开发工具配置...')
      
      // 同步读取localStorage缓存
      const cachedData = this.loadCachedData()
      
      if (cachedData) {
        // 立即应用CSS变量和布局
        this.applyStylesSync(cachedData)
        
        // 创建文本映射，供组件读取
        this.createTextMap(cachedData)
        
        console.log('同步配置加载完成')
      }
      
      this.isInitialized = true
    } catch (error) {
      console.error('同步配置加载失败:', error)
    }
  }

  /**
   * 同步读取缓存数据
   */
  loadCachedData() {
    try {
      const cachedDataStr = localStorage.getItem('devToolsStyles')
      if (!cachedDataStr) return null
      
      const parsedData = JSON.parse(cachedDataStr)
      
      // 检查缓存是否过期（1小时）
      if (parsedData.timestamp && (Date.now() - parsedData.timestamp) > 3600000) {
        console.log('缓存已过期')
        return null
      }
      
      // 获取当前页面的配置
      const currentPath = window.location.pathname
      const pageConfig = parsedData[currentPath] || parsedData.current || null
      
      return pageConfig
    } catch (error) {
      console.error('读取缓存数据失败:', error)
      return null
    }
  }

  /**
   * 同步应用CSS变量和布局修改
   */
  applyStylesSync(pageConfig) {
    if (!pageConfig) return

    // 应用CSS变量
    if (pageConfig.styles && Array.isArray(pageConfig.styles)) {
      pageConfig.styles.forEach(style => {
        if (style.value !== style.originalValue) {
          try {
            document.documentElement.style.setProperty(style.name, style.value)
            console.log('同步应用CSS变量:', style.name, style.value)
          } catch (error) {
            console.error('应用CSS变量失败:', error)
          }
        }
      })
    }

    // 应用布局修改
    if (pageConfig.layouts && Array.isArray(pageConfig.layouts)) {
      pageConfig.layouts.forEach(layout => {
        if (layout.currentValue !== layout.originalValue) {
          try {
            // 注意：这里先创建映射，DOM查询在组件渲染时进行
            console.log('准备应用布局修改:', layout.selector, layout.property, layout.currentValue)
          } catch (error) {
            console.error('应用布局修改失败:', error)
          }
        }
      })
    }
  }

  /**
   * 创建文本映射
   */
  createTextMap(pageConfig) {
    if (!pageConfig.texts || !Array.isArray(pageConfig.texts)) return

    pageConfig.texts.forEach(text => {
      if (text.currentValue !== text.originalValue) {
        // 使用选择器作为key，文本内容作为value
        this.textMap.set(text.selector, text.currentValue)
        console.log('创建文本映射:', text.selector, '→', text.currentValue)
      }
    })

    // 将文本映射暴露到全局，供Vue组件读取
    window.__devToolsTextMap = Object.fromEntries(this.textMap)
    
    // 同时创建一个快速查找映射（使用简化的选择器）
    this.createQuickLookupMap(pageConfig)
  }

  /**
   * 创建快速查找映射（用于组件直接查找）
   */
  createQuickLookupMap(pageConfig) {
    const quickMap = {}
    
    pageConfig.texts.forEach(text => {
      if (text.currentValue !== text.originalValue) {
        // 提取简化的选择器用于快速匹配
        const simpleSelector = text.selector
          .replace(/\.plugin-widget/g, '')
          .replace(/\s+/g, ' ')
          .trim()
        
        quickMap[simpleSelector] = text.currentValue
        
        // 也保存原始选择器
        quickMap[text.selector] = text.currentValue
      }
    })
    
    window.__devToolsQuickMap = quickMap
  }

  /**
   * 获取文本映射
   */
  getTextMap() {
    return this.textMap
  }

  /**
   * 查询映射的文本内容
   */
  getMappedText(selector) {
    return this.textMap.get(selector)
  }

  /**
   * 判断是否有映射
   */
  hasMapping() {
    return this.textMap.size > 0
  }
}

// 创建全局实例
const syncDevToolsLoader = new SyncDevToolsLoader()

// 导出
export { syncDevToolsLoader, SyncDevToolsLoader }
export default syncDevToolsLoader

