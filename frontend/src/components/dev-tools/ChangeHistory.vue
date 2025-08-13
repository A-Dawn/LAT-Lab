<template>
  <div class="change-history">
    <div class="editor-header">
      <h3>修改历史</h3>
      <p class="editor-description">
        查看和管理所有修改历史，可以撤销特定的修改。
      </p>
    </div>
    
    <div class="history-container">
      <div v-if="!changes.length" class="no-changes">
        暂无修改历史
      </div>
      
      <div v-else class="changes-list">
        <div 
          v-for="(change, index) in changes" 
          :key="index"
          class="change-item"
        >
          <div class="change-info">
            <div class="change-type" :class="change.type">
              {{ getChangeTypeLabel(change.type) }}
            </div>
            <div class="change-details">
              <div class="change-target">
                {{ getChangeTarget(change) }}
              </div>
              <div class="change-values">
                <div class="old-value">
                  <span class="value-label">原值:</span>
                  <code>{{ change.oldValue }}</code>
                </div>
                <div class="arrow">→</div>
                <div class="new-value">
                  <span class="value-label">新值:</span>
                  <code>{{ change.newValue }}</code>
                </div>
              </div>
            </div>
          </div>
          
          <div class="change-actions">
            <div class="change-time">
              {{ formatTime(change.timestamp) }}
            </div>
            <button 
              class="revert-button" 
              @click="revertChange(change)"
            >
              撤销
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  changes: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['revert']);

// 获取变更类型标签
const getChangeTypeLabel = (type) => {
  const labels = {
    'style': '样式',
    'text': '文本',
    'layout': '布局'
  };
  return labels[type] || type;
};

// 获取变更目标
const getChangeTarget = (change) => {
  if (change.type === 'style') {
    return change.name;
  } else if (change.type === 'text') {
    return change.selector;
  } else if (change.type === 'layout') {
    return `${change.selector} (${change.property})`;
  }
  return '';
};

// 格式化时间
const formatTime = (timestamp) => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch (error) {
    return '未知时间';
  }
};

// 撤销变更
const revertChange = (change) => {
  emit('revert', change);
};
</script>

<style scoped>
.change-history {
  width: 100%;
}

.editor-header {
  margin-bottom: 20px;
}

.editor-header h3 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.editor-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.history-container {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

.no-changes {
  padding: 20px;
  text-align: center;
  color: var(--text-tertiary);
  background-color: var(--bg-secondary);
  border-radius: 6px;
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.change-item {
  background-color: var(--bg-secondary);
  border-radius: 6px;
  padding: 15px;
  border: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.change-info {
  flex: 1;
  display: flex;
  gap: 15px;
}

.change-type {
  font-size: 0.8rem;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  min-width: 50px;
  text-align: center;
}

.change-type.style {
  background-color: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
}

.change-type.text {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.change-type.layout {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.change-details {
  flex: 1;
}

.change-target {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
  word-break: break-all;
}

.change-values {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.old-value, .new-value {
  display: flex;
  align-items: center;
  gap: 5px;
}

.value-label {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.change-values code {
  font-size: 0.85rem;
  color: var(--text-secondary);
  background-color: var(--bg-hover);
  padding: 2px 5px;
  border-radius: 3px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow {
  color: var(--text-tertiary);
  font-size: 1rem;
}

.change-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.change-time {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.revert-button {
  padding: 4px 10px;
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.revert-button:hover {
  background-color: var(--bg-hover);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

@media (max-width: 768px) {
  .change-item {
    flex-direction: column;
    gap: 15px;
  }
  
  .change-info {
    width: 100%;
  }
  
  .change-actions {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}
</style> 