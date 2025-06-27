<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { articleApi } from '../../services/api'

const router = useRouter()
const articles = ref([])
const filteredArticles = ref([])
const isLoading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const confirmDialogVisible = ref(false)
const articleToDelete = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = computed(() => Math.ceil(filteredArticles.value.length / pageSize.value))

const paginatedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredArticles.value.slice(start, end)
})

// 排序
const sortOptions = ref([
  { value: 'newest', label: '最新发布' },
  { value: 'oldest', label: '最早发布' },
  { value: 'view_count', label: '浏览量' }
])
const currentSort = ref('newest')

// 搜索和过滤
const updateFilteredArticles = () => {
  if (!searchQuery.value.trim()) {
    filteredArticles.value = [...articles.value]
  } else {
    const query = searchQuery.value.toLowerCase().trim()
    filteredArticles.value = articles.value.filter(article => 
      article.title.toLowerCase().includes(query) ||
      article.author?.username.toLowerCase().includes(query) ||
      article.summary?.toLowerCase().includes(query)
    )
  }
  
  // 应用排序
  applySorting()
  
  // 重置页码
  if (currentPage.value > totalPages.value && totalPages.value > 0) {
    currentPage.value = 1
  }
}

// 排序文章
const applySorting = () => {
  filteredArticles.value.sort((a, b) => {
    switch (currentSort.value) {
      case 'newest':
        return new Date(b.created_at) - new Date(a.created_at)
      case 'oldest':
        return new Date(a.created_at) - new Date(b.created_at)
      case 'view_count':
        return b.view_count - a.view_count
      default:
        return 0
    }
  })
}

// 页码导航
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 获取所有文章
const fetchArticles = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await articleApi.getArticles({ limit: 100 })
    articles.value = response || []
    updateFilteredArticles()
  } catch (err) {
    console.error('获取文章列表失败:', err)
    error.value = '获取文章列表失败'
  } finally {
    isLoading.value = false
  }
}

// 显示删除确认对话框
const showDeleteConfirm = (article) => {
  articleToDelete.value = article
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
    await articleApi.deleteArticle(articleToDelete.value.id)
    
    // 从列表中移除已删除的文章
    articles.value = articles.value.filter(article => article.id !== articleToDelete.value.id)
    updateFilteredArticles()
    closeDeleteConfirm()
  } catch (err) {
    console.error('删除文章失败:', err)
    error.value = '删除文章失败'
  }
}

// 编辑文章
const editArticle = (id) => {
  router.push(`/article/${id}/edit`)
}

// 查看文章
const viewArticle = (id) => {
  router.push(`/article/${id}`)
}

// 创建新文章
const createArticle = () => {
  router.push('/article/new')
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

// 监听搜索和排序变化
const handleSearchInput = () => {
  updateFilteredArticles()
}

const handleSortChange = () => {
  applySorting()
}

onMounted(fetchArticles)
</script>

<template>
  <div class="admin-articles">
    <div class="page-header">
      <h2>文章管理</h2>
      <button 
        @click="createArticle" 
        class="create-button"
        aria-label="创建新文章"
      >
        <span class="button-icon" aria-hidden="true">+</span>
        创建文章
      </button>
    </div>
    
    <div class="filter-bar">
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          @input="handleSearchInput"
          type="text" 
          placeholder="搜索文章标题或作者..."
          aria-label="搜索文章"
        >
        <span class="search-icon" aria-hidden="true">🔍</span>
      </div>
      
      <div class="sort-box">
        <label for="sort-select">排序:</label>
        <select 
          id="sort-select" 
          v-model="currentSort"
          @change="handleSortChange"
          aria-label="排序方式"
        >
          <option 
            v-for="option in sortOptions" 
            :key="option.value" 
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-state" aria-live="polite">
      <div class="loading-spinner" aria-hidden="true"></div>
      <p>加载文章列表中...</p>
    </div>
    
    <div v-else-if="error" class="error-state" role="alert">
      <p>{{ error }}</p>
      <button @click="fetchArticles" class="retry-button" aria-label="重试">重试</button>
    </div>
    
    <div v-else class="articles-table-container" role="region" aria-label="文章列表">
      <p v-if="filteredArticles.length" class="results-summary">
        显示 {{ paginatedArticles.length }} 篇文章，共 {{ filteredArticles.length }} 篇
      </p>
      
      <div v-if="filteredArticles.length === 0" class="empty-state">
        <div v-if="searchQuery" class="empty-search">
          <div class="empty-icon" aria-hidden="true">🔍</div>
          <h3>没有找到匹配的文章</h3>
          <p>尝试使用不同的搜索条件</p>
          <button @click="searchQuery = ''; updateFilteredArticles();" class="action-button">
            清除搜索
          </button>
        </div>
        <div v-else class="empty-list">
          <div class="empty-icon" aria-hidden="true">📝</div>
          <h3>还没有任何文章</h3>
          <p>创建您的第一篇文章</p>
          <button @click="createArticle" class="action-button">
            创建文章
          </button>
        </div>
      </div>
      
      <table v-else class="articles-table" aria-label="文章列表">
        <thead>
          <tr>
            <th scope="col">ID</th>
            <th scope="col">标题</th>
            <th scope="col">作者</th>
            <th scope="col">发布日期</th>
            <th scope="col">阅读量</th>
            <th scope="col" class="actions-header">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="article in paginatedArticles" :key="article.id">
            <td>{{ article.id }}</td>
            <td class="title-cell">{{ article.title }}</td>
            <td>{{ article.author?.username || '未知' }}</td>
            <td>{{ formatDate(article.created_at) }}</td>
            <td class="view-count">{{ article.view_count }}</td>
            <td class="actions-cell">
              <button 
                @click="viewArticle(article.id)" 
                class="action-button view"
                aria-label="查看文章"
              >
                <span class="action-icon" aria-hidden="true">👁️</span>
                <span class="action-text">查看</span>
              </button>
              <button 
                @click="editArticle(article.id)" 
                class="action-button edit"
                aria-label="编辑文章"
              >
                <span class="action-icon" aria-hidden="true">✏️</span>
                <span class="action-text">编辑</span>
              </button>
              <button 
                @click="showDeleteConfirm(article)" 
                class="action-button delete"
                aria-label="删除文章"
              >
                <span class="action-icon" aria-hidden="true">🗑️</span>
                <span class="action-text">删除</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 分页控制 -->
      <div v-if="totalPages > 1" class="pagination" role="navigation" aria-label="分页导航">
        <button 
          @click="goToPage(1)" 
          :disabled="currentPage === 1"
          class="page-button"
          aria-label="第一页"
        >
          &lt;&lt;
        </button>
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
        <button 
          @click="goToPage(totalPages)" 
          :disabled="currentPage === totalPages"
          class="page-button"
          aria-label="最后一页"
        >
          &gt;&gt;
        </button>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <div v-if="confirmDialogVisible" class="modal-overlay" @click="closeDeleteConfirm">
      <div class="confirm-dialog" @click.stop role="dialog" aria-labelledby="dialog-title">
        <h3 id="dialog-title">确认删除</h3>
        <p>您确定要删除文章 "<strong>{{ articleToDelete?.title }}</strong>" 吗？此操作不可恢复。</p>
        
        <div class="dialog-actions">
          <button 
            @click="deleteArticle" 
            class="dialog-button confirm-button"
            aria-label="确认删除"
          >
            确认删除
          </button>
          <button 
            @click="closeDeleteConfirm" 
            class="dialog-button cancel-button"
            aria-label="取消删除"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-articles {
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.create-button {
  display: flex;
  align-items: center;
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.button-icon {
  margin-right: 6px;
  font-size: 1.2rem;
}

.create-button:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.create-button:active {
  transform: translateY(0);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box input {
  width: 100%;
  padding: 10px 40px 10px 15px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  font-size: 1rem;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: all 0.3s;
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
}

.sort-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-box label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.sort-box select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.sort-box select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-spinner {
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

.retry-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
  transition: all 0.3s;
}

.retry-button:hover {
  filter: brightness(1.1);
}

.results-summary {
  color: var(--text-tertiary);
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 60px 0;
  background-color: var(--card-bg);
  border-radius: 8px;
  border: 1px dashed var(--border-color);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 20px;
  color: var(--text-tertiary);
}

.empty-state h3 {
  font-size: 1.2rem;
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
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95rem;
}

.action-button:hover {
  filter: brightness(1.1);
}

.articles-table-container {
  overflow-x: auto;
}

.articles-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
}

.articles-table th, .articles-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.articles-table th {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  font-weight: 500;
  position: sticky;
  top: 0;
  z-index: 1;
}

.articles-table tr {
  background-color: var(--card-bg);
  transition: all 0.2s;
}

.articles-table tr:hover {
  background-color: var(--bg-hover);
}

.articles-table tr:last-child td {
  border-bottom: none;
}

.title-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
  color: var(--text-primary);
}

.view-count {
  text-align: center;
}

.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  white-space: nowrap;
}

.actions-header {
  text-align: right;
}

.action-button {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.action-icon {
  margin-right: 5px;
  font-size: 0.9rem;
}

.action-button.view {
  background-color: rgba(76, 132, 255, 0.1);
  color: var(--primary-color);
}

.action-button.view:hover {
  background-color: rgba(76, 132, 255, 0.2);
}

.action-button.edit {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.action-button.edit:hover {
  background-color: rgba(103, 194, 58, 0.2);
}

.action-button.delete {
  background-color: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.action-button.delete:hover {
  background-color: rgba(245, 108, 108, 0.2);
}

/* 分页控制 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.page-button {
  min-width: 36px;
  height: 36px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
  padding: 0 8px;
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
  padding: 0 10px;
}

/* 删除确认对话框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fade-in 0.2s ease;
}

.confirm-dialog {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slide-up 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.confirm-dialog h3 {
  color: var(--text-primary);
  margin-top: 0;
  margin-bottom: 15px;
}

.confirm-dialog p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.dialog-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.confirm-button {
  background-color: #f56c6c;
  color: white;
}

.confirm-button:hover {
  background-color: #f78989;
}

.cancel-button {
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.cancel-button:hover {
  background-color: var(--bg-hover);
}

/* 响应式适配 */
@media (max-width: 992px) {
  .title-cell {
    max-width: 200px;
  }
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .search-box {
    max-width: none;
  }
  
  .action-text {
    display: none;
  }
  
  .action-button {
    padding: 6px;
  }
  
  .action-icon {
    margin-right: 0;
  }
  
  .title-cell {
    max-width: 150px;
  }
}

@media (max-width: 576px) {
  .articles-table th:not(:nth-child(2)):not(:last-child),
  .articles-table td:not(:nth-child(2)):not(:last-child) {
    display: none;
  }
  
  .title-cell {
    max-width: none;
  }
}
</style> 