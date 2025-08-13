<template>
  <div class="style-editor">
    <div class="editor-header">
      <h3>CSS变量编辑器</h3>
      <p class="editor-description">
        修改下面的CSS变量来自定义网站样式。所有更改将实时预览。
      </p>
    </div>
    
    <div class="variables-container">
      <div v-if="!cssVariables.length" class="no-variables">
        <div class="no-variables-title">没有找到可编辑的CSS变量</div>
        <div class="no-variables-hint">
          请确保：<br>
          • 已选择正确的页面<br>
          • 页面已完全加载<br>
          • 页面包含主题CSS变量
        </div>
        <button class="refresh-button" @click="$emit('refresh')">
          刷新页面元素
        </button>
      </div>
      
      <div v-else class="variables-grid">
        <div 
          v-for="variable in cssVariables" 
          :key="variable.name"
          class="variable-item"
        >
          <div class="variable-header">
            <label :for="variable.name.replace('--', '')">{{ formatVariableName(variable.name) }}</label>
            <code>{{ variable.name }}</code>
          </div>
          
          <div class="variable-input">
            <!-- 颜色变量使用颜色选择器 -->
            <div v-if="variable.type === 'color'" class="color-input-group">
              <input 
                :id="variable.name.replace('--', '')"
                type="color" 
                :value="variable.value" 
                @input="updateVariable(variable.name, $event.target.value)"
                class="color-picker"
              />
              <input 
                type="text" 
                :value="variable.value" 
                @input="updateVariable(variable.name, $event.target.value)"
                class="color-text"
              />
            </div>
            
            <!-- 其他变量使用文本输入框 -->
            <input 
              v-else
              :id="variable.name.replace('--', '')"
              type="text" 
              :value="variable.value" 
              @input="updateVariable(variable.name, $event.target.value)"
            />
          </div>
          
          <div class="variable-actions">
            <button 
              class="reset-button" 
              @click="resetVariable(variable.name)"
              :disabled="variable.value === variable.originalValue"
            >
              重置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  cssVariables: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update-variable', 'refresh']);

// 格式化变量名，使其更易读
const formatVariableName = (name) => {
  return name
    .replace('--', '')
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// 更新变量值
const updateVariable = (name, value) => {
  emit('update-variable', { name, value });
};

// 重置变量到原始值
const resetVariable = (name) => {
  const variable = props.cssVariables.find(v => v.name === name);
  if (variable) {
    updateVariable(name, variable.originalValue);
  }
};
</script>

<style scoped>
.style-editor {
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

.variables-container {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

.no-variables {
  padding: 20px;
  text-align: center;
  color: var(--text-tertiary);
  background-color: var(--bg-secondary);
  border-radius: 6px;
}

.no-variables-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.no-variables-hint {
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

.variables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.variable-item {
  background-color: var(--bg-secondary);
  border-radius: 6px;
  padding: 15px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.variable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.variable-header label {
  font-weight: 500;
  color: var(--text-primary);
}

.variable-header code {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  background-color: var(--bg-hover);
  padding: 2px 5px;
  border-radius: 3px;
}

.variable-input {
  width: 100%;
}

.variable-input input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
}

.variable-input input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

.color-input-group {
  display: flex;
  gap: 10px;
}

.color-picker {
  width: 40px !important;
  height: 40px;
  padding: 2px;
  border-radius: 4px;
  cursor: pointer;
}

.color-text {
  flex: 1;
}

.variable-actions {
  display: flex;
  justify-content: flex-end;
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
  .variables-grid {
    grid-template-columns: 1fr;
  }
}
</style> 