import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Register from '../views/Register.vue'
import ArticleDetail from '../views/ArticleDetail.vue'
import ArticleEditor from '../views/ArticleEditor.vue'
import UserProfile from '../views/UserProfile.vue'
import NotFound from '../views/NotFound.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminArticles from '../views/admin/AdminArticles.vue'
import AdminUsers from '../views/admin/AdminUsers.vue'
import AdminCategories from '../views/admin/AdminCategories.vue'
import AdminComments from '../views/admin/AdminComments.vue'
import AdminPlugins from '../views/admin/AdminPlugins.vue'
import AdminTags from '../views/admin/AdminTags.vue'
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
      requiresGuest: true  // 已登录用户不应该访问登录页
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { 
      requiresGuest: true  // 已登录用户不应该访问注册页
    }
  },
  {
    path: '/article/:id',
    name: 'ArticleDetail',
    component: ArticleDetail,
    props: true
  },
  {
    path: '/article/new',
    name: 'CreateArticle',
    component: ArticleEditor,
    meta: { 
      requiresAuth: true  // 需要登录
    }
  },
  {
    path: '/article/:id/edit',
    name: 'EditArticle',
    component: ArticleEditor,
    props: true,
    meta: { 
      requiresAuth: true  // 需要登录
    }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { 
      requiresAuth: true  // 需要登录
    }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: {
      requiresAuth: true,
      requiresAdmin: true  // 需要管理员权限
    },
    children: [
      {
        path: 'articles',
        name: 'AdminArticles',
        component: AdminArticles
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: AdminCategories
      },
      {
        path: 'comments',
        name: 'AdminComments',
        component: AdminComments
      },
      {
        path: 'plugins',
        name: 'AdminPlugins',
        component: AdminPlugins,
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
        component: AdminTags
      },
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

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 获取登录状态
  const token = localStorage.getItem('token')
  
  // 1. 如果有token但Vuex中没有用户信息，尝试异步获取
  if (token && !store.getters.isAuthenticated) {
    try {
      await store.dispatch('fetchCurrentUser')
    } catch (e) {
      // token无效，清除它
      console.error('获取用户信息失败, token可能已过期', e)
      await store.dispatch('logout') // 使用action来确保状态一致
    }
  }

  // 2. 在获取用户信息后，再获取最新的状态
  const isAuthenticated = store.getters.isAuthenticated
  const currentUser = store.getters.currentUser

  // 3. 根据最新的状态进行路由判断
  // 检查是否需要管理员权限
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