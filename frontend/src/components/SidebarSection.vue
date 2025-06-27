<!--
  @component SidebarSection
  @description 博客侧边栏组件，包含关于博主、分类和标签云等小部件
  @props {Array} categories - 文章分类列表
  @props {Array} tags - 文章标签列表
  @props {String} selectedCategory - 当前选中的分类ID
  @props {String} selectedTag - 当前选中的标签名称
  @props {Array} widgets - 显示在侧边栏的插件部件列表
  @emits {category-select} - 当用户选择分类时触发
  @emits {tag-select} - 当用户选择标签时触发
  @emits {widget-refresh} - 当用户刷新插件小部件时触发
-->
<script setup>
import { ref, computed } from 'vue'
import PluginWidget from './PluginWidget.vue'

const props = defineProps({
  // 分类列表
  categories: {
    type: Array,
    default: () => []
  },
  // 标签列表
  tags: {
    type: Array,
    default: () => []
  },
  // 当前选中的分类ID
  selectedCategory: {
    type: String,
    default: ''
  },
  // 当前选中的标签名称
  selectedTag: {
    type: String,
    default: ''
  },
  // 插件部件列表
  widgets: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['category-select', 'tag-select', 'widget-refresh'])

/**
 * 过滤文章分类
 * @param {String} categoryId - 分类ID
 */
const handleCategoryClick = (categoryId) => {
  // 如果已选中，则取消选中
  const newCategoryId = categoryId === props.selectedCategory ? '' : categoryId
  emit('category-select', newCategoryId)
}

/**
 * 过滤文章标签
 * @param {String} tagName - 标签名称
 */
const handleTagClick = (tagName) => {
  // 如果已选中，则取消选中
  const newTagName = tagName === props.selectedTag ? '' : tagName
  emit('tag-select', newTagName)
}

/**
 * 刷新插件小部件
 * @param {String} widgetId - 小部件ID
 */
const handleWidgetRefresh = (widgetId) => {
  emit('widget-refresh', widgetId)
}

// 计算侧边栏小部件
const sidebarWidgets = computed(() => {
  return props.widgets.filter(widget => widget.position === 'sidebar')
})
</script>

<template>
  <div class="sidebar">
    <!-- 显示在顶部的插件部件 -->
    <plugin-widget
      v-for="widget in sidebarWidgets"
      :key="widget.id"
      :widget="widget"
      @refresh="handleWidgetRefresh(widget.id)"
    />
    
    <!-- 关于博主 -->
    <div class="sidebar-widget about-widget">
      <h3 class="widget-title">关于博主</h3>
      <div class="widget-content">
        <!-- 头像占位符 -->
        <div class="about-avatar">
          <div class="avatar-placeholder" aria-label="博主头像">D</div>
        </div>
        
        <!-- 博主简介 -->
        <p class="about-text">
          欢迎来到我的博客！这里记录了我的学习、思考和分享。
        </p>
        
        <!-- 社交链接 -->
        <div class="about-social">
          <a href="#" class="social-link" aria-label="GitHub链接">GitHub</a>
          <a href="#" class="social-link" aria-label="Twitter链接">Twitter</a>
          <a href="#" class="social-link" aria-label="知乎链接">知乎</a>
        </div>
      </div>
    </div>
    
    <!-- 文章分类 -->
    <div v-if="categories.length > 0" class="sidebar-widget category-widget">
      <h3 class="widget-title">文章分类</h3>
      <div class="widget-content">
        <ul class="category-list">
          <li 
            v-for="category in categories" 
            :key="category.id"
            :class="{ active: selectedCategory === category.id.toString() }"
            @click="handleCategoryClick(category.id.toString())"
          >
            <span class="category-icon">🔹</span>
            {{ category.name }}
          </li>
        </ul>
      </div>
    </div>
    
    <!-- 标签云 -->
    <div v-if="tags.length > 0" class="sidebar-widget tag-widget">
      <h3 class="widget-title">标签云</h3>
      <div class="widget-content">
        <div class="tag-cloud">
          <span 
            v-for="tag in tags" 
            :key="tag.id"
            :class="{ active: selectedTag === tag.name }"
            @click="handleTagClick(tag.name)"
          >
            {{ tag.name }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 显示在底部的插件部件 -->
    <plugin-widget
      v-for="widget in widgets.filter(w => w.position === 'bottom')"
      :key="widget.id"
      :id="widget.id"
      :name="widget.name"
      :content="widget.content"
      :html="widget.html"
      position="bottom"
      @refresh="handleWidgetRefresh(widget.id)"
    />
  </div>
</template>

<style scoped>
/* 侧边栏基础样式 */
.sidebar {
  width: 100%;
  flex-shrink: 0;
}

/* 小部件通用样式 */
.sidebar-widget {
  background-color: var(--card-bg, white);
  border-radius: 12px;
  border: 1px solid var(--border-color, #ebeef5);
  box-shadow: var(--card-shadow, 0 2px 12px rgba(0, 0, 0, 0.1));
  margin-bottom: 25px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.sidebar-widget:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-3px);
}

/* 小部件标题 */
.widget-title {
  padding: 18px 20px;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color, #ebeef5);
  color: var(--text-primary, #303133);
  letter-spacing: -0.01em;
}

/* 小部件内容区域 */
.widget-content {
  padding: 20px;
}

/* 关于博主样式 */
.about-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: var(--primary-color, #4c84ff);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: bold;
}

/* 霓虹主题头像发光效果 */
:root[data-theme="neon"] .avatar-placeholder {
  box-shadow: var(--glow-primary);
}

.about-text {
  color: var(--text-secondary, #606266);
  text-align: center;
  margin-bottom: 20px;
  font-size: 0.95rem;
  line-height: 1.6;
}

.about-social {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 15px;
}

.social-link {
  color: var(--primary-color, #4c84ff);
  font-size: 0.9rem;
  padding: 5px 15px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.social-link:hover {
  background-color: var(--hover-color);
  transform: translateY(-2px);
}

/* 分类列表样式 */
.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-list li {
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.category-list a {
  color: var(--text-secondary, #606266);
  text-decoration: none;
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.category-icon {
  margin-right: 8px;
  color: var(--primary-color);
}

.category-list a:hover {
  color: var(--primary-color, #4c84ff);
  background-color: var(--hover-color);
  transform: translateX(5px);
}

.category-list li.active a {
  color: var(--primary-color, #4c84ff);
  font-weight: 500;
  background-color: var(--hover-color);
}

/* 标签云样式 */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-cloud-item {
  background-color: var(--hover-color, rgba(76, 132, 255, 0.1));
  color: var(--primary-color, #4c84ff);
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.3s ease;
}

.tag-cloud-item:hover,
.tag-cloud-item.active {
  background-color: var(--primary-color, #4c84ff);
  color: white;
  transform: translateY(-3px);
}

/* 霓虹主题标签样式 */
:root[data-theme="neon"] .tag-cloud-item {
  border: 1px solid var(--border-color);
}

:root[data-theme="neon"] .tag-cloud-item:hover,
:root[data-theme="neon"] .tag-cloud-item.active {
  box-shadow: var(--glow-primary);
}

/* 响应式设计 */
@media (max-width: 1100px) {
  .sidebar {
    width: 100%;
  }
  
  .about-avatar {
    margin-bottom: 15px;
  }
  
  .avatar-placeholder {
    width: 80px;
    height: 80px;
    font-size: 2rem;
  }
}
</style> 