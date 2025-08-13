<template>
  <div class="admin-container admin-plugins-container">
    <!-- 常规插件管理界面 -->
    <div v-if="!showPluginMarketplace">
      <div class="header-section">
        <h1>插件管理</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="openCreateDialog">添加插件</button>
          <button class="btn btn-secondary" @click="loadExamplePlugin">加载示例插件</button>
          <button class="btn btn-success" @click="loadOpenRouterPlugin">加载AI助手插件</button>
          <button class="btn btn-info" @click="openPluginMarketplace">插件市场</button>
        </div>
      </div>

      <!-- 插件列表 -->
      <div class="plugins-list">
        <table class="plugins-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>描述</th>
              <th>创建时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="plugin in plugins" :key="plugin.id">
              <td>{{ plugin.id }}</td>
              <td>{{ plugin.name }}</td>
              <td>{{ plugin.description }}</td>
              <td>{{ formatDate(plugin.created_at) }}</td>
              <td>
                <span :class="plugin.is_active ? 'status-active' : 'status-inactive'">
                  {{ plugin.is_active ? '已激活' : '未激活' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-sm btn-info" @click="viewPlugin(plugin)">查看</button>
                  <button class="btn btn-sm btn-primary" @click="editPlugin(plugin)">编辑</button>
                  <button 
                    class="btn btn-sm" 
                    :class="plugin.is_active ? 'btn-warning' : 'btn-success'"
                    @click="togglePluginStatus(plugin)">
                    {{ plugin.is_active ? '停用' : '激活' }}
                  </button>
                  <button class="btn btn-sm btn-success" :disabled="!plugin.is_active" @click="runPlugin(plugin)">运行</button>
                  <button class="btn btn-sm btn-danger" @click="openDeleteConfirm(plugin)">删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="plugins.length === 0">
              <td colspan="6" class="no-data">暂无插件数据</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 创建/编辑插件对话框 -->
      <div class="dialog-overlay" v-if="showDialog" @click="closeDialog"></div>
      <div class="dialog" v-if="showDialog">
        <div class="dialog-header">
          <h2>{{ isEditing ? '编辑插件' : '创建插件' }}</h2>
          <button class="btn-close" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <form @submit.prevent="savePlugin">
            <div class="form-group">
              <label for="plugin-name">插件名称</label>
              <input 
                id="plugin-name" 
                v-model="currentPlugin.name" 
                type="text" 
                class="form-control" 
                required
              />
            </div>
            
            <div class="form-group">
              <label for="plugin-description">插件描述</label>
              <textarea 
                id="plugin-description" 
                v-model="currentPlugin.description" 
                class="form-control"
                rows="2"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="plugin-code">插件代码</label>
              <textarea 
                id="plugin-code" 
                v-model="currentPlugin.code" 
                class="form-control code-editor"
                rows="15"
                required
              ></textarea>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeDialog">取消</button>
              <button type="submit" class="btn btn-primary">保存</button>
            </div>
          </form>
        </div>
      </div>

      <!-- 查看插件对话框 -->
      <div class="dialog-overlay" v-if="showViewDialog" @click="closeViewDialog"></div>
      <div class="dialog" v-if="showViewDialog">
        <div class="dialog-header">
          <h2>{{ currentPlugin.name }}</h2>
          <button class="btn-close" @click="closeViewDialog">×</button>
        </div>
        <div class="dialog-body">
          <div class="plugin-details">
            <p><strong>描述：</strong>{{ currentPlugin.description || '无' }}</p>
            <p><strong>状态：</strong>{{ currentPlugin.is_active ? '已激活' : '未激活' }}</p>
            <p><strong>创建时间：</strong>{{ formatDate(currentPlugin.created_at) }}</p>
            <p><strong>更新时间：</strong>{{ formatDate(currentPlugin.updated_at) }}</p>
            
            <div class="code-container">
              <h3>插件代码：</h3>
              <pre><code>{{ currentPlugin.code }}</code></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 运行插件结果对话框 -->
      <div class="dialog-overlay" v-if="showRunResultDialog" @click="closeRunResultDialog"></div>
      <div class="dialog" v-if="showRunResultDialog">
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

<script>
import { pluginApi } from '../../services/api'
import { ref, onMounted, defineAsyncComponent } from 'vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'

export default {
  name: 'AdminPlugins',
  components: {
    AdminPluginMarketplace: defineAsyncComponent(() => import('./AdminPluginMarketplace.vue')),
    ConfirmDialog
  },
  setup() {
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
        console.log('切换插件状态:', plugin.id)
        await pluginApi.activatePlugin(plugin.id, !plugin.is_active)
        console.log('插件状态切换成功')
        loadPlugins()
      } catch (error) {
        console.error('切换插件状态失败:', error)
        toast.error('切换插件状态失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 运行插件
    const runPlugin = async (plugin) => {
      try {
        console.log('运行插件:', plugin.id)
        const result = await pluginApi.runPlugin(plugin.id)
        console.log('插件运行结果:', result)
        
        // 格式化结果
        runResult.value = typeof result.output === 'object' 
          ? JSON.stringify(result.output, null, 2) 
          : (result.output || '插件执行成功，但没有返回数据')
        
        // 显示结果对话框
        currentPlugin.value = plugin
        showRunResultDialog.value = true
      } catch (error) {
        console.error('运行插件失败:', error)
        toast.error('运行插件失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 加载示例插件
    const loadExamplePlugin = async () => {
      try {
        console.log('获取示例插件列表')
        const examples = await pluginApi.getExamplePlugins()
        console.log('示例插件:', examples)
        
        // 如果没有示例插件，提示用户
        if (!examples || examples.length === 0) {
          toast.warning('没有可用的示例插件')
          return
        }
        
        // 提示用户选择示例插件
        let message = '可用的示例插件:\n\n'
        examples.forEach((example, index) => {
          message += `${index + 1}. ${example.name} - ${example.description}\n`
        })
        message += '\n请输入要加载的示例插件编号:'
        
        const selection = prompt(message)
        if (!selection) return
        
        // 验证用户输入
        const index = parseInt(selection) - 1
        if (isNaN(index) || index < 0 || index >= examples.length) {
          toast.error('无效的选择')
          return
        }
        
        // 获取选择的示例
        const selectedExample = examples[index]
        console.log('加载示例:', selectedExample.name)
        
        // 获取示例插件详情
        const exampleDetail = await pluginApi.getExamplePlugin(selectedExample.name)
        console.log('示例详情:', exampleDetail)
        
        // 创建插件
        currentPlugin.value = {
          name: exampleDetail.name,
          description: exampleDetail.description,
          code: exampleDetail.code,
          is_active: false
        }
        
        // 确认创建
        if (confirm(`是否创建示例插件 "${exampleDetail.name}"？`)) {
          await pluginApi.createPlugin(currentPlugin.value)
          console.log('示例插件创建成功')
          loadPlugins()
        }
      } catch (error) {
        console.error('加载示例插件失败:', error)
        toast.error('加载示例插件失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 加载 OpenRouter 插件
    const loadOpenRouterPlugin = async () => {
      try {
        const openRouterPlugin = await pluginApi.getExamplePlugin("openrouter_llm")
        
        if (!openRouterPlugin || !openRouterPlugin.code) {
          toast.error("找不到 OpenRouter 插件示例")
          return
        }
        
        currentPlugin.value = {
          name: "OpenRouter LLM API",
          description: "集成 OpenRouter API 提供 AI 大语言模型访问功能",
          code: openRouterPlugin.code,
          is_active: false
        }
        
        if (confirm("是否创建 OpenRouter LLM API 插件？\n\n此插件将允许您在博客中集成多种 AI 大语言模型。")) {
          await pluginApi.createPlugin(currentPlugin.value)
          toast.success("OpenRouter 插件创建成功！请配置您的 API Key，然后激活插件。")
          loadPlugins()
        }
      } catch (error) {
        console.error('加载 OpenRouter 插件失败:', error)
        toast.error('加载 OpenRouter 插件失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 插件市场相关
    const openPluginMarketplace = () => {
      showPluginMarketplace.value = true
    }
    
    const closePluginMarketplace = () => {
      showPluginMarketplace.value = false
    }
    
    const handlePluginInstalled = () => {
      // 关闭插件市场视图
      showPluginMarketplace.value = false
      // 重新加载插件列表
      loadPlugins()
      // 显示成功提示
      toast.success('插件已成功安装！')
    }

    onMounted(() => {
      loadPlugins()
    })

    return {
      plugins,
      currentPlugin,
      showDialog,
      showViewDialog,
      showRunResultDialog,
      isEditing,
      runResult,
      showPluginMarketplace,
      confirmDialogVisible,
      pluginToDelete,
      loadPlugins,
      formatDate,
      openCreateDialog,
      editPlugin,
      viewPlugin,
      closeDialog,
      closeViewDialog,
      closeRunResultDialog,
      savePlugin,
      openDeleteConfirm,
      closeDeleteConfirm,
      deletePlugin,
      togglePluginStatus,
      runPlugin,
      loadExamplePlugin,
      loadOpenRouterPlugin,
      openPluginMarketplace,
      closePluginMarketplace,
      handlePluginInstalled
    }
  }
}
</script>

<style scoped>
.admin-plugins-container {
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.plugins-list {
  margin-top: 20px;
  overflow-x: auto;
}

.plugins-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--card-bg-color);
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.plugins-table th,
.plugins-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.plugins-table th {
  background-color: var(--table-header-bg);
  font-weight: 600;
  color: var(--text-color);
}

.plugins-table tr:last-child td {
  border-bottom: none;
}

.plugins-table tr:hover {
  background-color: var(--hover-color);
}

.status-active {
  color: var(--success-color);
  font-weight: 500;
}

.status-inactive {
  color: var(--error-color);
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.action-buttons .btn {
  padding: 4px 8px;
  font-size: 0.8rem;
}

.no-data {
  text-align: center;
  padding: 15px;
  color: var(--text-tertiary);
  font-style: italic;
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
}

.dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: var(--card-bg-color);
  border-radius: 5px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  z-index: 1001;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--title-color);
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-color);
}

.dialog-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-color);
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  background-color: var(--input-bg-color);
  color: var(--text-color);
}

.code-editor {
  font-family: monospace;
  white-space: pre;
  min-height: 300px;
  line-height: 1.5;
  tab-size: 2;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 插件详情样式 */
.plugin-details p {
  margin: 10px 0;
  line-height: 1.6;
}

.code-container {
  margin-top: 20px;
}

.code-container h3 {
  margin-bottom: 10px;
}

.code-container pre {
  background-color: var(--code-bg-color);
  padding: 15px;
  border-radius: 5px;
  overflow: auto;
  font-family: monospace;
  line-height: 1.5;
  color: var(--code-text-color);
  max-height: 400px;
}

/* 运行结果样式 */
.run-result {
  max-height: 400px;
  overflow: auto;
}

.run-result pre {
  background-color: var(--code-bg-color);
  padding: 15px;
  border-radius: 5px;
  font-family: monospace;
  line-height: 1.5;
  color: var(--code-text-color);
  margin: 0;
  white-space: pre-wrap;
}
</style> 