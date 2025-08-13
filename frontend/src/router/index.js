import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import NotFound from '../views/NotFound.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { 
      requiresGuest: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { 
      requiresGuest: true
    }
  },
  {
    path: '/article/:id',
    name: 'ArticleDetail',
    component: () => import('../views/ArticleDetail.vue'),
    props: true
  },
  {
    path: '/article/new',
    name: 'CreateArticle',
    component: () => import('../views/ArticleEditor.vue'),
    meta: { 
      requiresAuth: true
    }
  },
  {
    path: '/article/:id/edit',
    name: 'EditArticle',
    component: () => import('../views/ArticleEditor.vue'),
    props: true,
    meta: { 
      requiresAuth: true
    }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfile.vue'),
    meta: { 
      requiresAuth: true
    }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true
    },
    children: [
      {
        path: 'articles',
        name: 'AdminArticles',
        component: () => import('../views/admin/AdminArticles.vue')
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/AdminUsers.vue')
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('../views/admin/AdminCategories.vue')
      },
      {
        path: 'comments',
        name: 'AdminComments',
        component: () => import('../views/admin/AdminComments.vue')
      },
      {
        path: 'plugins',
        name: 'AdminPlugins',
        component: () => import('../views/admin/AdminPlugins.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
        children: [
          {
            path: 'marketplace',
            name: 'PluginMarketplace',
            component: () => import('../views/admin/AdminPluginMarketplace.vue'),
            meta: { requiresAuth: true, requiresAdmin: true },
          }
        ]
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: () => import('../views/admin/AdminTags.vue')
      },
      {
        path: 'about',
        name: 'AdminAbout',
        component: () => import('../views/admin/AdminAbout.vue')
      },
      // 开发工具路由 - 仅在开发环境下可用
      ...(import.meta.env.DEV ? [{
        path: 'dev-tools',
        name: 'DevTools',
        component: () => import('../views/admin/DevTools.vue'),
        meta: { 
          requiresAuth: true, 
          requiresAdmin: true,
          requiresDev: true // 需要开发环境
        }
      }] : []),
      {
        path: '',
        redirect: { name: 'AdminArticles' }
      }
    ]
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: () => import('../views/VerifyEmail.vue'),
    meta: {
      title: '邮箱验证',
      requiresAuth: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  
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

  if (to.meta.requiresDev && import.meta.env.PROD) {
    console.log('此功能仅在开发环境下可用')
    next({ path: '/admin' })
    return
  }
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
  else if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('需要登录权限，但用户未登录')
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