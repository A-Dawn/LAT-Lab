<template>
  <div class="status-indicator">
    <div class="status-header">
      <h4>开发工具状态</h4>
    </div>
    
    <div class="status-items">
      <div class="status-item">
        <div class="status-label">当前页面:</div>
        <div class="status-value">{{ currentPage || '当前页面' }}</div>
      </div>
      
      <div class="status-item">
        <div class="status-label">CSS变量:</div>
        <div class="status-value" :class="getStatusClass(cssVariablesCount)">
          {{ cssVariablesCount }} 个
        </div>
      </div>
      
      <div class="status-item">
        <div class="status-label">文本元素:</div>
        <div class="status-value" :class="getStatusClass(textElementsCount)">
          {{ textElementsCount }} 个
        </div>
      </div>
      
      <div class="status-item">
        <div class="status-label">布局元素:</div>
        <div class="status-value" :class="getStatusClass(layoutElementsCount)">
          {{ layoutElementsCount }} 个
        </div>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-indicator">
      <div class="loading-spinner"></div>
      <span>正在加载页面元素...</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentPage: {
    type: String,
    default: ''
  },
  cssVariablesCount: {
    type: Number,
    default: 0
  },
  textElementsCount: {
    type: Number,
    default: 0
  },
  layoutElementsCount: {
    type: Number,
    default: 0
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

// 获取状态样式类
const getStatusClass = (count) => {
  if (count === 0) return 'status-empty';
  if (count < 5) return 'status-low';
  return 'status-good';
};
</script>

<style scoped>
.status-indicator {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
}

.status-header {
  margin-bottom: 12px;
}

.status-header h4 {
  margin: 0;
  font-size: 1rem;
  color: var(--text-primary);
}

.status-items {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.status-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.status-value {
  font-size: 0.85rem;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 3px;
}

.status-empty {
  color: var(--error-color);
  background-color: rgba(239, 68, 68, 0.1);
}

.status-low {
  color: var(--warning-color);
  background-color: rgba(245, 158, 11, 0.1);
}

.status-good {
  color: var(--success-color);
  background-color: rgba(34, 197, 94, 0.1);
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
  border-top: 1px solid var(--border-color);
  margin-top: 10px;
  padding-top: 10px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color);
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 