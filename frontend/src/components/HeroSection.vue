<!--
  @component HeroSection
  @description 首页顶部英雄区域组件，包含标题、副标题和搜索功能
  @props {String} title - 英雄区域的主标题
  @props {String} subtitle - 英雄区域的副标题
  @emits {search} - 当用户搜索时触发，带有搜索查询参数
-->
<script setup>
import { ref } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: 'LAT-Lab'
  },
  subtitle: {
    type: String,
    default: '探索技术与人生的光'
  }
});

const emit = defineEmits(['search']);

// 搜索查询
const searchQuery = ref('');

/**
 * 处理搜索事件
 * 当用户按下回车或点击搜索按钮时触发
 */
const handleSearch = () => {
  emit('search', searchQuery.value);
};
</script>

<template>
  <!-- 移除英雄区域，直接使用背景容器 -->
  <div class="content-background">
    <div class="hero-content">
      <!-- 标题 -->
      <h1 class="hero-title">
        欢迎来到 <span>{{ title }}</span>
      </h1>
      
      <!-- 副标题 -->
      <p class="hero-subtitle">{{ subtitle }}</p>
      
      <!-- 搜索框 -->
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索文章..." 
          @keyup.enter="handleSearch"
          class="search-input"
          aria-label="搜索文章"
        />
        <button 
          class="search-button" 
          @click="handleSearch"
          aria-label="搜索"
        >
          <span class="search-icon">🔍</span>
          <span>搜索</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 内容背景容器 - 使用原英雄区域的颜色 */
.content-background {
  background: var(--hero-gradient);
  padding: 30px 0;
  text-align: center;
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
  width: 100%;
  border-top: 1px solid rgba(255, 255, 255, 0.4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.15),
    0 10px 15px -3px rgba(0, 0, 0, 0.3); /* 添加下边框阴影 */
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.8s ease;
  padding: 0 20px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 主标题样式 */
.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 20px;
  color: white;
  text-shadow: 
    0 2px 10px rgba(0, 0, 0, 0.5),
    0 0 5px rgba(255, 255, 255, 0.5),
    0 0 15px rgba(255, 255, 255, 0.3);
  letter-spacing: -0.03em;
  line-height: 1.2;
}

/* 强调部分的样式 */
.hero-title span {
  color: white;
  position: relative;
  display: inline-block;
  text-shadow: 
    0 2px 15px rgba(0, 0, 0, 0.6),
    0 0 8px rgba(255, 255, 255, 0.6),
    0 0 20px rgba(255, 255, 255, 0.4);
}

/* 副标题样式 */
.hero-subtitle {
  font-size: 1.4rem;
  opacity: 0.95;
  margin-bottom: 35px;
  color: white;
  max-width: 600px;
  font-weight: 500;
  line-height: 1.5;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  background-color: rgba(0, 0, 0, 0.2);
  padding: 10px 20px;
  border-radius: 30px;
  backdrop-filter: blur(2px);
  display: inline-block;
}

/* 搜索框 */
.search-box {
  width: 80%;
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 50px;
  padding: 5px 5px 5px 10px;
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  position: relative;
}

.search-box:focus-within {
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 15px 20px;
  color: #fff;
  font-size: 1.1rem;
  outline: none;
  border-radius: 50px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 300;
}

.search-button {
  background-color: var(--primary-color);
  border: none;
  border-radius: 50px;
  padding: 12px 25px;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  margin: 3px;
}

.search-button:hover {
  background-color: var(--secondary-color);
  transform: translateX(3px);
}

.search-icon {
  font-size: 1.1rem;
}

/* 主题特定样式 */
:root[data-theme="light"] .search-button {
  background-color: var(--primary-color);
  color: white;
}

:root[data-theme="light"] .search-button:hover {
  background-color: var(--secondary-color);
}

/* 霓虹主题下的内容背景容器特殊样式 */
:root[data-theme="neon"] .content-background {
  border-top: 1px solid var(--primary-color);
  border-bottom: 1px solid var(--primary-color);
  box-shadow: 
    var(--glow-primary), 
    0 8px 32px rgba(0, 0, 0, 0.2),
    0 10px 15px -3px rgba(0, 0, 0, 0.4); /* 霓虹主题下的阴影 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
    padding: 8px 15px;
  }
  
  .search-box {
    width: 95%;
  }
  
  .content-background {
    padding: 20px 0;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .search-button span:not(.search-icon) {
    display: none;
  }
  
  .search-button {
    padding: 12px 15px;
  }
}
</style> 