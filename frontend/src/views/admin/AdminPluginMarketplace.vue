<template>
  <div class="admin-container admin-plugin-marketplace">
    <div class="header-section">
      <h1>插件市场</h1>
      <button class="btn btn-secondary" @click="$emit('close')">返回插件管理</button>
    </div>
    
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
            <MarkdownEditor :content="selectedPlugin.readme" />
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

export default {
  name: 'AdminPluginMarketplace',
  components: {
    MarkdownEditor
  },
  emits: ['close', 'plugin-installed'],
  setup(props, { emit }) {
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
    const viewPluginDetail = async (plugin) => {
      try {
        // 获取完整的插件详情
        const detail = await marketplaceApi.getMarketplacePlugin(plugin.id)
        selectedPlugin.value = detail
        showPluginDetail.value = true
      } catch (error) {
        console.error('获取插件详情失败:', error)
      }
    }
    
    // 关闭插件详情
    const closePluginDetail = () => {
      showPluginDetail.value = false
      selectedPlugin.value = null
    }
    
    // 打开全屏图片
    const openFullScreenImage = (imageUrl) => {
      fullscreenImage.value = imageUrl
    }
    
    // 关闭全屏图片
    const closeFullscreenImage = () => {
      fullscreenImage.value = null
    }
    
    // 安装插件
    const installPlugin = async (plugin) => {
      try {
        const result = await marketplaceApi.downloadMarketplacePlugin(plugin.id)
        if (result.success) {
          alert(result.message || `插件"${plugin.name}"已成功安装`)
          emit('plugin-installed', result.plugin_id)
          closePluginDetail()
        }
      } catch (error) {
        alert(`安装插件失败: ${error.response?.data?.detail || error.message}`)
      }
    }
    
    // 获取分类名称
    const getCategoryName = (categoryId) => {
      const category = categories.value.find(c => c.id === categoryId)
      return category ? category.name : '未分类'
    }
    
    onMounted(() => {
      fetchMarketplaceData()
    })
    
    return {
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
      handleSearch,
      handleTagChange,
      viewPluginDetail,
      closePluginDetail,
      openFullScreenImage,
      closeFullscreenImage,
      installPlugin,
      getCategoryName
    }
  }
}
</script>

<style scoped>
.admin-plugin-marketplace {
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.marketplace-info {
  background-color: #f0f8ff;
  padding: 10px 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.plugins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.plugin-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.plugin-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.plugin-icon {
  width: 60px;
  height: 60px;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plugin-icon img {
  max-width: 100%;
  max-height: 100%;
  border-radius: 5px;
}

.plugin-info {
  flex: 1;
}

.plugin-info h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.2rem;
}

.plugin-description {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.plugin-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.8rem;
  color: #777;
}

.plugin-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 10px;
}

.tag {
  font-size: 0.8rem;
  background-color: #e9ecef;
  padding: 2px 8px;
  border-radius: 10px;
}

.loading-indicator {
  text-align: center;
  padding: 30px;
}

.plugin-detail-dialog {
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.plugin-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.plugin-meta-info {
  flex: 1;
}

.plugin-meta-info p {
  margin: 5px 0;
}

.plugin-category-tags {
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.plugin-screenshots {
  margin-top: 20px;
}

.screenshots-container {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 10px 0;
}

.screenshots-container img {
  max-height: 150px;
  border-radius: 5px;
  cursor: pointer;
}

.plugin-readme {
  margin-top: 20px;
}

.markdown-content {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 15px;
  background-color: #f9f9f9;
}

.plugin-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.fullscreen-image-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  cursor: pointer;
}

.fullscreen-image-overlay img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.no-plugins {
  grid-column: 1 / -1;
  text-align: center;
  padding: 30px;
  color: #777;
}

/* 适配暗色主题 */
:root.dark .plugin-card {
  background-color: #2c2c2c;
  border-color: #444;
}

:root.dark .tag {
  background-color: #444;
}

:root.dark .marketplace-info {
  background-color: #2c2c2c;
}
</style> 