<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { marked } from 'marked'
import { articleApi, categoryApi, tagApi } from '../services/api'
import MarkdownEditor from '../components/MarkdownEditor.vue'
// 导入HTML净化工具
import { sanitizeMarkdown } from '../utils/sanitize'

const route = useRoute()
const router = useRouter()
const store = useStore()

// 获取用户登录状态
const isAuthenticated = computed(() => store.getters.isAuthenticated)
const currentUser = computed(() => store.getters.currentUser)

// 编辑模式（新建/编辑）
const isEditMode = computed(() => !!route.params.id)

// 文章表单数据
const articleForm = ref({
  title: '',
  content: '',
  summary: '',
  categoryId: '',
  tags: [],
  status: 'published',
  publishedAt: null,
  visibility: 'public',
  password: ''
})

// 表单验证
const validation = reactive({
  title: { valid: true, message: '' },
  content: { valid: true, message: '' },
  categoryId: { valid: true, message: '' },
  password: { valid: true, message: '' }
})

// 验证表单字段
const validateField = (field) => {
  switch (field) {
    case 'title':
      validation.title.valid = !!articleForm.value.title.trim()
      validation.title.message = validation.title.valid ? '' : '请输入文章标题'
      break
    case 'content':
      validation.content.valid = !!articleForm.value.content.trim()
      validation.content.message = validation.content.valid ? '' : '请输入文章内容'
      break
    case 'categoryId':
      validation.categoryId.valid = !!articleForm.value.categoryId
      validation.categoryId.message = validation.categoryId.valid ? '' : '请选择文章分类'
      break
    case 'password':
      if (articleForm.value.visibility === 'password') {
        validation.password.valid = !!articleForm.value.password.trim()
        validation.password.message = validation.password.valid ? '' : '请设置访问密码'
      } else {
        validation.password.valid = true
        validation.password.message = ''
      }
      break
  }
  return validation[field].valid
}

// 验证整个表单
const validateForm = () => {
  const fields = ['title', 'content', 'categoryId']
  
  if (articleForm.value.visibility === 'password') {
    fields.push('password')
  }
  
  return fields.every(field => validateField(field))
}

// 监听表单变化，实时验证
watch(() => articleForm.value.title, () => validateField('title'))
watch(() => articleForm.value.content, () => validateField('content'))
watch(() => articleForm.value.categoryId, () => validateField('categoryId'))
watch(() => articleForm.value.visibility, () => validateField('password'))
watch(() => articleForm.value.password, () => validateField('password'))

// 预览模式
const isPreviewMode = ref(false)

// 分类和标签列表
const categories = ref([])
const allTags = ref([])

// 加载状态
const isLoading = ref(false)
const isSaving = ref(false)
const error = ref(null)
const saveSuccess = ref(false)

// 关闭成功提示
const closeSaveSuccess = () => {
  saveSuccess.value = false
}

// 检查用户权限
const checkUserPermission = async () => {
  // 如果未登录，重定向到登录页
  if (!isAuthenticated.value) {
    router.push({ 
      path: '/login', 
      query: { redirect: route.fullPath } 
    })
    return false
  }
  
  // 检查邮箱验证状态（未验证邮箱的用户不能创建或编辑文章）
  if (!currentUser.value.is_verified) {
    error.value = '请先验证您的邮箱后再创建或编辑文章'
    // 重定向到个人中心，让用户验证邮箱
    router.push({ 
      path: '/profile',
      query: { message: '请先验证您的邮箱后再创建或编辑文章' }
    })
    return false
  }
  
  // 如果是编辑模式，需要检查是否有权限编辑该文章
  if (isEditMode.value) {
    try {
      const article = await articleApi.getArticle(route.params.id)
      
      // 如果不是管理员且不是文章作者，没有权限编辑
      if (currentUser.value.role !== 'admin' && article.author.id !== currentUser.value.id) {
        error.value = '您没有权限编辑此文章'
        return false
      }
    } catch (err) {
      error.value = '获取文章失败'
      console.error(err)
      return false
    }
  }
  
  return true
}

// 获取分类和标签
const fetchCategoriesAndTags = async () => {
  try {
    isLoading.value = true
    
    // 并行请求分类和标签
    const [categoriesRes, tagsRes] = await Promise.all([
      categoryApi.getCategories(),
      tagApi.getTags()
    ])
    
    categories.value = categoriesRes
    allTags.value = tagsRes || [] // 确保即使API返回null也有一个空数组
    
    // 如果是编辑模式，需要将标签ID转换为标签名称数组
    if (isEditMode.value && articleForm.value.tags.length > 0) {
      // 检查是否已经是标签名称数组
      if (typeof articleForm.value.tags[0] !== 'string') {
        articleForm.value.tags = articleForm.value.tags
          .map(tag => allTags.value.find(t => t.id === tag)?.name)
          .filter(Boolean)
      }
    }
  } catch (err) {
    error.value = '获取分类和标签失败'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

// 如果是编辑模式，获取文章数据
const fetchArticle = async (id) => {
  try {
    isLoading.value = true
    
    const article = await articleApi.getArticle(id)
    
    // 填充表单数据
    articleForm.value = {
      title: article.title,
      content: article.content,
      summary: article.summary || '',
      categoryId: article.category?.id || '',
      tags: article.tags?.map(tag => tag.id) || [],
      status: article.status || 'published',
      publishedAt: article.published_at || null,
      visibility: article.visibility || 'public',
      password: article.password || ''
    }

    // 初始化完成后验证表单
    Object.keys(validation).forEach(field => validateField(field))
  } catch (err) {
    error.value = '获取文章失败'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

// 自动生成摘要
const generateSummary = () => {
  if (!articleForm.value.content) return
  
  // 从内容中提取前150个字符作为摘要
  const plainText = articleForm.value.content
    .replace(/#{1,6}\s?/g, '') // 移除标题标记
    .replace(/\*\*/g, '')      // 移除加粗标记
    .replace(/\n/g, ' ')       // 将换行替换为空格
  
  articleForm.value.summary = plainText.substring(0, 150) + (plainText.length > 150 ? '...' : '')
}

// 渲染Markdown为HTML
const renderedContent = computed(() => {
  try {
    // 使用marked渲染，然后通过sanitizeMarkdown净化防止XSS
    return sanitizeMarkdown(marked.parse(articleForm.content || ''));
  } catch (e) {
    console.error('Markdown渲染失败:', e);
    return articleForm.content || '';
  }
});

// 切换预览模式
const togglePreview = () => {
  isPreviewMode.value = !isPreviewMode.value
}

// 保存文章
const saveArticle = async () => {
  try {
    // 检查用户权限
    const hasPermission = await checkUserPermission()
    if (!hasPermission) return
    
    // 表单验证
    if (!validateForm()) {
      // 表单验证失败
      error.value = '请完善表单内容'
      return
    }
    
    isSaving.value = true
    error.value = null
    
    // 如果没有摘要，自动生成
    if (!articleForm.value.summary) {
      generateSummary()
    }
    
    // 转换字段名称，后端使用蛇形命名法
    const articleData = {
      title: articleForm.value.title,
      content: articleForm.value.content,
      summary: articleForm.value.summary,
      category_id: articleForm.value.categoryId,
      tags: articleForm.value.tags,
      status: articleForm.value.status,
      published_at: articleForm.value.publishedAt,
      visibility: articleForm.value.visibility,
      password: articleForm.value.visibility === 'password' ? articleForm.value.password : null
    }
    
    let response
    
    if (isEditMode.value) {
      // 编辑现有文章
      response = await articleApi.updateArticle(route.params.id, articleData)
      saveSuccess.value = true
      setTimeout(() => {
        saveSuccess.value = false
      }, 3000)
    } else {
      // 创建新文章
      response = await articleApi.createArticle(articleData)
    // 跳转到文章详情页
    router.push(`/article/${response.id}`)
    }
  } catch (err) {
    error.value = isEditMode.value ? '更新文章失败' : '创建文章失败'
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

// 保存为草稿
const saveAsDraft = async () => {
  // 设置状态为草稿
  articleForm.value.status = 'draft'
  articleForm.value.publishedAt = null
  
  // 保存文章
  await saveArticle()
}

// 发布文章
const publishArticle = async () => {
  // 设置状态为已发布
  articleForm.value.status = 'published'
  
  // 如果没有设置发布时间，则使用当前时间
  if (!articleForm.value.publishedAt) {
    articleForm.value.publishedAt = new Date().toISOString()
  }
  
  // 保存文章
  await saveArticle()
}

// 取消编辑
const cancelEdit = () => {
  if (isEditMode.value) {
    router.push(`/article/${route.params.id}`)
  } else {
    router.push('/')
  }
}

// 初始化
onMounted(async () => {
  // 检查用户权限
  const hasPermission = await checkUserPermission()
  if (!hasPermission) return
  
  // 获取分类和标签
  await fetchCategoriesAndTags()
  
  // 如果是编辑模式，获取文章数据
  if (isEditMode.value) {
    await fetchArticle(route.params.id)
  }
})
</script>

<template>
  <div class="article-editor-page">
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container" aria-live="polite">
        <div class="loading-spinner" aria-hidden="true"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 编辑器 -->
      <div v-else class="editor-container">
        <div class="editor-header">
          <h1>{{ isEditMode ? '编辑文章' : '创建文章' }}</h1>
          
          <div class="editor-actions">
            <button 
              @click="togglePreview" 
              class="preview-button"
              :class="{ active: isPreviewMode }"
              aria-label="切换预览模式"
              :aria-pressed="isPreviewMode"
            >
              <span class="button-icon" aria-hidden="true">
                {{ isPreviewMode ? '✏️' : '👁️' }}
              </span>
              <span>{{ isPreviewMode ? '编辑' : '预览' }}</span>
            </button>
            
            <button 
              @click="saveAsDraft" 
              class="draft-button"
              :disabled="isSaving"
              aria-label="保存为草稿"
            >
              <span v-if="!isSaving">
                <span class="button-icon" aria-hidden="true">📝</span>
                保存为草稿
              </span>
              <span v-else>
                <span class="button-icon spinning" aria-hidden="true">⏳</span>
                保存中...
              </span>
            </button>
            
            <button 
              @click="publishArticle" 
              class="save-button"
              :disabled="isSaving"
              aria-label="发布文章"
            >
              <span v-if="!isSaving">
                <span class="button-icon" aria-hidden="true">📢</span>
                {{ articleForm.publishedAt && new Date(articleForm.publishedAt) > new Date() ? '定时发布' : '立即发布' }}
              </span>
              <span v-else>
                <span class="button-icon spinning" aria-hidden="true">⏳</span>
                发布中...
              </span>
            </button>
            
            <button 
              @click="cancelEdit" 
              class="cancel-button"
              aria-label="取消编辑"
            >
              <span class="button-icon" aria-hidden="true">❌</span>
              取消
            </button>
          </div>
        </div>
        
        <div v-if="error" class="error-message" role="alert">{{ error }}</div>
        
        <div v-if="saveSuccess" class="success-message" role="status">
          <div class="message-content">
            <span>文章已成功保存！</span>
            <button @click="closeSaveSuccess" class="close-message" aria-label="关闭提示">×</button>
          </div>
        </div>
        
        <div class="editor-body">
          <!-- 编辑表单 -->
          <div v-if="!isPreviewMode" class="edit-form">
            <div class="form-group" :class="{ 'has-error': !validation.title.valid }">
              <label for="title" class="required-field">标题</label>
              <input 
                id="title"
                v-model="articleForm.title"
                type="text"
                placeholder="请输入文章标题"
                :aria-invalid="!validation.title.valid"
                aria-required="true"
                :disabled="isLoading || isSaving"
              />
              <p v-if="!validation.title.valid" class="form-error-text">{{ validation.title.message }}</p>
            </div>
            
            <div class="form-group" :class="{ 'has-error': !validation.categoryId.valid }">
              <label for="category" class="required-field">分类</label>
              <select 
                id="category"
                v-model="articleForm.categoryId"
                :aria-invalid="!validation.categoryId.valid"
                aria-required="true"
              >
                <option value="">请选择分类</option>
                <option 
                  v-for="category in categories" 
                  :key="category.id" 
                  :value="category.id"
                >
                  {{ category.name }}
                </option>
              </select>
              <p v-if="!validation.categoryId.valid" class="form-error-text">{{ validation.categoryId.message }}</p>
            </div>
            
            <div class="form-group">
              <label for="status">文章状态</label>
              <select id="status" v-model="articleForm.status">
                <option value="published">已发布</option>
                <option value="draft">草稿</option>
              </select>
              <div class="field-help">
                <span>"草稿"状态的文章只有作者可见，不会公开显示</span>
              </div>
            </div>
            
            <div class="form-group" v-if="articleForm.status === 'published'">
              <label for="publishedAt">发布时间</label>
              <input 
                id="publishedAt"
                v-model="articleForm.publishedAt"
                type="datetime-local"
                placeholder="即时发布"
              />
              <div class="field-help">
                <span>设置未来的时间可以定时发布文章，留空表示立即发布</span>
              </div>
            </div>
            
            <div class="form-group">
              <label for="visibility">可见性</label>
              <select id="visibility" v-model="articleForm.visibility">
                <option value="public">公开</option>
                <option value="private">私密</option>
                <option value="password">密码保护</option>
              </select>
              <div class="field-help">
                <span>"私密"文章只有作者可见，"密码保护"文章需要密码才能查看</span>
              </div>
            </div>
            
            <div class="form-group" v-if="articleForm.visibility === 'password'" :class="{ 'has-error': !validation.password.valid }">
              <label for="password" class="required-field">访问密码</label>
              <input 
                id="password"
                v-model="articleForm.password"
                type="password"
                placeholder="请设置访问密码"
                :aria-invalid="!validation.password.valid"
                aria-required="true"
              />
              <p v-if="!validation.password.valid" class="form-error-text">{{ validation.password.message }}</p>
            </div>
            
            <div class="form-group">
              <label for="tags">标签</label>
              <div class="tags-help">
                <span>选择适合文章的标签（只能选择现有标签）</span>
              </div>
              <div class="tags-container" role="group" aria-label="文章标签">
                <label 
                  v-for="tag in allTags" 
                  :key="tag.id" 
                  class="tag-checkbox"
                >
                  <input 
                    type="checkbox"
                    :value="tag.name"
                    v-model="articleForm.tags"
                    :aria-label="`标签: ${tag.name}`"
                  />
                  <span>{{ tag.name }}</span>
                </label>
                
                <div v-if="allTags.length === 0" class="no-tags-message">
                  暂无可用标签，请联系管理员添加标签
                </div>
              </div>
            </div>
            
            <div class="form-group content-group" :class="{ 'has-error': !validation.content.valid }">
              <label for="content" class="required-field">内容</label>
              <div class="editor-wrapper">
                <MarkdownEditor
                  v-model="articleForm.content"
                  placeholder="请输入文章内容..."
                  height="500px"
                  @save="saveArticle"
                  :aria-invalid="!validation.content.valid"
                  aria-required="true"
                />
              </div>
              <p v-if="!validation.content.valid" class="form-error-text">{{ validation.content.message }}</p>
            </div>
            
            <div class="form-group">
              <label for="summary">摘要</label>
              <div class="summary-help">
                <span>可选，如不填写将自动生成</span>
                <button 
                  type="button" 
                  class="generate-button"
                  @click="generateSummary"
                  aria-label="自动生成摘要"
                >
                  自动生成
                </button>
              </div>
              <textarea 
                id="summary"
                v-model="articleForm.summary"
                placeholder="请输入文章摘要"
                rows="3"
              ></textarea>
            </div>
          </div>
          
          <!-- 预览模式 -->
          <div v-else class="preview-mode">
            <div class="preview-header">
              <h1>{{ articleForm.title || '无标题' }}</h1>
              
              <div class="preview-meta">
                <div v-if="articleForm.categoryId" class="preview-category">
                  分类：{{ categories.find(c => c.id === articleForm.categoryId)?.name || '未分类' }}
                </div>
                
                <div v-if="articleForm.tags.length" class="preview-tags">
                  标签：
                  <span 
                    v-for="tagId in articleForm.tags" 
                    :key="tagId"
                    class="preview-tag"
                  >
                    {{ allTags.find(t => t.id === tagId)?.name }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="preview-content" v-html="renderedContent"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.article-editor-page {
  padding: 40px 0;
  background-color: var(--bg-primary);
  min-height: 100vh;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 编辑器容器 */
.editor-container {
  background-color: var(--card-bg);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
  transition: all 0.3s ease;
}

.editor-header {
  padding: 20px 30px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-elevated);
}

.editor-header h1 {
  font-size: 1.8rem;
  color: var(--text-primary);
  margin: 0;
}

.editor-actions {
  display: flex;
  gap: 10px;
}

.button-icon {
  margin-right: 5px;
  font-size: 1.1rem;
}

.spinning {
  display: inline-block;
  animation: spin 1.5s linear infinite;
}

.preview-button,
.save-button,
.cancel-button {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.preview-button {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.preview-button:hover {
  background-color: var(--bg-hover);
}

.preview-button.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.save-button {
  background-color: var(--primary-color);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.save-button:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.save-button:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.save-button:disabled {
  background-color: var(--bg-secondary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.cancel-button {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.cancel-button:hover {
  background-color: var(--bg-hover);
  color: var(--error-color);
}

/* 错误消息 */
.error-message {
  background-color: rgba(var(--error-color-rgb, 245, 108, 108), 0.1);
  color: var(--error-color);
  padding: 12px 20px;
  border-radius: 4px;
  margin: 20px 30px 0;
  border-left: 4px solid var(--error-color);
  display: flex;
  align-items: center;
}

/* 成功消息 */
.success-message {
  background-color: rgba(var(--success-color-rgb, 103, 194, 58), 0.1);
  color: var(--success-color);
  padding: 12px 20px;
  border-radius: 4px;
  margin: 20px 30px 0;
  border-left: 4px solid var(--success-color);
}

.message-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.close-message {
  background: none;
  border: none;
  color: currentColor;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

/* 编辑器主体 */
.editor-body {
  padding: 30px;
}

/* 表单样式 */
.form-group {
  margin-bottom: 25px;
}

.required-field::after {
  content: ' *';
  color: var(--error-color);
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  transition: all 0.3s;
  font-family: inherit;
  background-color: var(--input-bg);
  color: var(--text-primary);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

.has-error input,
.has-error select,
.has-error textarea,
.has-error .editor-wrapper {
  border-color: var(--error-color);
}

.form-error-text {
  color: var(--error-color);
  font-size: 0.85rem;
  margin: 5px 0 0;
}

.content-help,
.summary-help,
.tags-help {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.generate-button {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0;
}

.generate-button:hover {
  text-decoration: underline;
}

/* 标签选择 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background-color: var(--bg-elevated);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.tag-checkbox:hover {
  background-color: var(--bg-hover);
}

.tag-checkbox input:checked + span {
  color: var(--primary-color);
  font-weight: 500;
}

.tag-checkbox input {
  width: auto;
}

/* 编辑器包装器 */
.editor-wrapper {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.3s;
}

/* 预览模式 */
.preview-mode {
  padding: 20px 0;
}

.preview-header {
  margin-bottom: 30px;
}

.preview-header h1 {
  font-size: 2.2rem;
  color: var(--text-primary);
  margin: 0 0 20px;
  line-height: 1.3;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.preview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  color: var(--text-tertiary);
}

.preview-category {
  background-color: var(--bg-elevated);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.preview-tag {
  background-color: var(--bg-hover);
  color: var(--primary-color);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-right: 5px;
  display: inline-block;
  margin-bottom: 5px;
}

.preview-content {
  line-height: 1.8;
  color: var(--text-primary);
}

.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3),
.preview-content :deep(h4),
.preview-content :deep(h5),
.preview-content :deep(h6) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.25;
  color: var(--text-primary);
}

.preview-content :deep(h1) {
  font-size: 2em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border-color);
}

.preview-content :deep(h2) {
  font-size: 1.5em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border-color);
}

.preview-content :deep(h3) {
  font-size: 1.25em;
}

.preview-content :deep(p) {
  margin: 1em 0;
  color: var(--text-secondary);
}

.preview-content :deep(strong) {
  color: var(--text-primary);
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
  color: var(--text-secondary);
}

.preview-content :deep(li) {
  margin: 0.5em 0;
}

.preview-content :deep(a) {
  color: var(--primary-color);
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(code) {
  background-color: var(--bg-elevated);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9em;
}

.preview-content :deep(pre) {
  background-color: var(--bg-elevated);
  padding: 16px;
  border-radius: 4px;
  overflow: auto;
  margin: 1em 0;
}

.preview-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.preview-content :deep(blockquote) {
  margin: 1em 0;
  padding: 0 1em;
  color: var(--text-tertiary);
  border-left: 4px solid var(--border-color);
  font-style: italic;
}

.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  border: 1px solid var(--border-color);
  padding: 8px;
  text-align: left;
}

.preview-content :deep(th) {
  background-color: var(--bg-elevated);
}

.preview-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .article-editor-page {
    padding: 20px 0;
  }
  
  .container {
    padding: 0 15px;
  }
  
  .editor-header {
    flex-direction: column;
    gap: 15px;
    padding: 15px 20px;
  }
  
  .editor-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .editor-body {
    padding: 20px;
  }
  
  .preview-header h1 {
    font-size: 1.8rem;
  }
  
  .tags-container {
    gap: 8px;
  }
  
  .tag-checkbox {
    padding: 3px 8px;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .preview-button span:not(.button-icon),
  .save-button span:not(.button-icon),
  .cancel-button span:not(.button-icon) {
    display: none;
  }
  
  .button-icon {
    margin-right: 0;
  }
  
  .preview-button,
  .save-button,
  .cancel-button {
    padding: 8px;
    justify-content: center;
  }
  
  .preview-meta {
    flex-direction: column;
    gap: 10px;
  }
}

.no-tags-message {
  color: var(--text-tertiary);
  font-style: italic;
  padding: 10px;
  background-color: var(--bg-elevated);
  border-radius: 4px;
  text-align: center;
  width: 100%;
}

.field-help {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  margin-top: 5px;
}

.draft-button {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.draft-button:hover {
  background-color: var(--bg-hover);
  color: var(--primary-color);
}
</style> 