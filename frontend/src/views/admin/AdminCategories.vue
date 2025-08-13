<script setup>
import { ref, onMounted } from 'vue'
import { categoryApi } from '../../services/api'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import toast from '../../utils/toast'

const categories = ref([])
const isLoading = ref(true)
const error = ref(null)

// 新分类表单
const newCategory = ref({
  name: '',
  description: ''
})

// 编辑模式
const editingCategory = ref(null)
const editForm = ref({
  name: '',
  description: ''
})

// 删除确认对话框状态
const confirmDialogVisible = ref(false)
const categoryToDelete = ref(null)

// 获取所有分类
const fetchCategories = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await categoryApi.getCategories()
    categories.value = response || []
  } catch (err) {
    console.error('获取分类列表失败:', err)
    error.value = '获取分类列表失败'
  } finally {
    isLoading.value = false
  }
}

// 创建分类
const createCategory = async () => {
  if (!newCategory.value.name) {
    toast.warning('请输入分类名称')
    return
  }
  
  try {
    const response = await categoryApi.createCategory(newCategory.value)
    
    // 添加到列表
    categories.value.push(response)
    
    // 清空表单
    newCategory.value = {
      name: '',
      description: ''
    }
    
    toast.success('分类创建成功')
  } catch (err) {
    console.error('创建分类失败:', err)
    toast.error('创建分类失败')
  }
}

// 开始编辑分类
const startEdit = (category) => {
  editingCategory.value = category
  editForm.value = {
    name: category.name,
    description: category.description || ''
  }
}

// 取消编辑
const cancelEdit = () => {
  editingCategory.value = null
}

// 保存编辑
const saveEdit = async () => {
  if (!editForm.value.name) {
    toast.warning('请输入分类名称')
    return
  }
  
  try {
    const response = await categoryApi.updateCategory(editingCategory.value.id, editForm.value)
    
    // 更新列表中的分类
    const index = categories.value.findIndex(c => c.id === editingCategory.value.id)
    if (index !== -1) {
      categories.value[index] = response
    }
    
    // 退出编辑模式
    editingCategory.value = null
    
    toast.success('分类更新成功')
  } catch (err) {
    console.error('更新分类失败:', err)
    toast.error('更新分类失败')
  }
}

// 打开删除确认对话框
const openDeleteConfirm = (category) => {
  categoryToDelete.value = category
  confirmDialogVisible.value = true
}

// 关闭删除确认对话框
const closeDeleteConfirm = () => {
  confirmDialogVisible.value = false
  categoryToDelete.value = null
}

// 删除分类
const deleteCategory = async () => {
  if (!categoryToDelete.value) return
  
  try {
    await categoryApi.deleteCategory(categoryToDelete.value.id)
    
    // 从列表中移除
    categories.value = categories.value.filter(c => c.id !== categoryToDelete.value.id)
    
    // 关闭对话框
    closeDeleteConfirm()
    
    toast.success('分类删除成功')
  } catch (err) {
    console.error('删除分类失败:', err)
    toast.error('删除分类失败')
  }
}

onMounted(fetchCategories)
</script>

<template>
  <div class="admin-categories">
    <div class="page-header">
      <h2>分类管理</h2>
    </div>
    
    <div class="create-category-form">
      <h3>创建新分类</h3>
      <div class="form-row">
        <input 
          v-model="newCategory.name"
          type="text"
          placeholder="分类名称"
          class="form-input"
        />
        <input 
          v-model="newCategory.description"
          type="text"
          placeholder="分类描述（可选）"
          class="form-input"
        />
        <button @click="createCategory" class="create-button">
          创建
        </button>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchCategories" class="retry-button">重试</button>
    </div>
    
    <div v-else class="categories-table-container">
      <table class="categories-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>描述</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="category in categories" :key="category.id">
            <!-- 正常显示模式 -->
            <template v-if="editingCategory?.id !== category.id">
              <td>{{ category.id }}</td>
              <td>{{ category.name }}</td>
              <td>{{ category.description || '-' }}</td>
              <td class="actions-cell">
                <button @click="startEdit(category)" class="action-button edit">
                  编辑
                </button>
                <button @click="openDeleteConfirm(category)" class="action-button delete">
                  删除
                </button>
              </td>
            </template>
            
            <!-- 编辑模式 -->
            <template v-else>
              <td>{{ category.id }}</td>
              <td>
                <input 
                  v-model="editForm.name"
                  type="text"
                  class="edit-input"
                />
              </td>
              <td>
                <input 
                  v-model="editForm.description"
                  type="text"
                  class="edit-input"
                />
              </td>
              <td class="actions-cell">
                <button @click="saveEdit" class="action-button save">
                  保存
                </button>
                <button @click="cancelEdit" class="action-button cancel">
                  取消
                </button>
              </td>
            </template>
          </tr>
          <tr v-if="categories.length === 0">
            <td colspan="4" class="empty-message">暂无分类</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 删除确认对话框 -->
    <ConfirmDialog 
      :visible="confirmDialogVisible"
      title="确认删除"
      :message="categoryToDelete ? `您确定要删除这个分类吗？此操作不可恢复。` : ''"
      confirmText="确认删除"
      cancelText="取消"
      @confirm="deleteCategory"
      @cancel="closeDeleteConfirm"
    />
  </div>
</template>

<style scoped>
.admin-categories {
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

.create-category-form {
  background-color: var(--card-bg);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--card-shadow);
}

.create-category-form h3 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: var(--text-primary);
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

.create-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.create-button:hover {
  background-color: var(--secondary-color);
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

.categories-table-container {
  overflow-x: auto;
  background-color: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: var(--card-shadow);
}

.categories-table {
  width: 100%;
  border-collapse: collapse;
}

.categories-table th, .categories-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.categories-table th {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  font-weight: 500;
}

.categories-table tbody tr:hover {
  background-color: var(--hover-color);
}

.edit-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: border-color 0.3s ease;
}

.edit-input:focus {
  outline: none;
  border-color: var(--primary-color);
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

.action-button.save {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border: 1px solid rgba(var(--primary-rgb), 0.2);
}

.action-button.save:hover {
  background-color: rgba(var(--primary-rgb), 0.2);
}

.action-button.cancel {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.action-button.cancel:hover {
  background-color: var(--hover-color);
}

.empty-message {
  text-align: center;
  color: var(--text-tertiary);
  padding: 20px 0;
}
</style> 