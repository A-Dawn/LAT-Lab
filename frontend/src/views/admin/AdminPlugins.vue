<template>
  <div class="admin-plugins">
    <div v-if="!showPluginMarketplace">
      <div class="container-header">
        <h2>插件管理</h2>
        <div class="action-buttons">
          <button @click="openCreateDialog" class="admin-btn admin-btn-primary">
            <i class="icon-plus"></i>
            创建插件
          </button>
          <button @click="openPluginMarketplace" class="admin-btn admin-btn-secondary">
            <i class="icon-download"></i>
            插件市场
          </button>
        </div>
      </div>

      <!-- 插件列表 -->
      <div class="plugins-list">
        <div v-if="plugins.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <h3>暂无插件</h3>
          <p>创建您的第一个插件或从插件市场安装</p>
          <button @click="openCreateDialog" class="admin-btn admin-btn-primary">
            创建插件
          </button>
        </div>
        
        <div v-else class="plugins-grid">
          <div 
            v-for="plugin in plugins" 
            :key="plugin.id" 
            class="plugin-card"
            :class="{ 'inactive': !plugin.is_active }"
          >
            <div class="plugin-header">
              <h3 class="plugin-name">{{ plugin.name }}</h3>
              <div class="plugin-status">
                <span 
                  :class="['status-badge', plugin.is_active ? 'active' : 'inactive']"
                >
                  {{ plugin.is_active ? '启用' : '禁用' }}
                </span>
              </div>
            </div>
            
            <p class="plugin-description">{{ plugin.description || '暂无描述' }}</p>
            
            <div class="plugin-meta">
              <span class="meta-item">
                <i class="icon-calendar"></i>
                {{ formatDate(plugin.created_at) }}
              </span>
              <span v-if="plugin.updated_at" class="meta-item">
                <i class="icon-edit"></i>
                {{ formatDate(plugin.updated_at) }}
              </span>
            </div>
            
            <div class="plugin-actions">
              <button 
                @click="viewPlugin(plugin)" 
                class="action-button view"
                title="查看插件"
              >
                <i class="icon-eye"></i>
                查看
              </button>
              <button 
                @click="editPlugin(plugin)" 
                class="action-button edit"
                title="编辑插件"
              >
                <i class="icon-edit"></i>
                编辑
              </button>
              <button 
                @click="togglePluginStatus(plugin)" 
                :class="['action-button', plugin.is_active ? 'deactivate' : 'activate']"
                :title="plugin.is_active ? '禁用插件' : '启用插件'"
              >
                <i :class="plugin.is_active ? 'icon-pause' : 'icon-play'"></i>
                {{ plugin.is_active ? '禁用' : '启用' }}
              </button>
              <button 
                @click="runPlugin(plugin)" 
                class="action-button run"
                title="运行插件"
              >
                <i class="icon-play"></i>
                运行
              </button>
              <button 
                @click="openDeleteConfirm(plugin)" 
                class="action-button delete"
                title="删除插件"
              >
                <i class="icon-trash"></i>
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 创建/编辑插件对话框 -->
      <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
        <div class="dialog" @click.stop>
          <div class="dialog-header">
            <h2>{{ isEditing ? '编辑插件' : '创建插件' }}</h2>
            <button class="btn-close" @click="closeDialog">×</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label for="plugin-name">插件名称</label>
              <input 
                id="plugin-name"
                v-model="currentPlugin.name" 
                type="text" 
                placeholder="输入插件名称"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="plugin-description">插件描述</label>
              <textarea 
                id="plugin-description"
                v-model="currentPlugin.description" 
                placeholder="输入插件描述"
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="plugin-code">插件代码</label>
              <textarea 
                id="plugin-code"
                v-model="currentPlugin.code" 
                placeholder="输入插件代码"
                class="form-textarea code-editor"
                rows="10"
              ></textarea>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  v-model="currentPlugin.is_active" 
                  type="checkbox"
                />
                <span class="checkmark"></span>
                启用插件
              </label>
            </div>
          </div>
          <div class="dialog-footer">
            <button @click="closeDialog" class="admin-btn admin-btn-secondary">
              取消
            </button>
            <button @click="savePlugin" class="admin-btn admin-btn-primary">
              保存
            </button>
          </div>
        </div>
      </div>

      <!-- 查看插件对话框 -->
      <div v-if="showViewDialog" class="dialog-overlay" @click="closeViewDialog">
        <div class="dialog large" @click.stop>
          <div class="dialog-header">
            <h2>查看插件: {{ currentPlugin.name }}</h2>
            <button class="btn-close" @click="closeViewDialog">×</button>
          </div>
          <div class="dialog-body">
            <div class="plugin-info">
              <div class="info-row">
                <label>插件名称:</label>
                <span>{{ currentPlugin.name }}</span>
              </div>
              <div class="info-row">
                <label>插件描述:</label>
                <span>{{ currentPlugin.description || '暂无描述' }}</span>
              </div>
              <div class="info-row">
                <label>插件状态:</label>
                <span :class="['status-badge', currentPlugin.is_active ? 'active' : 'inactive']">
                  {{ currentPlugin.is_active ? '启用' : '禁用' }}
                </span>
              </div>
              <div class="info-row">
                <label>创建时间:</label>
                <span>{{ formatDate(currentPlugin.created_at) }}</span>
              </div>
              <div v-if="currentPlugin.updated_at" class="info-row">
                <label>更新时间:</label>
                <span>{{ formatDate(currentPlugin.updated_at) }}</span>
              </div>
            </div>
            <div class="code-section">
              <label>插件代码:</label>
              <pre><code>{{ currentPlugin.code }}</code></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 运行插件结果对话框 -->
      <div v-if="showRunResultDialog" class="dialog-overlay" @click="closeRunResultDialog">
        <div class="dialog" @click.stop>
          <div class="dialog-header">
            <h2>运行结果: {{ currentPlugin.name }}</h2>
            <button class="btn-close" @click="closeRunResultDialog">×</button>
          </div>
          <div class="dialog-body">
            <div class="run-result">
              <pre><code>{{ runResult }}</code></pre>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 删除确认对话框 -->
      <ConfirmDialog 
        :visible="confirmDialogVisible"
        title="确认删除"
        :message="pluginToDelete ? `确定要删除插件 '${pluginToDelete.name}' 吗？此操作不可恢复。` : ''"
        confirmText="确认删除"
        cancelText="取消"
        @confirm="deletePlugin"
        @cancel="closeDeleteConfirm"
      />
    </div>

    <!-- 插件市场组件 -->
    <AdminPluginMarketplace 
      v-else
      @close="closePluginMarketplace"
      @plugin-installed="handlePluginInstalled"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, defineAsyncComponent } from 'vue'
import { pluginApi } from '../../services/api'
import toast from '../../utils/toast'

// 异步组件
const ConfirmDialog = defineAsyncComponent(() => import('../../components/ConfirmDialog.vue'))
const AdminPluginMarketplace = defineAsyncComponent(() => import('./AdminPluginMarketplace.vue'))

// 响应式数据
const plugins = ref([])
const currentPlugin = ref({
  name: '',
  description: '',
  code: '',
  is_active: false
})
const showDialog = ref(false)
const showViewDialog = ref(false)
const showRunResultDialog = ref(false)
const isEditing = ref(false)
const runResult = ref('')
const showPluginMarketplace = ref(false)

// 删除确认对话框状态
const confirmDialogVisible = ref(false)
const pluginToDelete = ref(null)

// 加载插件列表
const loadPlugins = async () => {
  try {
    console.log('加载插件列表...')
    plugins.value = await pluginApi.getPlugins()
    console.log('获取到插件列表:', plugins.value.length, '个插件')
  } catch (error) {
    console.error('获取插件列表失败:', error)
    toast.error('获取插件列表失败')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 打开创建对话框
const openCreateDialog = () => {
  currentPlugin.value = {
    name: '',
    description: '',
    code: '',
    is_active: false
  }
  isEditing.value = false
  showDialog.value = true
}

// 编辑插件
const editPlugin = (plugin) => {
  currentPlugin.value = { ...plugin }
  isEditing.value = true
  showDialog.value = true
}

// 查看插件
const viewPlugin = (plugin) => {
  currentPlugin.value = { ...plugin }
  showViewDialog.value = true
}

// 关闭对话框
const closeDialog = () => {
  showDialog.value = false
}

// 关闭查看对话框
const closeViewDialog = () => {
  showViewDialog.value = false
}

// 关闭运行结果对话框
const closeRunResultDialog = () => {
  showRunResultDialog.value = false
  runResult.value = ''
}

// 保存插件
const savePlugin = async () => {
  try {
    if (isEditing.value) {
      console.log('更新插件:', currentPlugin.value.id)
      await pluginApi.updatePlugin(currentPlugin.value.id, currentPlugin.value)
      console.log('插件更新成功')
    } else {
      console.log('创建新插件')
      await pluginApi.createPlugin(currentPlugin.value)
      console.log('插件创建成功')
    }
    closeDialog()
    loadPlugins()
  } catch (error) {
    console.error('保存插件失败:', error)
    toast.error('保存插件失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 打开删除确认对话框
const openDeleteConfirm = (plugin) => {
  pluginToDelete.value = plugin
  confirmDialogVisible.value = true
}

// 关闭删除确认对话框
const closeDeleteConfirm = () => {
  confirmDialogVisible.value = false
  pluginToDelete.value = null
}

// 删除插件
const deletePlugin = async () => {
  if (!pluginToDelete.value) return
  
  try {
    console.log('删除插件:', pluginToDelete.value.id)
    await pluginApi.deletePlugin(pluginToDelete.value.id)
    console.log('插件删除成功')
    loadPlugins()
    
    // 关闭对话框
    closeDeleteConfirm()
  } catch (error) {
    console.error('删除插件失败:', error)
    toast.error('删除插件失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 切换插件状态
const togglePluginStatus = async (plugin) => {
  try {
    const newStatus = !plugin.is_active
    await pluginApi.updatePlugin(plugin.id, { is_active: newStatus })
    plugin.is_active = newStatus
    toast.success(`插件已${newStatus ? '启用' : '禁用'}`)
  } catch (error) {
    console.error('切换插件状态失败:', error)
    toast.error('切换插件状态失败')
  }
}

// 运行插件
const runPlugin = async (plugin) => {
  try {
    console.log('运行插件:', plugin.name)
    const result = await pluginApi.runPlugin(plugin.id)
    runResult.value = result.output || '插件执行完成，无输出'
    currentPlugin.value = plugin
    showRunResultDialog.value = true
  } catch (error) {
    console.error('运行插件失败:', error)
    toast.error('运行插件失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 打开插件市场
const openPluginMarketplace = () => {
  showPluginMarketplace.value = true
}

// 关闭插件市场
const closePluginMarketplace = () => {
  showPluginMarketplace.value = false
}

// 处理插件安装
const handlePluginInstalled = () => {
  closePluginMarketplace()
  loadPlugins()
  toast.success('插件安装成功')
}

// 组件挂载时加载插件列表
onMounted(() => {
  loadPlugins()
})
</script>

<style scoped>
.admin-plugins {
  padding: 20px;
  height: 100%;
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
  font-size: 1.8rem;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.admin-btn {
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
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
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.admin-btn-secondary:hover {
  background-color: var(--bg-hover);
}

/* 插件列表样式 */
.plugins-list {
  margin-top: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0 0 20px 0;
  color: var(--text-tertiary);
}

.plugins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.plugin-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--card-shadow);
  transition: all 0.3s;
}

.plugin-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.plugin-card.inactive {
  opacity: 0.7;
}

.plugin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.plugin-name {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  flex: 1;
}

.plugin-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: rgba(var(--success-rgb), 0.1);
  color: var(--success-color);
}

.status-badge.inactive {
  background-color: rgba(var(--error-rgb), 0.1);
  color: var(--error-color);
}

.plugin-description {
  color: var(--text-secondary);
  margin: 0 0 15px 0;
  line-height: 1.5;
}

.plugin-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-tertiary);
  font-size: 0.85rem;
}

.plugin-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-button {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-button.view {
  background-color: rgba(var(--info-rgb), 0.1);
  color: var(--info-color);
}

.action-button.view:hover {
  background-color: rgba(var(--info-rgb), 0.2);
}

.action-button.edit {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
}

.action-button.edit:hover {
  background-color: rgba(var(--primary-rgb), 0.2);
}

.action-button.activate {
  background-color: rgba(var(--success-rgb), 0.1);
  color: var(--success-color);
}

.action-button.activate:hover {
  background-color: rgba(var(--success-rgb), 0.2);
}

.action-button.deactivate {
  background-color: rgba(var(--warning-rgb), 0.1);
  color: var(--warning-color);
}

.action-button.deactivate:hover {
  background-color: rgba(var(--warning-rgb), 0.2);
}

.action-button.run {
  background-color: rgba(var(--accent-rgb), 0.1);
  color: var(--accent-color);
}

.action-button.run:hover {
  background-color: rgba(var(--accent-rgb), 0.2);
}

.action-button.delete {
  background-color: rgba(var(--error-rgb), 0.1);
  color: var(--error-color);
}

.action-button.delete:hover {
  background-color: rgba(var(--error-rgb), 0.2);
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog {
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog.large {
  max-width: 800px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-close:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: var(--input-bg);
  color: var(--text-primary);
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-textarea.code-editor {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  tab-size: 2;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* 插件信息样式 */
.plugin-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
}

.info-row label {
  font-weight: 500;
  color: var(--text-primary);
  min-width: 100px;
  margin-right: 15px;
}

.info-row span {
  color: var(--text-secondary);
}

.code-section {
  margin-top: 20px;
}

.code-section label {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
  color: var(--text-primary);
}

.code-section pre {
  background-color: var(--code-bg);
  padding: 15px;
  border-radius: 6px;
  overflow: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.5;
  color: var(--code-text);
  max-height: 400px;
  margin: 0;
}

/* 运行结果样式 */
.run-result {
  max-height: 400px;
  overflow: auto;
}

.run-result pre {
  background-color: var(--code-bg);
  padding: 15px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.5;
  color: var(--code-text);
  margin: 0;
  white-space: pre-wrap;
}

/* 图标样式 */
.icon-plus::before { content: "➕"; }
.icon-download::before { content: "⬇️"; }
.icon-eye::before { content: "👁️"; }
.icon-edit::before { content: "✏️"; }
.icon-play::before { content: "▶️"; }
.icon-pause::before { content: "⏸️"; }
.icon-trash::before { content: "🗑️"; }
.icon-calendar::before { content: "📅"; }
.icon-edit::before { content: "✏️"; }

/* 响应式设计 */
@media (max-width: 768px) {
  .container-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .plugins-grid {
    grid-template-columns: 1fr;
  }
  
  .plugin-actions {
    justify-content: center;
  }
  
  .dialog {
    width: 95%;
    margin: 10px;
  }
}
</style> 