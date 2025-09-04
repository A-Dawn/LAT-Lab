import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import NotFound from '../views/NotFound.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { 
      transition: 'glass-fade'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { 
      requiresGuest: true,
      transition: 'glass-slide'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { 
      requiresGuest: true,
      transition: 'glass-slide'
    }
  },
  {
    path: '/article/:id',
    name: 'ArticleDetail',
    component: () => import('../views/ArticleDetail.vue'),
    props: true,
    meta: {
      transition: 'glass-rise'
    }
  },
  {
    path: '/article/new',
    name: 'CreateArticle',
    component: () => import('../views/ArticleEditor.vue'),
    meta: { 
      requiresAuth: true,
      transition: 'glass-slide'
    }
  },
  {
    path: '/article/:id/edit',
    name: 'EditArticle',
    component: () => import('../views/ArticleEditor.vue'),
    props: true,
    meta: { 
      requiresAuth: true,
      transition: 'glass-slide'
    }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfile.vue'),
    meta: { 
      requiresAuth: false,  // 允许未认证用户访问
      transition: 'glass-fade'
    }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      transition: 'glass-fade'
    },
    // 所有子路由放在一个children数组中
    children: [
      // 文章管理
      {
        path: 'articles',
        name: 'AdminArticles',
        component: () => import('../views/admin/AdminArticles.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/AdminUsers.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        }
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('../views/admin/AdminCategories.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        }
      },
      {
        path: 'comments',
        name: 'AdminComments',
        component: () => import('../views/admin/AdminComments.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        }
      },
      {
        path: 'article-approval',
        name: 'AdminArticleApproval',
        component: () => import('../views/admin/AdminArticleApproval.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        }
      },
      {
        path: 'plugins',
        name: 'AdminPlugins',
        component: () => import('../views/admin/AdminPlugins.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        },
        children: [
          {
            path: 'marketplace',
            name: 'PluginMarketplace',
            component: () => import('../views/admin/AdminPluginMarketplace.vue'),
            meta: { 
              requiresAuth: true, 
              requiresAdmin: true,
              transition: 'glass-fade'
            }
          }
        ]
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: () => import('../views/admin/AdminTags.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        }
      },
      {
        path: 'about',
        name: 'AdminAbout',
        component: () => import('../views/admin/AdminAbout.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-fade'
        }
      },
      // 开发工具路由
      {
        path: 'dev-tools',
        name: 'DevTools',
        component: () => import('../views/admin/DevTools.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          transition: 'glass-bounce'
        }
      },
      // 默认重定向到文章管理
      {
        path: '',
        redirect: '/admin/articles'
      }
    ]
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: () => import('../views/VerifyEmail.vue'),
    meta: {
      title: '邮箱验证',
      requiresAuth: false,
      transition: 'glass-fade'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      transition: 'glass-fade'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const guestMode = localStorage.getItem('guest_mode') === 'true'
  
  // 对于邮箱验证页面，直接允许访问，不进行任何认证检查
  if (to.path === '/verify-email') {
    console.log('访问邮箱验证页面，直接允许')
    next()
    return
  }
  
  if (token && !store.getters.isAuthenticated) {
    try {
      await store.dispatch('fetchCurrentUser')
    } catch (e) {
      console.error('获取用户信息失败, token可能已过期', e)
      await store.dispatch('logout')
    }
  }

  const isAuthenticated = store.getters.isAuthenticated
  const currentUser = store.getters.currentUser
  const canAccessContent = store.getters.canAccessContent
  
  if (to.meta.requiresAdmin) {
    if (!isAuthenticated || !currentUser || currentUser.role !== 'admin') {
      console.log('需要管理员权限，但用户不是管理员或未登录')
      next({ 
        path: '/login', 
        query: { redirect: to.fullPath, message: '需要管理员权限' } 
      })
    } else {
      next()
    }
  } 
  // 检查是否需要登录权限
  else if (to.meta.requiresAuth && !canAccessContent) {
    console.log('需要登录权限，但用户未登录且不是访客模式')
    next({ 
      path: '/login', 
      query: { redirect: to.fullPath } 
    })
  } 
  // 检查是否是仅游客可访问的页面
  else if (to.meta.requiresGuest && isAuthenticated) {
    console.log('已登录用户访问游客页面')
    next({ path: '/' })
  }
  // 其他情况正常导航
  else {
    next()
  }
})

export default router 