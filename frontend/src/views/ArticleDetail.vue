<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { articleApi, commentApi } from '../services/api'
import CommentItem from '../components/CommentItem.vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const route = useRoute()
const router = useRouter()
const store = useStore()
const article = ref(null)
const comments = ref([])
const isLoading = ref(true)
const error = ref(null)
const commentContent = ref('')
const isSubmittingComment = ref(false)
const commentError = ref('')
const likedArticles = ref(JSON.parse(localStorage.getItem('likedArticles') || '[]'))
const likeCount = ref(0)
const hasLiked = computed(() => likedArticles.value.includes(article.value?.id))

// 密码保护相关
const isPasswordProtected = ref(false)
const articlePassword = ref('')
const isCheckingPassword = ref(false)
const passwordError = ref('')

// 配置marked解析器
marked.setOptions({
  highlight: function(code, language) {
    const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
    return hljs.highlight(validLanguage, code).value;
  },
  breaks: true,
  gfm: true
})

// 获取认证状态
const isAuthenticated = computed(() => store.getters.isAuthenticated)
const currentUser = computed(() => store.getters.currentUser)
const isAdmin = computed(() => currentUser.value?.role === 'admin')
const isAuthor = computed(() => currentUser.value?.id === article.value?.author_id)

// 渲染Markdown内容
const renderedContent = computed(() => {
  if (!article.value || !article.value.content) return '';
  try {
    return marked(article.value.content);
  } catch (e) {
    console.error('Markdown渲染失败:', e);
    return article.value.content;
  }
})

// 获取文章详情
const fetchArticle = async (password = null) => {
  try {
    isLoading.value = true
    error.value = null
    passwordError.value = ''
    
    // 从API获取文章数据
    const articleId = parseInt(route.params.id)
    if (isNaN(articleId)) {
      error.value = '无效的文章ID'
      return
    }
    
    console.log('正在获取文章:', articleId)
    let data
    
    // 如果提供了密码，使用带密码的API
    if (password) {
      data = await articleApi.getArticleWithPassword(articleId, password)
    } else {
      data = await articleApi.getArticle(articleId)
    }
    
    console.log('获取到文章数据:', data)
    
    if (!data) {
      error.value = '获取文章失败: 没有返回数据'
      return
    }
    
    article.value = data
    likeCount.value = data.likes_count || 0
    
    // 判断是否需要密码
    isPasswordProtected.value = data.visibility === 'password' && !isAuthor.value && !isAdmin.value
    
    // 如果需要密码且未提供密码，显示密码输入框
    if (isPasswordProtected.value && !password) {
      return
    }
    
    // 获取文章评论
    await fetchComments()
  } catch (e) {
    console.error('获取文章失败, 详细错误:', e)
    if (e.response) {
      if (e.response.status === 403 && e.response.data?.detail?.includes('密码')) {
        // 密码错误
        passwordError.value = '密码错误，请重试'
        isPasswordProtected.value = true
      } else {
      error.value = `获取文章失败 (${e.response.status}): ${e.response.data?.detail || '服务器错误'}`
      }
    } else if (e.request) {
      error.value = '获取文章失败: 服务器无响应'
    } else {
      error.value = `获取文章失败: ${e.message || '未知错误'}`
    }
  } finally {
    isLoading.value = false
    isCheckingPassword.value = false
  }
}

// 提交密码
const submitPassword = async () => {
  if (!articlePassword.value.trim()) {
    passwordError.value = '请输入密码'
    return
  }
  
  isCheckingPassword.value = true
  await fetchArticle(articlePassword.value)
}

// 获取文章评论
const fetchComments = async () => {
  if (!article.value) return
  
  try {
    const data = await commentApi.getComments(article.value.id)
    comments.value = data || []
  } catch (e) {
    console.error('获取评论失败:', e)
  }
}

// 提交评论
const submitComment = async () => {
  if (!isAuthenticated.value) {
    alert('请先登录后再发表评论')
    router.push('/login')
    return
  }
  
  if (!commentContent.value.trim()) {
    commentError.value = '评论内容不能为空'
    return
  }
  
  try {
    isSubmittingComment.value = true
    commentError.value = ''
    
    await commentApi.addComment(article.value.id, {
      content: commentContent.value
    })
    
    // 提交成功后刷新评论
    await fetchComments()
    
    // 清空评论框
    commentContent.value = ''
  } catch (e) {
    console.error('提交评论失败:', e)
    commentError.value = '提交评论失败，请稍后再试'
  } finally {
    isSubmittingComment.value = false
  }
}

// 点赞文章
const likeArticle = async () => {
  if (!article.value) return
  
  try {
    // 检查是否已点赞
    if (hasLiked.value) {
      // 取消点赞
      const index = likedArticles.value.indexOf(article.value.id)
      if (index > -1) {
        likedArticles.value.splice(index, 1)
        likeCount.value -= 1
      }
    } else {
      // 添加点赞
      likedArticles.value.push(article.value.id)
      likeCount.value += 1
    }
    
    // 保存到本地存储
    localStorage.setItem('likedArticles', JSON.stringify(likedArticles.value))
    
    // 尝试调用后端API（如果有的话）
    try {
      await articleApi.likeArticle(article.value.id)
    } catch (e) {
      // 如果后端API不存在或失败，不影响前端显示
      console.warn('后端点赞API不可用:', e)
    }
  } catch (e) {
    console.error('点赞失败:', e)
  }
}

// 分享文章
const shareArticle = async () => {
  if (!article.value) return
  
  // 尝试使用Web Share API
  if (navigator.share) {
    try {
      await navigator.share({
        title: article.value.title,
        text: article.value.summary || '来看看这篇文章吧！',
        url: window.location.href
      })
      return
    } catch (e) {
      if (e.name !== 'AbortError') {
        console.error('Web Share API分享失败:', e)
      }
    }
  }
  
  // 回退：复制链接到剪贴板
  try {
    await navigator.clipboard.writeText(window.location.href)
    alert('链接已复制到剪贴板')
  } catch (e) {
    console.error('复制链接失败:', e)
    // 最后的回退方案：提示用户手动复制
    const url = window.location.href
    window.prompt('复制下面的链接进行分享:', url)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(fetchArticle)
</script>

<template>
  <div class="article-detail-page">
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载文章...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">!</div>
        <h3>出错了</h3>
        <p>{{ error }}</p>
        <button @click="router.go(-1)" class="back-button">返回上一页</button>
      </div>
      
      <!-- 密码保护 -->
      <div v-else-if="isPasswordProtected" class="password-container">
        <div class="password-box">
          <div class="password-icon">🔒</div>
          <h3>此文章受密码保护</h3>
          <p>请输入密码以查看文章内容</p>
          
          <div class="password-form">
            <input 
              type="password" 
              v-model="articlePassword" 
              placeholder="请输入密码"
              @keyup.enter="submitPassword"
              :disabled="isCheckingPassword"
            />
            <button 
              @click="submitPassword" 
              :disabled="isCheckingPassword"
              class="password-submit"
            >
              <span v-if="!isCheckingPassword">确认</span>
              <span v-else>验证中...</span>
            </button>
          </div>
          
          <p v-if="passwordError" class="password-error">{{ passwordError }}</p>
        </div>
      </div>
      
      <!-- 文章内容 -->
      <div v-else-if="article" class="article-container">
        <!-- 草稿状态通知 -->
        <div v-if="article.status === 'draft'" class="article-status-banner draft">
          <span class="status-icon">📝</span>
          <span>此文章目前是草稿状态，仅作者可见</span>
        </div>
        
        <!-- 私密文章通知 -->
        <div v-if="article.visibility === 'private'" class="article-status-banner private">
          <span class="status-icon">🔒</span>
          <span>此文章是私密文章，仅作者可见</span>
        </div>
        
        <!-- 密码保护文章通知 -->
        <div v-if="article.visibility === 'password' && (isAdmin || isAuthor)" class="article-status-banner password">
          <span class="status-icon">🔑</span>
          <span>此文章是密码保护文章，访问者需要输入密码才能查看</span>
        </div>
        
        <!-- 定时发布通知 -->
        <div v-if="article.status === 'published' && article.published_at && new Date(article.published_at) > new Date()" class="article-status-banner scheduled">
          <span class="status-icon">⏲️</span>
          <span>此文章已设定于 {{ formatDate(article.published_at) }} 发布</span>
        </div>
        
        <div class="article-header">
          <h1>{{ article.title }}</h1>
          
          <div class="article-meta">
            <div class="meta-item">
              <i class="icon-user"></i>
              <span>{{ article.author?.username || '未知作者' }}</span>
            </div>
            <div class="meta-item">
              <i class="icon-calendar"></i>
              <span>{{ formatDate(article.created_at || article.created_date || new Date()) }}</span>
            </div>
            <div class="meta-item" v-if="article.category">
              <i class="icon-folder"></i>
              <span>{{ article.category.name }}</span>
            </div>
            <div class="meta-item">
              <i class="icon-eye"></i>
              <span>{{ article.view_count || 0 }} 次阅读</span>
            </div>
          </div>
          
          <div class="article-tags" v-if="article.tags && article.tags.length > 0">
            <span v-for="tag in article.tags" :key="tag.id" class="tag">
              {{ tag.name }}
            </span>
          </div>
        </div>
        
        <div class="article-content markdown-body" v-html="renderedContent"></div>
        
        <div class="article-actions">
          <button class="action-button like-button" :class="{ 'liked': hasLiked }" @click="likeArticle">
            <i class="icon-heart"></i>
            <span>{{ likeCount }}</span>
          </button>
          <button class="action-button share-button" @click="shareArticle">
            <i class="icon-share"></i>
            <span>分享</span>
          </button>
        </div>
        
        <div class="article-comments">
          <h3>评论 ({{ comments.length || 0 }})</h3>
          
          <div class="comment-list" v-if="comments.length > 0">
            <CommentItem 
              v-for="comment in comments" 
              :key="comment.id" 
              :comment="comment"
              :article-id="article.id"
              @refresh-comments="fetchComments"
            />
          </div>
          <div v-else class="empty-comments">
            <p>暂无评论，来发表第一条评论吧！</p>
          </div>
          
          <div class="comment-form">
            <h4>发表评论</h4>
            <div v-if="!isAuthenticated" class="login-notice">
              请 <router-link to="/login">登录</router-link> 后发表评论
            </div>
            <template v-else>
              <div v-if="commentError" class="comment-error">{{ commentError }}</div>
              <textarea 
                v-model="commentContent" 
                placeholder="写下你的想法..." 
                rows="4"
                :disabled="isSubmittingComment"
              ></textarea>
              <div class="comment-form-footer">
                <div class="comment-tips">
                  <span v-if="isAdmin">管理员评论将自动通过审核</span>
                  <span v-else>评论将在审核后显示</span>
                </div>
                <button 
                  class="submit-button" 
                  @click="submitComment"
                  :disabled="isSubmittingComment"
                >
                  {{ isSubmittingComment ? '提交中...' : '提交评论' }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>
      
      <!-- 文章不存在 -->
      <div v-else class="not-found-container">
        <h2>文章不存在</h2>
        <p>抱歉，您访问的文章不存在或已被删除。</p>
        <button @click="router.push('/')" class="back-button">返回首页</button>
      </div>
    </div>
  </div>
</template>

<style>
/* Markdown样式 */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  line-height: 1.6;
  word-wrap: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
.markdown-body h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
.markdown-body h3 { font-size: 1.25em; }
.markdown-body h4 { font-size: 1em; }
.markdown-body h5 { font-size: 0.875em; }
.markdown-body h6 { font-size: 0.85em; }

.markdown-body p {
  margin-top: 0;
  margin-bottom: 1em;
}

.markdown-body blockquote {
  margin: 0;
  padding: 0 1em;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 1em;
}

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27,31,35,0.05);
  border-radius: 3px;
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body pre code {
  display: inline;
  max-width: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  line-height: inherit;
  word-wrap: normal;
  background-color: transparent;
  border: 0;
}

.markdown-body img {
  max-width: 100%;
  box-sizing: content-box;
  border-style: none;
}

.markdown-body table {
  border-spacing: 0;
  border-collapse: collapse;
  width: 100%;
  overflow: auto;
  margin-bottom: 16px;
}

.markdown-body table th,
.markdown-body table td {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-body table tr {
  border-top: 1px solid #c6cbd1;
}

.markdown-body table tr:nth-child(2n) {
  background-color: #f6f8fa;
}
</style>

<style scoped>
.article-detail-page {
  padding: 40px 0;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.container {
  max-width: 900px;
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
  border-left-color: #4c84ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 错误状态 */
.error-container {
  text-align: center;
  padding: 60px 0;
}

.error-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background-color: #f56c6c;
  color: white;
  font-size: 40px;
  font-weight: bold;
  border-radius: 50%;
  margin: 0 auto 20px;
}

.error-container h3 {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: #303133;
}

.error-container p {
  color: #606266;
  margin-bottom: 20px;
}

.back-button {
  padding: 10px 20px;
  background-color: #4c84ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #3a70e3;
}

/* 文章容器 */
.article-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 30px;
  margin-bottom: 30px;
}

.article-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 20px;
}

.article-header h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 15px;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 15px;
  color: #909399;
  font-size: 0.9rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  background-color: #ecf5ff;
  color: #4c84ff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.article-actions {
  display: flex;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.like-button {
  background-color: #fef0f0;
  color: #f56c6c;
}

.like-button:hover, .like-button.liked {
  background-color: #f56c6c;
  color: white;
}

.share-button {
  background-color: #ecf5ff;
  color: #4c84ff;
}

.share-button:hover {
  background-color: #4c84ff;
  color: white;
}

/* 评论区 */
.article-comments {
  margin-top: 30px;
}

.article-comments h3 {
  font-size: 1.3rem;
  color: #303133;
  margin-bottom: 20px;
}

.empty-comments {
  text-align: center;
  padding: 30px 0;
  color: #909399;
}

.comment-form {
  margin-top: 30px;
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
}

.comment-form h4 {
  font-size: 1.1rem;
  color: #303133;
  margin-bottom: 15px;
}

.login-notice {
  text-align: center;
  padding: 20px 0;
  color: #606266;
}

.login-notice a {
  color: #4c84ff;
  font-weight: bold;
}

.comment-error {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
  font-size: 1rem;
  margin-bottom: 15px;
}

.comment-form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-tips {
  font-size: 0.9rem;
  color: #909399;
}

.submit-button {
  padding: 10px 20px;
  background-color: #4c84ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #3a70e3;
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 文章不存在 */
.not-found-container {
  text-align: center;
  padding: 60px 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.not-found-container h2 {
  font-size: 1.8rem;
  color: #303133;
  margin-bottom: 15px;
}

.not-found-container p {
  color: #606266;
  margin-bottom: 20px;
}

/* 新增样式 */
.password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 40px 20px;
}

.password-box {
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 30px;
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.password-icon {
  font-size: 50px;
  margin-bottom: 20px;
}

.password-form {
  display: flex;
  margin: 25px 0 15px;
}

.password-form input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid var(--border-color);
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
  background-color: var(--input-bg);
  color: var(--text-primary);
}

.password-submit {
  padding: 12px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.password-submit:hover {
  background-color: var(--primary-color-hover);
}

.password-submit:disabled {
  background-color: var(--disabled-color);
  cursor: not-allowed;
}

.password-error {
  color: #f56c6c;
  margin-top: 15px;
}

.article-status-banner {
  padding: 10px 15px;
  margin-bottom: 20px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.article-status-banner.draft {
  background-color: rgba(144, 147, 153, 0.1);
  border-left: 4px solid #909399;
  color: #606266;
}

.article-status-banner.private {
  background-color: rgba(245, 108, 108, 0.1);
  border-left: 4px solid #f56c6c;
  color: #f56c6c;
}

.article-status-banner.password {
  background-color: rgba(230, 162, 60, 0.1);
  border-left: 4px solid #e6a23c;
  color: #e6a23c;
}

.article-status-banner.scheduled {
  background-color: rgba(103, 194, 58, 0.1);
  border-left: 4px solid #67c23a;
  color: #67c23a;
}

.status-icon {
  margin-right: 10px;
  font-size: 1.2rem;
}
</style> 