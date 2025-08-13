<script setup>
import { ref, onMounted } from 'vue'
import { tagApi } from '../../services/api'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import toast from '../../utils/toast'

// 标签列表
const tags = ref([])

// 加载状态
const isLoading = ref(false)
const isSaving = ref(false)
const error = ref(null)

// 对话框状态
const showDialog = ref(false)
const dialogMode = ref('add') // 'add' 或 'edit'
const editingTag = ref(null)

// 删除确认对话框状态
const confirmDialogVisible = ref(false)
const tagToDelete = ref(null)

// 新标签表单
const tagForm = ref({
  name: ''
})

// 获取所有标签
const fetchTags = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await tagApi.getAllTags()
    tags.value = response || []
  } catch (err) {
    console.error('获取标签失败:', err)
    error.value = '获取标签列表失败'
  } finally {
    isLoading.value = false
  }
}

// 打开添加标签对话框
const openAddDialog = () => {
  dialogMode.value = 'add'
  tagForm.value = { name: '' }
  showDialog.value = true
}

// 打开编辑标签对话框
const openEditDialog = (tag) => {
  dialogMode.value = 'edit'
  editingTag.value = tag
  tagForm.value = { name: tag.name }
  showDialog.value = true
}

// 关闭对话框
const closeDialog = () => {
  showDialog.value = false
  tagForm.value = { name: '' }
  editingTag.value = null
}

// 保存标签
const saveTag = async () => {
  // 表单验证
  if (!tagForm.value.name.trim()) {
    error.value = '标签名称不能为空'
    return
  }
  
  try {
    isSaving.value = true
    error.value = null
    
    if (dialogMode.value === 'add') {
      // 添加新标签
      await tagApi.createTag({ name: tagForm.value.name })
      toast.success('标签添加成功')
    } else {
      // 更新现有标签
      await tagApi.updateTag(editingTag.value.id, { name: tagForm.value.name })
      toast.success('标签更新成功')
    }
    
    // 重新获取标签列表
    await fetchTags()
    
    // 关闭对话框
    closeDialog()
  } catch (err) {
    console.error('保存标签失败:', err)
    error.value = dialogMode.value === 'add' ? '添加标签失败' : '更新标签失败'
  } finally {
    isSaving.value = false
  }
}

// 打开删除确认对话框
const openDeleteConfirm = (tag) => {
  tagToDelete.value = tag
  confirmDialogVisible.value = true
}

// 关闭删除确认对话框
const closeDeleteConfirm = () => {
  confirmDialogVisible.value = false
  tagToDelete.value = null
}

// 删除标签
const deleteTag = async () => {
  if (!tagToDelete.value) return
  
  try {
    isLoading.value = true
    error.value = null
    
    await tagApi.deleteTag(tagToDelete.value.id)
    
    // 重新获取标签列表
    await fetchTags()
    
    toast.success('标签删除成功')
    
    // 关闭对话框
    closeDeleteConfirm()
  } catch (err) {
    console.error('删除标签失败:', err)
    error.value = '删除标签失败'
  } finally {
    isLoading.value = false
  }
}

// 初始化
onMounted(() => {
  fetchTags()
})
</script>

<template>
  <div class="admin-tags">
    <div class="admin-container">
      <div class="container-header">
        <h2>标签管理</h2>
        <button 
          @click="openAddDialog" 
          class="admin-btn admin-btn-primary"
          aria-label="添加标签"
        >
          添加标签
        </button>
      </div>
      
      <!-- 错误消息 -->
      <div v-if="error" class="error-message" role="alert">
        {{ error }}
        <button @click="fetchTags" class="retry-button">重试</button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="admin-loading">
        <div class="admin-loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 标签列表 -->
      <div v-else-if="tags.length > 0" class="tags-list">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>标签名称</th>
              <th>文章数量</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tag in tags" :key="tag.id">
              <td>{{ tag.id }}</td>
              <td>{{ tag.name }}</td>
              <td>{{ tag.article_count || 0 }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="openEditDialog(tag)" 
                    class="action-button edit"
                    aria-label="编辑标签"
                  >
                    编辑
                  </button>
                  <button 
                    @click="openDeleteConfirm(tag)" 
                    class="action-button delete"
                    aria-label="删除标签"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-state">
        <p>暂无标签</p>
        <button 
          @click="openAddDialog" 
          class="admin-btn admin-btn-primary"
          aria-label="添加第一个标签"
        >
          添加第一个标签
        </button>
      </div>
      
      <!-- 添加/编辑标签对话框 -->
      <div v-if="showDialog" class="dialog-overlay" @click.self="closeDialog">
        <div class="dialog" role="dialog" aria-labelledby="dialog-title">
          <div class="dialog-header">
            <h3 id="dialog-title">{{ dialogMode === 'add' ? '添加标签' : '编辑标签' }}</h3>
            <button @click="closeDialog" class="close-button" aria-label="关闭对话框">&times;</button>
          </div>
          
          <div class="dialog-content">
            <div v-if="error" class="error-message" role="alert">
              {{ error }}
            </div>
            
            <div class="admin-form-group">
              <label for="tag-name">标签名称</label>
              <input 
                id="tag-name"
                v-model="tagForm.name"
                type="text"
                placeholder="输入标签名称"
                aria-required="true"
                :disabled="isSaving"
              />
            </div>
          </div>
          
          <div class="dialog-footer">
            <button 
              @click="closeDialog" 
              class="admin-btn admin-btn-secondary"
              :disabled="isSaving"
              aria-label="取消"
            >
              取消
            </button>
            <button 
              @click="saveTag" 
              class="admin-btn admin-btn-primary"
              :disabled="isSaving"
              aria-label="保存标签"
            >
              <span v-if="isSaving">保存中...</span>
              <span v-else>保存</span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 删除确认对话框 -->
      <ConfirmDialog 
        :visible="confirmDialogVisible"
        title="确认删除"
        :message="tagToDelete ? `您确定要删除标签 '${tagToDelete.name}' 吗？这可能会影响使用此标签的文章。` : ''"
        confirmText="确认删除"
        cancelText="取消"
        @confirm="deleteTag"
        @cancel="closeDeleteConfirm"
      />
    </div>
  </div>
</template>

<style scoped>
.admin-tags {
  width: 100%;
}

.container-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.container-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.tags-list {
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-button {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.action-button.edit {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border: 1px solid rgba(var(--primary-rgb), 0.2);
}

.action-button.edit:hover {
  background-color: rgba(var(--primary-rgb), 0.2);
}

.action-button.delete {
  background-color: rgba(var(--accent-rgb), 0.1);
  color: var(--error-color);
  border: 1px solid rgba(var(--accent-rgb), 0.2);
}

.action-button.delete:hover {
  background-color: rgba(var(--accent-rgb), 0.2);
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
}

.empty-state p {
  margin-bottom: 20px;
}

.dialog-overlay {
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
}

.dialog {
  width: 400px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  background-color: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: var(--card-shadow);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 10px 20px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.dialog-content {
  padding: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 10px 20px 20px 20px;
  border-top: 1px solid var(--border-color);
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-tertiary);
  transition: color 0.3s ease;
}

.close-button:hover {
  color: var(--text-primary);
}

.success-message {
  background-color: rgba(var(--success-color), 0.1);
  color: var(--success-color);
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid rgba(var(--success-color), 0.2);
  border-left: 4px solid var(--success-color);
}

.error-message {
  background-color: rgba(var(--error-color), 0.1);
  color: var(--error-color);
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid rgba(var(--error-color), 0.2);
  border-left: 4px solid var(--error-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-button {
  background: none;
  border: none;
  color: var(--error-color);
  text-decoration: underline;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.retry-button:hover {
  opacity: 0.8;
}

/* 表单样式 */
.admin-form-group {
  margin-bottom: 15px;
}

.admin-form-group label {
  display: block;
  margin-bottom: 5px;
  color: var(--text-secondary);
  font-weight: 500;
}

.admin-form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: border-color 0.3s ease;
}

.admin-form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.admin-form-group input::placeholder {
  color: var(--text-tertiary);
}

/* 按钮样式 */
.admin-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-weight: 500;
}

.admin-btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.admin-btn-primary:hover {
  background-color: var(--secondary-color);
}

.admin-btn-secondary {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.admin-btn-secondary:hover {
  background-color: var(--hover-color);
}

.admin-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  border: 3px solid var(--border-color);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .container-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 5px;
  }
  
  .action-button {
    width: 100%;
  }
  
  .dialog {
    width: 95%;
    margin: 10px;
  }
  
  .dialog-footer {
    flex-direction: column;
  }
  
  .admin-btn {
    width: 100%;
  }
}
</style> 