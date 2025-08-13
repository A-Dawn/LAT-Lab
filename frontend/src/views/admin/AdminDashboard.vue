<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

// 侧边栏收起状态
const isSidebarCollapsed = ref(false)
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// 计算是否显示遮罩层（只在中等屏幕且侧边栏展开时显示）
const showOverlay = computed(() => {
  if (window.innerWidth > 992) return false;
  if (window.innerWidth <= 768) return false;
  return !isSidebarCollapsed.value;
})

// 点击遮罩层时收起侧边栏
const handleOverlayClick = () => {
  isSidebarCollapsed.value = true;
}

// 获取当前用户信息
const currentUser = computed(() => store.getters.currentUser)

// 检查是否是管理员
const isAdmin = computed(() => {
  return currentUser.value && currentUser.value.role === 'admin'
})

// 检查是否是开发环境
const isDevelopment = computed(() => {
  return import.meta.env.DEV
})

// 如果不是管理员，重定向到首页
onMounted(() => {
if (!isAdmin.value) {
  router.push('/')
}
  
  // 添加窗口大小变化监听，用于处理响应式布局
  window.addEventListener('resize', handleResize);
})

// 在组件销毁时移除事件监听
const handleResize = () => {
  // 如果是大屏幕且侧边栏是折叠状态，则可能需要展开
  if (window.innerWidth > 992 && isSidebarCollapsed.value) {
    // 可以选择自动展开或保持现状
  }
}

// 在组件销毁时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
})

// 导航项 - 生产环境构建时开发工具项将被完全移除
const navItems = computed(() => {
  const baseItems = [
    { path: '/admin/articles', icon: '📄', label: '文章管理' },
    { path: '/admin/users', icon: '👤', label: '用户管理' },
    { path: '/admin/categories', icon: '📁', label: '分类管理' },
    { path: '/admin/tags', icon: '🏷️', label: '标签管理' },
    { path: '/admin/comments', icon: '💬', label: '评论管理' },
    { path: '/admin/plugins', icon: '🧩', label: '插件管理' },
    { path: '/admin/about', icon: '👨‍💻', label: '关于博主' }
  ]
  
  // 开发工具项仅在开发环境下包含
  if (isDevelopment.value) {
    baseItems.push({ path: '/admin/dev-tools', icon: '🛠️', label: '开发工具' })
  }
  
  return baseItems
})
</script>

<template>
  <div class="admin-dashboard">
    <div class="admin-header" aria-label="管理员面板头部">
      <div class="container">
        <div class="header-left">
          <button 
            class="sidebar-toggle" 
            :class="{ 'collapsed': isSidebarCollapsed }"
            @click="toggleSidebar" 
            aria-label="切换侧边栏"
          >
            <span class="toggle-icon" aria-hidden="true"></span>
          </button>
        <h1 class="admin-title">管理员面板</h1>
        </div>
        
        <div class="admin-user">
          <span>{{ currentUser?.username }}</span>
          <span class="admin-role">管理员</span>
          <!-- 开发环境标识 - 生产构建时此元素将被完全移除 -->
          <span v-if="isDevelopment" class="dev-badge" title="开发环境">DEV</span>
          <router-link to="/" class="home-link" aria-label="返回首页">
            <span aria-hidden="true">🏠</span>
          </router-link>
        </div>
      </div>
    </div>
    
    <div class="admin-content">
      <div class="container">
        <div class="admin-layout">
          <!-- 遮罩层 -->
          <div 
            v-if="showOverlay" 
            class="sidebar-overlay" 
            @click="handleOverlayClick"
          ></div>
          
          <!-- 侧边导航 -->
          <div 
            class="admin-sidebar" 
            :class="{ 'collapsed': isSidebarCollapsed }" 
            role="navigation"
            aria-label="管理导航"
          >
            <div class="sidebar-header">
              <h2>LAT-Lab 管理系统</h2>
            </div>
            
            <nav class="sidebar-nav">
              <router-link 
                v-for="item in navItems" 
                :key="item.path"
                :to="item.path" 
                class="nav-item"
                :aria-label="item.label"
              >
                <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
                <span class="nav-label">{{ item.label }}</span>
              </router-link>
              
              <a @click="router.push('/')" class="nav-item nav-home" aria-label="返回首页">
                <span class="nav-icon" aria-hidden="true">🏠</span>
                <span class="nav-label">返回首页</span>
              </a>
            </nav>
          </div>
          
          <!-- 主要内容区域 -->
          <div 
            class="admin-main" 
            :class="{ 'expanded': isSidebarCollapsed }"
            role="main"
            aria-label="管理内容"
          >
            <router-view />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* 将通用样式移到非scoped部分，确保应用于子组件 */
.admin-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background-color: var(--card-bg);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
}

.admin-table th,
.admin-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.admin-table th {
  background-color: var(--bg-elevated);
  font-weight: 600;
  color: var(--text-primary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.admin-table tr:hover {
  background-color: var(--bg-hover);
}

.admin-table tr:last-child td {
  border-bottom: none;
}

/* 管理员页面的容器 */
.admin-container {
  background-color: var(--card-bg);
  color: var(--text-primary);
  padding: 20px;
  border-radius: 8px;
  box-shadow: var(--card-shadow);
}

/* 插件卡片 */
.plugins-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--card-bg);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
}

.plugins-table th,
.plugins-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.plugins-table th {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.plugins-table tr:hover {
  background-color: var(--bg-hover);
}

.plugins-table tr:last-child td {
  border-bottom: none;
}

/* 弹窗背景 */
.dialog {
  background-color: var(--card-bg);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0;
  overflow: hidden;
}

.dialog-header {
  background-color: var(--bg-elevated);
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.dialog-content {
  padding: 16px;
}

.dialog-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 表单样式 */
.admin-form-group {
  margin-bottom: 16px;
}

.admin-form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--text-secondary);
}

.admin-form-group input,
.admin-form-group textarea,
.admin-form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 1rem;
}

.admin-form-group input:focus,
.admin-form-group textarea:focus,
.admin-form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

/* 按钮样式 */
.admin-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.admin-btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.admin-btn-primary:hover {
  filter: brightness(1.1);
}

.admin-btn-secondary {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.admin-btn-secondary:hover {
  background-color: var(--bg-hover);
}

.admin-btn-danger {
  background-color: var(--error-color);
  color: white;
}

.admin-btn-danger:hover {
  background-color: var(--error-hover);
}

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-active {
  background-color: rgba(var(--success-color), 0.1);
  color: var(--success-color);
}

.status-inactive {
  background-color: rgba(var(--text-tertiary), 0.1);
  color: var(--text-tertiary);
}

/* 加载状态 */
.admin-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--text-secondary);
}

.admin-loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(76, 132, 255, 0.2);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 段落和提示 */
.admin-hint {
  color: var(--text-tertiary);
  font-size: 0.9rem;
  margin: 8px 0;
}
</style>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.admin-header {
  background-color: var(--bg-secondary);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 10;
}

.container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 20px;
}

.admin-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--text-primary);
  border-radius: 4px;
  transition: all 0.3s;
}

.sidebar-toggle:hover {
  background-color: var(--bg-hover);
}

.toggle-icon {
  position: relative;
  width: 18px;
  height: 2px;
  background-color: currentColor;
  transition: all 0.3s;
}

.toggle-icon::before,
.toggle-icon::after {
  content: '';
  position: absolute;
  width: 18px;
  height: 2px;
  background-color: currentColor;
  transition: all 0.3s;
  left: 0;
}

.toggle-icon::before {
  transform: translateY(-6px);
}

.toggle-icon::after {
  transform: translateY(6px);
}

/* 添加折叠状态的按钮样式 */
.collapsed .toggle-icon {
  background-color: transparent;
}

.collapsed .toggle-icon::before {
  transform: rotate(45deg);
}

.collapsed .toggle-icon::after {
  transform: rotate(-45deg);
}

.admin-title {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
}

.admin-role {
  background-color: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

/* 开发环境标识 */
.dev-badge {
  background-color: var(--success-color);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.home-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.3s ease;
}

.home-link:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-2px);
}

.admin-layout {
  display: flex;
  min-height: calc(100vh - 100px);
  position: relative;
  overflow-x: auto;
}

.admin-content {
  padding: 20px 0;
  overflow-x: auto;
  width: 100%;
}

.admin-sidebar {
  width: 250px;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  flex-shrink: 0;
  border: 1px solid var(--border-color);
  transition: width 0.3s ease;
  position: absolute;
  top: 0;
  left: 0;
  height: calc(100vh - 100px);
  overflow-y: auto;
  z-index: 10;
}

.admin-sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.collapsed .sidebar-header {
  padding: 15px 10px;
  text-align: center;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
  transition: all 0.3s ease;
  white-space: nowrap;
}

.collapsed .sidebar-header h2 {
  font-size: 0;
}

.sidebar-nav {
  padding: 10px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: var(--text-secondary);
  transition: all 0.3s;
  cursor: pointer;
  text-decoration: none;
  border-radius: 4px;
  margin: 0 10px 5px 10px;
}

.collapsed .nav-item {
  padding: 12px;
  justify-content: center;
}

.nav-item:hover, .nav-item.router-link-active {
  background-color: var(--bg-hover);
  color: var(--primary-color);
}

.nav-item.router-link-active {
  background-color: rgba(76, 132, 255, 0.1);
  font-weight: 500;
}

.nav-icon {
  margin-right: 10px;
  font-size: 1.2rem;
  transition: margin 0.3s;
  width: 18px;
  display: inline-block;
  text-align: center;
}

.collapsed .nav-icon {
  margin-right: 0;
  width: auto;
}

.nav-label {
  transition: opacity 0.2s, visibility 0.2s, width 0.2s;
  white-space: nowrap;
}

.collapsed .nav-label {
  opacity: 0;
  visibility: hidden;
  width: 0;
  display: none;
  overflow: hidden;
}

.admin-main {
  flex: 1;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: margin-left 0.3s ease;
  min-height: calc(100vh - 100px);
  min-width: 800px;
  width: 100%;
  margin-left: 270px; /* 侧边栏宽度(250px) + 间距(20px) */
}

.admin-main.expanded {
  margin-left: 90px; /* 折叠后侧边栏宽度(70px) + 间距(20px) */
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .admin-main {
    min-width: 700px;
  }
}

@media (max-width: 992px) {
  .admin-sidebar {
    position: fixed;
    z-index: 1000;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
    top: 65px;
  }
  
  .admin-main {
    margin-left: 0;
    min-width: 100%;
  }
}

@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
  }
  
  .admin-sidebar {
    width: 100%;
    position: relative;
    top: 0;
    height: auto;
    margin-bottom: 20px;
    box-shadow: none;
  }
  
  .admin-sidebar.collapsed {
    width: 100%;
  }
  
  .collapsed .nav-label {
    opacity: 1;
    visibility: visible;
    width: auto;
    display: inline;
  }
  
  .collapsed .nav-icon {
    margin-right: 10px;
  }
  
  .admin-main {
    margin-left: 0 !important;
    min-width: 100%;
  }
  
  .sidebar-toggle {
    display: none;
  }
}

@media (max-width: 480px) {
  .admin-header .container {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .admin-user {
    width: 100%;
    justify-content: flex-end;
  }
  
  .admin-main {
    padding: 15px;
  }
}

/* 添加遮罩层样式 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9;
}
</style> 