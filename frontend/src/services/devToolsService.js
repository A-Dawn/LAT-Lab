/**
 * 开发工具配置服务
 */

import { adminApi } from './api'

class DevToolsService {
  constructor() {
    this.cache = null
    this.cacheTime = null
    this.cacheTTL = 2 * 60 * 1000 // 2分钟缓存
  }

  /**
   * 检查缓存是否有效
   */
  isCacheValid() {
    if (!this.cache || !this.cacheTime) {
      return false
    }
    return Date.now() - this.cacheTime < this.cacheTTL
  }

  /**
   * 设置缓存
   */
  setCache(data) {
    this.cache = data
    this.cacheTime = Date.now()
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cache = null
    this.cacheTime = null
  }

  /**
   * 获取开发工具配置
   * @param {boolean} useCache - 是否使用缓存
   * @returns {Promise<Object>}
   */
  async getDevToolsConfig(useCache = false) {
    try {
      // 检查缓存（开发工具通常不使用缓存以确保实时性）
      if (useCache && this.isCacheValid()) {
        return {
          success: true,
          data: this.cache,
          fromCache: true
        }
      }

      // 从API获取数据
      const response = await adminApi.getDevToolsConfig()
      
      if (response?.success) {
        const data = response.data
        
        // 数据标准化
        const normalizedData = this.normalizeData(data)
        
        // 设置缓存
        if (useCache) {
          this.setCache(normalizedData)
        }
        
        return {
          success: true,
          data: normalizedData,
          fromCache: false
        }
      } else {
        throw new Error('响应数据格式错误')
      }
    } catch (error) {
      console.error('获取开发工具配置失败:', error)
      throw error
    }
  }

  /**
   * 更新开发工具配置
   * @param {Object} data - 配置数据
   * @returns {Promise<Object>}
   */
  async updateDevToolsConfig(data) {
    try {
      // 数据验证
      const validatedData = this.validateData(data)
      
      // 发送更新请求
      const response = await adminApi.updateDevToolsConfig(validatedData)
      
      if (response?.success) {
        // 清除缓存
        this.clearCache()
        
        return {
          success: true,
          data: response.data,
          message: response.message || '更新成功'
        }
      } else {
        throw new Error(response?.message || '更新失败')
      }
    } catch (error) {
      console.error('更新开发工具配置失败:', error)
      throw error
    }
  }

  /**
   * 清除开发工具配置
   * @param {string} page - 页面标识（可选）
   * @returns {Promise<Object>}
   */
  async clearDevToolsConfig(page = null) {
    try {
      const response = await adminApi.clearDevToolsConfig(page)
      
      if (response?.success) {
        // 清除缓存
        this.clearCache()
        
        return {
          success: true,
          message: response.message || '清除成功'
        }
      } else {
        throw new Error(response?.message || '清除失败')
      }
    } catch (error) {
      console.error('清除开发工具配置失败:', error)
      throw error
    }
  }

  /**
   * 数据标准化
   * @param {Object} data - 原始数据
   * @returns {Object} - 标准化后的数据
   */
  normalizeData(data) {
    const normalized = {
      styles: data.styles || [],
      texts: data.texts || [],
      layouts: data.layouts || [],
      page_data: data.page_data || {},
      current_page: data.current_page || 'current',
      last_updated: data.last_updated || null
    }

    // 确保每个样式项都有必要的字段
    normalized.styles = normalized.styles.map(style => ({
      name: style.name || '',
      value: style.value || '',
      originalValue: style.originalValue || style.value || '',
      description: style.description || ''
    }))

    // 确保每个文本项都有必要的字段
    normalized.texts = normalized.texts.map(text => ({
      id: text.id || '',
      selector: text.selector || '',
      description: text.description || '',
      currentValue: text.currentValue || '',
      originalValue: text.originalValue || text.currentValue || ''
    }))

    // 确保每个布局项都有必要的字段
    normalized.layouts = normalized.layouts.map(layout => ({
      id: layout.id || '',
      selector: layout.selector || '',
      property: layout.property || '',
      description: layout.description || '',
      currentValue: layout.currentValue || '',
      originalValue: layout.originalValue || layout.currentValue || '',
      unit: layout.unit || ''
    }))

    return normalized
  }

  /**
   * 数据验证
   * @param {Object} data - 待验证的数据
   * @returns {Object} - 验证后的数据
   */
  validateData(data) {
    const errors = []

    // 验证基本结构
    if (!data || typeof data !== 'object') {
      errors.push('配置数据格式错误')
    }

    // 验证样式数据
    if (data.styles && !Array.isArray(data.styles)) {
      errors.push('样式配置必须是数组格式')
    }

    // 验证文本数据
    if (data.texts && !Array.isArray(data.texts)) {
      errors.push('文本配置必须是数组格式')
    }

    // 验证布局数据
    if (data.layouts && !Array.isArray(data.layouts)) {
      errors.push('布局配置必须是数组格式')
    }

    // 验证样式项
    if (data.styles) {
      data.styles.forEach((style, index) => {
        if (!style.name || !style.name.trim()) {
          errors.push(`第${index + 1}个样式项缺少名称`)
        }
        if (style.name && !style.name.startsWith('--')) {
          errors.push(`第${index + 1}个样式项名称必须以--开头`)
        }
      })
    }

    // 验证文本项
    if (data.texts) {
      data.texts.forEach((text, index) => {
        if (!text.selector || !text.selector.trim()) {
          errors.push(`第${index + 1}个文本项缺少选择器`)
        }
      })
    }

    // 验证布局项
    if (data.layouts) {
      data.layouts.forEach((layout, index) => {
        if (!layout.selector || !layout.selector.trim()) {
          errors.push(`第${index + 1}个布局项缺少选择器`)
        }
        if (!layout.property || !layout.property.trim()) {
          errors.push(`第${index + 1}个布局项缺少属性名`)
        }
      })
    }

    if (errors.length > 0) {
      throw new Error(errors[0])
    }

    // 清理数据
    return {
      styles: (data.styles || []).map(style => ({
        name: style.name.trim(),
        value: style.value || '',
        originalValue: style.originalValue || style.value || '',
        description: (style.description || '').trim()
      })),
      texts: (data.texts || []).map(text => ({
        id: text.id || '',
        selector: text.selector.trim(),
        description: (text.description || '').trim(),
        currentValue: text.currentValue || '',
        originalValue: text.originalValue || text.currentValue || ''
      })),
      layouts: (data.layouts || []).map(layout => ({
        id: layout.id || '',
        selector: layout.selector.trim(),
        property: layout.property.trim(),
        description: (layout.description || '').trim(),
        currentValue: layout.currentValue || '',
        originalValue: layout.originalValue || layout.currentValue || '',
        unit: layout.unit || ''
      })),
      page_data: data.page_data || {},
      current_page: data.current_page || 'current'
    }
  }

  /**
   * 获取默认配置
   * @returns {Object} - 默认配置
   */
  getDefaultConfig() {
    return {
      styles: [],
      texts: [],
      layouts: [],
      page_data: {},
      current_page: 'current'
    }
  }

  /**
   * 生成变更历史记录
   * @param {string} type - 变更类型 (style|text|layout)
   * @param {Object} change - 变更数据
   * @returns {Object} - 历史记录项
   */
  createHistoryEntry(type, change) {
    return {
      type,
      timestamp: new Date().toISOString(),
      page: change.page || 'current',
      ...change
    }
  }
}

// 创建单例实例
export const devToolsService = new DevToolsService()
export default devToolsService
