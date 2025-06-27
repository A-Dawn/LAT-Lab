<template>
  <div class="article-card" :class="{ 'featured': article.is_pinned }">
    <!-- 置顶标记 -->
    <div class="pinned-badge" v-if="article.is_pinned">置顶</div>
    
    <!-- 草稿标记 -->
    <div class="draft-badge" v-if="article.status === 'draft'">草稿</div>
    
    <!-- 定时发布标记 -->
    <div class="scheduled-badge" v-if="article.status === 'published' && article.published_at && isScheduled(article.published_at)">
      定时发布: {{ formatDate(article.published_at) }}
    </div>
    
    <!-- 可见性标记 -->
    <div class="visibility-badge" v-if="article.visibility !== 'public'">
      <span v-if="article.visibility === 'private'">
        <span class="badge-icon">🔒</span> 私密
      </span>
      <span v-else-if="article.visibility === 'password'">
        <span class="badge-icon">🔑</span> 密码保护
      </span>
    </div>
    
    <!-- 文章内容 -->
    <div class="article-content">
      <!-- 文章标题和链接 -->
      <router-link :to="'/article/' + article.id" class="article-title">
        {{ article.title }}
      </router-link>
      
      <!-- 文章摘要 -->
      <p class="article-excerpt">{{ formatExcerpt(article.content) }}</p>
      
      <!-- 文章元数据 -->
      <div class="article-meta">
        <div class="meta-left">
          <span class="meta-item author">
            <span class="meta-icon">👤</span>
            {{ article.author_name || '匿名' }}
          </span>
          
          <span class="meta-item category" v-if="article.category_name">
            <span class="meta-icon">📁</span>
            {{ article.category_name }}
          </span>
          
          <span class="meta-item date">
            <span class="meta-icon">📅</span>
            {{ formatDate(article.created_at) }}
          </span>
        </div>
        
        <div class="meta-right">
          <span class="meta-item views">
            <span class="meta-icon">👁️</span>
            {{ article.views || 0 }}
          </span>
          
          <span class="meta-item likes">
            <span class="meta-icon">❤️</span>
            {{ article.likes_count || 0 }}
          </span>
          
          <span class="meta-item comments">
            <span class="meta-icon">💬</span>
            {{ article.comments_count || 0 }}
          </span>
        </div>
      </div>
      
      <!-- 标签列表 -->
      <div class="article-tags" v-if="article.tags && article.tags.length > 0">
        <span class="tag" v-for="tag in article.tags" :key="tag">{{ tag }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ArticleItem',
  props: {
    article: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatExcerpt(content) {
      if (!content) return '暂无内容';
      
      // 移除Markdown标记
      let plainText = content
        .replace(/#+\s/g, '')
        .replace(/\*\*|\*|~~|__|\[|\]\(.*?\)/g, '')
        .replace(/```.*?```/gs, '代码片段...')
        .replace(/`/g, '');
      
      return plainText.length > 150 ? plainText.substring(0, 150) + '...' : plainText;
    },
    formatDate(dateStr) {
      if (!dateStr) return '未知时间';
      
      const date = new Date(dateStr);
      
      if (isNaN(date.getTime())) {
        return '无效日期';
      }
      
      // 格式化为 YYYY-MM-DD
      return date.toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
      });
    },
    isScheduled(dateStr) {
      if (!dateStr) return false;
      
      const publishDate = new Date(dateStr);
      const now = new Date();
      
      return publishDate > now;
    }
  }
}
</script>

<style scoped>
.article-card {
  background-color: var(--card-bg, #fff);
  border-radius: 12px;
  box-shadow: var(--card-shadow, 0 2px 12px rgba(0, 0, 0, 0.08));
  margin-bottom: 25px;
  padding: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color, #ebeef5);
  backface-visibility: hidden;
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--card-shadow-hover, 0 5px 15px rgba(0, 0, 0, 0.15));
}

.article-card.featured {
  border-left: 5px solid var(--primary-color, #4c84ff);
  background-color: var(--card-bg);
  position: relative;
}

.article-card.featured::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent 97%, var(--primary-color) 97%);
  opacity: 0.05;
  z-index: 0;
  pointer-events: none;
}

.pinned-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: var(--primary-color, #4c84ff);
  color: white;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  border-bottom-left-radius: 8px;
  z-index: 2;
  letter-spacing: 0.5px;
}

/* 草稿标记 */
.draft-badge {
  position: absolute;
  top: 0;
  right: 70px;
  background-color: #909399;
  color: white;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  z-index: 2;
  letter-spacing: 0.5px;
}

/* 定时发布标记 */
.scheduled-badge {
  position: absolute;
  top: 35px;
  right: 0;
  background-color: #e6a23c;
  color: white;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
  z-index: 2;
  letter-spacing: 0.5px;
}

/* 可见性标记 */
.visibility-badge {
  position: absolute;
  top: 0;
  left: 0;
  background-color: #f56c6c;
  color: white;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  border-bottom-right-radius: 8px;
  z-index: 2;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.badge-icon {
  font-size: 14px;
}

/* 为不同主题设置特定样式 */
:root[data-theme="dark"] .article-card {
  background-color: var(--card-bg);
  box-shadow: var(--card-shadow);
}

:root[data-theme="neon"] .article-card {
  background-color: var(--card-bg);
  box-shadow: var(--card-shadow);
  border-color: var(--border-color);
  backdrop-filter: blur(10px);
}

:root[data-theme="neon"] .pinned-badge,
:root[data-theme="neon"] .draft-badge,
:root[data-theme="neon"] .scheduled-badge,
:root[data-theme="neon"] .visibility-badge {
  box-shadow: var(--glow-primary);
}

.article-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.article-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary, #303133);
  margin-bottom: 10px;
  text-decoration: none;
  line-height: 1.3;
  transition: color 0.3s ease;
  letter-spacing: -0.01em;
}

.article-title:hover {
  color: var(--primary-color, #4c84ff);
}

.article-excerpt {
  color: var(--text-secondary, #606266);
  font-size: 1rem;
  line-height: 1.6;
  margin: 8px 0 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  transition: color 0.3s ease;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  color: var(--text-tertiary, #909399);
  font-size: 0.85rem;
  margin-top: 12px;
  transition: color 0.3s ease;
  border-top: 1px dashed var(--divider-color);
  padding-top: 12px;
}

.meta-left, .meta-right {
  display: flex;
  gap: 18px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  transition: transform 0.2s ease;
}

.meta-item:hover {
  transform: translateY(-2px);
  color: var(--primary-color);
}

.meta-icon {
  font-size: 0.9rem;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag {
  background-color: var(--hover-color, rgba(76, 132, 255, 0.1));
  color: var(--primary-color, #4c84ff);
  padding: 4px 10px;
  font-size: 0.8rem;
  border-radius: 30px;
  transition: background-color 0.3s, color 0.3s, transform 0.2s;
  border: 1px solid transparent;
  display: inline-block;
}

.tag:hover {
  background-color: rgba(var(--primary-rgb, 76, 132, 255), 0.15);
  color: var(--primary-color);
  transform: translateY(-2px);
  text-decoration: none;
}

.tag:active {
  transform: translateY(0);
}

:root[data-theme="dark"] .tag {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

:root[data-theme="neon"] .tag {
  border: 1px solid var(--border-color);
  background-color: var(--hover-color);
  color: var(--primary-color);
}

:root[data-theme="neon"] .tag:hover {
  box-shadow: var(--glow-primary);
  border-color: var(--primary-color);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .article-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .meta-right {
    justify-content: flex-start;
  }
  
  .article-card {
    padding: 18px;
  }
  
  .article-title {
    font-size: 1.4rem;
  }
}
</style> 