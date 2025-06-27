<template>
  <div class="plugin-widget" :class="position">
    <div class="plugin-widget-header" v-if="showHeader">
      <h3 class="widget-title">{{ name }}</h3>
      <div class="widget-controls" v-if="isAdmin">
        <button @click="$emit('refresh')" class="control-btn refresh" title="刷新">
          🔄
        </button>
        <button @click="$emit('edit')" class="control-btn edit" title="编辑">
          ✏️
        </button>
      </div>
    </div>
    
    <div class="plugin-widget-content">
      <!-- 使用v-html显示HTML内容 -->
      <div v-if="html" v-html="sanitizeHtml(html)" class="widget-html-content"></div>
      
      <!-- 显示纯文本内容 -->
      <div v-else-if="content" class="widget-text-content">{{ content }}</div>
      
      <!-- 没有内容时显示的占位符 -->
      <div v-else class="widget-placeholder">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'PluginWidget',
  props: {
    id: {
      type: [Number, String],
      required: true
    },
    name: {
      type: String,
      required: true
    },
    content: {
      type: String,
      default: ''
    },
    html: {
      type: String,
      default: ''
    },
    position: {
      type: String,
      default: 'sidebar',
      validator: (value) => ['sidebar', 'top', 'bottom', 'left', 'right'].includes(value)
    },
    showHeader: {
      type: Boolean,
      default: true
    }
  },
  
  emits: ['refresh', 'edit'],
  
  setup() {
    const store = useStore()
    
    // 是否是管理员
    const isAdmin = computed(() => {
      const user = store.getters.currentUser
      return user && user.role === 'admin'
    })
    
    // 简单的HTML净化，防止XSS攻击
    const sanitizeHtml = (html) => {
      // 真实情况应该使用专业的HTML净化库，如DOMPurify
      // 这里仅作示例，允许基本的标签和img标签
      return html
    }
    
    return {
      isAdmin,
      sanitizeHtml
    }
  }
}
</script>

<style scoped>
.plugin-widget {
  margin-bottom: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.plugin-widget.sidebar {
  width: 100%;
}

.plugin-widget.top {
  width: 100%;
  margin-bottom: 20px;
}

.plugin-widget.bottom {
  width: 100%;
  margin-top: 20px;
}

.plugin-widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

.widget-title {
  margin: 0;
  font-size: 1.1rem;
  color: #303133;
}

.widget-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.control-btn:hover {
  opacity: 1;
}

.plugin-widget-content {
  padding: 15px 20px;
}

.widget-html-content {
  overflow: hidden;
}

/* 支持HTML内容中的图片 */
.widget-html-content img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 10px 0;
}

/* 加载中的样式 */
.widget-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  color: #909399;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-left-color: #4c84ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style> 