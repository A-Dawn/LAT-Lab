import { createStore } from 'vuex'
import { userApi, pluginApi } from '../services/api'

const store = createStore({
  state() {
    return {
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      plugins: {
        activePlugins: [],
        frontendExtensions: [],
        homeWidgets: []
      }
    }
  },
  
  getters: {
    currentUser: state => state.user,
    isAuthenticated: state => state.isAuthenticated,
    isLoading: state => state.isLoading,
    error: state => state.error,
    activePlugins: state => state.plugins.activePlugins,
    frontendExtensions: state => state.plugins.frontendExtensions,
    homeWidgets: state => state.plugins.homeWidgets
  },
  
  mutations: {
    setUser(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    },
    
    setLoading(state, status) {
      state.isLoading = status
    },
    
    setError(state, error) {
      state.error = error
    },
    
    clearError(state) {
      state.error = null
    },
    
    setActivePlugins(state, plugins) {
      state.plugins.activePlugins = plugins
    },
    
    addFrontendExtension(state, extension) {
      state.plugins.frontendExtensions.push(extension)
    },
    
    removeFrontendExtension(state, id) {
      state.plugins.frontendExtensions = state.plugins.frontendExtensions.filter(ext => ext.id !== id)
    },
    
    addHomeWidget(state, widget) {
      state.plugins.homeWidgets.push(widget)
    },
    
    removeHomeWidget(state, id) {
      state.plugins.homeWidgets = state.plugins.homeWidgets.filter(w => w.id !== id)
    },
    
    clearPluginExtensions(state) {
      state.plugins.frontendExtensions = []
      state.plugins.homeWidgets = []
    }
  },
  
  actions: {
    async fetchCurrentUser({ commit }) {
      try {
        commit('setLoading', true)
        commit('clearError')
        
        const token = localStorage.getItem('token')
        
        if (!token) {
          commit('setUser', null)
          return null
        }
        
        const timestamp = new Date().getTime()
        const userData = await userApi.getCurrentUser()
        console.log('获取到用户信息:', userData)
        commit('setUser', userData)
        return userData
      } catch (error) {
        console.error('获取用户信息失败:', error)
        commit('setUser', null)
        commit('setError', error.response?.data?.detail || '获取用户信息失败')
        localStorage.removeItem('token')
        return null
      } finally {
        commit('setLoading', false)
      }
    },
    
    // 用户登录
    async login({ commit, dispatch }, credentials) {
      try {
        commit('setLoading', true)
        commit('clearError')
        
        // 先清除之前的用户状态
        commit('setUser', null)
        
        const response = await userApi.login(credentials)
        
        // 保存token到本地存储
        localStorage.setItem('token', response.access_token)
        
        // 获取用户信息
        const userData = await dispatch('fetchCurrentUser')
        
        if (!userData) {
          throw new Error('登录后获取用户信息失败')
        }
        
        // 登录成功后加载插件扩展（所有用户都加载）
        dispatch('loadPluginExtensions')
        
        return response
      } catch (error) {
        commit('setError', error.response?.data?.detail || '登录失败')
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    // 用户注册
    async register({ commit }, userData) {
      try {
        commit('setLoading', true)
        commit('clearError')
        
        const response = await userApi.register(userData)
        return response
      } catch (error) {
        commit('setError', error.response?.data?.detail || '注册失败')
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    // 用户登出
    logout({ commit }) {
      // 清除本地存储中的token
      localStorage.removeItem('token')
      localStorage.removeItem('remember')
      
      // 清除用户状态
      commit('setUser', null)
      
      // 清除插件扩展
      commit('clearPluginExtensions')
      
      // 清除可能存在的错误信息
      commit('clearError')
      
      console.log('用户已登出，状态已清除')
    },
    
    // 更新用户资料
    async updateProfile({ commit, state }, userData) {
      try {
        commit('setLoading', true)
        commit('clearError')
        
        const response = await userApi.updateProfile(userData)
        
        // 更新本地用户数据
        commit('setUser', { ...state.user, ...response })
        
        return response
      } catch (error) {
        commit('setError', error.response?.data?.detail || '更新资料失败')
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    // 修改密码
    async changePassword({ commit }, passwordData) {
      try {
        commit('setLoading', true)
        commit('clearError')
        
        const response = await userApi.changePassword(passwordData)
        return response
      } catch (error) {
        commit('setError', error.response?.data?.detail || '修改密码失败')
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    // 加载插件扩展
    async loadPluginExtensions({ commit, state }) {
      try {
        console.log('开始加载插件扩展...')
        
        // 清除现有扩展
        commit('clearPluginExtensions')
        
        // 获取激活的插件
        const activePlugins = await pluginApi.getPlugins({ active_only: true })
        commit('setActivePlugins', activePlugins)
        
        // 遍历插件，查找扩展类型的插件
        for (const plugin of activePlugins) {
          if (plugin.name.toLowerCase().includes('extension') || 
              plugin.description.toLowerCase().includes('extension') ||
              plugin.name.toLowerCase().includes('widget') || 
              plugin.description.toLowerCase().includes('widget')) {
            
            console.log('发现扩展插件:', plugin.name)
            
            try {
              // 运行插件获取扩展内容
              const result = await pluginApi.runPlugin(plugin.id)
              
              if (result && result.output) {
                // 尝试从插件输出中提取JSON配置
                const configMatch = result.output.match(/```json([\s\S]*?)```/)
                if (configMatch && configMatch[1]) {
                  try {
                    const config = JSON.parse(configMatch[1].trim())
                    
                    // 处理不同类型的扩展
                    if (config.type === 'home-widget') {
                      commit('addHomeWidget', {
                        id: plugin.id,
                        name: config.name || plugin.name,
                        content: config.content || '',
                        position: config.position || 'sidebar',
                        priority: config.priority || 100,
                        html: config.html || ''
                      })
                      console.log('添加了首页小部件:', config.name)
                    } else if (config.type === 'frontend-extension') {
                      commit('addFrontendExtension', {
                        id: plugin.id,
                        name: config.name || plugin.name,
                        target: config.target || 'all',
                        html: config.html || '',
                        js: config.js || '',
                        css: config.css || ''
                      })
                      console.log('添加了前端扩展:', config.name)
                    }
                  } catch (parseError) {
                    console.error('解析插件配置失败:', parseError)
                  }
                }
              }
            } catch (runError) {
              console.error('运行插件失败:', runError)
            }
          }
        }
        
        console.log('插件扩展加载完成')
      } catch (error) {
        console.error('加载插件扩展失败:', error)
      }
    }
  },
  
  // 动态注册模块
  modules: {}
})

// 在开发环境下注册开发工具模块
// 生产环境构建时此代码块将被完全移除
if (import.meta.env.DEV) {
  // 使用动态导入确保生产环境不包含此代码
  import('./modules/devTools.js').then(module => {
    store.registerModule('devTools', module.default);
    console.log('开发工具模块已注册');
  }).catch(error => {
    console.error('开发工具模块加载失败:', error);
  });
}

export default store 