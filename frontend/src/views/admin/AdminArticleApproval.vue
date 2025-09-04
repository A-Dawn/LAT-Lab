<template>
  <div class="admin-article-approval">
    <div class="page-header">
      <h1>文章审核管理</h1>
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-number">{{ stats.total }}</div>
          <div class="stat-label">总文章数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.approved }}</div>
          <div class="stat-label">已审核</div>
        </div>
        <div class="stat-card pending">
          <div class="stat-number">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.approval_rate }}%</div>
          <div class="stat-label">审核通过率</div>
        </div>
      </div>
    </div>

    <div class="content-area">
      <div v-if="isLoading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchData" class="retry-btn">重试</button>
      </div>

      <div v-else>
        <div class="articles-list">
          <div v-if="pendingArticles.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>暂无待审核文章</h3>
            <p>所有文章都已审核完成</p>
          </div>

          <div v-else class="article-items">
            <div 
              v-for="article in paginatedArticles" 
              :key="article.id" 
              class="article-item"
              :class="{ 'pending': !article.is_approved }"
            >
              <div class="article-header">
                <div class="article-title">
                  <h3>{{ article.title }}</h3>
                  <span v-if="!article.is_approved" class="status-badge pending">待审核</span>
                </div>
                <div class="article-meta">
                  <span class="author">作者: {{ article.author?.username || '未知' }}</span>
                  <span class="date">{{ formatDate(article.created_at) }}</span>
                </div>
              </div>

              <div class="article-content">
                <p class="summary">{{ article.summary || '暂无摘要' }}</p>
                <div class="article-stats">
                  <span class="stat">浏览量: {{ article.view_count || 0 }}</span>
                  <span class="stat">点赞: {{ article.likes_count || 0 }}</span>
                  <span class="stat">状态: {{ getStatusText(article.status) }}</span>
                </div>
              </div>

              <div class="article-actions">
                <button 
                  @click="viewArticle(article.id)" 
                  class="btn btn-secondary"
                >
                  查看文章
                </button>
                <button 
                  @click="approveArticle(article.id)" 
                  class="btn btn-success"
                  :disabled="article.is_approved"
                >
                  审核通过
                </button>
                <button 
                  @click="openRejectDialog(article)" 
                  class="btn btn-danger"
                  :disabled="article.is_approved"
                >
                  拒绝
                </button>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="totalPages > 1" class="pagination">
            <button 
              @click="goToPage(currentPage - 1)" 
              :disabled="currentPage === 1"
              class="page-btn"
            >
              上一页
            </button>
            
            <span class="page-info">
              第 {{ currentPage }} 页，共 {{ totalPages }} 页
            </span>
            
            <button 
              @click="goToPage(currentPage + 1)" 
              :disabled="currentPage === totalPages"
              class="page-btn"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 拒绝原因对话框 -->
    <div v-if="rejectDialogVisible" class="modal-overlay" @click="closeRejectDialog">
      <div class="modal-content" @click.stop>
        <h3>拒绝文章</h3>
        <p>请提供拒绝原因（可选）：</p>
        <textarea 
          v-model="rejectReason" 
          placeholder="请输入拒绝原因..."
          rows="4"
          class="reject-reason-input"
        ></textarea>
        <div class="modal-actions">
          <button @click="closeRejectDialog" class="btn btn-secondary">取消</button>
          <button @click="confirmReject" class="btn btn-danger">确认拒绝</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { articleApi } from '../../services/api'
import toast from '../../utils/toast'

const router = useRouter()

// 响应式数据
const pendingArticles = ref([])
const stats = ref({
  total: 0,
  approved: 0,
  pending: 0,
  approval_rate: 0
})
const isLoading = ref(true)
const error = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = 10
const totalPages = computed(() => Math.ceil(pendingArticles.value.length / pageSize))

const paginatedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return pendingArticles.value.slice(start, end)
})

// 拒绝对话框
const rejectDialogVisible = ref(false)
const articleToReject = ref(null)
const rejectReason = ref('')

// 获取数据
const fetchData = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // 并行获取待审核文章和统计信息
    const [articlesResponse, statsResponse] = await Promise.all([
      articleApi.getPendingArticles({ limit: 100 }),
      articleApi.getApprovalStats()
    ])
    
    pendingArticles.value = articlesResponse || []
    stats.value = statsResponse || {
      total: 0,
      approved: 0,
      pending: 0,
      approval_rate: 0
    }
  } catch (err) {
    console.error('获取数据失败:', err)
    error.value = '获取数据失败'
  } finally {
    isLoading.value = false
  }
}

// 审核通过文章
const approveArticle = async (articleId) => {
  try {
    await articleApi.approveArticle(articleId)
    
    // 从列表中移除已审核的文章
    pendingArticles.value = pendingArticles.value.filter(article => article.id !== articleId)
    
    // 更新统计信息
    stats.value.approved += 1
    stats.value.pending -= 1
    stats.value.approval_rate = Math.round(stats.value.approved / stats.value.total * 100)
    
    toast.success('文章审核通过')
  } catch (err) {
    console.error('审核文章失败:', err)
    toast.error('审核文章失败')
  }
}

// 打开拒绝对话框
const openRejectDialog = (article) => {
  articleToReject.value = article
  rejectDialogVisible.value = true
  rejectReason.value = ''
}

// 关闭拒绝对话框
const closeRejectDialog = () => {
  rejectDialogVisible.value = false
  articleToReject.value = null
  rejectReason.value = ''
}

// 确认拒绝文章
const confirmReject = async () => {
  if (!articleToReject.value) return
  
  try {
    await articleApi.rejectArticle(articleToReject.value.id, rejectReason.value)
    
    // 从列表中移除被拒绝的文章
    pendingArticles.value = pendingArticles.value.filter(article => article.id !== articleToReject.value.id)
    
    // 更新统计信息
    stats.value.total -= 1
    stats.value.pending -= 1
    if (stats.value.total > 0) {
      stats.value.approval_rate = Math.round(stats.value.approved / stats.value.total * 100)
    }
    
    closeRejectDialog()
    toast.success('文章已拒绝')
  } catch (err) {
    console.error('拒绝文章失败:', err)
    toast.error('拒绝文章失败')
  }
}

// 查看文章
const viewArticle = (articleId) => {
  router.push(`/article/${articleId}`)
}

// 分页导航
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'published': '已发布'
  }
  return statusMap[status] || status
}

// 页面加载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.admin-article-approval {
  padding: 20px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: var(--text-primary);
  margin-bottom: 20px;
  font-size: 2rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: var(--card-shadow);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}

.stat-card.pending {
  border-left: 4px solid var(--warning-color);
  background: var(--bg-elevated);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 5px;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.content-area {
  background: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 40px 20px;
  color: var(--error-color);
}

.retry-btn {
  margin-top: 15px;
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: var(--secondary-color);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.article-items {
  padding: 20px;
}

.article-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: var(--card-bg);
  transition: box-shadow 0.2s;
}

.article-item:hover {
  box-shadow: var(--card-shadow-hover);
}

.article-item.pending {
  border-left: 4px solid var(--warning-color);
  background: var(--bg-elevated);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.article-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.article-title h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 18px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.pending {
  background: var(--warning-color);
  color: white;
}

.article-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
  font-size: 14px;
  color: var(--text-secondary);
}

.article-content {
  margin-bottom: 20px;
}

.summary {
  color: var(--text-secondary);
  margin-bottom: 10px;
  line-height: 1.5;
}

.article-stats {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: var(--text-tertiary);
}

.article-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--text-tertiary);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: var(--text-secondary);
}

.btn-success {
  background: var(--success-color);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: var(--success-color);
  filter: brightness(0.9);
}

.btn-danger {
  background: var(--error-color);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: var(--error-color);
  filter: brightness(0.9);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.page-btn {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: var(--secondary-color);
}

.page-btn:disabled {
  background: var(--text-tertiary);
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: var(--card-bg);
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  border: 1px solid var(--border-color);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
}

.reject-reason-input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  margin-bottom: 20px;
  font-family: inherit;
  resize: vertical;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.reject-reason-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.25);
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .admin-article-approval {
    padding: 10px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .article-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .article-meta {
    align-items: flex-start;
  }
  
  .article-actions {
    flex-direction: column;
  }
  
  .article-stats {
    flex-direction: column;
    gap: 5px;
  }
}
</style> 