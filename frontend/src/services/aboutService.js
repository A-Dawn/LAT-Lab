/**
 * 关于博主配置服务
 */

import { adminApi } from './api'

class AboutService {
  constructor() {
    this.cache = null
    this.cacheTime = null
    this.cacheTTL = 5 * 60 * 1000 // 5分钟缓存
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
   * 获取关于博主配置（管理员接口的别名）
   * @returns {Promise<Object>}
   */
  async getAboutSection() {
    return this.getAboutConfig(false) // 管理员界面不使用缓存
  }

  /**
   * 获取关于博主配置
   * @param {boolean} useCache - 是否使用缓存
   * @returns {Promise<Object>}
   */
  async getAboutConfig(useCache = true) {
    try {
      // 检查缓存
      if (useCache && this.isCacheValid()) {
        return {
          success: true,
          data: this.cache,
          fromCache: true
        }
      }

      // 从API获取数据
      const response = await adminApi.getAboutSection()
      
      // 由于响应拦截器已经处理了response.data，所以直接使用response
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
      console.error('获取关于博主配置失败:', error)
      throw error
    }
  }

  /**
   * 更新关于博主配置
   * @param {Object} data - 配置数据
   * @returns {Promise<Object>}
   */
  async updateAboutConfig(data) {
    try {
      // 数据验证
      const validatedData = this.validateData(data)
      
      // 发送更新请求
      const response = await adminApi.updateAboutSection(validatedData)
      
      // 由于响应拦截器已经处理了response.data，所以直接使用response
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
      console.error('更新关于博主配置失败:', error)
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
      title: data.title || '关于博主',
      description: data.description || '',
      social_links: []
    }

    // 处理社交链接兼容性
    const socialLinks = data.social_links || data.socialLinks || []
    normalized.social_links = socialLinks.map(link => ({
      name: link.name || '',
      url: link.url || '',
      icon: link.icon || ''
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

    // 验证标题
    if (!data.title || !data.title.trim()) {
      errors.push('标题不能为空')
    } else if (data.title.length > 50) {
      errors.push('标题长度不能超过50字符')
    }

    // 验证描述
    if (data.description && data.description.length > 500) {
      errors.push('描述长度不能超过500字符')
    }

    // 验证社交链接
    if (data.social_links) {
      if (data.social_links.length > 10) {
        errors.push('社交链接数量不能超过10个')
      }

      data.social_links.forEach((link, index) => {
        if (link.name && link.name.trim()) {
          if (!link.url || !link.url.trim()) {
            errors.push(`第${index + 1}个社交链接缺少URL`)
          } else if (!this.isValidUrl(link.url)) {
            errors.push(`第${index + 1}个社交链接URL格式不正确`)
          }
        }
        if (link.url && link.url.trim() && (!link.name || !link.name.trim())) {
          errors.push(`第${index + 1}个社交链接缺少名称`)
        }
      })
    }

    if (errors.length > 0) {
      throw new Error(errors[0])
    }

    // 清理数据
    return {
      title: data.title.trim(),
      description: (data.description || '').trim(),
      social_links: (data.social_links || []).filter(link => 
        link.name && link.name.trim() && link.url && link.url.trim()
      ).map(link => ({
        name: link.name.trim(),
        url: link.url.trim(),
        icon: (link.icon || '').trim()
      }))
    }
  }

  /**
   * 验证URL格式
   * @param {string} url - URL字符串
   * @returns {boolean} - 是否有效
   */
  isValidUrl(url) {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  /**
   * 获取默认配置
   * @returns {Object} - 默认配置
   */
  getDefaultConfig() {
    return {
      title: '关于博主',
      description: '热爱技术，喜欢分享，记录学习过程中的点点滴滴。',
      social_links: [
        { name: 'GitHub', url: 'https://github.com', icon: 'github' },
        { name: '邮箱', url: 'mailto:example@email.com', icon: 'email' }
      ]
    }
  }
}

// 创建单例实例
export const aboutService = new AboutService()
export default aboutService 