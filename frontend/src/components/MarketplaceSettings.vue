<template>
  <div class="marketplace-settings">
    <h2>插件市场设置</h2>
    
    <div class="card">
      <h3>当前数据源设置</h3>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else>
        <p><strong>数据源类型:</strong> {{ currentSettings.source === 'local' ? '本地文件' : 'Git仓库' }}</p>
        <p v-if="currentSettings.source === 'local'">
          <strong>本地路径:</strong> {{ currentSettings.local_path }}
        </p>
        <p v-else-if="currentSettings.source === 'git'">
          <strong>Git仓库地址:</strong> {{ currentSettings.git_repo }}
        </p>
      </div>
    </div>
    
    <div class="card">
      <h3>更新数据源设置</h3>
      <div v-if="message" :class="['alert', `alert-${messageType}`]">
        {{ message }}
      </div>
      
      <form @submit.prevent="updateSettings">
        <div class="form-group">
          <label for="source">数据源类型:</label>
          <select id="source" v-model="form.source" class="form-control">
            <option value="local">本地文件</option>
            <option value="git">Git仓库</option>
          </select>
        </div>
        
        <div v-if="form.source === 'git'" class="form-group">
          <label for="git-repo">Git仓库地址:</label>
          <input
            type="text"
            id="git-repo"
            v-model="form.gitRepo"
            class="form-control"
            placeholder="https://github.com/A-Dawn/LAT-Lab-marketplace"
          >
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="updating">
          {{ updating ? '更新中...' : '保存设置' }}
        </button>
      </form>
    </div>
    
    <div class="card">
      <h3>插件列表</h3>
      <button @click="refreshPlugins" class="btn btn-secondary" :disabled="refreshing">
        {{ refreshing ? '刷新中...' : '刷新插件列表' }}
      </button>
      
      <div v-if="pluginsLoading" class="loading mt-3">加载中...</div>
      <div v-else-if="plugins.length === 0" class="mt-3">没有找到插件</div>
      <ul v-else class="plugins-list mt-3">
        <li v-for="plugin in plugins" :key="plugin.id" class="plugin-item">
          <h4>{{ plugin.name }} <small>{{ plugin.version }}</small></h4>
          <p>{{ plugin.description }}</p>
          <div class="plugin-tags">
            <span v-for="tag in plugin.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { marketplaceApi } from '../services/api'

export default {
  name: 'MarketplaceSettings',
  
  data() {
    return {
      // 当前设置
      currentSettings: {
        source: 'local',
        git_repo: null,
        local_path: null
      },
      
      // 表单数据
      form: {
        source: 'local',
        gitRepo: ''
      },
      
      // 插件列表
      plugins: [],
      
      // 状态标志
      loading: true,
      updating: false,
      pluginsLoading: true,
      refreshing: false,
      
      // 消息提示
      message: '',
      messageType: 'success'
    };
  },
  
  created() {
    this.fetchSettings();
    this.fetchPlugins();
  },
  
  methods: {
    // 获取当前设置
    async fetchSettings() {
      this.loading = true;
      
      try {
        const data = await marketplaceApi.getMarketplaceSource();
        this.currentSettings = data;
        this.form.source = data.source;
        this.form.gitRepo = data.git_repo || '';
      } catch (error) {
        console.error('获取设置失败:', error);
        this.showMessage(`获取设置失败: ${error.message}`, 'danger');
      } finally {
        this.loading = false;
      }
    },
    
    // 更新设置
    async updateSettings() {
      if (this.form.source === 'git' && !this.form.gitRepo.trim()) {
        this.showMessage('请输入Git仓库地址', 'danger');
        return;
      }
      
      this.updating = true;
      
      try {
        const settings = {
          source: this.form.source,
          git_repo: this.form.source === 'git' ? this.form.gitRepo.trim() : null
        };
        
        const data = await marketplaceApi.updateMarketplaceSource(settings);
        this.currentSettings = data;
        this.showMessage('设置已成功更新!');
        
        // 刷新插件列表
        this.fetchPlugins();
      } catch (error) {
        console.error('更新设置失败:', error);
        this.showMessage(`更新设置失败: ${error.message}`, 'danger');
      } finally {
        this.updating = false;
      }
    },
    
    // 获取插件列表
    async fetchPlugins() {
      this.pluginsLoading = true;
      
      try {
        const data = await marketplaceApi.getMarketplacePlugins();
        this.plugins = data;
      } catch (error) {
        console.error('获取插件失败:', error);
        this.showMessage(`获取插件失败: ${error.message}`, 'danger');
      } finally {
        this.pluginsLoading = false;
      }
    },
    
    // 刷新插件列表
    async refreshPlugins() {
      this.refreshing = true;
      
      try {
        await marketplaceApi.refreshMarketplace();
        this.showMessage('插件列表已刷新!');
        await this.fetchPlugins();
      } catch (error) {
        console.error('刷新插件失败:', error);
        this.showMessage(`刷新插件失败: ${error.message}`, 'danger');
      } finally {
        this.refreshing = false;
      }
    },
    
    // 显示消息
    showMessage(message, type = 'success') {
      this.message = message;
      this.messageType = type;
      
      setTimeout(() => {
        this.message = '';
      }, 5000);
    }
  }
};
</script>

<style scoped>
.marketplace-settings {
  max-width: 800px;
  margin: 0 auto;
}

.card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.btn {
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.alert {
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.loading {
  color: #6c757d;
  font-style: italic;
}

.mt-3 {
  margin-top: 15px;
}

.plugins-list {
  list-style: none;
  padding: 0;
}

.plugin-item {
  border-bottom: 1px solid #eee;
  padding: 15px 0;
}

.plugin-item:last-child {
  border-bottom: none;
}

.plugin-tags {
  margin-top: 8px;
}

.tag {
  display: inline-block;
  background-color: #e9f5fe;
  color: #3498db;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 5px;
  margin-bottom: 5px;
}
</style> 