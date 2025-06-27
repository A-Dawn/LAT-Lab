<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import ThemeSwitch from './components/ThemeSwitch.vue'

const store = useStore()
const router = useRouter()
const isDropdownOpen = ref(false)

// 获取用户认证状态
const isAuthenticated = computed(() => store.getters.isAuthenticated)
const currentUser = computed(() => store.getters.currentUser)
const isAdmin = computed(() => currentUser.value?.role === 'admin')

// 在组件挂载时获取用户信息
onMounted(async () => {
  if (localStorage.getItem('token')) {
    await store.dispatch('fetchCurrentUser')
  }
  
  // 加载插件扩展，所有用户都需要
  try {
    await store.dispatch('loadPluginExtensions')
  } catch (error) {
    console.error('加载插件扩展失败:', error)
  }
})

// 监听路由变化，确保用户信息是最新的
watch(() => router.currentRoute.value.path, async (newPath) => {
  if (localStorage.getItem('token') && !currentUser.value) {
    await store.dispatch('fetchCurrentUser')
  }
})

// 切换下拉菜单
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

// 关闭下拉菜单
const closeDropdown = () => {
  isDropdownOpen.value = false
}

// 退出登录
const logout = () => {
  store.dispatch('logout')
  router.push('/login')
  closeDropdown()
}

// 获取头像完整URL
const getAvatarUrl = (path) => {
  if (!path) return null
  // 如果已经是完整URL，则直接返回
  if (path.startsWith('http')) return path
  // 添加完整的后端服务器URL
  return `http://localhost:8000${path}`
}
</script>

<template>
  <div class="app-container" @click="closeDropdown">
    <!-- 全局导航栏 -->
    <header class="app-header">
      <div class="header-container">
        <div class="logo">
          <router-link to="/">
            <span class="logo-text">LAT-Lab</span>
            <span class="logo-dot">.</span>
          </router-link>
        </div>
        
        <nav class="main-nav">
          <ul class="nav-list">
            <li class="nav-item">
              <router-link to="/" class="nav-link">首页</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/article/new" class="nav-link">写文章</router-link>
            </li>
          </ul>
        </nav>
        
        <div class="user-actions">
          <!-- 主题切换 -->
          <ThemeSwitch @theme-changed="theme => $forceUpdate()" />
          
          <template v-if="isAuthenticated">
            <div class="user-dropdown">
              <div class="user-info" @click.stop="toggleDropdown">
                <div v-if="currentUser.avatar" class="avatar">
                  <img :src="getAvatarUrl(currentUser.avatar)" :alt="`${currentUser.username}的头像`" class="avatar-img" />
                </div>
                <div v-else class="avatar">{{ currentUser.username ? currentUser.username.charAt(0).toUpperCase() : '?' }}</div>
                <span class="username">{{ currentUser.username }}</span>
                <span class="dropdown-arrow">▼</span>
              </div>
              
              <div class="dropdown-menu" v-show="isDropdownOpen" @click.stop>
                <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
                  <span class="dropdown-icon">👤</span>
                  个人中心
                </router-link>
                <router-link v-if="isAdmin" to="/admin" class="dropdown-item" @click="closeDropdown">
                  <span class="dropdown-icon">⚙️</span>
                  管理员面板
                </router-link>
                <button @click="logout" class="dropdown-item">
                  <span class="dropdown-icon">🚪</span>
                  退出登录
                </button>
              </div>
            </div>
          </template>
          
          <template v-else>
            <router-link to="/login" class="login-button">登录</router-link>
            <router-link to="/register" class="register-button">注册</router-link>
          </template>
        </div>
      </div>
    </header>
    
    <!-- 主要内容 -->
    <main class="app-main">
      <router-view />
    </main>
    
    <!-- 页脚 -->
    <footer class="app-footer">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-logo">
            <span class="logo-text">LAT-Lab</span>
            <span class="logo-dot">.</span>
          </div>
          <p class="footer-description">
            探索技术与人生的光。一个关于技术探索和生活思考的平台。
          </p>
        </div>
        <div class="footer-links">
          <div class="footer-section">
            <h4 class="footer-heading">导航</h4>
            <router-link to="/" class="footer-link">首页</router-link>
            <router-link to="/article/new" class="footer-link">写文章</router-link>
            <router-link to="/profile" class="footer-link">个人中心</router-link>
            <a href="http://localhost:8000/api/rss/feed" target="_blank" class="footer-link rss-link">
              <span class="footer-icon">📡</span> RSS订阅
            </a>
          </div>
          <div class="footer-section">
            <h4 class="footer-heading">关于</h4>
            <a href="https://luminarc.tech" target="_blank" class="footer-link">官方网站</a>
            <a href="mailto:contact@luminarc.tech" class="footer-link">联系我们</a>
            <a href="#" class="footer-link">使用条款</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="copyright">
          &copy; {{ new Date().getFullYear() }} LAT-Lab. 保留所有权利。
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
/* 全局样式，会应用到所有页面 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--bg-primary);
  transition: all 0.3s ease;
}

/* 确保html元素也继承主题颜色 */
html {
  color: var(--text-primary);
  background-color: var(--bg-primary);
}

/* 容器样式 */
.container, 
.card, 
.panel, 
.box,
.article-card,
.plugin-widget,
.sidebar-widget {
  background-color: var(--card-bg);
  color: var(--text-primary);
  border-color: var(--border-color);
}

a {
  text-decoration: none;
  color: var(--primary-color);
  transition: color 0.3s;
}

a:hover {
  color: var(--secondary-color);
}

ul {
  list-style: none;
}

button {
  cursor: pointer;
  font-family: inherit;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部导航栏 */
.app-header {
  background-color: var(--bg-secondary);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.logo a {
  text-decoration: none;
}

.logo-text {
  color: var(--primary-color);
  transition: all 0.3s ease;
}

.logo-dot {
  color: var(--secondary-color);
  font-size: 2rem;
}

.logo a:hover .logo-text {
  transform: translateX(-2px);
}

.main-nav {
  flex: 1;
  margin-left: 60px;
}

.nav-list {
  display: flex;
  gap: 30px;
}

.nav-link {
  color: var(--text-secondary);
  font-size: 1.05rem;
  font-weight: 500;
  padding: 8px 0;
  position: relative;
  transition: color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--primary-color);
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
  transform: scaleX(1);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.nav-link:hover::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
  transform: scaleX(0.6);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.login-button,
.register-button {
  padding: 10px 20px;
  border-radius: 30px;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s;
}

.login-button {
  color: var(--primary-color);
  background-color: transparent;
  border: 1px solid var(--primary-color);
}

.login-button:hover {
  background-color: var(--hover-color);
  transform: translateY(-2px);
}

.register-button {
  color: white !important;
  background-color: var(--primary-color);
  border: 1px solid var(--primary-color);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.register-button:hover {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

/* 用户下拉菜单 */
.user-dropdown {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 30px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background-color: var(--hover-color);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.username {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-arrow {
  font-size: 0.7rem;
  color: var(--text-tertiary);
  margin-left: 3px;
  transition: transform 0.3s ease;
}

.user-info:hover .dropdown-arrow {
  transform: translateY(2px);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  z-index: 1000;
  overflow: hidden;
  transform-origin: top right;
  animation: dropdownFadeIn 0.3s ease;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 0.95rem;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background-color: var(--hover-color);
}

.dropdown-icon {
  font-size: 1.1rem;
}

/* 主要内容区域 */
.app-main {
  flex: 1;
  width: 100%;
  margin: 0 auto;
}

/* 页脚 */
.app-footer {
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 0;
  margin-top: 60px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 50px 20px;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 40px;
}

.footer-content {
  max-width: 400px;
}

.footer-logo {
  display: flex;
  align-items: baseline;
  margin-bottom: 15px;
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.footer-logo a {
  text-decoration: none;
}

.footer-description {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
}

.footer-links {
  display: flex;
  gap: 60px;
}

.footer-section {
  display: flex;
  flex-direction: column;
}

.footer-heading {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.footer-link {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.footer-link:hover {
  color: var(--primary-color);
  transform: translateX(5px);
}

.footer-icon {
  display: inline-block;
  margin-right: 5px;
  font-size: 1.1rem;
  vertical-align: middle;
}

.rss-link {
  display: flex;
  align-items: center;
  gap: 5px;
}

.footer-bottom {
  background-color: var(--bg-elevated);
  padding: 20px 0;
  text-align: center;
}

.copyright {
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header-container {
    flex-wrap: wrap;
    height: auto;
    padding: 15px 20px;
    gap: 10px;
  }

  .logo {
    margin-bottom: 0;
    flex: 1;
  }

  .user-actions {
    order: 2;
    margin-left: 0;
    display: flex;
    justify-content: flex-end;
    flex: 1;
  }

  .main-nav {
    order: 3;
    width: 100%;
    margin-left: 0;
    margin-top: 12px;
    border-top: 1px solid var(--border-color);
    padding-top: 10px;
  }

  .nav-list {
    justify-content: space-around;
    padding: 8px 0;
  }
  
  .login-button, 
  .register-button {
    padding: 6px 12px;
    font-size: 0.9rem;
  }

  .user-dropdown {
    position: static;
  }

  .dropdown-menu {
    position: absolute;
    right: 20px;
    top: 60px;
    width: calc(100% - 40px);
    max-width: 280px;
  }

  .user-info {
    padding: 4px 8px;
  }

  .avatar {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }

  .theme-switch {
    margin-right: 5px;
  }

  .footer-container {
    flex-direction: column;
    gap: 30px;
    padding: 30px 20px;
  }
  
  .footer-content {
    max-width: 100%;
    text-align: center;
  }

  .footer-links {
    gap: 30px;
    flex-wrap: wrap;
    justify-content: center;
    width: 100%;
  }
  
  .app-footer {
    margin-top: 40px;
  }
}

/* 更小屏幕的进一步优化 */
@media (max-width: 480px) {
  .header-container {
    padding: 12px 15px;
  }
  
  .logo-text {
    font-size: 1.5rem;
  }
  
  .username {
    display: none;
  }
  
  .dropdown-arrow {
    margin-left: 0;
  }
  
  .nav-list {
    gap: 15px;
  }
  
  .nav-link {
    font-size: 0.95rem;
  }
  
  .login-button, 
  .register-button {
    padding: 5px 10px;
    font-size: 0.85rem;
  }
  
  .theme-switch {
    transform: scale(0.9);
    margin-right: 0;
  }
  
  .footer-section {
    width: 100%;
    text-align: center;
  }
}
</style>
