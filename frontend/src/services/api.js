import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api', // 使用环境变量，并提供一个备用值
  timeout: 10000,  // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从本地存储获取token
    const token = localStorage.getItem('token')
    
    // 如果token存在，将其添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  async error => { // 将函数标记为async
    // 检查URL是否包含/plugins/
    const isPluginRequest = error.config && error.config.url && error.config.url.includes('/plugins/')
    
    // 处理403错误（没有权限）和401错误（未授权）
    if (error.response && (error.response.status === 401 || (error.response.status === 403 && !isPluginRequest))) {
      // 如果是插件相关请求，允许错误正常处理
      if (isPluginRequest) {
        console.warn('插件请求失败，但不重定向:', error.config.url)
        return Promise.reject(error)
      }
      
      // 清除token
      localStorage.removeItem('token')

      // 使用动态导入来避免循环依赖，并用router进行跳转
      const router = (await import('../router')).default
      if (router.currentRoute.value.path !== '/login') {
        router.replace({
          path: '/login',
          query: {
            redirect: router.currentRoute.value.fullPath
          }
        })
      }
    }
    
    return Promise.reject(error)
  }
)

// 用户相关API
export const userApi = {
  // 登录
  login(credentials) {
    // 使用FormData格式提交，符合OAuth2PasswordRequestForm的要求
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    // 先清除旧的用户信息和token，确保不会使用缓存的数据
    localStorage.removeItem('token')
    
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },
  
  // 注册
  register(userData) {
    return api.post('/auth/register', userData)
  },
  
  // 获取当前用户信息
  getCurrentUser() {
    return api.get('/users/me')
  },
  
  // 更新用户信息
  updateProfile(userData) {
    return api.put('/users/me', userData)
  },
  
  // 修改密码
  changePassword(passwordData) {
    return api.put('/users/me/password', passwordData)
  },
  
  // 上传头像
  uploadAvatar(formData) {
    return api.post('/users/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 获取所有用户（管理员）
  getUsers(params = {}) {
    return api.get('/users', { params })
  },
  
  // 获取单个用户信息（管理员）
  getUser(userId) {
    return api.get(`/users/${userId}`)
  },
  
  // 更新用户信息（管理员）
  updateUser(userId, userData) {
    return api.put(`/users/${userId}`, userData)
  },
  
  // 删除用户（管理员）
  deleteUser(userId) {
    return api.delete(`/users/${userId}`)
  }
}

// 文章相关API
export const articleApi = {
  // 获取文章列表
  getArticles(params) {
    return api.get('/articles', { params })
  },
  
  // 获取文章详情
  getArticle(id) {
    return api.get(`/articles/${id}`)
  },
  
  // 获取文章详情（带密码）
  getArticleWithPassword(id, password) {
    return api.get(`/articles/${id}`, { params: { password } })
  },
  
  // 创建文章
  createArticle(articleData) {
    return api.post('/articles', articleData)
  },
  
  // 更新文章
  updateArticle(id, articleData) {
    return api.put(`/articles/${id}`, articleData)
  },
  
  // 删除文章
  deleteArticle(id) {
    return api.delete(`/articles/${id}`)
  },
  
  // 获取用户的文章
  getUserArticles(params) {
    return api.get('/articles/me', { params })
  },
  
  // 获取用户的草稿文章
  getUserDrafts() {
    return api.get('/articles/drafts')
  },
  
  // 发布草稿文章
  publishArticle(id, publishTime) {
    return api.post(`/articles/${id}/publish`, { publish_time: publishTime })
  },
  
  // 点赞文章
  likeArticle(id) {
    return api.post(`/articles/${id}/like`)
      .catch(error => {
        // 如果后端API不存在，静默失败
        console.warn('点赞API调用失败', error);
        return { success: false, error: error.message };
      });
  },
  
  // 发送LLM查询
  async sendLlmQuery(params) {
    try {
      // 查找激活的OpenRouter插件
      const plugins = await pluginApi.getPlugins({ active_only: true })
      
      // 确保plugins是数组
      if (!Array.isArray(plugins)) {
        return "获取插件列表失败，请稍后再试。"
      }
      
      // 过滤出OpenRouter插件
      const openRouterPlugin = plugins.find(p => 
        p && p.name && p.name.toLowerCase().includes('openrouter') || 
        p && p.description && p.description.toLowerCase().includes('openrouter')
      )
      
      if (!openRouterPlugin) {
        return "没有找到激活的OpenRouter插件，请联系管理员激活或创建插件。"
      }
      
      // 添加action参数，默认为空，表示执行普通查询
      const apiParams = {
        ...params,
        action: params.action || ''
      }
      
      console.log('调用插件参数:', apiParams)
      
      // 调用插件
      const response = await pluginApi.runPlugin(openRouterPlugin.id, apiParams)
      console.log('插件响应:', response)
      
      // 如果是请求模型列表，直接返回结果
      if (params.action === 'get_models') {
        if (response && response.output) {
          try {
            return JSON.parse(response.output)
          } catch (e) {
            console.error('解析模型列表失败:', e)
            return { 
              success: false,
              message: "解析模型列表失败",
              models: []
            }
          }
        }
        return { 
          success: false,
          message: "获取模型列表失败",
          models: []
        }
      }
      
      // 普通查询，提取生成的内容
      if (response && response.output) {
        // 尝试解析JSON
        try {
          const jsonData = JSON.parse(response.output)
          if (jsonData && jsonData.response) {
            return jsonData.response
          }
          return jsonData
        } catch (e) {
          // 如果不是JSON，则查找"生成内容"部分
          const contentMatch = response.output.match(/## 生成内容\s*\n\s*([\s\S]*?)(?:\n\s*##|\n\s*---|\n\s*$)/)
          if (contentMatch && contentMatch[1]) {
            return contentMatch[1].trim()
          }
          return response.output
        }
      }
      
      return "没有获取到有效的回复"
    } catch (error) {
      console.error("LLM查询失败:", error)
      return "查询失败：" + (error.message || "未知错误")
    }
  }
}

// 评论相关API
export const commentApi = {
  // 获取文章评论
  getComments(articleId) {
    return api.get(`/comments/article/${articleId}`)
  },
  
  // 获取评论回复
  getReplies(commentId) {
    return api.get(`/comments/${commentId}/replies`)
  },
  
  // 添加评论
  addComment(articleId, commentData) {
    const data = {
      ...commentData,
      article_id: articleId
    }
    return api.post(`/comments`, data)
  },
  
  // 更新评论
  updateComment(commentId, updateData) {
    return api.put(`/comments/${commentId}`, updateData)
  },
  
  // 删除评论
  deleteComment(commentId) {
    return api.delete(`/comments/${commentId}`)
  },
  
  // 点赞评论
  likeComment(commentId) {
    return api.post(`/comments/${commentId}/like`)
  },
  
  // 获取所有评论（管理员）
  getAllComments(params = {}) {
    return api.get('/comments', { params })
  }
}

// 分类相关API
export const categoryApi = {
  // 获取所有分类
  getCategories() {
    return api.get('/categories')
  },
  
  // 创建分类
  createCategory(categoryData) {
    return api.post('/categories', categoryData)
  },
  
  // 更新分类
  updateCategory(id, categoryData) {
    return api.put(`/categories/${id}`, categoryData)
  },
  
  // 删除分类
  deleteCategory(id) {
    return api.delete(`/categories/${id}`)
  }
}

// 标签相关API
export const tagApi = {
  // 获取所有标签
  getTags() {
    return api.get('/articles/tags')
      .catch(error => {
        console.error('获取标签失败:', error)
        return [] // 如果出错，返回空数组
      })
  },
  
  // 获取所有标签（管理员用，包含更多信息）
  getAllTags() {
    return api.get('/admin/tags')
      .catch(error => {
        console.error('获取标签失败:', error)
        return [] // 如果出错，返回空数组
      })
  },
  
  // 创建标签
  createTag(tagData) {
    return api.post('/admin/tags', tagData)
  },
  
  // 更新标签
  updateTag(id, tagData) {
    return api.put(`/admin/tags/${id}`, tagData)
  },
  
  // 删除标签
  deleteTag(id) {
    return api.delete(`/admin/tags/${id}`)
  }
}

// 插件相关API
export const pluginApi = {
  // 获取插件列表
  getPlugins(params) {
    return api.get('/plugins', { params })
      .catch(error => {
        // 如果是403错误，且是请求激活的插件，返回空数组
        if (error.response && error.response.status === 403 && params && params.active_only) {
          console.warn('用户无权限获取插件列表，返回空数组')
          return []
        }
        throw error
      })
  },
  
  // 获取插件详情
  getPlugin(id) {
    return api.get(`/plugins/${id}`)
      .catch(error => {
        // 如果是403错误，返回null
        if (error.response && error.response.status === 403) {
          console.warn('用户无权限获取此插件详情')
          return null
        }
        throw error
      })
  },
  
  // 创建插件
  createPlugin(pluginData) {
    return api.post('/plugins', pluginData)
  },
  
  // 更新插件
  updatePlugin(id, pluginData) {
    return api.put(`/plugins/${id}`, pluginData)
  },
  
  // 删除插件
  deletePlugin(id) {
    return api.delete(`/plugins/${id}`)
  },
  
  // 激活/停用插件
  activatePlugin(id, activate) {
    return api.post(`/plugins/${id}/activate`, { activate })
  },
  
  // 运行插件（支持传递参数）
  runPlugin(id, params) {
    return api.post(`/plugins/${id}/run`, params || {})
  },
  
  // 获取所有示例插件列表
  getExamplePlugins() {
    return api.get('/plugins/examples')
  },
  
  // 获取特定示例插件
  getExamplePlugin(name) {
    return api.get(`/plugins/examples/${name}`)
  },
  
  // 插件市场相关API
  
  // 获取插件分类列表
  getCategories() {
    return api.get('/plugins/categories')
  },
  
  // 创建插件分类（管理员）
  createCategory(categoryData) {
    return api.post('/plugins/categories', categoryData)
  },
  
  // 更新插件分类（管理员）
  updateCategory(id, categoryData) {
    return api.put(`/plugins/categories/${id}`, categoryData)
  },
  
  // 删除插件分类（管理员）
  deleteCategory(id) {
    return api.delete(`/plugins/categories/${id}`)
  },
  
  // 获取插件标签列表
  getTags() {
    return api.get('/plugins/tags')
  },
  
  // 创建插件标签（管理员）
  createTag(tagName) {
    return api.post('/plugins/tags', { name: tagName })
  },
  
  // 删除插件标签（管理员）
  deleteTag(tagName) {
    return api.delete(`/plugins/tags/${tagName}`)
  },
  
  // 搜索插件
  searchPlugins(searchQuery) {
    return api.post('/plugins/search', searchQuery)
  },
  
  // 获取精选插件
  getFeaturedPlugins(limit = 6) {
    return api.get('/plugins/featured', { params: { limit } })
  },
  
  // 获取最新插件
  getNewestPlugins(limit = 10) {
    return api.get('/plugins/newest', { params: { limit } })
  },
  
  // 获取最受欢迎插件
  getPopularPlugins(limit = 10) {
    return api.get('/plugins/popular', { params: { limit } })
  },
  
  // 获取插件详情（含分类、标签、评论）
  getPluginDetail(id) {
    return api.get(`/plugins/${id}/detail`)
  },
  
  // 下载/安装插件
  downloadPlugin(id) {
    return api.post(`/plugins/${id}/download`)
  },
  
  // 获取插件评论
  getPluginReviews(id) {
    return api.get(`/plugins/${id}/reviews`)
  },
  
  // 添加插件评论
  reviewPlugin(id, reviewData) {
    return api.post(`/plugins/${id}/reviews`, reviewData)
  },
  
  // 更新插件评论
  updateReview(reviewId, reviewData) {
    return api.put(`/plugins/reviews/${reviewId}`, reviewData)
  },
  
  // 删除插件评论
  deleteReview(reviewId) {
    return api.delete(`/plugins/reviews/${reviewId}`)
  },
  
  // 插件市场相关API - 基于配置文件
  
  // 获取插件市场信息
  getMarketplaceInfo() {
    return api.get('/plugins/marketplace/info')
  },
  
  // 获取插件市场分类
  getMarketplaceCategories() {
    return api.get('/plugins/marketplace/categories')
  },
  
  // 获取插件市场标签
  getMarketplaceTags() {
    return api.get('/plugins/marketplace/tags')
  },
  
  // 获取插件市场插件列表
  getMarketplacePlugins(params = {}) {
    return api.get('/plugins/marketplace/plugins', { params })
  },
  
  // 获取插件市场特定插件
  getMarketplacePlugin(pluginId) {
    return api.get(`/plugins/marketplace/plugins/${pluginId}`)
  },
  
  // 从插件市场下载插件
  downloadMarketplacePlugin(pluginId) {
    return api.post(`/plugins/marketplace/download/${pluginId}`)
  },
  
  // 获取精选插件
  getFeaturedPlugins(limit = 6) {
    return this.getMarketplacePlugins({ featured: true, limit })
  },
  
  // 获取最新插件
  getNewestPlugins(limit = 10) {
    return this.getMarketplacePlugins({ limit })
  },
  
  // 搜索插件
  searchPlugins(searchParams) {
    // 转换搜索参数以适配新的API
    const params = {
      query: searchParams.query,
      category_id: searchParams.category_id,
      tag: searchParams.tags && searchParams.tags.length > 0 ? searchParams.tags[0] : undefined,
      featured: searchParams.featured,
      skip: 0,
      limit: 20
    }
    
    return this.getMarketplacePlugins(params)
  },
  
  // 获取插件详情
  getPluginDetail(pluginId) {
    return this.getMarketplacePlugin(pluginId)
  },
  
  // 评论插件 - 这个功能暂时不可用，因为基于文件的插件市场不支持评论
  reviewPlugin(pluginId, reviewData) {
    console.warn('基于文件的插件市场不支持评论功能')
    return Promise.resolve({ success: false, message: '基于文件的插件市场不支持评论功能' })
  }
}

// 邮箱验证相关API
export const verifyEmail = (token) => {
  console.log('验证邮箱，令牌:', token);
  return api.post('/auth/verify-email', { token });
};

export const resendVerificationEmail = (email) => {
  return api.post('/auth/resend-verification', { email });
};

export const testEmailSending = (email) => {
  return api.post(`/auth/test-email?email=${encodeURIComponent(email)}`, {});
};

// 插件市场API
export const marketplaceApi = {
  // 获取插件市场基本信息
  getMarketplaceInfo() {
    return api.get('/plugins/marketplace/info')
  },
  
  // 获取插件市场分类
  getMarketplaceCategories() {
    return api.get('/plugins/marketplace/categories')
  },
  
  // 获取插件市场标签
  getMarketplaceTags() {
    return api.get('/plugins/marketplace/tags')
  },
  
  // 获取插件市场插件列表
  getMarketplacePlugins(params = {}) {
    return api.get('/plugins/marketplace/plugins', { params })
  },
  
  // 获取插件市场插件详情
  getMarketplacePlugin(pluginId) {
    return api.get(`/plugins/marketplace/plugins/${pluginId}`)
  },
  
  // 下载/安装插件市场插件
  downloadMarketplacePlugin(pluginId) {
    return api.post(`/plugins/marketplace/plugins/${pluginId}/download`)
  },
  
  // 获取精选插件
  getFeaturedPlugins(limit = 6) {
    return api.get('/plugins/marketplace/plugins', { 
      params: { featured: true, limit }
    })
  },
  
  // 搜索插件
  searchPlugins(params = {}) {
    return api.get('/plugins/marketplace/plugins', { params })
  }
}

export default api 