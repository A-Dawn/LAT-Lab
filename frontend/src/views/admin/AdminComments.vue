<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { commentApi } from '../../services/api'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import toast from '../../utils/toast'

const router = useRouter()
const comments = ref([])
const pendingComments = ref([])
const approvedComments = ref([])
const isLoading = ref(true)
const error = ref(null)
const activeTab = ref('pending')

const confirmDialogVisible = ref(false)
const commentToDelete = ref(null)

const fetchComments = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await commentApi.getAllComments()
    
    comments.value = response || []
    
    pendingComments.value = comments.value.filter(comment => !comment.is_approved)
    approvedComments.value = comments.value.filter(comment => comment.is_approved)
  } catch (err) {
    console.error('获取评论列表失败:', err)
    error.value = '获取评论列表失败'
  } finally {
    isLoading.value = false
  }
}

const approveComment = async (commentId) => {
  try {
    await commentApi.updateComment(commentId, {
      is_approved: true
    })
    
    const comment = comments.value.find(c => c.id === commentId)
    if (comment) {
      comment.is_approved = true
      
      pendingComments.value = pendingComments.value.filter(c => c.id !== commentId)
      approvedComments.value.push(comment)
    }
    
    toast.success('评论审核成功')
  } catch (err) {
    console.error('审核评论失败:', err)
    toast.error('审核评论失败')
  }
}

const openDeleteConfirm = (comment) => {
  commentToDelete.value = comment
  confirmDialogVisible.value = true
}
const closeDeleteConfirm = () => {
  confirmDialogVisible.value = false
  commentToDelete.value = null
}

const deleteComment = async () => {
  if (!commentToDelete.value) return
  
  try {
    await commentApi.deleteComment(commentToDelete.value.id)
    
    comments.value = comments.value.filter(c => c.id !== commentToDelete.value.id)
    pendingComments.value = pendingComments.value.filter(c => c.id !== commentToDelete.value.id)
    approvedComments.value = approvedComments.value.filter(c => c.id !== commentToDelete.value.id)
    
    closeDeleteConfirm()
    
    toast.success('评论删除成功')
  } catch (err) {
    console.error('删除评论失败:', err)
    toast.error('删除评论失败')
  }
}

const viewArticle = (articleId) => {
  router.push(`/article/${articleId}`)
}

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

const switchTab = (tab) => {
  activeTab.value = tab
}

onMounted(fetchComments)
</script>

<template>
  <div class="admin-comments">
    <div class="page-header">
      <h2>评论管理</h2>
    </div>
    
    <div class="tabs">
      <button 
        class="tab-button" 
        :class="{ active: activeTab === 'pending' }"
        @click="switchTab('pending')"
      >
        待审核 ({{ pendingComments.length }})
      </button>
      <button 
        class="tab-button" 
        :class="{ active: activeTab === 'approved' }"
        @click="switchTab('approved')"
      >
        已审核 ({{ approvedComments.length }})
      </button>
      <button 
        class="tab-button" 
        :class="{ active: activeTab === 'all' }"
        @click="switchTab('all')"
      >
        全部 ({{ comments.length }})
      </button>
    </div>
    
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchComments" class="retry-button">重试</button>
    </div>
    
    <div v-else class="comments-table-container">
      <!-- 待审核评论 -->
      <div v-if="activeTab === 'pending'">
        <div v-if="pendingComments.length === 0" class="empty-message">
          没有待审核的评论
        </div>
        <table v-else class="comments-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>内容</th>
              <th>用户</th>
              <th>文章</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="comment in pendingComments" :key="comment.id">
              <td>{{ comment.id }}</td>
              <td class="content-cell">{{ comment.content }}</td>
              <td>{{ comment.user?.username || '未知' }}</td>
              <td class="article-cell">
                <a @click="viewArticle(comment.article_id)" class="article-link">
                  {{ comment.article?.title || `文章 #${comment.article_id}` }}
                </a>
              </td>
              <td>{{ formatDate(comment.created_at) }}</td>
              <td class="actions-cell">
                <button @click="approveComment(comment.id)" class="action-button approve">
                  通过
                </button>
                <button @click="openDeleteConfirm(comment)" class="action-button delete">
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 已审核评论 -->
      <div v-if="activeTab === 'approved'">
        <div v-if="approvedComments.length === 0" class="empty-message">
          没有已审核的评论
        </div>
        <table v-else class="comments-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>内容</th>
              <th>用户</th>
              <th>文章</th>
              <th>时间</th>
              <th>点赞</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="comment in approvedComments" :key="comment.id">
              <td>{{ comment.id }}</td>
              <td class="content-cell">{{ comment.content }}</td>
              <td>{{ comment.user?.username || '未知' }}</td>
              <td class="article-cell">
                <a @click="viewArticle(comment.article_id)" class="article-link">
                  {{ comment.article?.title || `文章 #${comment.article_id}` }}
                </a>
              </td>
              <td>{{ formatDate(comment.created_at) }}</td>
              <td>{{ comment.likes || 0 }}</td>
              <td class="actions-cell">
                <button @click="openDeleteConfirm(comment)" class="action-button delete">
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 全部评论 -->
      <div v-if="activeTab === 'all'">
        <div v-if="comments.length === 0" class="empty-message">
          没有评论
        </div>
        <table v-else class="comments-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>内容</th>
              <th>用户</th>
              <th>文章</th>
              <th>状态</th>
              <th>时间</th>
              <th>点赞</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="comment in comments" :key="comment.id">
              <td>{{ comment.id }}</td>
              <td class="content-cell">{{ comment.content }}</td>
              <td>{{ comment.user?.username || '未知' }}</td>
              <td class="article-cell">
                <a @click="viewArticle(comment.article_id)" class="article-link">
                  {{ comment.article?.title || `文章 #${comment.article_id}` }}
                </a>
              </td>
              <td>
                <span :class="['status-badge', comment.is_approved ? 'approved' : 'pending']">
                  {{ comment.is_approved ? '已审核' : '待审核' }}
                </span>
              </td>
              <td>{{ formatDate(comment.created_at) }}</td>
              <td>{{ comment.likes || 0 }}</td>
              <td class="actions-cell">
                <button 
                  v-if="!comment.is_approved" 
                  @click="approveComment(comment.id)" 
                  class="action-button approve"
                >
                  通过
                </button>
                <button @click="openDeleteConfirm(comment)" class="action-button delete">
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <ConfirmDialog 
      :visible="confirmDialogVisible"
      title="确认删除"
      :message="commentToDelete ? `您确定要删除这条评论吗？此操作不可恢复。` : ''"
      confirmText="确认删除"
      cancelText="取消"
      @confirm="deleteComment"
      @cancel="closeDeleteConfirm"
    />
  </div>
</template>

<style scoped>
.admin-comments {
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

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-button:hover {
  color: var(--primary-color);
}

.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
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
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background-color: var(--secondary-color);
}

.comments-table-container {
  overflow-x: auto;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
}

.comments-table {
  width: 100%;
  border-collapse: collapse;
}

.comments-table th, .comments-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.comments-table th {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  font-weight: 500;
  position: sticky;
  top: 0;
}

.comments-table tr:hover {
  background-color: var(--hover-color);
}

.comments-table tr:last-child td {
  border-bottom: none;
}

.content-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-cell {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-link {
  color: var(--primary-color);
  cursor: pointer;
  transition: color 0.3s ease;
}

.article-link:hover {
  text-decoration: underline;
  color: var(--secondary-color);
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.approved {
  background-color: rgba(var(--success-color), 0.1);
  color: var(--success-color);
  border: 1px solid rgba(var(--success-color), 0.2);
}

.status-badge.pending {
  background-color: rgba(var(--warning-color), 0.1);
  color: var(--warning-color);
  border: 1px solid rgba(var(--warning-color), 0.2);
}

.actions-cell {
  display: flex;
  gap: 5px;
}

.action-button {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.action-button.approve {
  background-color: rgba(var(--success-color), 0.1);
  color: var(--success-color);
  border: 1px solid rgba(var(--success-color), 0.2);
}

.action-button.approve:hover {
  background-color: rgba(var(--success-color), 0.2);
}

.action-button.delete {
  background-color: rgba(var(--error-color), 0.1);
  color: var(--error-color);
  border: 1px solid rgba(var(--error-color), 0.2);
}

.action-button.delete:hover {
  background-color: rgba(var(--error-color), 0.2);
}

.empty-message {
  text-align: center;
  color: var(--text-tertiary);
  padding: 20px 0;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tabs {
    flex-wrap: wrap;
  }
  
  .tab-button {
    padding: 8px 16px;
    font-size: 0.9rem;
  }
  
  .comments-table th,
  .comments-table td {
    padding: 8px 10px;
    font-size: 0.9rem;
  }
  
  .content-cell,
  .article-cell {
    max-width: 150px;
  }
  
  .actions-cell {
    flex-direction: column;
    gap: 3px;
  }
  
  .action-button {
    width: 100%;
    text-align: center;
  }
}
</style> 