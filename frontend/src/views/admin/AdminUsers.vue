<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { userApi } from '../../services/api'

const store = useStore()
const users = ref([])
const isLoading = ref(true)
const error = ref(null)
const currentUser = ref(null)

// 获取所有用户
const fetchUsers = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // 先获取当前用户
    currentUser.value = store.getters.currentUser
    
    // 调用API获取所有用户
    const response = await userApi.getUsers()
    
    users.value = response || []
    console.log('获取到的用户列表:', users.value)
  } catch (err) {
    console.error('获取用户列表失败:', err)
    error.value = '获取用户列表失败，可能是权限不足'
  } finally {
    isLoading.value = false
  }
}

// 修改用户角色
const changeUserRole = async (userId, newRole) => {
  try {
    await userApi.updateUser(userId, { role: newRole })
    
    // 更新本地用户列表
    const userIndex = users.value.findIndex(user => user.id === userId)
    if (userIndex !== -1) {
      users.value[userIndex].role = newRole
    }
  } catch (err) {
    console.error('修改用户角色失败:', err)
    alert('修改用户角色失败')
  }
}

// 删除用户
const deleteUser = async (userId) => {
  if (userId === currentUser.value?.id) {
    alert('不能删除自己的账号')
    return
  }
  
  if (!confirm('确定要删除这个用户吗？此操作不可恢复。')) {
    return
  }
  
  try {
    await userApi.deleteUser(userId)
    
    // 从列表中移除已删除的用户
    users.value = users.value.filter(user => user.id !== userId)
  } catch (err) {
    console.error('删除用户失败:', err)
    alert('删除用户失败')
  }
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

onMounted(fetchUsers)
</script>

<template>
  <div class="admin-users">
    <div class="page-header">
      <h2>用户管理</h2>
    </div>
    
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchUsers" class="retry-button">重试</button>
    </div>
    
    <div v-else class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>注册日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span :class="['role-badge', user.role]">
                {{ user.role === 'admin' ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td class="actions-cell">
              <select 
                v-if="user.id !== currentUser?.id"
                :value="user.role"
                @change="changeUserRole(user.id, $event.target.value)"
                class="role-select"
              >
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
              <button 
                v-if="user.id !== currentUser?.id"
                @click="deleteUser(user.id)" 
                class="action-button delete"
              >
                删除
              </button>
              <span v-else class="current-user-badge">当前用户</span>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="empty-message">暂无用户</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.admin-users {
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

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th, .users-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.users-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.role-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.role-badge.admin {
  background-color: #4c84ff;
  color: white;
}

.role-badge.user {
  background-color: #67c23a;
  color: white;
}

.actions-cell {
  display: flex;
  gap: 10px;
  align-items: center;
}

.role-select {
  padding: 4px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: white;
  color: #606266;
}

.action-button {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.action-button.delete {
  background-color: #fef0f0;
  color: #f56c6c;
}

.current-user-badge {
  background-color: #909399;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.empty-message {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}
</style> 