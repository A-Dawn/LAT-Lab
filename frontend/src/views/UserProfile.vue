<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { userApi, articleApi, resendVerificationEmail } from '../services/api'
import ResendVerificationButton from '../components/ResendVerificationButton.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import toast from '../utils/toast'

const store = useStore()
const router = useRouter()
const route = useRoute()

// 加载状态
const isLoading = ref(true)
const isArticlesLoading = ref(false)
const isSaving = ref(false)
const isUploading = ref(false)
const error = ref(null)

// 获取当前用户信息
const currentUser = computed(() => store.getters.currentUser)

// 检查用户是否已认证
const isAuthenticated = computed(() => store.getters.isAuthenticated)

// 检查是否为访客模式
const isGuestMode = computed(() => store.getters.isGuestMode)

// 检查是否可以访问内容（已认证用户或访客模式）
const canAccessContent = computed(() => store.getters.canAccessContent)

// 用户文章列表
const userArticles = ref([])
// 用户统计信息
const userStats = ref({
  totalViews: 0,
  totalLikes: 0,
  totalComments: 0,
  lastActive: ''
})

// 确认对话框
const confirmDialogVisible = ref(false)
const articleToDelete = ref(null)
// 分页
const currentPage = ref(1)
const pageSize = ref(5)
const totalPages = computed(() => Math.ceil(userArticles.value.length / pageSize.value))
const paginatedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return userArticles.value.slice(start, end)
})

// 当前激活的标签页
const activeTab = ref('articles')

// 编辑模式
const isEditMode = ref(false)
const editForm = ref({
  username: '',
  email: '',
  bio: ''
})

// 用户名修改
const isUsernameEditMode = ref(false)
const usernameForm = ref({
  newUsername: ''
})
const usernameError = ref('')
const usernameSuccess = ref('')

// 密码修改
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordError = ref('')
const passwordSuccess = ref('')

// 密码强度
const passwordStrength = ref(0)
const passwordStrengthText = computed(() => {
  if (passwordStrength.value === 0) return ''
  if (passwordStrength.value < 30) return '弱'
  if (passwordStrength.value < 60) return '中'
  return '强'
})
const passwordStrengthClass = computed(() => {
  if (passwordStrength.value === 0) return ''
  if (passwordStrength.value < 30) return 'medium'
  return 'strong'
})

// 头像上传
const avatarFile = ref(null)
const avatarPreview = ref('')
const fileInputRef = ref(null)

// 检查用户是否已验证
const isUserVerified = computed(() => currentUser.value?.is_verified)

// 处理URL查询参数中的消息
const urlMessage = computed(() => route.query.message || '')

// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab
  
  // 如果切换到文章标签页且尚未加载文章，则加载用户文章
  if (tab === 'articles' && userArticles.value.length === 0) {
    fetchUserArticles()
  }
}

// 分页导航
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 计算用户统计信息
const calculateUserStats = () => {
  if (!userArticles.value.length) return
  
  let totalViews = 0
  let totalLikes = 0
  let totalComments = 0
  let lastActive = null
  
  userArticles.value.forEach(article => {
    totalViews += article.view_count || 0
    totalLikes += article.likes_count || 0
    totalComments += article.comments_count || 0
    
    const createdDate = new Date(article.created_at)
    const updatedDate = article.updated_at ? new Date(article.updated_at) : null
    
    const articleLastActive = updatedDate && updatedDate > createdDate ? updatedDate : createdDate
    
    if (!lastActive || articleLastActive > lastActive) {
      lastActive = articleLastActive
    }
  })
  
  userStats.value = {
    totalViews,
    totalLikes,
    totalComments,
    lastActive: lastActive ? formatDate(lastActive) : '未知'
  }
}

// 选择头像文件
const selectAvatarFile = () => {
  fileInputRef.value.click()
}

// 处理头像选择
const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件'
    return
  }
  
  // 设置预览
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

// 上传头像
const uploadAvatar = async () => {
  if (!avatarFile.value) return
  
  try {
    isUploading.value = true
    
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', avatarFile.value)  // 修改这里，将'avatar'改为'file'以匹配后端API期望的参数名
    
    // 调用API上传头像
    await userApi.uploadAvatar(formData)
    
    // 更新Vuex中的用户信息
    await store.dispatch('fetchCurrentUser')
    
    // 清除预览和文件
    avatarFile.value = null
    avatarPreview.value = ''
    
  } catch (err) {
    console.error('上传头像失败:', err)
    error.value = '上传头像失败'
  } finally {
    isUploading.value = false
  }
}

// 取消头像上传
const cancelAvatarUpload = () => {
  avatarFile.value = null
  avatarPreview.value = ''
}

// 检查密码强度
const checkPasswordStrength = (password) => {
  if (!password) {
    passwordStrength.value = 0
    return
  }
  
  let strength = 0
  
  // 长度检查
  if (password.length >= 8) strength += 10
  if (password.length >= 12) strength += 10
  
  // 复杂度检查
  if (/[a-z]/.test(password)) strength += 10
  if (/[A-Z]/.test(password)) strength += 10
  if (/[0-9]/.test(password)) strength += 10
  if (/[^a-zA-Z0-9]/.test(password)) strength += 20
  
  // 多样性检查
  const uniqueChars = new Set(password).size
  strength += Math.min(20, uniqueChars * 2)
  
  passwordStrength.value = Math.min(100, strength)
}

// 监听新密码变化
watch(() => passwordForm.value.newPassword, (newVal) => {
  checkPasswordStrength(newVal)
})

// 获取用户文章
const fetchUserArticles = async () => {
  try {
    isArticlesLoading.value = true
    error.value = null
    
    // 调用API获取当前用户的文章
    const articles = await articleApi.getUserArticles()
    userArticles.value = articles
    
    // 计算用户统计信息
    calculateUserStats()
  } catch (err) {
    console.error('获取用户文章失败:', err)
    error.value = '获取用户文章失败'
  } finally {
    isArticlesLoading.value = false
  }
}

// 切换编辑模式
const toggleEditMode = () => {
  if (isEditMode.value) {
    // 保存编辑
    saveUserProfile()
  } else {
    // 进入编辑模式
    editForm.value = {
      username: currentUser.value?.username || '',
      email: currentUser.value?.email || '',
      bio: currentUser.value?.bio || ''
    }
    isEditMode.value = true
  }
}

// 保存用户资料
const saveUserProfile = async () => {
  try {
    error.value = null
    isSaving.value = true
    
    // 表单验证
    if (!editForm.value.username.trim()) {
      error.value = '用户名不能为空'
      isSaving.value = false
      return
    }
    
    // 调用API更新用户资料，不包含邮箱字段
    await userApi.updateProfile({
      username: editForm.value.username,
      bio: editForm.value.bio
      // 移除邮箱字段，确保不会尝试更新邮箱
    })
    
    // 如果有头像文件，上传头像
    if (avatarFile.value) {
      await uploadAvatar()
    }
    
    // 更新Vuex中的用户信息
    await store.dispatch('fetchCurrentUser')
    
    // 退出编辑模式
    isEditMode.value = false
  } catch (err) {
    console.error('更新用户资料失败:', err)
    error.value = err.response?.data?.detail || '更新用户资料失败'
  } finally {
    isSaving.value = false
  }
}

// 修改用户名
const changeUsername = async () => {
  // 表单验证
  if (!usernameForm.value.newUsername.trim()) {
    usernameError.value = '新用户名不能为空'
    return
  }
  
  if (usernameForm.value.newUsername === currentUser.value?.username) {
    usernameError.value = '新用户名不能与当前用户名相同'
    return
  }
  
  try {
    usernameError.value = ''
    usernameSuccess.value = ''
    
    // 调用API修改用户名
    await userApi.updateUsername(usernameForm.value.newUsername)
    
    // 更新Vuex中的用户信息
    await store.dispatch('fetchCurrentUser')
    
    // 清空表单
    usernameForm.value.newUsername = ''
    
    // 退出编辑模式
    isUsernameEditMode.value = false
    
    usernameSuccess.value = '用户名修改成功！由于系统使用邮箱作为登录标识符，您的登录状态不会受到影响。'
    
    // 3秒后清除成功消息
    setTimeout(() => {
      usernameSuccess.value = ''
    }, 3000)
  } catch (err) {
    console.error('修改用户名失败:', err)
    usernameError.value = err.response?.data?.detail || '修改用户名失败'
  }
}

// 取消用户名编辑
const cancelUsernameEdit = () => {
  isUsernameEditMode.value = false
  usernameForm.value.newUsername = ''
  usernameError.value = ''
  usernameSuccess.value = ''
}

// 修改密码
const changePassword = async () => {
  // 表单验证
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    passwordError.value = '请填写所有密码字段'
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  
  try {
    passwordError.value = ''
    passwordSuccess.value = ''
    
    // 调用API修改密码
    await userApi.changePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    
    // 清空表单
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    
    passwordSuccess.value = '密码修改成功'
  } catch (err) {
    console.error('修改密码失败:', err)
    passwordError.value = err.response?.data?.detail || '修改密码失败'
  }
}

// 取消编辑
const cancelEdit = () => {
  isEditMode.value = false
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取用户头像首字母
const getAvatarText = (username) => {
  return username ? username.charAt(0).toUpperCase() : '?'
}

// 获取头像完整URL
const getAvatarUrl = (path) => {
  if (!path) return null
  // 如果已经是完整URL，则直接返回
  if (path.startsWith('http')) return path
  // 确保路径以斜杠开头
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  // 如果路径已经包含/uploads，则直接返回，避免重复
  if (cleanPath.includes('/uploads/')) return cleanPath
  // 否则添加基础路径，但要避免重复的/uploads
  const baseUrl = (import.meta.env.VITE_UPLOAD_URL || '').replace(/\/?$/, '')
  // 如果基础URL和路径都以/uploads开头，则只使用路径
  if (baseUrl.endsWith('/uploads') && cleanPath.startsWith('/uploads/')) {
    return cleanPath
  }
  return `${baseUrl}${cleanPath}`
}

// 打开删除确认对话框
const openDeleteConfirm = (articleId) => {
  articleToDelete.value = articleId
  confirmDialogVisible.value = true
}

// 关闭删除确认对话框
const closeDeleteConfirm = () => {
  confirmDialogVisible.value = false
  articleToDelete.value = null
}

// 删除文章
const deleteArticle = async () => {
  if (!articleToDelete.value) return
  
  try {
    // 调用API删除文章
    await articleApi.deleteArticle(articleToDelete.value)
    
    // 从列表中移除已删除的文章
    userArticles.value = userArticles.value.filter(article => article.id !== articleToDelete.value)
    toast.success('文章删除成功')
    closeDeleteConfirm()
  } catch (err) {
    console.error('删除文章失败:', err)
    toast.error('删除文章失败')
  }
}

// 退出访客模式
const exitGuestMode = () => {
  store.dispatch('exitGuestMode')
  toast.success('已退出访客模式')
  router.push('/') // 跳转到首页
}

// 初始化
onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // 如果是访客模式，直接显示访客界面
    if (isGuestMode.value) {
      isLoading.value = false
      return
    }
    
    // 如果是已认证用户，获取用户信息
    if (isAuthenticated.value && currentUser.value) {
      await fetchUserArticles()
    } else {
      // 未认证用户，显示提示信息
      error.value = '请先登录以查看个人资料'
    }
  } catch (err) {
    console.error('初始化失败:', err)
    error.value = '加载个人资料失败'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="profile-page">
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state" aria-live="polite">
        <div class="loading-spinner" aria-hidden="true"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state" role="alert">
        <p>{{ error }}</p>
        <button @click="$router.go(0)" class="retry-button" aria-label="重试">重试</button>
      </div>
      
      <!-- 用户资料 -->
      <template v-else>
        <div class="profile-header">
          <div class="profile-avatar">
            <div v-if="!currentUser?.avatar && !avatarPreview" class="avatar-placeholder" aria-label="用户头像">
              {{ getAvatarText(currentUser?.username) }}
            </div>
            <img v-else-if="avatarPreview" :src="avatarPreview" alt="头像预览" class="avatar-image" />
            <img v-else :src="getAvatarUrl(currentUser.avatar)" :alt="`${currentUser?.username}的头像`" class="avatar-image" />
            
            <div v-if="isEditMode" class="avatar-actions">
              <input 
                type="file" 
                ref="fileInputRef" 
                @change="handleAvatarChange" 
                accept="image/*" 
                class="file-input" 
              />
              <button 
                v-if="!avatarPreview" 
                @click="selectAvatarFile" 
                class="avatar-button"
                aria-label="上传头像"
              >
                更换头像
              </button>
              <div v-else class="avatar-preview-actions">
                <button 
                  @click="cancelAvatarUpload" 
                  class="avatar-button cancel"
                  aria-label="取消上传"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
          
          <div class="profile-info">
            <!-- 访客模式显示 -->
            <div v-if="isGuestMode" class="guest-mode-notice">
              <div class="guest-icon">🚶</div>
              <h1>访客模式</h1>
              <p class="guest-description">您正在以访客身份浏览网站</p>
              <p class="guest-limitations">访客模式功能限制：</p>
              <ul class="guest-limitations-list">
                <li>✅ 可以浏览首页和文章内容</li>
                <li>✅ 可以查看个人中心</li>
                <li>❌ 无法发布、编辑或删除文章</li>
                <li>❌ 无法发表评论</li>
                <li>❌ 无法修改个人资料</li>
              </ul>
              <div class="guest-actions">
                <router-link to="/login" class="guest-action-button primary">
                  🔐 登录账号
                </router-link>
                <button @click="exitGuestMode" class="guest-action-button secondary">
                  🚪 退出访客模式
                </button>
              </div>
            </div>
            
            <!-- 正常用户资料显示 -->
            <div v-else-if="currentUser" class="info-display">
              <h1>{{ currentUser.username }}</h1>
              <p class="bio">{{ currentUser.bio || '这个人很懒，还没有填写个人简介' }}</p>
              <p class="join-date">加入于 {{ formatDate(currentUser.created_at) }}</p>
              
              <!-- 只有已认证用户才能编辑个人资料 -->
              <button 
                v-if="isAuthenticated"
                @click="toggleEditMode" 
                class="edit-button"
                aria-label="编辑个人资料"
              >
                编辑个人资料
              </button>
              
              <!-- 未认证用户显示提示 -->
              <div v-else class="verification-notice">
                <p>请先验证您的邮箱以解锁更多功能</p>
              </div>
            </div>
            
            <div v-else class="edit-form">
              <h2>编辑个人资料</h2>
              
              <div v-if="error" class="form-error" role="alert">{{ error }}</div>
              
              <div class="form-group">
                <label for="username">用户名</label>
                <input 
                  id="username"
                  v-model="editForm.username"
                  type="text"
                  placeholder="用户名"
                  aria-required="true"
                />
              </div>
              
              <div class="form-group">
                <label for="email">邮箱</label>
                <input 
                  id="email"
                  v-model="editForm.email"
                  type="email"
                  placeholder="邮箱地址"
                  aria-required="true"
                  readonly
                  class="readonly-field"
                />
                <small class="field-info">邮箱作为身份标识符不可修改</small>
              </div>
              
              <div class="form-group">
                <label for="bio">个人简介</label>
                <textarea 
                  id="bio"
                  v-model="editForm.bio"
                  placeholder="介绍一下自己吧..."
                  rows="3"
                ></textarea>
              </div>
              
              <div class="form-actions">
                <button 
                  @click="toggleEditMode" 
                  class="save-button"
                  aria-label="保存个人资料"
                >
                  保存
                </button>
                <button 
                  @click="cancelEdit" 
                  class="cancel-button"
                  aria-label="取消编辑"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 用户统计信息区域 -->
        <div v-if="currentUser && !isGuestMode" class="profile-stats-section">
          <h2 class="stats-section-title">数据统计</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">📝</div>
              <div class="stat-content">
                <span class="stat-value">{{ userArticles.length }}</span>
                <span class="stat-label">文章</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">👁️</div>
              <div class="stat-content">
                <span class="stat-value">{{ userStats.totalViews }}</span>
                <span class="stat-label">阅读</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">👍</div>
              <div class="stat-content">
                <span class="stat-value">{{ userStats.totalLikes }}</span>
                <span class="stat-label">点赞</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">💬</div>
              <div class="stat-content">
                <span class="stat-value">{{ userStats.totalComments }}</span>
                <span class="stat-label">评论</span>
              </div>
            </div>
          </div>
          <div class="activity-info">
            <p>最近活动: {{ userStats.lastActive }}</p>
          </div>
        </div>
        
        <div class="profile-content">
          <div class="tabs" role="tablist">
            <button 
              :class="['tab-button', { active: activeTab === 'articles' }]"
              @click="switchTab('articles')"
              role="tab"
              :aria-selected="activeTab === 'articles'"
              aria-controls="articles-tab"
              id="tab-articles"
            >
              文章
            </button>
            <button 
              :class="['tab-button', { active: activeTab === 'settings' }]"
              @click="switchTab('settings')"
              role="tab"
              :aria-selected="activeTab === 'settings'"
              aria-controls="settings-tab"
              id="tab-settings"
            >
              设置
            </button>
          </div>
          
          <!-- 文章列表 -->
          <div 
            v-if="activeTab === 'articles'" 
            class="tab-content"
            role="tabpanel"
            id="articles-tab"
            aria-labelledby="tab-articles"
          >
            <div v-if="isArticlesLoading" class="loading-state" aria-live="polite">
              <div class="loading-spinner" aria-hidden="true"></div>
              <p>加载中...</p>
            </div>
            
            <div v-else-if="userArticles.length === 0" class="empty-state">
              <div class="empty-icon" aria-hidden="true">📝</div>
              <h3>还没有发布任何文章</h3>
              <p v-if="isAuthenticated">写下你的第一篇文章，分享你的知识和经验</p>
              <p v-else>请先验证您的邮箱以解锁写文章功能</p>
              <button 
                v-if="isAuthenticated"
                @click="$router.push('/article/new')" 
                class="action-button"
              >
                写文章
              </button>
              <div v-else class="verification-notice">
                <p>验证邮箱后即可开始创作</p>
              </div>
            </div>
            
            <div v-else class="article-list">
              <div v-for="article in paginatedArticles" :key="article.id" class="article-item">
                <h3 class="article-title">
                  <router-link :to="`/article/${article.id}`">{{ article.title }}</router-link>
                </h3>
                <p class="article-summary">{{ article.summary }}</p>
                <div class="article-meta">
                  <span class="meta-item">
                    <i class="icon-calendar" aria-hidden="true"></i>
                    <span>{{ formatDate(article.created_at) }}</span>
                  </span>
                  <span class="meta-item">
                    <i class="icon-eye" aria-hidden="true"></i>
                    <span>{{ article.view_count }} 次阅读</span>
                  </span>
                  <span v-if="article.likes_count !== undefined" class="meta-item">
                    <i class="icon-heart" aria-hidden="true"></i>
                    <span>{{ article.likes_count }} 次点赞</span>
                  </span>
                </div>
                <div class="article-actions">
                  <router-link 
                    v-if="isAuthenticated"
                    :to="`/article/${article.id}/edit`" 
                    class="action-link"
                  >
                    编辑
                  </router-link>
                  <button 
                    v-if="isAuthenticated"
                    @click="openDeleteConfirm(article.id)" 
                    class="action-link danger"
                    aria-label="删除文章"
                  >
                    删除
                  </button>
                  <div v-else class="verification-notice">
                    <p>验证邮箱后即可管理文章</p>
                  </div>
                </div>
              </div>
              
              <!-- 分页控制 -->
              <div v-if="totalPages > 1" class="pagination">
                <button 
                  @click="goToPage(currentPage - 1)" 
                  :disabled="currentPage === 1"
                  class="page-button"
                  aria-label="上一页"
                >
                  &lt;
                </button>
                <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
                <button 
                  @click="goToPage(currentPage + 1)" 
                  :disabled="currentPage === totalPages"
                  class="page-button"
                  aria-label="下一页"
                >
                  &gt;
                </button>
              </div>
            </div>
          </div>
          
          <!-- 设置页面 -->
          <div 
            v-else-if="activeTab === 'settings'" 
            class="tab-content"
            role="tabpanel"
            id="settings-tab"
            aria-labelledby="tab-settings"
          >
            <!-- 只有已认证用户才能修改用户名 -->
            <div v-if="isAuthenticated" class="settings-section">
              <h3>修改用户名</h3>
              
              <div v-if="usernameError" class="form-error" role="alert">{{ usernameError }}</div>
              <div v-if="usernameSuccess" class="form-success" role="status">{{ usernameSuccess }}</div>
              
              <div v-if="!isUsernameEditMode" class="username-display">
                <p>当前用户名: <strong>{{ currentUser?.username }}</strong></p>
                <button 
                  @click="isUsernameEditMode = true" 
                  class="action-button"
                  aria-label="修改用户名"
                >
                  修改用户名
                </button>
              </div>
              
              <div v-else class="username-edit-form">
                <div class="form-group">
                  <label for="new-username">新用户名</label>
                  <input 
                    id="new-username"
                    v-model="usernameForm.newUsername"
                    type="text"
                    placeholder="输入新用户名"
                    aria-required="true"
                    maxlength="32"
                  />
                  <small class="field-info">用户名长度3-32个字符，只能包含字母、数字和下划线</small>
                </div>
                
                <div class="form-actions">
                  <button 
                    @click="changeUsername" 
                    class="save-button"
                    aria-label="保存新用户名"
                  >
                    保存
                  </button>
                  <button 
                    @click="cancelUsernameEdit" 
                    class="cancel-button"
                    aria-label="取消修改"
                  >
                    取消
                  </button>
                </div>
              </div>
            </div>

            <!-- 只有已认证用户才能修改密码 -->
            <div v-if="isAuthenticated" class="settings-section">
              <h3>修改密码</h3>
              
              <div v-if="passwordError" class="form-error" role="alert">{{ passwordError }}</div>
              <div v-if="passwordSuccess" class="form-success" role="status">{{ passwordSuccess }}</div>
              
              <div class="form-group">
                <label for="old-password">当前密码</label>
                <div class="password-input-container">
                <input 
                  id="old-password"
                  v-model="passwordForm.oldPassword"
                  type="password"
                  placeholder="输入当前密码"
                    aria-required="true"
                />
                </div>
              </div>
              
              <div class="form-group">
                <label for="new-password">新密码</label>
                <div class="password-input-container">
                <input 
                  id="new-password"
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="输入新密码"
                    aria-required="true"
                />
                </div>
                <div v-if="passwordForm.newPassword" class="password-strength">
                  <div class="strength-bar-container">
                    <div 
                      class="strength-bar" 
                      :class="passwordStrengthClass"
                      :style="{ width: `${passwordStrength}%` }"
                    ></div>
                  </div>
                  <span class="strength-text" :class="passwordStrengthClass">
                    密码强度: {{ passwordStrengthText }}
                  </span>
                </div>
                <p class="password-hint">建议使用包含字母、数字和特殊符号的强密码</p>
              </div>
              
              <div class="form-group">
                <label for="confirm-password">确认密码</label>
                <div class="password-input-container">
                <input 
                  id="confirm-password"
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="再次输入新密码"
                    aria-required="true"
                />
                </div>
              </div>
              
              <button 
                @click="changePassword" 
                class="action-button"
                :disabled="isLoading"
                aria-label="更新密码"
              >
                <span v-if="isLoading">更新中...</span>
                <span v-else>更新密码</span>
              </button>
            </div>

            <!-- 邮箱验证部分 - 所有用户都可以访问 -->
            <div class="settings-section">
              <h3>邮箱验证</h3>
              
              <!-- 显示URL查询参数中的消息 -->
              <div v-if="urlMessage" class="form-error" role="alert">
                {{ urlMessage }}
              </div>
              
              <p v-if="isUserVerified">您的邮箱已验证，无需重复验证。</p>
              <p v-else>您的邮箱未验证，请点击下方按钮重新发送验证邮件。</p>
              <ResendVerificationButton 
                v-if="!isUserVerified && currentUser?.email"
                :email="currentUser.email"
                button-text="重新发送验证邮件"
              />
            </div>
            
            <!-- 未认证用户提示 -->
            <div v-if="!isAuthenticated" class="verification-notice">
              <h3>功能限制</h3>
              <p>由于您的邮箱尚未验证，以下功能暂时不可用：</p>
              <ul>
                <li>发布和编辑文章</li>
                <li>修改密码</li>
                <li>编辑个人资料</li>
              </ul>
              <p>请先验证您的邮箱以解锁所有功能。</p>
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <!-- 删除确认对话框 -->
    <ConfirmDialog 
      :visible="confirmDialogVisible"
      title="确认删除"
      message="确定要删除这篇文章吗？此操作不可恢复。"
      confirmText="确认删除"
      cancelText="取消"
      @confirm="deleteArticle"
      @cancel="closeDeleteConfirm"
    />
  </div>
</template>

<style scoped>
.profile-page {
  padding: 40px 0;
  background-color: var(--bg-primary);
  min-height: 100vh;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(76, 132, 255, 0.2);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.retry-button {
  margin-top: 20px;
  padding: 8px 16px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-button:hover {
  filter: brightness(1.1);
}

.retry-button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 表单错误和成功消息 */
.form-error {
  background-color: rgba(var(--error-color), 0.1);
  color: var(--error-color);
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid rgba(var(--error-color), 0.2);
  border-left: 4px solid var(--error-color);
}

.form-success {
  background-color: rgba(var(--success-color), 0.1);
  color: var(--success-color);
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid rgba(var(--success-color), 0.2);
  border-left: 4px solid var(--success-color);
}

/* 个人资料头部 */
.profile-header {
  display: flex;
  gap: 30px;
  background-color: var(--card-bg);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  padding: 30px;
  margin-bottom: 30px;
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 120px;
  height: 120px;
  background-color: var(--primary-color);
  color: white;
  font-size: 3rem;
  font-weight: bold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.avatar-actions {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.file-input {
  display: none;
}

.avatar-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-button:hover {
  filter: brightness(1.1);
}

.avatar-button.cancel {
  background-color: var(--error-color);
}

.avatar-preview-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.profile-info {
  flex: 1;
}

/* 访客模式显示 */
.guest-mode-notice {
  text-align: center;
  padding: 40px 0;
  background-color: var(--bg-elevated);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.guest-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  color: var(--warning-color);
}

.guest-mode-notice h1 {
  font-size: 1.8rem;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.guest-description {
  color: var(--text-secondary);
  margin: 0 0 15px;
  line-height: 1.5;
}

.guest-limitations {
  font-size: 1rem;
  color: var(--text-primary);
  margin: 0 0 15px;
  font-weight: 500;
}

.guest-limitations-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px;
}

.guest-limitations-list li {
  margin: 8px 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.guest-limitations-list li i {
  margin-right: 8px;
  color: var(--success-color);
}

.guest-limitations-list li.negative i {
  color: var(--error-color);
}

.guest-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.guest-action-button {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  white-space: nowrap;
}

.guest-action-button.primary {
  background-color: var(--primary-color);
  color: white;
}

.guest-action-button.primary:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.guest-action-button.secondary {
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.guest-action-button.secondary:hover {
  background-color: var(--bg-elevated);
}

.guest-action-button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.info-display h1 {
  font-size: 1.8rem;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.bio {
  color: var(--text-secondary);
  margin: 0 0 10px;
  line-height: 1.5;
}

.join-date {
  color: var(--text-tertiary);
  font-size: 0.9rem;
  margin: 0 0 20px;
}

.stats {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  background-color: var(--bg-elevated);
  border-radius: 8px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-primary);
}

.stat-label {
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.edit-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.edit-button:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.edit-button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 编辑表单 */
.edit-form {
  background-color: var(--bg-elevated);
  padding: 20px;
  border-radius: 8px;
}

.edit-form h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: all 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
  outline: none;
}

.password-hint {
  font-size: 0.85rem;
  color: var(--text-tertiary);
  margin-top: 5px;
}

.form-actions {
  display: flex;
  gap: 10px;
}

.save-button,
.cancel-button {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
}

.save-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
}

.save-button:hover {
  filter: brightness(1.1);
}

.cancel-button {
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.cancel-button:hover {
  background-color: var(--bg-elevated);
}

/* 标签页 */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.tab-button {
  background: none;
  border: none;
  padding: 12px 20px;
  font-size: 1rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.tab-button:hover {
  color: var(--primary-color);
}

.tab-button.active {
  color: var(--primary-color);
  font-weight: 500;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
}

.tab-content {
  background-color: var(--card-bg);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  padding: 20px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 0;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 20px;
  color: var(--text-tertiary);
}

.empty-state h3 {
  font-size: 1.4rem;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.empty-state p {
  color: var(--text-tertiary);
  margin: 0 0 20px;
}

.action-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-button:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.action-button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 文章列表 */
.article-item {
  padding: 20px;
  border-radius: 8px;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.3s;
}

.article-item:hover {
  background-color: var(--bg-hover);
}

.article-item:last-child {
  border-bottom: none;
}

.article-title {
  font-size: 1.3rem;
  margin: 0 0 10px;
}

.article-title a {
  color: var(--text-primary);
  text-decoration: none;
  transition: color 0.3s;
}

.article-title a:hover {
  color: var(--primary-color);
}

.article-summary {
  color: var(--text-secondary);
  margin: 0 0 15px;
  line-height: 1.6;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  color: var(--text-tertiary);
  font-size: 0.85rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.article-actions {
  display: flex;
  gap: 15px;
}

.action-link {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 0.9rem;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s;
}

.action-link:hover {
  background-color: var(--bg-elevated);
  text-decoration: none;
}

.action-link.danger {
  color: var(--error-color);
}

.action-link.danger:hover {
  background-color: rgba(var(--error-color), 0.1);
}

/* 分页控制 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.page-button {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.page-button:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--primary-color);
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
  align-items: center;
    text-align: center;
    gap: 20px;
}

  .stats {
    justify-content: center;
  }
  
  .article-meta {
    justify-content: center;
  }
  
  .article-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .form-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .save-button,
  .cancel-button,
  .edit-button,
  .action-button {
    width: 100%;
  }
  
  .tab-button {
    flex: 1;
    padding: 12px 5px;
  }
}

.user-activity {
  margin-bottom: 20px;
}

.activity-info {
  color: var(--text-tertiary);
  font-size: 0.9rem;
  padding: 5px 10px;
  background-color: var(--bg-elevated);
  border-radius: 4px;
  display: inline-block;
}

.password-strength {
  margin-top: 8px;
}

.strength-bar-container {
  height: 5px;
  background-color: var(--border-color);
  border-radius: 3px;
  margin-bottom: 5px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.strength-bar.weak {
  background-color: var(--error-color);
}

.strength-bar.medium {
  background-color: var(--warning-color);
}

.strength-bar.strong {
  background-color: var(--success-color);
}

.strength-text {
  font-size: 0.8rem;
  font-weight: 500;
}

.strength-text.weak {
  color: var(--error-color);
}

.strength-text.medium {
  color: var(--warning-color);
}

.strength-text.strong {
  color: var(--success-color);
}

/* 添加到样式表的末尾 */
.readonly-field {
  background-color: var(--bg-elevated);
  cursor: not-allowed;
  opacity: 0.8;
  border: 1px solid var(--border-color);
}
  
.field-info {
  display: block;
  margin-top: 5px;
  font-size: 0.85rem;
  color: var(--text-tertiary);
  font-style: italic;
}

/* 用户名修改样式 */
.username-display {
  margin-bottom: 15px;
}

.username-display p {
  margin: 0 0 15px 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.username-display strong {
  color: var(--text-primary);
  font-weight: 600;
}

.username-edit-form {
  background-color: var(--bg-elevated);
  padding: 15px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

/* 邮箱验证样式 */
.settings-section {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid var(--border-color);
}

.settings-section h3 {
  margin: 0 0 15px 0;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.settings-section p {
  margin: 0 0 15px 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.settings-section .action-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.settings-section .action-button:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.settings-section .action-button:disabled {
  background-color: rgba(var(--primary-color-rgb), 0.5);
  cursor: not-allowed;
  transform: none;
}

.settings-section .action-button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 新增样式 */
.verification-notice {
  background-color: rgba(var(--warning-color-rgb), 0.1);
  color: var(--warning-color);
  padding: 12px;
  border-radius: 4px;
  margin-top: 20px;
  border: 1px solid rgba(var(--warning-color-rgb), 0.2);
  border-left: 4px solid var(--warning-color);
}

.verification-notice p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
}

.verification-notice h3 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: var(--warning-color);
}

.verification-notice ul {
  margin: 10px 0;
  padding-left: 20px;
}

.verification-notice li {
  margin: 5px 0;
  font-size: 0.9rem;
}

/* 统计信息区域样式 */
.profile-stats-section {
  background-color: var(--card-bg);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  padding: 25px;
  margin-bottom: 30px;
}

.stats-section-title {
  font-size: 1.3rem;
  color: var(--text-primary);
  margin: 0 0 20px 0;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background-color: var(--bg-elevated);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-color);
  color: white;
  border-radius: 50%;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  color: var(--text-tertiary);
  font-size: 0.9rem;
  margin-top: 5px;
}

.activity-info {
  text-align: center;
  padding: 15px;
  background-color: var(--bg-elevated);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.activity-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    font-size: 1.5rem;
    width: 40px;
    height: 40px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 12px;
  }
}
</style>