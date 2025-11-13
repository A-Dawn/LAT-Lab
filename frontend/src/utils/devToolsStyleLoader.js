/**
 * 开发工具样式加载器
 * 用于在前端页面加载时自动应用后端保存的样式配置
 */

import { devToolsService } from '../services/devToolsService'

class DevToolsStyleLoader {
  constructor() {
    this.isLoaded = false
    this.currentPageUrl = window.location.pathname
  }

  /**
   * 初始化样式加载器
   */
  async init() {
    if (this.isLoaded) return
    
    try {
      console.log('开发工具样式加载器：开始加载配置...')
      
      // 从后端获取样式配置
      const response = await devToolsService.getDevToolsConfig()
      
      if (response?.success && response?.data?.page_data) {
        const pageData = response.data.page_data
        console.log('获取到页面配置数据:', pageData)
        
        // 应用当前页面的配置
        await this.applyPageConfig(pageData)
        
        // 应用全局配置（如果有）
        if (pageData['current']) {
          await this.applyConfigToCurrentPage(pageData['current'])
        }
        
        console.log('开发工具样式配置应用完成')
      }
      
      this.isLoaded = true
    } catch (error) {
      console.error('开发工具样式加载失败:', error)
    }
  }

  /**
   * 应用页面配置
   */
  async applyPageConfig(pageData) {
    // 尝试匹配当前页面的配置
    const currentPage = this.currentPageUrl
    
    // 检查是否有当前页面的特定配置
    if (pageData[currentPage]) {
      console.log('应用页面特定配置:', currentPage)
      await this.applyConfigToCurrentPage(pageData[currentPage])
    }
    
    // 检查是否有通用配置
    const commonPages = ['/', '/home', '/index']
    for (const page of commonPages) {
      if (pageData[page] && page !== currentPage) {
        console.log('应用通用页面配置:', page)
        await this.applyConfigToCurrentPage(pageData[page])
        break
      }
    }
  }

  /**
   * 将配置应用到当前页面
   */
  async applyConfigToCurrentPage(pageConfig) {
    if (!pageConfig) return

    try {
      // 应用CSS变量
      if (pageConfig.styles && Array.isArray(pageConfig.styles)) {
        pageConfig.styles.forEach(style => {
          if (style.value !== style.originalValue) {
            console.log('应用CSS变量:', style.name, style.value)
            document.documentElement.style.setProperty(style.name, style.value)
          }
        })
      }

      // 应用文本修改 - 使用安全的HTML应用
      if (pageConfig.texts && Array.isArray(pageConfig.texts)) {
        // 动态导入 HTML 净化工具
        const { safelyApplyContent } = await import('./htmlSanitizer.js')
        
        pageConfig.texts.forEach(text => {
          if (text.currentValue !== text.originalValue) {
            console.log('应用文本修改:', text.selector, text.currentValue)
            const elements = document.querySelectorAll(text.selector)
            elements.forEach(el => {
              // 使用安全的内容应用方法
              safelyApplyContent(el, text.currentValue)
            })
          }
        })
      }

      // 应用布局修改
      if (pageConfig.layouts && Array.isArray(pageConfig.layouts)) {
        pageConfig.layouts.forEach(layout => {
          if (layout.currentValue !== layout.originalValue) {
            console.log('应用布局修改:', layout.selector, layout.property, layout.currentValue)
            const elements = document.querySelectorAll(layout.selector)
            elements.forEach(el => {
              el.style[layout.property] = layout.currentValue
            })
          }
        })
      }
    } catch (error) {
      console.error('应用页面配置失败:', error)
    }
  }

  /**
   * 重新加载配置
   */
  async reload() {
    this.isLoaded = false
    await this.init()
  }
}

// 创建全局实例
const devToolsStyleLoader = new DevToolsStyleLoader()

// 导出实例和类
export { devToolsStyleLoader, DevToolsStyleLoader }
export default devToolsStyleLoader
