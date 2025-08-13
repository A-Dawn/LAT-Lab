<!--
  @component AdminAbout
  @description 管理员管理"关于博主"内容的组件
  @features 
    - 编辑关于博主的标题和描述
    - 管理社交链接
    - 实时预览效果
    - 保存配置到后端
-->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminApi } from '../../services/api'
import { aboutService } from '../../services/aboutService'

// 消息状态
const message = ref('')
const messageType = ref('success')
const loading = ref(false)

// 表单数据 - 统一使用后端期望的字段名
const formData = ref({
  title: '关于博主',
  description: '',
  social_links: []
})

// 默认配置
const DEFAULT_CONFIG = {
  title: '关于博主',
  description: '热爱技术，喜欢分享，记录学习过程中的点点滴滴。',
  social_links: [
    { name: 'GitHub', url: 'https://github.com' },
    { name: '邮箱', url: 'mailto:example@email.com' }
  ]
}

// 计算属性 - 用于向后兼容旧的字段名
const config = computed(() => ({
  ...formData.value,
  socialLinks: formData.value.social_links // 为模板提供兼容性
}))

// 数据加载
const loadConfig = async () => {
  try {
    console.log('正在加载配置...')
    const response = await aboutService.getAboutSection()
    console.log('API响应:', response)
    
    if (response?.success && response?.data) {
      const data = response.data
      console.log('收到配置数据:', data)
      
      // 确保社交链接是数组格式
      let socialLinks = []
      if (Array.isArray(data.social_links)) {
        socialLinks = data.social_links
      } else if (Array.isArray(data.socialLinks)) {
        socialLinks = data.socialLinks
      } else {
        socialLinks = DEFAULT_CONFIG.social_links
      }
      
             // 准备新的数据对象
       const newData = {
         title: data.title || DEFAULT_CONFIG.title,
         description: data.description || DEFAULT_CONFIG.description,
         social_links: socialLinks.map(link => ({
           name: link.name || '',
           url: link.url || '',
           icon: link.icon || ''
         }))
       }
       
       // 如果没有社交链接，添加一个空的输入框
       if (newData.social_links.length === 0) {
         newData.social_links.push({ name: '', url: '', icon: '' })
       }
       
       // 一次性更新整个formData，确保响应式更新
       formData.value = newData
      
      console.log('更新后的表单数据:', formData.value)
      console.log('表单标题:', formData.value.title)
      console.log('表单描述:', formData.value.description)
      console.log('社交链接数量:', formData.value.social_links.length)
      
      showMessage('配置加载成功', 'success')
    } else {
      throw new Error('响应数据格式错误')
    }
  } catch (error) {
    console.error('配置加载失败:', error)
    showMessage('配置加载失败，使用默认配置', 'error')
    resetToDefault()
  }
}

// 数据保存
const saveConfig = async () => {
  if (loading.value) return
  
  // 基础验证
  if (!formData.value.title.trim()) {
    showMessage('标题不能为空', 'error')
    return
  }
  
  loading.value = true
  try {
    console.log('正在保存配置:', formData.value)
    
    // 准备保存数据 - 统一使用下划线命名
    const saveData = {
      title: formData.value.title.trim(),
      description: formData.value.description.trim(),
      // 使用下划线命名，与后端统一
      social_links: formData.value.social_links.filter(link => 
        link.name.trim() && link.url.trim()
      )
    }
    
    console.log('发送保存数据:', saveData)
    await aboutService.updateAboutConfig(saveData)
    
    showMessage('配置保存成功！', 'success')
    console.log('配置保存成功')
  } catch (error) {
    console.error('配置保存失败:', error)
    const errorMsg = error.response?.data?.detail || '保存失败，请重试'
    showMessage(errorMsg, 'error')
  } finally {
    loading.value = false
  }
}

// 重置为默认配置
const resetToDefault = () => {
  formData.value = JSON.parse(JSON.stringify(DEFAULT_CONFIG))
  showMessage('已重置为默认配置', 'info')
}

// 社交链接管理
const addSocialLink = () => {
  formData.value.social_links.push({ name: '', url: '', icon: '' })
}

const removeSocialLink = (index) => {
  if (index >= 0 && index < formData.value.social_links.length) {
    formData.value.social_links.splice(index, 1)
  }
}

// 消息显示
const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

// 表单验证
const validateForm = () => {
  const errors = []
  
  if (!formData.value.title.trim()) {
    errors.push('标题不能为空')
  }
  
  if (formData.value.title.length > 50) {
    errors.push('标题长度不能超过50字符')
  }
  
  if (formData.value.description.length > 500) {
    errors.push('描述长度不能超过500字符')
  }
  
  // 验证社交链接
  formData.value.social_links.forEach((link, index) => {
    if (link.name.trim() && !link.url.trim()) {
      errors.push(`第${index + 1}个社交链接缺少URL`)
    }
    if (!link.name.trim() && link.url.trim()) {
      errors.push(`第${index + 1}个社交链接缺少名称`)
    }
  })
  
  return errors
}

// 表单提交处理
const handleSubmit = async () => {
  const errors = validateForm()
  
  if (errors.length > 0) {
    showMessage(errors[0], 'error')
    return
  }
  
  await saveConfig()
}

// 组件挂载
onMounted(() => {
  loadConfig()
})
</script>

<template>
  <div class="admin-about">
    <div class="admin-about-header">
      <h2>关于博主管理</h2>
      <p>在这里配置博客侧边栏中"关于博主"区域的展示内容</p>
    </div>

    <div class="admin-about-content">
      <!-- 配置表单 -->
      <div class="config-section">
        <h3>配置信息</h3>
        <form @submit.prevent="handleSubmit" class="config-form">
          <div class="form-group">
            <label for="title">标题 <span class="required">*</span></label>
            <input 
              type="text" 
              id="title"
              v-model.trim="formData.title" 
              placeholder="例如：关于博主"
              class="form-input"
              maxlength="50"
              required
            />
            <small class="form-hint">{{ formData.title.length }}/50</small>
          </div>

          <div class="form-group">
            <label for="description">描述</label>
            <textarea 
              id="description"
              v-model.trim="formData.description" 
              placeholder="介绍一下自己..."
              class="form-textarea"
              rows="4"
              maxlength="500"
            ></textarea>
            <small class="form-hint">{{ formData.description.length }}/500</small>
          </div>

          <div class="form-group">
            <label>社交链接</label>
            <div class="social-links">
              <div 
                v-for="(link, index) in formData.social_links" 
                :key="index" 
                class="social-link-item"
              >
                <input 
                  type="text" 
                  v-model.trim="link.name" 
                  placeholder="平台名称（如：GitHub）"
                  class="form-input social-name"
                />
                <input 
                  type="url" 
                  v-model.trim="link.url" 
                  placeholder="完整的链接地址"
                  class="form-input social-url"
                />
                <button 
                  type="button" 
                  @click="removeSocialLink(index)"
                  class="btn btn-danger btn-sm"
                  title="删除此链接"
                >
                  删除
                </button>
              </div>
              <button 
                type="button" 
                @click="addSocialLink"
                class="btn btn-secondary"
              >
                + 添加社交链接
              </button>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '保存中...' : '保存配置' }}
            </button>
            <button type="button" @click="resetToDefault" class="btn btn-secondary">
              重置为默认
            </button>
          </div>
        </form>
      </div>

      <!-- 预览区域 -->
      <div class="preview-section">
        <h3>预览效果</h3>
        <div class="preview-container">
          <div class="sidebar-preview">
            <div class="sidebar-section-preview">
              <h3 class="sidebar-title">{{ formData.title || '关于博主' }}</h3>
              <div class="sidebar-content">
                <p class="sidebar-description">
                  {{ formData.description || '这里将显示您的个人描述...' }}
                </p>
                <div v-if="formData.social_links.length > 0" class="sidebar-social">
                  <div 
                    v-for="(link, index) in formData.social_links" 
                    :key="index"
                    v-show="link.name.trim() && link.url.trim()"
                    class="social-item"
                  >
                    <a :href="link.url" target="_blank" rel="noopener noreferrer">
                      {{ link.name }}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<style scoped>
.admin-about {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-about-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.admin-about-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.admin-about-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.admin-about-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.config-section,
.preview-section {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.config-section h3,
.preview-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.required {
  color: #dc3545;
}

.form-input,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  color: #6c757d;
  font-size: 12px;
}

.social-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.social-link-item {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  gap: 10px;
  align-items: center;
}

.social-name {
  min-width: 100px;
}

.social-url {
  flex: 1;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.form-actions {
  display: flex;
  gap: 10px;
  padding-top: 10px;
}

.preview-container {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 20px;
}

.sidebar-preview {
  max-width: 300px;
  margin: 0 auto;
}

.sidebar-section-preview {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sidebar-title {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 8px;
}

.sidebar-content {
  color: #666;
}

.sidebar-description {
  margin: 0 0 15px 0;
  line-height: 1.6;
  font-size: 14px;
}

.sidebar-social {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.social-item a {
  display: inline-block;
  padding: 6px 12px;
  background: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 12px;
  transition: background-color 0.2s;
}

.social-item a:hover {
  background: #0056b3;
}

.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.message.success {
  background-color: #28a745;
}

.message.error {
  background-color: #dc3545;
}

.message.info {
  background-color: #17a2b8;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-about-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .social-link-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .admin-about {
    padding: 15px;
  }
}
</style> 