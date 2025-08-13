<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { userApi } from '../../services/api'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import toast from '../../utils/toast'

const store = useStore()
const users = ref([])
const isLoading = ref(true)
const error = ref(null)
const currentUser = ref(null)

// 删除确认对话框状态
const confirmDialogVisible = ref(false)
const userToDelete = ref(null)

// 重置密码对话框状态
const resetPasswordDialogVisible = ref(false)
const userToReset = ref(null)
const newPassword = ref('')
const isResetting = ref(false)
const resetSuccess = ref(false)
const resetError = ref('')

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
    
    toast.success('用户角色修改成功')
  } catch (err) {
    console.error('修改用户角色失败:', err)
    toast.error('修改用户角色失败')
  }
}

// 打开删除确认对话框
const openDeleteConfirm = (user) => {
  if (user.id === currentUser.value?.id) {
    toast.error('不能删除自己的账号')
    return
  }
  userToDelete.value = user
  confirmDialogVisible.value = true
}

// 关闭删除确认对话框
const closeDeleteConfirm = () => {
  confirmDialogVisible.value = false
  userToDelete.value = null
}

// 删除用户
const deleteUser = async () => {
  if (!userToDelete.value) return
  
  try {
    await userApi.deleteUser(userToDelete.value.id)
    
    // 从列表中移除已删除的用户
    users.value = users.value.filter(user => user.id !== userToDelete.value.id)
    
    // 关闭对话框
    closeDeleteConfirm()
    
    toast.success('用户删除成功')
  } catch (err) {
    console.error('删除用户失败:', err)
    toast.error('删除用户失败')
  }
}

// 打开重置密码对话框
const openResetPassword = (user) => {
  userToReset.value = user
  newPassword.value = generateRandomPassword()
  resetPasswordDialogVisible.value = true
  resetSuccess.value = false
  resetError.value = ''
}

// 关闭重置密码对话框
const closeResetPasswordDialog = () => {
  resetPasswordDialogVisible.value = false
  userToReset.value = null
  newPassword.value = ''
  isResetting.value = false
  resetSuccess.value = false
  resetError.value = ''
}

// 重置用户密码
const resetUserPassword = async () => {
  if (!userToReset.value) return
  
  try {
    isResetting.value = true
    resetError.value = ''
    
    await userApi.resetUserPassword(userToReset.value.id, newPassword.value)
    resetSuccess.value = true
  } catch (err) {
    console.error('重置密码失败:', err)
    resetError.value = '重置密码失败，请重试'
    resetSuccess.value = false
  } finally {
    isResetting.value = false
  }
}

// 生成随机密码
const generateRandomPassword = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789'
  let password = ''
  for (let i = 0; i < 10; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return password
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

// 复制到剪贴板
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    toast.success('密码已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
    toast.error('复制失败，请手动复制')
  }
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
                @click="openResetPassword(user)" 
                class="action-button reset"
                title="重置密码"
              >
                重置密码
              </button>
              <button 
                v-if="user.id !== currentUser?.id"
                @click="openDeleteConfirm(user)" 
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
    
    <!-- 删除确认对话框 -->
    <ConfirmDialog 
      :visible="confirmDialogVisible"
      title="确认删除"
      :message="userToDelete ? `您确定要删除这个用户吗？此操作不可恢复。` : ''"
      confirmText="确认删除"
      cancelText="取消"
      @confirm="deleteUser"
      @cancel="closeDeleteConfirm"
    />
    
    <!-- 重置密码对话框 -->
    <div v-if="resetPasswordDialogVisible" class="modal-overlay" @click.self="closeResetPasswordDialog">
      <div class="reset-password-dialog" @click.stop>
        <h3>重置用户密码</h3>
        <p v-if="userToReset">您正在重置用户 <strong>{{ userToReset.username }}</strong> 的密码</p>
        
        <div v-if="resetSuccess" class="success-message">
          <p>密码重置成功！新密码为：</p>
          <div class="password-display">
            <span>{{ newPassword }}</span>
            <button @click="copyToClipboard(newPassword)" class="copy-button">复制</button>
          </div>
          <p class="tip">请将此密码安全地传递给用户。</p>
        </div>
        
        <div v-else class="password-form">
          <div class="form-group">
            <label for="new-password">新密码</label>
            <div class="password-input-group">
              <input 
                id="new-password" 
                v-model="newPassword" 
                type="text" 
                class="password-input"
                :disabled="isResetting"
              />
              <button 
                @click="newPassword = generateRandomPassword()" 
                class="regenerate-button"
                :disabled="isResetting"
              >
                重新生成
              </button>
            </div>
          </div>
          
          <div v-if="resetError" class="error-message">{{ resetError }}</div>
        </div>
        
        <div class="dialog-actions">
          <button 
            v-if="!resetSuccess"
            @click="resetUserPassword" 
            class="dialog-button reset-button"
            :disabled="isResetting || !newPassword"
          >
            {{ isResetting ? '重置中...' : '确认重置' }}
          </button>
          <button 
            @click="closeResetPasswordDialog" 
            class="dialog-button cancel-button"
          >
            {{ resetSuccess ? '关闭' : '取消' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 基础样式 */
.admin-users {
  width: 100%;
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

.users-table-container {
  overflow-x: auto;
  background-color: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: var(--card-shadow);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th, .users-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.users-table th {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  font-weight: 500;
}

.users-table tbody tr:hover {
  background-color: var(--hover-color);
}

.role-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.role-badge.admin {
  background-color: var(--primary-color);
  color: white;
}

.role-badge.user {
  background-color: var(--success-color);
  color: white;
}

.actions-cell {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.role-select {
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: border-color 0.3s ease;
}

.role-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.action-button {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.action-button.delete {
  background-color: rgba(var(--accent-rgb), 0.1);
  color: var(--error-color);
  border: 1px solid rgba(var(--accent-rgb), 0.2);
}

.action-button.delete:hover {
  background-color: rgba(var(--accent-rgb), 0.2);
}

.action-button.reset {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border: 1px solid rgba(var(--primary-rgb), 0.2);
}

.action-button.reset:hover {
  background-color: rgba(var(--primary-rgb), 0.2);
}

.current-user-badge {
  background-color: var(--text-tertiary);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.empty-message {
  text-align: center;
  color: var(--text-tertiary);
  padding: 20px 0;
}

/* 重置密码对话框样式 */
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

.reset-password-dialog {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slide-up 0.3s ease;
  border: 1px solid var(--border-color);
}

.reset-password-dialog h3 {
  color: var(--text-primary);
  margin-top: 0;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: var(--text-secondary);
}

.password-input-group {
  display: flex;
  gap: 10px;
}

.password-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-family: monospace;
  font-size: 1rem;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: border-color 0.3s ease;
}

.password-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.regenerate-button {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border: 1px solid rgba(var(--primary-rgb), 0.2);
  border-radius: 4px;
  padding: 0 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.regenerate-button:hover {
  background-color: rgba(var(--primary-rgb), 0.2);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.dialog-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.reset-button {
  background-color: var(--primary-color);
  color: white;
}

.reset-button:hover {
  background-color: var(--secondary-color);
}

.cancel-button {
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.cancel-button:hover {
  background-color: var(--hover-color);
}

.success-message {
  background-color: rgba(var(--success-color), 0.1);
  color: var(--success-color);
  padding: 15px;
  border-radius: 4px;
  margin: 15px 0;
  border: 1px solid rgba(var(--success-color), 0.2);
}

.error-message {
  background-color: rgba(var(--error-color), 0.1);
  color: var(--error-color);
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
  border: 1px solid rgba(var(--error-color), 0.2);
}

.password-display {
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  padding: 10px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}

.password-display span {
  font-family: monospace;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.copy-button {
  background-color: var(--success-color);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.copy-button:hover {
  filter: brightness(1.1);
}

.tip {
  font-size: 0.9rem;
  margin: 10px 0 0 0;
  color: var(--text-tertiary);
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style> 