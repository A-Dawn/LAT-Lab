<template>
  <div class="plugin-widget" :class="position">
    <div class="plugin-widget-header" v-if="showHeader">
      <h3 class="widget-title">{{ displayTitle }}</h3>
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
      <!-- 使用v-html显示HTML内容，通过sanitizeHtml函数处理防止XSS攻击 -->
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
import { computed, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { sanitizeHtml } from '../utils/sanitize'

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
  
  setup(props) {
    const store = useStore()
    
    // 用于存储映射的文本内容
    const mappedTitle = ref(null)
    
    // 是否是管理员
    const isAdmin = computed(() => {
      const user = store.getters.currentUser
      return user && user.role === 'admin'
    })
    
    // 从全局映射中读取标题
    const getMappedTitle = () => {
      if (mappedTitle.value) return mappedTitle.value
      
      // 尝试从快速查找映射中查找
      if (window.__devToolsQuickMap) {
        // 尝试多种选择器格式
        const selectors = [
          '.widget-title',
          '.plugin-widget .widget-title',
          'h3.widget-title'
        ]
        
        for (const selector of selectors) {
          const mapped = window.__devToolsQuickMap[selector]
          if (mapped) {
            mappedTitle.value = mapped
            return mapped
          }
        }
      }
      
      // 返回原始值
      return props.name
    }
    
    // 在mounted时检查是否需要更新
    onMounted(() => {
      // 延迟一点点，确保同步加载已完成
      setTimeout(() => {
        if (window.__devToolsQuickMap) {
          const selectors = [
            '.widget-title',
            '.plugin-widget .widget-title',
            'h3.widget-title'
          ]
          
          for (const selector of selectors) {
            const mapped = window.__devToolsQuickMap[selector]
            if (mapped && mapped !== props.name) {
              mappedTitle.value = mapped
              break
            }
          }
        }
      }, 0)
    })
    
    return {
      isAdmin,
      sanitizeHtml,
      getMappedTitle,
      displayTitle: computed(() => getMappedTitle())
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