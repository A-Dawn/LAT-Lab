<template>
  <div class="layout-editor">
    <div class="editor-header">
      <h3>布局调整器</h3>
      <p class="editor-description">
        调整页面元素的布局属性，所有更改将实时预览。
      </p>
    </div>
    
    <div class="layout-elements-container">
      <div v-if="!layoutElements.length" class="no-elements">
        <div class="no-elements-title">没有找到可调整的布局元素</div>
        <div class="no-elements-hint">
          请确保：<br>
          • 已选择正确的页面<br>
          • 页面已完全加载<br>
          • 页面包含可调整的布局元素
        </div>
        <button class="refresh-button" @click="$emit('refresh')">
          刷新页面元素
        </button>
      </div>
      
      <div v-else class="elements-list">
        <div 
          v-for="element in layoutElements" 
          :key="element.id"
          class="layout-element-item"
        >
          <div class="element-header">
            <div class="element-info">
              <label :for="element.id">{{ element.description }}</label>
              <div class="element-details">
                <code>{{ element.selector }}</code>
                <span class="property-badge">{{ element.property }}</span>
              </div>
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
            <!-- 特殊值处理：max-width 可以设置为 none -->
            <div v-if="element.property === 'max-width'" class="special-value-control">
              <label class="special-value-label">
                <input 
                  type="checkbox" 
                  :checked="element.currentValue === 'none'"
                  @change="handleSpecialValueToggle(element)"
                />
                <span>移除最大宽度限制 (设置为 none)</span>
              </label>
            </div>
            
            <div v-if="element.currentValue !== 'none'" class="slider-container">
              <input 
                :id="element.id"
                type="range" 
                :min="element.min" 
                :max="element.max" 
                :value="parseValueNumber(element.currentValue)" 
                @input="updateLayout(element.id, $event.target.value)"
                class="slider"
              />
              <div class="slider-value">
                <input 
                  type="number" 
                  :min="element.min" 
                  :max="element.max" 
                  :value="parseValueNumber(element.currentValue)" 
                  @input="updateLayout(element.id, $event.target.value)"
                  class="number-input"
                />
                <span class="unit">{{ element.unit }}</span>
              </div>
            </div>
          </div>
          
          <div class="element-preview">
            <div class="preview-label">当前值:</div>
            <div class="preview-content">{{ element.currentValue === 'none' ? 'none (无限制)' : element.currentValue }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  layoutElements: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update-layout', 'refresh']);

// 解析值为数字（去掉单位）
const parseValueNumber = (value) => {
  if (typeof value === 'string') {
    // 处理特殊值
    if (value === 'none' || value === 'auto' || value === 'inherit' || value === 'initial') {
      return 0;
    }
    // 提取数值部分（支持负数和小数）
    const match = value.match(/^([-+]?\d*\.?\d+)/);
    if (match) {
      return parseFloat(match[1]) || 0;
    }
    return parseInt(value.replace(/[^\d.-]/g, '')) || 0;
  }
  return value;
};

// 更新布局属性
const updateLayout = (id, value) => {
  emit('update-layout', { id, value });
};

// 重置布局属性到原始值
const resetElement = (id) => {
  const element = props.layoutElements.find(el => el.id === id);
  if (element) {
    // 如果原始值是特殊值（如 'none'），直接使用原始值
    if (element.originalValue === 'none' || element.originalValue === 'auto') {
      emit('update-layout', { id, value: element.originalValue });
    } else {
    updateLayout(id, parseValueNumber(element.originalValue));
    }
  }
};

// 处理特殊值切换（如 max-width: none）
const handleSpecialValueToggle = (element) => {
  if (element.currentValue === 'none') {
    // 从 none 切换回数值：使用原始值或默认值
    const defaultValue = element.originalValue !== 'none' 
      ? parseValueNumber(element.originalValue) 
      : 1200; // 默认值
    updateLayout(element.id, defaultValue);
  } else {
    // 切换到 none
    emit('update-layout', { id: element.id, value: 'none' });
  }
};
</script>

<style scoped>
.layout-editor {
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

.layout-elements-container {
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

.layout-element-item {
  background-color: var(--bg-secondary);
  border-radius: 6px;
  padding: 15px;
  border: 1px solid var(--border-color);
}

.element-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
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

.element-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.element-details code {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  background-color: var(--bg-hover);
  padding: 2px 5px;
  border-radius: 3px;
}

.property-badge {
  background-color: var(--primary-color);
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 10px;
}

.element-input {
  margin-bottom: 15px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.slider {
  flex: 1;
  -webkit-appearance: none;
  height: 6px;
  background: var(--bg-hover);
  border-radius: 3px;
  outline: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s;
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider::-moz-range-thumb:hover {
  transform: scale(1.2);
}

.slider-value {
  display: flex;
  align-items: center;
  min-width: 80px;
}

.number-input {
  width: 50px;
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  text-align: right;
}

.number-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.unit {
  margin-left: 5px;
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.element-preview {
  background-color: var(--bg-primary);
  border-radius: 4px;
  padding: 10px;
  border: 1px dashed var(--border-color);
  display: flex;
  align-items: center;
}

.preview-label {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  margin-right: 10px;
}

.preview-content {
  color: var(--text-primary);
  font-weight: 500;
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

.special-value-control {
  margin-bottom: 15px;
  padding: 12px;
  background-color: var(--bg-elevated);
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.special-value-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--text-primary);
}

.special-value-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--primary-color);
  cursor: pointer;
}

.special-value-label span {
  user-select: none;
}

@media (max-width: 768px) {
  .element-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .element-header button {
    align-self: flex-end;
  }
  
  .slider-container {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .slider-value {
    align-self: flex-end;
  }
}
</style> 