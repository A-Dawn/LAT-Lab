import { createStore } from 'vuex'
import { userApi, pluginApi } from '../services/api'

const store = createStore({
  state() {
    return {
      user: null,
      isAuthenticated: false,
      isGuestMode: false,
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
    isGuestMode: state => state.isGuestMode,
    canAccessContent: state => state.isAuthenticated || state.isGuestMode,
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
      // 如果设置用户，则退出访客模式
      if (user) {
        state.isGuestMode = false
      }
    },
    
    setGuestMode(state, isGuest) {
      state.isGuestMode = isGuest
      // 如果进入访客模式，则清除用户认证状态
      if (isGuest) {
        state.user = null
        state.isAuthenticated = false
      }
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
        const guestMode = localStorage.getItem('guest_mode') === 'true'
        
        // 如果是访客模式，不尝试获取用户信息
        if (guestMode && !token) {
          commit('setUser', null)
          return null
        }
        
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
        
        // 在访客模式下，不显示错误消息
        const guestMode = localStorage.getItem('guest_mode') === 'true'
        if (!guestMode) {
          commit('setError', error.response?.data?.detail || '获取用户信息失败')
        }
        
        localStorage.removeItem('token')
        return null
      } finally {
        commit('setLoading', false)
      }
    },
    
    async loadPluginExtensions({ commit }) {
      try {
        console.log('开始加载插件扩展...')
        
        // 获取前端扩展
        let extensions = []
        try {
          const response = await pluginApi.getFrontendExtensions()
          // 确保返回的是数组
          extensions = Array.isArray(response) ? response : []
          console.log('获取到前端扩展:', extensions)
        } catch (error) {
          const status = error.response?.status
          const guestMode = localStorage.getItem('guest_mode') === 'true'
          
          // 处理特定错误状态
          if (status === 422) {
            console.warn('前端扩展API返回422错误，可能是请求参数问题:', error.response?.data)
          } else if (status === 401 || status === 403) {
            // 访客模式下的权限错误是正常的，不需要警告
            if (!guestMode) {
              console.warn('无权限获取前端扩展:', error)
            } else {
              console.log('访客模式下跳过加载前端扩展')
            }
          } else {
            console.warn('获取前端扩展失败，使用空数组:', error)
          }
          extensions = []
        }
        
        // 设置激活的插件
        commit('setActivePlugins', extensions)
        
        // 动态加载前端扩展
        for (const extension of extensions) {
          if (extension && extension.type === 'frontend' && extension.enabled) {
            try {
              // 确保modulePath存在且有效
              if (!extension.modulePath) {
                console.error('前端扩展缺少modulePath:', extension)
                continue
              }
              
              // 动态导入扩展模块
              const module = await import(/* @vite-ignore */ extension.modulePath)
                .catch(err => {
                  console.error(`动态导入扩展模块 ${extension.modulePath} 失败:`, err)
                  return null
                })
                
              if (module?.default?.install) {
                try {
                  await module.default.install()
                  commit('addFrontendExtension', extension)
                  console.log(`前端扩展 ${extension.name} 加载成功`)
                } catch (err) {
                  console.error(`安装前端扩展 ${extension.name} 失败:`, err)
                }
              } else {
                console.error(`前端扩展 ${extension.name} 格式不正确，缺少install方法`)
              }
            } catch (error) {
              console.error(`加载前端扩展 ${extension.name} 失败:`, error)
            }
          }
        }
        
        // 加载首页小部件
        let widgets = []
        try {
          const response = await pluginApi.getHomeWidgets()
          // 确保返回的是数组
          widgets = Array.isArray(response) ? response : []
          console.log('获取到首页小部件:', widgets)
        } catch (error) {
          const status = error.response?.status
          const guestMode = localStorage.getItem('guest_mode') === 'true'
          
          // 处理特定错误状态
          if (status === 422) {
            console.warn('首页小部件API返回422错误，可能是请求参数问题:', error.response?.data)
          } else if (status === 401 || status === 403) {
            // 访客模式下的权限错误是正常的，不需要警告
            if (!guestMode) {
              console.warn('无权限获取首页小部件:', error)
            } else {
              console.log('访客模式下跳过加载首页小部件')
            }
          } else {
            console.warn('获取首页小部件失败，使用空数组:', error)
          }
          widgets = []
        }
        
        for (const widget of widgets) {
          if (widget && widget.enabled) {
            commit('addHomeWidget', widget)
          }
        }
        
        console.log('插件扩展加载完成')
      } catch (error) {
        console.error('加载插件扩展失败:', error)
        // 确保即使出错也设置空数组，避免后续错误
        commit('setActivePlugins', [])
      }
    },
    
    async login({ commit }, credentials) {
      try {
        commit('setLoading', true)
        commit('clearError')
        
        const response = await userApi.login(credentials)
        
        // 保存token到localStorage
        localStorage.setItem('token', response.access_token)
        
        // 获取用户信息
        const userData = await userApi.getCurrentUser()
        commit('setUser', userData)
        
        // 返回完整的登录响应信息，包括验证状态
        return {
          ...userData,
          is_verified: response.is_verified,
          email: response.email
        }
      } catch (error) {
        console.error('登录失败:', error)
        commit('setError', error.response?.data?.detail || '登录失败，请检查用户名和密码')
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    async logout({ commit }) {
      try {
        commit('setUser', null)
        commit('setGuestMode', false)
        localStorage.removeItem('token')
        localStorage.removeItem('guest_mode')
        console.log('用户已退出登录')
      } catch (error) {
        console.error('退出登录失败:', error)
        // 即使出错也要清除本地状态
        commit('setUser', null)
        commit('setGuestMode', false)
        localStorage.removeItem('token')
        localStorage.removeItem('guest_mode')
      }
    },
    
    enterGuestMode({ commit }) {
      commit('setGuestMode', true)
      localStorage.setItem('guest_mode', 'true')
      console.log('已进入访客模式')
    },
    
    exitGuestMode({ commit }) {
      commit('setGuestMode', false)
      localStorage.removeItem('guest_mode')
      console.log('已退出访客模式')
    }
  }
})

// 导入devTools模块
import devToolsModule from './modules/devTools'

// 注册devTools模块
if (!store.hasModule('devTools')) {
  store.registerModule('devTools', devToolsModule)
  console.log('✅ devTools module registered successfully')
}

// 兼容旧代码，保留loadDevToolsModule方法
const loadDevToolsModule = async () => {
  if (!store.hasModule('devTools')) {
    store.registerModule('devTools', devToolsModule)
    console.log('✅ devTools module registered successfully (via loadDevToolsModule)')
    return true
  }
  return true
}

// 导出 store 实例
export default store