<!--
  @component ArticleList
  @description 文章列表组件，展示博客文章列表，支持分页和加载状态
-->
<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { articleApi } from '../services/api'

// 定义props
const props = defineProps({
  articles: {
    type: Array,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  currentPage: {
    type: Number,
    default: 1
  },
  totalArticles: {
    type: Number,
    default: 0
  },
  pageSize: {
    type: Number,
    default: 10
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emit = defineEmits(['retry', 'page-change'])

// 路由
const router = useRouter()

// 计算总页数
const totalPages = computed(() => {
  return Math.max(1, Math.ceil(props.totalArticles / props.pageSize))
})

// 计算分页显示范围
const pageRange = computed(() => {
  const range = []
  const delta = 2 // 当前页前后显示的页数
  
  let start = Math.max(1, props.currentPage - delta)
  let end = Math.min(totalPages.value, props.currentPage + delta)
  
  // 调整以确保显示足够的页码
  if (end - start < 2 * delta) {
    if (start === 1) {
      end = Math.min(start + 2 * delta, totalPages.value)
    } else if (end === totalPages.value) {
      start = Math.max(1, end - 2 * delta)
    }
  }
  
  // 生成页码
  for (let i = start; i <= end; i++) {
    range.push(i)
  }
  
  return range
})

// 处理页面变化
const handlePageChange = (page) => {
  if (page < 1 || page > totalPages.value || page === props.currentPage) return
  emit('page-change', page)
  
  // 滚动到页面顶部
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// 处理文章点击
const handleArticleClick = (articleId) => {
  router.push(`/article/${articleId}`)
}

// 处理重试
const handleRetry = () => {
  emit('retry')
}

// 处理点赞
const handleLike = async (articleId, event) => {
  event.stopPropagation() // 阻止事件冒泡，避免触发文章点击
  
  if (!props.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    // 找到当前文章
    const article = props.articles.find(a => a.id === articleId)
    if (!article) return
    
    // 乐观更新UI
    article.likes_count = (article.likes_count || 0) + 1
    
    // 调用API
    await articleApi.likeArticle(articleId)
  } catch (err) {
    console.error('点赞失败:', err)
  }
}

// 处理标签点击
const handleTagClick = (tagName, event) => {
  event.stopPropagation() // 阻止事件冒泡，避免触发文章点击
  
  // 使用路由导航到带有标签筛选的首页
  router.push({
    path: '/',
    query: { tag: tagName }
  })
}

// 处理分类点击
const handleCategoryClick = (categoryId, event) => {
  event.stopPropagation() // 阻止事件冒泡，避免触发文章点击
  
  // 使用路由导航到带有分类筛选的首页
  router.push({
    path: '/',
    query: { category: categoryId }
  })
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

// 截断文本
const truncateText = (text, length = 100) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

// 监视文章数据变化，用于调试
watch(() => props.articles, (newArticles) => {
  console.log('ArticleList组件接收到新的文章数据:', newArticles)
}, { deep: true })
</script>

<template>
  <div class="article-list">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载文章...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button class="retry-button" @click="handleRetry">重试</button>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="articles.length === 0" class="empty-container">
      <p>暂无文章</p>
    </div>
    
    <!-- 文章列表 -->
    <div v-else class="articles-container">
      <div 
        v-for="article in articles" 
        :key="article.id" 
        class="article-card"
        :class="{ 'article-pinned': article.is_pinned }"
        @click="handleArticleClick(article.id)"
      >
        <!-- 文章标题和置顶标记 -->
        <div class="article-header">
          <h2 class="article-title">{{ article.title }}</h2>
          <span v-if="article.is_pinned" class="pin-badge">置顶</span>
        </div>
        
        <!-- 文章摘要 -->
        <p class="article-summary">{{ truncateText(article.summary) }}</p>
        
        <!-- 文章元数据 -->
        <div class="article-meta">
          <!-- 作者和日期 -->
          <div class="meta-left">
            <span class="article-author">
              {{ article.author ? article.author.username : '未知作者' }}
            </span>
            <span class="article-date">{{ formatDate(article.created_at) }}</span>
          </div>
          
          <!-- 阅读量和点赞 -->
          <div class="meta-right">
            <span class="article-views">
              <i class="icon-eye"></i> {{ article.view_count || 0 }}
            </span>
            <span 
              class="article-likes"
              @click="handleLike(article.id, $event)"
            >
              <i class="icon-heart"></i> {{ article.likes_count || 0 }}
            </span>
          </div>
        </div>
        
        <!-- 分类和标签 -->
        <div class="article-tags-categories">
          <span 
            v-if="article.category" 
            class="article-category"
            @click="handleCategoryClick(article.category.id, $event)"
          >
            {{ article.category.name }}
          </span>
          
          <div class="article-tags">
            <span 
              v-for="tag in article.tags" 
              :key="tag.id" 
              class="article-tag"
              @click="handleTagClick(tag.name, $event)"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 分页控件 -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="page-button"
          :disabled="currentPage === 1"
          @click="handlePageChange(currentPage - 1)"
        >
          上一页
        </button>
        
        <button 
          v-if="pageRange[0] > 1" 
          class="page-button"
          @click="handlePageChange(1)"
        >
          1
        </button>
        
        <span v-if="pageRange[0] > 2" class="page-ellipsis">...</span>
        
        <button 
          v-for="page in pageRange" 
          :key="page"
          class="page-button"
          :class="{ active: page === currentPage }"
          @click="handlePageChange(page)"
        >
          {{ page }}
        </button>
        
        <span v-if="pageRange[pageRange.length - 1] < totalPages - 1" class="page-ellipsis">...</span>
        
        <button 
          v-if="pageRange[pageRange.length - 1] < totalPages" 
          class="page-button"
          @click="handlePageChange(totalPages)"
        >
          {{ totalPages }}
        </button>
        
        <button 
          class="page-button"
          :disabled="currentPage === totalPages"
          @click="handlePageChange(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 文章列表容器 */
.article-list {
  width: 100%;
  margin: 0 auto;
}

/* 文章卡片 */
.article-card {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--card-shadow);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid transparent;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}

/* 置顶文章样式 */
.article-pinned {
  border-left-color: var(--primary-color);
}

/* 文章标题区域 */
.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.article-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.pin-badge {
  background-color: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

/* 文章摘要 */
.article-summary {
  color: var(--text-secondary);
  margin-bottom: 15px;
  line-height: 1.6;
}

/* 文章元数据 */
.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-size: 0.9rem;
  color: var(--text-tertiary);
}

.meta-left, .meta-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.article-author {
  font-weight: 500;
}

.article-views, .article-likes {
  display: flex;
  align-items: center;
  gap: 5px;
}

.article-likes {
  cursor: pointer;
  transition: color 0.2s;
}

.article-likes:hover {
  color: var(--primary-color);
}

/* 图标样式 */
.icon-eye, .icon-heart {
  font-size: 1rem;
}

/* 分类和标签 */
.article-tags-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.article-category {
  background-color: var(--primary-color);
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.article-tag {
  background-color: var(--tag-bg);
  color: var(--tag-color);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.article-tag:hover, .article-category:hover {
  opacity: 0.8;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error-container {
  text-align: center;
  padding: 40px 0;
}

.error-message {
  color: var(--error-color);
  margin-bottom: 15px;
}

.retry-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-button:hover {
  background-color: var(--primary-dark);
}

/* 空状态 */
.empty-container {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
}

/* 分页控件 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 30px;
}

.page-button {
  min-width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
  color: var(--text-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-button:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.page-button.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-ellipsis {
  color: var(--text-tertiary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .article-card {
    padding: 15px;
  }
  
  .article-title {
    font-size: 1.2rem;
  }
  
  .article-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .meta-right {
    width: 100%;
    justify-content: flex-start;
  }
}
</style> 