<script setup>
import { ref, onMounted } from 'vue'
import { categoryApi } from '../../services/api'

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
    alert('请输入分类名称')
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
  } catch (err) {
    console.error('创建分类失败:', err)
    alert('创建分类失败')
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
    alert('请输入分类名称')
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
  } catch (err) {
    console.error('更新分类失败:', err)
    alert('更新分类失败')
  }
}

// 删除分类
const deleteCategory = async (id) => {
  if (!confirm('确定要删除这个分类吗？此操作不可恢复。')) {
    return
  }
  
  try {
    await categoryApi.deleteCategory(id)
    
    // 从列表中移除
    categories.value = categories.value.filter(c => c.id !== id)
  } catch (err) {
    console.error('删除分类失败:', err)
    alert('删除分类失败')
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
                <button @click="deleteCategory(category.id)" class="action-button delete">
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
  color: #303133;
}

.create-category-form {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.create-category-form h3 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: #303133;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.create-button {
  background-color: #4c84ff;
  color: white;
  border: none;
  padding: 0 16px;
  border-radius: 4px;
  cursor: pointer;
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
  border-top-color: #4c84ff;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.retry-button {
  background-color: #4c84ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.categories-table-container {
  overflow-x: auto;
}

.categories-table {
  width: 100%;
  border-collapse: collapse;
}

.categories-table th, .categories-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.categories-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.edit-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
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
}

.action-button.edit {
  background-color: #f0f9eb;
  color: #67c23a;
}

.action-button.delete {
  background-color: #fef0f0;
  color: #f56c6c;
}

.action-button.save {
  background-color: #ecf5ff;
  color: #4c84ff;
}

.action-button.cancel {
  background-color: #f4f4f5;
  color: #909399;
}

.empty-message {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}
</style> 