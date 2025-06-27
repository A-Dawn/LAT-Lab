<script setup>
import { computed, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

// 侧边栏收起状态
const isSidebarCollapsed = ref(false)
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// 获取当前用户信息
const currentUser = computed(() => store.getters.currentUser)

// 检查是否是管理员
const isAdmin = computed(() => {
  return currentUser.value && currentUser.value.role === 'admin'
})

// 如果不是管理员，重定向到首页
onMounted(() => {
if (!isAdmin.value) {
  router.push('/')
}
})

// 导航项
const navItems = [
  { path: '/admin/articles', icon: '📄', label: '文章管理' },
  { path: '/admin/users', icon: '👤', label: '用户管理' },
  { path: '/admin/categories', icon: '📁', label: '分类管理' },
  { path: '/admin/tags', icon: '🏷️', label: '标签管理' },
  { path: '/admin/comments', icon: '💬', label: '评论管理' },
  { path: '/admin/plugins', icon: '🧩', label: '插件管理' }
]
</script>

<template>
  <div class="admin-dashboard">
    <div class="admin-header" aria-label="管理员面板头部">
      <div class="container">
        <div class="header-left">
          <button 
            class="sidebar-toggle" 
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
          <router-link to="/" class="home-link" aria-label="返回首页">
            <span aria-hidden="true">🏠</span>
          </router-link>
        </div>
      </div>
    </div>
    
    <div class="admin-content">
      <div class="container">
        <div class="admin-layout">
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
  background-color: #f56c6c;
  color: white;
}

.admin-btn-danger:hover {
  filter: brightness(1.1);
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
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.status-inactive {
  background-color: rgba(144, 147, 153, 0.1);
  color: #909399;
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
  max-width: 1200px;
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
}

.toggle-icon::before {
  transform: translateY(-6px);
}

.toggle-icon::after {
  transform: translateY(6px);
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

.admin-content {
  padding: 20px 0;
}

.admin-layout {
  display: flex;
  gap: 20px;
  min-height: calc(100vh - 100px);
  position: relative;
}

.admin-sidebar {
  width: 250px;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  flex-shrink: 0;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  position: sticky;
  top: 80px;
  height: calc(100vh - 100px);
  overflow-y: auto;
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
}

.collapsed .nav-icon {
  margin-right: 0;
}

.nav-label {
  transition: opacity 0.3s, visibility 0.3s;
  white-space: nowrap;
}

.collapsed .nav-label {
  opacity: 0;
  visibility: hidden;
  width: 0;
  overflow: hidden;
}

.admin-main {
  flex: 1;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  min-height: calc(100vh - 100px);
}

.admin-main.expanded {
  margin-left: -160px;
}

/* 响应式调整 */
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
  }
  
  .admin-sidebar.collapsed {
    width: 100%;
  }
  
  .collapsed .nav-label {
    opacity: 1;
    visibility: visible;
    width: auto;
  }
  
  .collapsed .nav-icon {
    margin-right: 10px;
  }
  
  .admin-main.expanded {
    margin-left: 0;
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
</style> 