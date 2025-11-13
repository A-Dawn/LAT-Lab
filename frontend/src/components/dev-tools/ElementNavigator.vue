<template>
  <div class="element-navigator">
    <div class="navigator-header">
      <h3>元素导航</h3>
      <button class="collapse-btn" @click="collapsed = !collapsed">
        {{ collapsed ? '展开' : '收起' }}
      </button>
    </div>
    
    <div v-if="!collapsed" class="navigator-content">
      <!-- 搜索框 -->
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索元素..."
          class="search-input"
        />
        <button v-if="searchQuery" @click="searchQuery = ''" class="clear-btn">✕</button>
      </div>
      
      <!-- 分类统计 -->
      <div class="category-stats">
        <div class="stat-item" v-for="stat in categoryStats" :key="stat.category">
          <span class="stat-label">{{ stat.label }}</span>
          <span class="stat-count">{{ stat.count }}</span>
        </div>
      </div>
      
      <!-- 分类树 -->
      <div class="category-tree">
        <div 
          v-for="category in filteredCategories" 
          :key="category.id"
          class="category-group"
        >
          <div 
            class="category-header"
            :class="{ active: expandedCategories.includes(category.id) }"
            @click="toggleCategory(category.id)"
          >
            <span class="expand-icon">{{ expandedCategories.includes(category.id) ? '▼' : '▶' }}</span>
            <span class="category-name">{{ category.name }}</span>
            <span class="category-count">({{ category.items.length }})</span>
          </div>
          
          <div v-if="expandedCategories.includes(category.id)" class="category-items">
            <div 
              v-for="(item, index) in category.items" 
              :key="`${category.id}-${index}`"
              class="item-entry"
              :class="{ selected: selectedItem === item.id }"
              @click="selectItem(item)"
              @mouseenter="highlightItem(item)"
              @mouseleave="unhighlightItem()"
            >
              <span class="item-index">{{ String(index + 1).padStart(3, '0') }}</span>
              <span class="item-tag">{{ item.tag }}</span>
              <span class="item-description">{{ item.description }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 快速跳转 -->
      <div class="quick-jump">
        <label>快速跳转到索引：</label>
        <input 
          type="number" 
          v-model.number="jumpIndex"
          @keyup.enter="jumpToIndex"
          placeholder="输入索引号"
          class="jump-input"
        />
        <button @click="jumpToIndex" class="jump-btn">跳转</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  elements: {
    type: Object,
    required: true,
    default: () => ({
      styles: [],
      texts: [],
      layouts: []
    })
  }
})

const emit = defineEmits(['select-item', 'highlight-item', 'unhighlight-item'])

const collapsed = ref(false)
const searchQuery = ref('')
const expandedCategories = ref(['heading', 'paragraph', 'button'])
const selectedItem = ref(null)
const jumpIndex = ref(null)

// 构建分类结构
const categories = computed(() => {
  const cats = []
  
  // CSS变量分类
  if (props.elements.styles && props.elements.styles.length > 0) {
    const stylesByCategory = {}
    
    props.elements.styles.forEach(style => {
      const category = style.category || 'other'
      if (!stylesByCategory[category]) {
        stylesByCategory[category] = []
      }
      stylesByCategory[category].push({
        id: `style-${style.name}`,
        tag: 'CSS变量',
        description: style.name,
        type: 'style',
        data: style
      })
    })
    
    Object.keys(stylesByCategory).forEach(category => {
      cats.push({
        id: `styles-${category}`,
        name: `CSS变量 - ${getCategoryLabel(category)}`,
        items: stylesByCategory[category],
        type: 'styles'
      })
    })
  }
  
  // 文本元素分类
  if (props.elements.texts && props.elements.texts.length > 0) {
    const textsByTag = {}
    
    props.elements.texts.forEach(text => {
      const tag = getElementTag(text.selector)
      if (!textsByTag[tag]) {
        textsByTag[tag] = []
      }
      textsByTag[tag].push({
        id: text.id,
        tag: tag.toUpperCase(),
        description: text.description,
        type: 'text',
        data: text
      })

    })
    
    Object.keys(textsByTag).forEach(tag => {
      cats.push({
        id: `text-${tag}`,
        name: `${getTagLabel(tag)} 文本`,
        items: textsByTag[tag],
        type: 'texts'
      })
    })
  }
  
  // 布局元素分类
  if (props.elements.layouts && props.elements.layouts.length > 0) {
    const layoutsByProperty = {}
    
    props.elements.layouts.forEach(layout => {
      const property = layout.property || 'other'
      if (!layoutsByProperty[property]) {
        layoutsByProperty[property] = []
      }
      layoutsByProperty[property].push({
        id: layout.id,
        tag: property,
        description: layout.description,
        type: 'layout',
        data: layout
      })
    })
    
    Object.keys(layoutsByProperty).forEach(property => {
      cats.push({
        id: `layout-${property}`,
        name: `布局 - ${property}`,
        items: layoutsByProperty[property],
        type: 'layouts'
      })
    })
  }
  
  return cats
})

// 过滤后的分类
const filteredCategories = computed(() => {
  if (!searchQuery.value) return categories.value
  
  const query = searchQuery.value.toLowerCase()
  return categories.value.map(category => {
    const filteredItems = category.items.filter(item => 
      item.tag.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      (item.data.selector && item.data.selector.toLowerCase().includes(query))
    )
    
    return {
      ...category,
      items: filteredItems
    }
  }).filter(category => category.items.length > 0)
})

// 分类统计
const categoryStats = computed(() => {
  return [
    { category: 'styles', label: 'CSS变量', count: props.elements.styles?.length || 0 },
    { category: 'texts', label: '文本元素', count: props.elements.texts?.length || 0 },
    { category: 'layouts', label: '布局元素', count: props.elements.layouts?.length || 0 }
  ]
})

// 辅助函数
function getElementTag(selector) {
  if (!selector) return 'unknown'
  
  const match = selector.match(/^([a-z]+[0-9]?)/i)
  return match ? match[1] : 'unknown'
}

function getTagLabel(tag) {
  const labels = {
    h1: '一级标题', h2: '二级标题', h3: '三级标题',
    h4: '四级标题', h5: '五级标题', h6: '六级标题',
    p: '段落', button: '按钮', label: '标签',
    a: '链接', li: '列表项', span: '文本',
    div: '容器文本', td: '表格单元格', th: '表格标题',
    dt: '定义标题', dd: '定义描述', time: '时间',
    blockquote: '引用'
  }
  return labels[tag.toLowerCase()] || tag.toUpperCase()
}

function getCategoryLabel(category) {
  const labels = {
    color: '颜色', layout: '布局', typography: '排版',
    effect: '特效', animation: '动画', theme: '主题',
    general: '通用', other: '其他'
  }
  return labels[category] || category
}

function toggleCategory(categoryId) {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

function selectItem(item) {
  selectedItem.value = item.id
  emit('select-item', item)
}

function highlightItem(item) {
  emit('highlight-item', item)
}

function unhighlightItem() {
  emit('unhighlight-item')
}

function jumpToIndex() {
  if (jumpIndex.value === null || jumpIndex.value === undefined) return
  
  // 查找对应索引的元素
  for (const category of categories.value) {
    if (jumpIndex.value <= category.items.length) {
      const item = category.items[jumpIndex.value - 1]
      if (item) {
        // 展开分类
        if (!expandedCategories.value.includes(category.id)) {
          expandedCategories.value.push(category.id)
        }
        // 选中元素
        selectItem(item)
        break
      }
    }
  }
}

// 监听搜索，自动展开有结果的分类
watch(searchQuery, (newQuery) => {
  if (newQuery) {
    expandedCategories.value = filteredCategories.value.map(c => c.id)
  }
})
</script>

<style scoped>
.element-navigator {
  background: var(--bg-elevated);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.navigator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.navigator-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.collapse-btn {
  padding: 5px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: var(--bg-hover);
}

.search-box {
  position: relative;
  margin-bottom: 15px;
}

.search-input {
  width: 100%;
  padding: 8px 30px 8px 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.9rem;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.1);
}

.clear-btn {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 5px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 1rem;
}

.clear-btn:hover {
  color: var(--text-primary);
}

.category-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 10px;
  background: var(--bg-secondary);
  border-radius: 4px;
  font-size: 0.85rem;
}

.stat-label {
  color: var(--text-secondary);
}

.stat-count {
  color: var(--primary-color);
  font-weight: 600;
}

.category-tree {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 5px;
  background: var(--bg-primary);
}

.category-group {
  margin-bottom: 5px;
}

.category-header {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  background: var(--bg-secondary);
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.category-header:hover {
  background: var(--bg-hover);
}

.category-header.active {
  background: var(--primary-color);
  color: white;
}

.expand-icon {
  margin-right: 8px;
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.category-header.active .expand-icon {
  color: white;
}

.category-name {
  flex: 1;
  font-weight: 500;
  font-size: 0.9rem;
}

.category-count {
  font-size: 0.85rem;
  color: var(--text-tertiary);
}

.category-header.active .category-count {
  color: rgba(255, 255, 255, 0.8);
}

.category-items {
  margin-top: 5px;
  padding-left: 20px;
}

.item-entry {
  display: flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
  margin-bottom: 2px;
}

.item-entry:hover {
  background: var(--bg-hover);
}

.item-entry.selected {
  background: rgba(76, 132, 255, 0.1);
  border-left: 3px solid var(--primary-color);
  padding-left: 7px;
}

.item-index {
  font-family: monospace;
  color: var(--text-tertiary);
  margin-right: 8px;
  font-size: 0.8rem;
}

.item-tag {
  display: inline-block;
  padding: 2px 6px;
  background: var(--bg-elevated);
  border-radius: 3px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--primary-color);
  margin-right: 8px;
  min-width: 60px;
  text-align: center;
}

.item-description {
  flex: 1;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quick-jump {
  margin-top: 15px;
  padding: 10px;
  background: var(--bg-secondary);
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-jump label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.jump-input {
  flex: 1;
  padding: 5px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.85rem;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.jump-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.jump-btn {
  padding: 5px 15px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: opacity 0.2s;
}

.jump-btn:hover {
  opacity: 0.9;
}

/* 滚动条样式 */
.category-tree::-webkit-scrollbar {
  width: 6px;
}

.category-tree::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 3px;
}

.category-tree::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.category-tree::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}
</style>


