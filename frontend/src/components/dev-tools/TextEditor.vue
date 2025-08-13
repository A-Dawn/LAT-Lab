<template>
  <div class="text-editor">
    <div class="editor-header">
      <h3>文本内容编辑器</h3>
      <p class="editor-description">
        修改页面上的文本内容，所有更改将实时预览。
      </p>
    </div>
    
    <div class="text-elements-container">
      <div v-if="!textElements.length" class="no-elements">
        <div class="no-elements-title">没有找到可编辑的文本元素</div>
        <div class="no-elements-hint">
          请确保：<br>
          • 已选择正确的页面<br>
          • 页面已完全加载<br>
          • 页面包含可编辑的文本内容
        </div>
        <button class="refresh-button" @click="$emit('refresh')">
          刷新页面元素
        </button>
      </div>
      
      <div v-else class="elements-list">
        <div 
          v-for="element in textElements" 
          :key="element.id"
          class="text-element-item"
        >
          <div class="element-header">
            <div class="element-info">
              <label :for="element.id">{{ element.description }}</label>
              <code>{{ element.selector }}</code>
            </div>
            <button 
              class="reset-button" 
              @click="resetElement(element.id)"
              :disabled="element.currentValue === element.originalValue"
            >
              重置
            </button>
          </div>
          
          <div class="element-input">
            <textarea 
              :id="element.id"
              :value="element.currentValue" 
              @input="updateText(element.id, $event.target.value)"
              rows="2"
            ></textarea>
          </div>
          
          <div class="element-preview">
            <div class="preview-label">预览:</div>
            <div class="preview-content">{{ element.currentValue }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  textElements: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update-text', 'refresh']);

// 更新文本内容
const updateText = (id, value) => {
  emit('update-text', { id, value });
};

// 重置文本到原始值
const resetElement = (id) => {
  const element = props.textElements.find(el => el.id === id);
  if (element) {
    updateText(id, element.originalValue);
  }
};
</script>

<style scoped>
.text-editor {
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

.text-elements-container {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

.no-elements {
  padding: 20px;
  text-align: center;
  color: var(--text-tertiary);
  background-color: var(--bg-secondary);
  border-radius: 6px;
}

.no-elements-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.no-elements-hint {
  font-size: 0.85rem;
  line-height: 1.4;
  text-align: left;
  display: inline-block;
}

.refresh-button {
  margin-top: 12px;
  padding: 6px 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.refresh-button:hover {
  background-color: var(--primary-dark);
}

.elements-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.text-element-item {
  background-color: var(--bg-secondary);
  border-radius: 6px;
  padding: 15px;
  border: 1px solid var(--border-color);
}

.element-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.element-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.element-info label {
  font-weight: 500;
  color: var(--text-primary);
}

.element-info code {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  background-color: var(--bg-hover);
  padding: 2px 5px;
  border-radius: 3px;
}

.element-input {
  margin-bottom: 10px;
}

.element-input textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  font-family: inherit;
  resize: vertical;
}

.element-input textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

.element-preview {
  background-color: var(--bg-primary);
  border-radius: 4px;
  padding: 10px;
  border: 1px dashed var(--border-color);
}

.preview-label {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  margin-bottom: 5px;
}

.preview-content {
  color: var(--text-primary);
  word-break: break-word;
}

.reset-button {
  padding: 4px 10px;
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.reset-button:hover:not(:disabled) {
  background-color: var(--bg-hover);
}

.reset-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .element-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .element-header button {
    align-self: flex-end;
  }
}
</style> 