<script setup>
import { ref, onMounted } from 'vue'
import { tagApi } from '../../services/api'

// 标签列表
const tags = ref([])

// 加载状态
const isLoading = ref(false)
const isSaving = ref(false)
const error = ref(null)
const successMessage = ref('')

// 对话框状态
const showDialog = ref(false)
const dialogMode = ref('add') // 'add' 或 'edit'
const editingTag = ref(null)

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
      successMessage.value = '标签添加成功'
    } else {
      // 更新现有标签
      await tagApi.updateTag(editingTag.value.id, { name: tagForm.value.name })
      successMessage.value = '标签更新成功'
    }
    
    // 重新获取标签列表
    await fetchTags()
    
    // 关闭对话框
    closeDialog()
    
    // 3秒后清除成功消息
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    console.error('保存标签失败:', err)
    error.value = dialogMode.value === 'add' ? '添加标签失败' : '更新标签失败'
  } finally {
    isSaving.value = false
  }
}

// 删除标签
const deleteTag = async (tag) => {
  if (!confirm(`确定要删除标签 "${tag.name}" 吗？这可能会影响使用此标签的文章。`)) {
    return
  }
  
  try {
    isLoading.value = true
    error.value = null
    
    await tagApi.deleteTag(tag.id)
    
    // 重新获取标签列表
    await fetchTags()
    
    successMessage.value = '标签删除成功'
    
    // 3秒后清除成功消息
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
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
      
      <!-- 成功消息 -->
      <div v-if="successMessage" class="success-message" role="status">
        {{ successMessage }}
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
                    @click="deleteTag(tag)" 
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
  background-color: var(--primary-color);
  color: white;
}

.action-button.edit:hover {
  filter: brightness(1.1);
}

.action-button.delete {
  background-color: #f56c6c;
  color: white;
}

.action-button.delete:hover {
  filter: brightness(1.1);
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
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-tertiary);
}

.close-button:hover {
  color: var(--text-primary);
}

.success-message {
  background-color: #f0f9eb;
  color: #67c23a;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border-left: 4px solid #67c23a;
}

.error-message {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border-left: 4px solid #f56c6c;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-button {
  background: none;
  border: none;
  color: #f56c6c;
  text-decoration: underline;
  cursor: pointer;
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
}
</style> 