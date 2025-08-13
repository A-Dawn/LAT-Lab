<template>
  <div class="admin-container admin-plugin-marketplace">
    <div class="header-section">
      <h1>插件市场</h1>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="$emit('close')">返回插件管理</button>
        <button class="btn btn-primary" @click="activeTab = 'settings'" v-if="activeTab !== 'settings'">
          数据源设置
        </button>
      </div>
    </div>
    
    <!-- 选项卡导航 -->
    <div class="tabs-nav" v-if="!showPluginDetail">
      <button 
        class="tab-button" 
        :class="{ active: activeTab === 'marketplace' }" 
        @click="activeTab = 'marketplace'"
      >
        浏览插件
      </button>
      <button 
        class="tab-button" 
        :class="{ active: activeTab === 'settings' }" 
        @click="activeTab = 'settings'"
      >
        数据源设置
      </button>
    </div>
    
    <!-- 插件市场设置 -->
    <div v-if="activeTab === 'settings'">
      <MarketplaceSettings @refresh-marketplace="fetchMarketplaceData" />
    </div>
    
    <!-- 插件市场浏览 -->
    <div v-else-if="activeTab === 'marketplace'">
      <div class="marketplace-info" v-if="marketplaceInfo">
        <p>版本: {{ marketplaceInfo.version }} | 最近更新: {{ marketplaceInfo.last_updated }}</p>
        <p>{{ marketplaceInfo.description }}</p>
      </div>
      
      <div class="filter-section">
        <div class="search-box">
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="搜索插件..." 
            @input="handleSearch"
            class="form-control"
          />
        </div>
        
        <div class="category-filter">
          <select v-model="filters.category_id" @change="handleSearch" class="form-select">
            <option :value="null">所有分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        
        <div class="tag-filter">
          <select v-model="selectedTag" @change="handleTagChange" class="form-select">
            <option value="">所有标签</option>
            <option v-for="tag in tags" :key="tag" :value="tag">
              {{ tag }}
            </option>
          </select>
        </div>
        
        <div class="featured-filter">
          <label>
            <input type="checkbox" v-model="filters.featured" @change="handleSearch" />
            仅显示精选插件
          </label>
        </div>
      </div>
      
      <div class="plugins-grid" v-if="!loading">
        <div v-for="plugin in plugins" :key="plugin.id" class="plugin-card" @click="viewPluginDetail(plugin)">
          <div class="plugin-icon">
            <img :src="plugin.icon || '/default-plugin-icon.png'" alt="插件图标" />
          </div>
          <div class="plugin-info">
            <h3>{{ plugin.name }}</h3>
            <p class="plugin-description">{{ plugin.description }}</p>
            <div class="plugin-meta">
              <span class="plugin-author">作者: {{ plugin.author }}</span>
              <span class="plugin-version">版本: {{ plugin.version }}</span>
              <span class="plugin-rating">评分: {{ plugin.rating }} ({{ plugin.ratings_count }})</span>
              <span class="plugin-downloads">下载: {{ plugin.downloads }}</span>
            </div>
            <div class="plugin-tags">
              <span v-for="tag in plugin.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
        
        <div class="no-plugins" v-if="plugins.length === 0">
          <p>没有找到符合条件的插件</p>
        </div>
      </div>
      
      <div class="loading-indicator" v-else>
        <p>正在加载插件...</p>
      </div>
    </div>
    
    <!-- 插件详情对话框 -->
    <div class="dialog-overlay" v-if="showPluginDetail" @click="closePluginDetail"></div>
    <div class="dialog plugin-detail-dialog" v-if="showPluginDetail">
      <div class="dialog-header">
        <h2>{{ selectedPlugin.name }}</h2>
        <button class="btn-close" @click="closePluginDetail">×</button>
      </div>
      
      <div class="dialog-body">
        <div class="plugin-header">
          <img :src="selectedPlugin.icon || '/default-plugin-icon.png'" alt="插件图标" class="plugin-icon" />
          <div class="plugin-meta-info">
            <p><strong>版本:</strong> {{ selectedPlugin.version }}</p>
            <p><strong>作者:</strong> {{ selectedPlugin.author }}</p>
            <p><strong>评分:</strong> {{ selectedPlugin.rating }} ({{ selectedPlugin.ratings_count }} 评价)</p>
            <p><strong>下载数:</strong> {{ selectedPlugin.downloads }}</p>
          </div>
        </div>
        
        <div class="plugin-description">
          <p>{{ selectedPlugin.description }}</p>
        </div>
        
        <div class="plugin-category-tags">
          <div class="plugin-category">
            <strong>分类:</strong>
            <span>{{ getCategoryName(selectedPlugin.category_id) }}</span>
          </div>
          <div class="plugin-tags">
            <strong>标签:</strong>
            <span v-for="tag in selectedPlugin.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
        
        <div class="plugin-screenshots" v-if="selectedPlugin.screenshots && selectedPlugin.screenshots.length > 0">
          <h3>插件截图</h3>
          <div class="screenshots-container">
            <img 
              v-for="(screenshot, index) in selectedPlugin.screenshots" 
              :key="index" 
              :src="screenshot" 
              alt="插件截图"
              @click="openFullScreenImage(screenshot)"
            />
          </div>
        </div>
        
        <div class="plugin-readme" v-if="selectedPlugin.readme">
          <h3>插件说明</h3>
          <div class="markdown-content">
            <MarkdownEditor :content="selectedPlugin.readme" :readonly="true" />
          </div>
        </div>
        
        <div class="plugin-actions">
          <button @click="installPlugin(selectedPlugin)" class="btn btn-primary">安装插件</button>
          <a v-if="selectedPlugin.repository_url" :href="selectedPlugin.repository_url" target="_blank" class="btn btn-link">
            查看源代码
          </a>
        </div>
      </div>
    </div>
    
    <!-- 全屏图片查看器 -->
    <div class="fullscreen-image-overlay" v-if="fullscreenImage" @click="closeFullscreenImage">
      <img :src="fullscreenImage" alt="插件截图" />
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { marketplaceApi } from '../../services/api'
import MarkdownEditor from '../../components/MarkdownEditor.vue'
import MarketplaceSettings from '../../components/MarketplaceSettings.vue'

export default {
  name: 'AdminPluginMarketplace',
  components: {
    MarkdownEditor,
    MarketplaceSettings
  },
  emits: ['close', 'plugin-installed'],
  setup(props, { emit }) {
    // 选项卡
    const activeTab = ref('marketplace')
    
    // 数据
    const loading = ref(true)
    const marketplaceInfo = ref(null)
    const categories = ref([])
    const tags = ref([])
    const plugins = ref([])
    
    // 过滤条件
    const filters = reactive({
      search: '',
      category_id: null,
      tags: [],
      featured: false
    })
    
    const selectedTag = ref('')
    
    // 插件详情
    const showPluginDetail = ref(false)
    const selectedPlugin = ref(null)
    const fullscreenImage = ref(null)
    
    // 获取所有数据
    const fetchMarketplaceData = async () => {
      if (activeTab.value !== 'marketplace') {
        return;
      }
      
      loading.value = true
      try {
        // 获取基本信息
        const info = await marketplaceApi.getMarketplaceInfo()
        marketplaceInfo.value = info
        
        // 获取分类
        const cats = await marketplaceApi.getMarketplaceCategories()
        categories.value = cats
        
        // 获取标签
        const tagsList = await marketplaceApi.getMarketplaceTags()
        tags.value = tagsList
        
        // 获取插件
        await searchPlugins()
      } catch (error) {
        console.error('获取插件市场数据失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 搜索插件
    const searchPlugins = async () => {
      try {
        // 构建查询参数
        const params = { ...filters }
        
        // 转换标签为逗号分隔字符串
        if (params.tags && params.tags.length > 0) {
          params.tags = params.tags.join(',')
        } else {
          delete params.tags
        }
        
        // 清理null和空字符串
        Object.keys(params).forEach(key => {
          if (params[key] === null || params[key] === '') {
            delete params[key]
          }
        })
        
        const result = await marketplaceApi.searchPlugins(params)
        plugins.value = result
      } catch (error) {
        console.error('搜索插件失败:', error)
      }
    }
    
    // 处理搜索
    const handleSearch = () => {
      searchPlugins()
    }
    
    // 处理标签选择
    const handleTagChange = () => {
      if (selectedTag.value) {
        filters.tags = [selectedTag.value]
      } else {
        filters.tags = []
      }
      searchPlugins()
    }
    
    // 查看插件详情
    const viewPluginDetail = (plugin) => {
      selectedPlugin.value = plugin
      showPluginDetail.value = true
    }
    
    // 关闭插件详情
    const closePluginDetail = () => {
      showPluginDetail.value = false
    }
    
    // 安装插件
    const installPlugin = async (plugin) => {
      try {
        await marketplaceApi.downloadMarketplacePlugin(plugin.id)
        toast.success(`插件 ${plugin.name} 已成功安装`)
        emit('plugin-installed')
      } catch (error) {
        console.error('安装插件失败:', error)
        toast.error(`安装插件失败: ${error.message || '未知错误'}`)
      }
    }
    
    // 获取分类名称
    const getCategoryName = (categoryId) => {
      const category = categories.value.find(c => c.id === categoryId)
      return category ? category.name : '未分类'
    }
    
    // 全屏显示图片
    const openFullScreenImage = (imageSrc) => {
      fullscreenImage.value = imageSrc
    }
    
    // 关闭全屏图片
    const closeFullscreenImage = () => {
      fullscreenImage.value = null
    }
    
    // 监听选项卡变化，在切换到marketplace时加载数据
    const watchTabChange = () => {
      if (activeTab.value === 'marketplace') {
        fetchMarketplaceData()
      }
    }
    
    onMounted(() => {
      fetchMarketplaceData()
    })
    
    return {
      activeTab,
      loading,
      marketplaceInfo,
      categories,
      tags,
      plugins,
      filters,
      selectedTag,
      showPluginDetail,
      selectedPlugin,
      fullscreenImage,
      fetchMarketplaceData,
      handleSearch,
      handleTagChange,
      viewPluginDetail,
      closePluginDetail,
      installPlugin,
      getCategoryName,
      openFullScreenImage,
      closeFullscreenImage,
      watchTabChange
    }
  },
  watch: {
    activeTab() {
      this.watchTabChange()
    }
  }
};
</script>

<style scoped>
.admin-plugin-marketplace {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-section h1 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 选项卡样式 */
.tabs-nav {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-button:hover {
  background-color: var(--hover-color);
  color: var(--text-primary);
}

.tab-button.active {
  border-bottom: 2px solid var(--primary-color);
  color: var(--primary-color);
  font-weight: bold;
}

.marketplace-info {
  background-color: var(--bg-elevated);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: var(--text-secondary);
}

.filter-section {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}

.search-box {
  flex: 2;
  min-width: 200px;
}

.category-filter,
.tag-filter {
  flex: 1;
  min-width: 150px;
}

.featured-filter {
  white-space: nowrap;
}

.plugins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.plugin-card {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  background-color: var(--card-bg);
}

.plugin-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--card-shadow-hover);
}

.plugin-icon {
  width: 100%;
  height: 150px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-elevated);
}

.plugin-icon img {
  max-width: 80%;
  max-height: 80%;
  object-fit: contain;
}

.plugin-info {
  padding: 15px;
}

.plugin-info h3 {
  margin: 0 0 10px 0;
}

.plugin-description {
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.plugin-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5px;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 10px;
}

.plugin-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid rgba(var(--primary-rgb), 0.2);
}

.loading-indicator,
.no-plugins {
  text-align: center;
  padding: 40px;
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
  z-index: 100;
}

.dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow-hover);
  z-index: 101;
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
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
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.dialog-body {
  padding: 20px;
}

.plugin-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.plugin-header .plugin-icon {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.plugin-meta-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.plugin-description {
  margin-bottom: 20px;
}

.plugin-category-tags {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.plugin-screenshots {
  margin-bottom: 20px;
}

.screenshots-container {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 10px 0;
}

.screenshots-container img {
  height: 150px;
  border-radius: 4px;
  cursor: pointer;
}

.plugin-readme {
  margin-bottom: 20px;
}

.markdown-content {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 15px;
  background-color: var(--bg-elevated);
  color: var(--text-primary);
}

.plugin-actions {
  display: flex;
  gap: 10px;
}

/* 全屏图片查看器 */
.fullscreen-image-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  z-index: 200;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.fullscreen-image-overlay img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.form-control, .form-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 16px;
  width: 100%;
  background-color: var(--input-bg);
  color: var(--text-primary);
}

.form-control:focus, .form-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.2);
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--secondary-color);
}

.btn-secondary {
  background-color: var(--text-tertiary);
  color: white;
}

.btn-secondary:hover {
  opacity: 0.8;
}

.btn-link {
  background: none;
  color: var(--primary-color);
  text-decoration: none;
  padding: 8px 15px;
  border: 1px solid transparent;
}

.btn-link:hover {
  color: var(--secondary-color);
  text-decoration: underline;
}
</style> 