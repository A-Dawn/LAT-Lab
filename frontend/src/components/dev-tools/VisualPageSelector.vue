<template>
  <div class="visual-page-selector">
    <div class="selector-header">
      <h3>选择页面</h3>
      <p class="selector-description">
        点击下方卡片选择要编辑的页面，可以修改不同页面的样式、文本和布局。
      </p>
    </div>
    
    <div class="page-grid">
      <div 
        v-for="page in availablePages" 
        :key="page.url"
        :class="['page-card', { active: selectedPageUrl === page.url }]"
        @click="selectPage(page)"
      >
        <div class="page-icon">
          {{ page.icon }}
        </div>
        <div class="page-info">
          <h4 class="page-name">{{ page.name }}</h4>
          <p class="page-description">{{ page.description }}</p>
          <div class="page-meta">
            <span class="page-category">{{ page.category }}</span>
            <span v-if="page.isNew" class="new-badge">NEW</span>
          </div>
        </div>
        <div class="page-actions">
          <button 
            class="preview-btn"
            @click.stop="openPreviewPage(page)"
            title="预览页面"
          >
            
          </button>
          <button 
            class="edit-btn"
            @click.stop="editPage(page)"
            title="编辑页面"
          >
            
          </button>
        </div>
      </div>
      
      <!-- 当前页面卡片 -->
      <div 
        :class="['page-card', 'current-page', { active: selectedPageUrl === '' }]"
        @click="selectCurrentPage"
      >
        <div class="page-icon">
          
        </div>
        <div class="page-info">
          <h4 class="page-name">当前页面</h4>
          <p class="page-description">编辑当前正在浏览的页面</p>
          <div class="page-meta">
            <span class="page-category">实时编辑</span>
            <span class="current-badge">CURRENT</span>
          </div>
        </div>
        <div class="page-actions">
          <button 
            class="edit-btn"
            @click.stop="editCurrentPage"
            title="编辑当前页面"
          >
            
          </button>
        </div>
      </div>
    </div>
    
    <!-- 页面预览模态框 -->
    <div v-if="showPreview" class="preview-modal" @click="closePreview">
      <div class="preview-content" @click.stop>
        <div class="preview-header">
          <h3>{{ previewedPage?.name }} - 页面预览</h3>
          <button class="close-btn" @click="closePreview"></button>
        </div>
        <div class="preview-iframe-container">
          <iframe 
            :src="previewUrl" 
            class="preview-iframe"
            @load="onPreviewLoad"
          ></iframe>
        </div>
        <div class="preview-actions">
          <button class="admin-btn admin-btn-secondary" @click="closePreview">
            关闭预览
          </button>
          <button class="admin-btn admin-btn-primary" @click="selectAndClosePreview">
            选择此页面
          </button>
        </div>
      </div>
    </div>
    
    <!-- 动态内容控制 -->
    <div class="dynamic-content-control">
      <label class="toggle-label">
        <input 
          type="checkbox" 
          v-model="includeDynamicContent"
          @change="handleDynamicContentToggle"
        />
        <span class="toggle-text">包含动态内容</span>
        <span class="toggle-description">
          开启后将包含从API获取的动态内容，关闭则只显示静态模板元素
        </span>
      </label>
    </div>
    
    <!-- 调试信息 -->
    <div class="debug-info" v-if="isDev">
      <small>
        页面总数: {{ availablePages.length + 1 }} | 
        当前选择: {{ selectedPageUrl || '当前页面' }}
      </small>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  currentPage: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['page-change', 'elements-loaded', 'iframe-ready']);

const router = useRouter();
const selectedPageUrl = ref('');
const showPreview = ref(false);
const previewedPage = ref(null);
const includeDynamicContent = ref(false);

// 开发环境判断
const isDev = computed(() => {
  return process.env.NODE_ENV === 'development';
});

// 预览URL
const previewUrl = computed(() => {
  if (!previewedPage.value) return '';
  
  const url = new URL(previewedPage.value.url, window.location.origin);
  url.searchParams.append('devtools', 'true');
  return url.toString();
});

// 可用页面列表 - 按类别组织
const availablePages = [
  // 主要页面
  {
    name: '首页',
    url: '/',
    description: '博客首页，包含文章列表和导航',
    category: '主要页面',
    icon: '',
    isNew: false
  },
  {
    name: '文章详情页',
    url: '/article/1',
    description: '单篇文章的详细页面',
    category: '主要页面',
    icon: '',
    isNew: false
  },
  {
    name: '用户资料',
    url: '/profile',
    description: '用户个人资料页面',
    category: '主要页面',
    icon: '',
    isNew: false
  },
  
  // 编辑页面
  {
    name: '创建文章',
    url: '/article/new',
    description: '创建新文章的编辑器',
    category: '编辑页面',
    icon: '',
    isNew: false
  },
  {
    name: '编辑文章',
    url: '/article/1/edit',
    description: '编辑已有文章的页面',
    category: '编辑页面',
    icon: '',
    isNew: false
  },
  
  // 认证页面
  {
    name: '登录页面',
    url: '/login',
    description: '用户登录界面',
    category: '认证页面',
    icon: '',
    isNew: false
  },
  {
    name: '注册页面',
    url: '/register',
    description: '用户注册界面',
    category: '认证页面',
    icon: '',
    isNew: false
  },
  
  // 管理员页面
  {
    name: '管理员首页',
    url: '/admin',
    description: '管理员仪表板',
    category: '管理员页面',
    icon: '',
    isNew: false
  },
  {
    name: '文章管理',
    url: '/admin/articles',
    description: '管理所有文章',
    category: '管理员页面',
    icon: '',
    isNew: false
  },
  {
    name: '用户管理',
    url: '/admin/users',
    description: '管理系统用户',
    category: '管理员页面',
    icon: '',
    isNew: false
  },
  {
    name: '分类管理',
    url: '/admin/categories',
    description: '管理文章分类',
    category: '管理员页面',
    icon: '',
    isNew: false
  },
  {
    name: '标签管理',
    url: '/admin/tags',
    description: '管理文章标签',
    category: '管理员页面',
    icon: '',
    isNew: false
  },
  {
    name: '评论管理',
    url: '/admin/comments',
    description: '管理用户评论',
    category: '管理员页面',
    icon: '',
    isNew: false
  },
  {
    name: '插件管理',
    url: '/admin/plugins',
    description: '管理系统插件',
    category: '管理员页面',
    icon: '',
    isNew: false
  },
  {
    name: '插件市场',
    url: '/admin/plugins/marketplace',
    description: '浏览和安装插件',
    category: '管理员页面',
    icon: '',
    isNew: true
  }
];

// 选择页面
const selectPage = (page) => {
  selectedPageUrl.value = page.url;
  emit('page-change', page.url);
  console.log('选择页面:', page.name, page.url);
};

// 选择当前页面
const selectCurrentPage = () => {
  selectedPageUrl.value = '';
  emit('page-change', '');
  console.log('选择当前页面');
};

// 预览页面
const openPreviewPage = (page) => {
  previewedPage.value = page;
  showPreview.value = true;
};

// 关闭预览
const closePreview = () => {
  showPreview.value = false;
  previewedPage.value = null;
};

// 选择并关闭预览
const selectAndClosePreview = () => {
  if (previewedPage.value) {
    selectPage(previewedPage.value);
  }
  closePreview();
};

// 编辑页面
const editPage = (page) => {
  selectPage(page);
  // 可以在这里添加额外的编辑逻辑
};

// 编辑当前页面
const editCurrentPage = () => {
  selectCurrentPage();
  // 可以在这里添加额外的编辑逻辑
};

// 处理动态内容切换
const handleDynamicContentToggle = () => {
  console.log('动态内容设置已更改:', includeDynamicContent.value);
  // 重新触发页面变更事件
  emit('page-change', selectedPageUrl.value);
};

// 预览加载完成
const onPreviewLoad = () => {
  console.log('预览页面加载完成');
};

// 初始化
onMounted(() => {
  console.log('VisualPageSelector mounted, 可用页面数量:', availablePages.length);
  
  // 默认选择当前页面
  selectCurrentPage();
});

// 暴露方法给父组件
defineExpose({
  selectedPageUrl,
  selectPage,
  selectCurrentPage
});
</script>

<style scoped>
.visual-page-selector {
  margin-bottom: 20px;
}

.selector-header {
  margin-bottom: 20px;
}

.selector-header h3 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
  font-size: 1.5rem;
}

.selector-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.page-card {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.page-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(76, 132, 255, 0.15);
  transform: translateY(-2px);
}

.page-card.active {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
}

.page-card.current-page {
  border-color: var(--success-color);
  background: linear-gradient(135deg, var(--success-color), var(--info-color));
  color: white;
}

.page-card.current-page:hover {
  border-color: var(--success-color);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.15);
}

.page-icon {
  font-size: 2rem;
  margin-bottom: 12px;
  text-align: center;
}

.page-info {
  flex: 1;
}

.page-name {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: inherit;
}

.page-description {
  margin: 0 0 12px 0;
  font-size: 0.85rem;
  color: inherit;
  opacity: 0.8;
  line-height: 1.4;
}

.page-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.page-category {
  font-size: 0.75rem;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: inherit;
  opacity: 0.9;
}

.new-badge, .current-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

.new-badge {
  background: var(--warning-color);
  color: white;
}

.current-badge {
  background: var(--success-color);
  color: white;
}

.page-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.preview-btn, .edit-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  color: inherit;
}

.preview-btn:hover, .edit-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* 预览模态框 */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.preview-content {
  background: var(--card-bg);
  border-radius: 12px;
  width: 100%;
  max-width: var(--layout-max-width, 1400px);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.preview-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.preview-iframe-container {
  flex: 1;
  min-height: 400px;
  position: relative;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: white;
}

.preview-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

/* 动态内容控制 */
.dynamic-content-control {
  margin-top: 20px;
  padding: 16px;
  background-color: var(--bg-elevated);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.toggle-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
}

.toggle-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  accent-color: var(--primary-color);
}

.toggle-text {
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.toggle-description {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-left: 24px;
  line-height: 1.4;
}

/* 调试信息 */
.debug-info {
  margin-top: 16px;
  padding: 8px 12px;
  background-color: #f0f0f0;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #666;
  border: 1px dashed #ccc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-grid {
    grid-template-columns: 1fr;
  }
  
  .page-card {
    padding: 12px;
  }
  
  .preview-modal {
    padding: 10px;
  }
  
  .preview-content {
    max-height: 95vh;
  }
  
  .preview-iframe-container {
    min-height: 300px;
  }
}

@media (max-width: 480px) {
  .page-actions {
    flex-direction: column;
  }
  
  .preview-btn, .edit-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
