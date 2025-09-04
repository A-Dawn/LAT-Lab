<!--
  @component Home
  @description 博客网站首页，展示文章列表、分类、标签和AI功能
-->
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { articleApi, categoryApi, tagApi, pluginApi } from '../services/api'

import HeroSection from '../components/HeroSection.vue'
import ArticleList from '../components/ArticleList.vue'
import SidebarSection from '../components/SidebarSection.vue'
import MainLayout from '../components/MainLayout.vue'

const store = useStore()
const route = useRoute()
const router = useRouter()

const isAuthenticated = computed(() => store.getters.isAuthenticated)
const homeWidgets = computed(() => store.getters.homeWidgets)

const articles = ref([])
const categories = ref([])
const tags = ref([])

const isLoading = ref(true)
const error = ref(null)

const currentPage = ref(1)
const pageSize = ref(10)
const totalArticles = ref(0)

const selectedCategory = ref('')
const selectedTag = ref('')
const searchQuery = ref('')

const updateFiltersFromRoute = () => {
  const categoryParam = validateNumericParam(route.query.category);
  const tagParam = validateStringParam(route.query.tag);
  const searchParam = validateStringParam(route.query.search, 100);
  const pageParam = validatePageParam(route.query.page);
  
  selectedCategory.value = categoryParam;
  selectedTag.value = tagParam;
  searchQuery.value = searchParam;
  currentPage.value = pageParam;
}

const validateNumericParam = (param) => {
  if (!param) return '';
  return /^\d+$/.test(param) && parseInt(param) > 0 ? param : '';
}

const validateStringParam = (param, maxLength = 50) => {
  if (!param) return '';
  if (typeof param !== 'string') return '';
  return param.substring(0, maxLength).replace(/[<>]/g, '');
}

const validatePageParam = (param) => {
  if (!param) return 1;
  const page = parseInt(param);
  return !isNaN(page) && page > 0 && page <= 1000 ? page : 1;
  
  console.log('从URL更新筛选条件:', {
    category: selectedCategory.value,
    tag: selectedTag.value,
    search: searchQuery.value,
    page: currentPage.value
  })
}

const fetchArticles = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    updateFiltersFromRoute()
    
    console.log('正在获取文章列表，参数:', {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      category_id: selectedCategory.value || undefined,
      tag: selectedTag.value || undefined,
      search: searchQuery.value || undefined
    })
    
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      include_pending: false  // 只获取已审核的文章
    }
    
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    
    if (selectedTag.value) {
      params.tag = selectedTag.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await articleApi.getArticles(params)
    console.log('API返回的文章数据:', response)
    
    if (Array.isArray(response)) {
      articles.value = response
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
    articles.value = []
    totalArticles.value = 0
  } finally {
    isLoading.value = false
  }
}

const fetchCategoriesAndTags = async () => {
  try {
    const categoriesRes = await categoryApi.getCategories().catch(err => {
      console.error('获取分类失败:', err)
      return []
    })
    
    categories.value = categoriesRes || []
    console.log('获取到的分类:', categories.value)
    
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

const filterByCategory = (categoryId) => {
  router.push({
    path: '/',
    query: {
      ...route.query,
      category: categoryId || undefined,
      page: 1
    }
  })
}

const filterByTag = (tagName) => {
  router.push({
    path: '/',
    query: {
      ...route.query,
      tag: tagName || undefined,
      page: 1
    }
  })
}

const handleSearch = (query) => {
  router.push({
    path: '/',
    query: {
      ...route.query,
      search: query || undefined,
      page: 1
    }
  })
}

const changePage = (page) => {
  router.push({
    path: '/',
    query: {
      ...route.query,
      page: page
    }
  })
}

const refreshWidget = async (widgetId) => {
  try {
    await store.dispatch('loadPluginExtensions')
    console.log('刷新了插件小部件:', widgetId)
  } catch (err) {
    console.error('刷新插件小部件失败:', err)
  }
}

watch(
  () => route.query,
  () => {
    fetchArticles()
  },
  { deep: true, immediate: true }
)

onMounted(async () => {
  await fetchCategoriesAndTags()
  
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