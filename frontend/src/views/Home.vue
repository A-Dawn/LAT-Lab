<!--
  @component Home
  @description 博客网站首页，展示文章列表、分类、标签和AI功能
-->
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { articleApi, categoryApi, tagApi, pluginApi } from '../services/api'

// 导入组件
import HeroSection from '../components/HeroSection.vue'
import ArticleList from '../components/ArticleList.vue'
import SidebarSection from '../components/SidebarSection.vue'
import MainLayout from '../components/MainLayout.vue'

// Vuex存储
const store = useStore()
const route = useRoute()
const router = useRouter()

// 获取用户登录状态
const isAuthenticated = computed(() => store.getters.isAuthenticated)

// 插件小部件
const homeWidgets = computed(() => store.getters.homeWidgets)

// 文章列表
const articles = ref([])

// 分类和标签
const categories = ref([])
const tags = ref([])

// 加载状态
const isLoading = ref(true)
const error = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const totalArticles = ref(0)

// 筛选
const selectedCategory = ref('')
const selectedTag = ref('')
const searchQuery = ref('')

/**
 * 从URL参数更新筛选条件
 */
const updateFiltersFromRoute = () => {
  // 从URL参数获取筛选条件并验证
  const categoryParam = validateNumericParam(route.query.category);
  const tagParam = validateStringParam(route.query.tag);
  const searchParam = validateStringParam(route.query.search, 100); // 限制搜索参数长度
  const pageParam = validatePageParam(route.query.page);
  
  // 更新本地状态
  selectedCategory.value = categoryParam;
  selectedTag.value = tagParam;
  searchQuery.value = searchParam;
  currentPage.value = pageParam;
}

// 验证数字参数
const validateNumericParam = (param) => {
  if (!param) return '';
  // 确保是数字并且是合理的正整数
  return /^\d+$/.test(param) && parseInt(param) > 0 ? param : '';
}

// 验证字符串参数
const validateStringParam = (param, maxLength = 50) => {
  if (!param) return '';
  if (typeof param !== 'string') return '';
  // 防止过长参数和恶意输入
  return param.substring(0, maxLength).replace(/[<>]/g, '');
}

// 验证页码参数
const validatePageParam = (param) => {
  if (!param) return 1;
  const page = parseInt(param);
  // 确保页码是正整数且在合理范围内
  return !isNaN(page) && page > 0 && page <= 1000 ? page : 1;
  
  console.log('从URL更新筛选条件:', {
    category: selectedCategory.value,
    tag: selectedTag.value,
    search: searchQuery.value,
    page: currentPage.value
  })
}

/**
 * 获取文章列表
 * 根据筛选条件和分页信息获取文章
 */
const fetchArticles = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // 确保从URL获取最新的筛选参数
    updateFiltersFromRoute()
    
    console.log('正在获取文章列表，参数:', {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      category_id: selectedCategory.value || undefined,
      tag: selectedTag.value || undefined,
      search: searchQuery.value || undefined
    })
    
    // 构建查询参数
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    // 添加可选参数
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    
    if (selectedTag.value) {
      params.tag = selectedTag.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    // 从API获取数据
    const response = await articleApi.getArticles(params)
    console.log('API返回的文章数据:', response)
    
    // 确保响应是数组
    if (Array.isArray(response)) {
      articles.value = response
      // 设置总数为数组长度
      totalArticles.value = response.length
    } else {
      console.warn('API返回的不是数组:', response)
      articles.value = []
      totalArticles.value = 0
      error.value = '获取文章列表失败: 服务器返回格式不正确'
    }
  } catch (err) {
    console.error('获取文章列表失败, 详细错误:', err)
    if (err.response) {
      error.value = `获取文章列表失败 (${err.response.status}): ${err.response.data?.detail || '未知错误'}`
    } else if (err.request) {
      error.value = '获取文章列表失败: 服务器无响应'
    } else {
      error.value = `获取文章列表失败: ${err.message || '未知错误'}`
    }
    articles.value = [] // 清空文章列表
    totalArticles.value = 0
  } finally {
    isLoading.value = false
  }
}

/**
 * 获取分类和标签
 * 从API获取文章分类和标签列表
 */
const fetchCategoriesAndTags = async () => {
  try {
    // 获取分类
    const categoriesRes = await categoryApi.getCategories().catch(err => {
      console.error('获取分类失败:', err)
      return []
    })
    
    categories.value = categoriesRes || []
    console.log('获取到的分类:', categories.value)
    
    // 获取标签
    try {
      const tagsRes = await tagApi.getTags()
      tags.value = tagsRes || []
      console.log('获取到的标签:', tags.value)
    } catch (tagErr) {
      console.error('获取标签失败:', tagErr)
      tags.value = []
    }
  } catch (err) {
    console.error('获取分类和标签失败:', err)
    categories.value = []
    tags.value = []
  }
}

/**
 * 切换分类
 * @param {String} categoryId - 分类ID
 */
const filterByCategory = (categoryId) => {
  // 更新路由而不是直接调用API
  router.push({
    path: '/',
    query: {
      ...route.query,
      category: categoryId || undefined,
      page: 1 // 重置页码
    }
  })
}

/**
 * 切换标签
 * @param {String} tagName - 标签名称
 */
const filterByTag = (tagName) => {
  // 更新路由而不是直接调用API
  router.push({
    path: '/',
    query: {
      ...route.query,
      tag: tagName || undefined,
      page: 1 // 重置页码
    }
  })
}

/**
 * 搜索处理
 * @param {String} query - 搜索查询
 */
const handleSearch = (query) => {
  // 更新路由而不是直接调用API
  router.push({
    path: '/',
    query: {
      ...route.query,
      search: query || undefined,
      page: 1 // 重置页码
    }
  })
}

/**
 * 切换页面
 * @param {Number} page - 新页码
 */
const changePage = (page) => {
  // 更新路由而不是直接调用API
  router.push({
    path: '/',
    query: {
      ...route.query,
      page: page
    }
  })
}

/**
 * 刷新插件小部件
 * @param {String} widgetId - 小部件ID
 */
const refreshWidget = async (widgetId) => {
  try {
    await store.dispatch('loadPluginExtensions')
    console.log('刷新了插件小部件:', widgetId)
  } catch (err) {
    console.error('刷新插件小部件失败:', err)
  }
}

// 监听路由变化，更新文章列表
watch(
  () => route.query,
  () => {
    fetchArticles()
  },
  { deep: true, immediate: true }
)

// 初始化页面
onMounted(async () => {
  await fetchCategoriesAndTags()
  
  // 加载插件扩展
  try {
    await store.dispatch('loadPluginExtensions')
  } catch (error) {
    console.error('加载插件扩展失败:', error)
  }
})
</script>

<template>
  <div class="home-page">
    <!-- 英雄区域 -->
    <HeroSection @search="handleSearch" />
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <MainLayout :widgets="homeWidgets" @widget-refresh="refreshWidget">
        <!-- 主内容区域 -->
        <template #main>
          <ArticleList 
            :articles="articles"
            :isLoading="isLoading"
            :error="error"
            :currentPage="currentPage"
            :totalArticles="totalArticles"
            :pageSize="pageSize"
            :isAuthenticated="isAuthenticated"
            @retry="fetchArticles"
            @page-change="changePage"
          />
        </template>
        
        <!-- 侧边栏 -->
        <template #right>
          <SidebarSection 
            :categories="categories"
            :tags="tags"
            :selectedCategory="selectedCategory"
            :selectedTag="selectedTag"
            :widgets="homeWidgets"
            @category-select="filterByCategory"
            @tag-select="filterByTag"
            @widget-refresh="refreshWidget"
          />
        </template>
      </MainLayout>
    </div>
  </div>
</template>

<style scoped>
/* 首页样式 */
.home-page {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 确保主内容区域正确继承主题颜色 */
.main-content {
  color: inherit;
  background-color: inherit;
  padding-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-page {
    gap: 30px;
  }
}
</style> 