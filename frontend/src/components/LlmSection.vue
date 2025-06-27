<!--
  @component LlmSection
  @description LLM (Large Language Model) 查询功能组件，允许用户与AI模型交互
  @props {Array} modelList - 可用的AI模型列表
  @props {Boolean} isLoading - 是否正在加载AI响应
  @props {String} response - AI响应内容
  @emits {query} - 当用户发送查询时触发，带有prompt和model参数
-->
<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  // 模型列表，格式为 [{value: 'model_id', name: 'Model Name'}, ...]
  modelList: {
    type: Array,
    default: () => []
  },
  // 加载状态
  isLoading: {
    type: Boolean,
    default: false
  },
  // AI响应内容
  response: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['query']);

// 用户输入的提示词
const promptInput = ref('');
// 选择的模型
const selectedModel = ref('google/gemini-2.5-flash-lite-preview-06-17');

// 当模型列表变化时，如果列表非空，设置默认选中第一个模型
watch(() => props.modelList, (newList) => {
  if (newList && newList.length > 0) {
    selectedModel.value = newList[0].value;
  }
}, { immediate: true });

/**
 * 发送AI查询
 * 验证输入并触发查询事件
 */
const sendQuery = () => {
  if (!promptInput.value.trim()) {
    return; // 不发送空查询
  }
  
  emit('query', {
    prompt: promptInput.value,
    model: selectedModel.value
  });
};

/**
 * 重置表单
 * 清空输入和响应
 */
const resetForm = () => {
  promptInput.value = '';
};
</script>

<template>
  <div class="llm-section">
    <!-- 组件标题 -->
    <h3 class="llm-title">AI助手</h3>
    
    <div class="llm-container">
      <!-- 模型选择器 -->
      <div class="model-selector">
        <label for="model-select">选择AI模型：</label>
        <select 
          id="model-select" 
          v-model="selectedModel"
          class="model-select"
          aria-label="选择AI模型"
          :disabled="isLoading"
        >
          <option 
            v-for="model in modelList" 
            :key="model.value" 
            :value="model.value"
          >
            {{ model.name }}
          </option>
        </select>
      </div>
      
      <!-- 提示输入区域 -->
      <div class="prompt-area">
        <label for="prompt-input">输入你的问题：</label>
        <textarea 
          id="prompt-input"
          v-model="promptInput"
          class="prompt-input"
          rows="4"
          placeholder="例如：如何学习Vue.js？请推荐一些学习资源..."
          :disabled="isLoading"
          @keydown.ctrl.enter="sendQuery"
        ></textarea>
        <div class="hint">提示：按Ctrl+Enter快速发送</div>
      </div>
      
      <!-- 控制按钮 -->
      <div class="controls">
        <button 
          class="reset-button"
          @click="resetForm"
          :disabled="isLoading || !promptInput"
          aria-label="重置输入"
        >
          清空
        </button>
        
        <button 
          class="send-button"
          @click="sendQuery"
          :disabled="isLoading || !promptInput"
          aria-label="发送查询"
        >
          <span v-if="isLoading">
            <span class="loading-dot">.</span>
            <span class="loading-dot">.</span>
            <span class="loading-dot">.</span>
          </span>
          <span v-else>发送查询</span>
        </button>
      </div>
      
      <!-- 响应区域 -->
      <div 
        v-if="response" 
        class="response-area"
        aria-live="polite"
        aria-label="AI响应"
      >
        <h4>AI响应：</h4>
        <div class="response-content">
          <!-- 使用白色空格保留格式 -->
          <pre>{{ response }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* LLM 部分样式 */
.llm-section {
  background-color: var(--card-bg, white);
  border-radius: 12px;
  border: 1px solid var(--border-color, #ebeef5);
  box-shadow: var(--card-shadow, 0 2px 12px rgba(0, 0, 0, 0.1));
  margin-bottom: 25px;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.llm-section:hover {
  box-shadow: var(--card-shadow-hover);
}

.llm-title {
  padding: 18px 20px;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color, #ebeef5);
  color: var(--text-primary, #303133);
  letter-spacing: -0.01em;
}

.llm-container {
  padding: 20px;
}

/* 模型选择器 */
.model-selector {
  margin-bottom: 15px;
}

.model-selector label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.model-select {
  width: 100%;
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg, white);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: border-color 0.3s;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 1em;
}

.model-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.2);
}

/* 提示输入区域 */
.prompt-area {
  margin-bottom: 15px;
}

.prompt-area label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.prompt-input {
  width: 100%;
  padding: 12px 15px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg, white);
  color: var(--text-primary);
  font-size: 0.95rem;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s, box-shadow 0.3s;
  font-family: inherit;
}

.prompt-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.2);
}

.hint {
  margin-top: 5px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: right;
}

/* 控制按钮 */
.controls {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-bottom: 20px;
}

.reset-button, 
.send-button {
  padding: 10px 20px;
  border-radius: 30px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.reset-button {
  background-color: var(--button-bg);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.send-button {
  background-color: var(--primary-color);
  color: white;
  min-width: 120px;
}

.reset-button:hover:not(:disabled) {
  background-color: var(--hover-color);
}

.send-button:hover:not(:disabled) {
  background-color: var(--secondary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.reset-button:disabled,
.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载动画 */
.loading-dot {
  animation: loadingDots 1.4s infinite;
  display: inline-block;
}

.loading-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes loadingDots {
  0%, 100% {
    opacity: 0.2;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-5px);
  }
}

/* 响应区域 */
.response-area {
  margin-top: 5px;
  border-top: 1px solid var(--border-color);
  padding-top: 15px;
}

.response-area h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: var(--text-primary);
  font-weight: 600;
  padding-left: 5px;
  border-left: 3px solid var(--primary-color);
}

.response-content {
  background-color: var(--code-bg, rgba(0, 0, 0, 0.03));
  border-radius: 8px;
  padding: 20px;
  overflow-x: auto;
  box-shadow: inset 0 1px 5px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
  line-height: 1.7;
  font-size: 0.95rem;
  position: relative;
}

/* 深色主题的响应区域 */
:root[data-theme="dark"] .response-content {
  background-color: rgba(0, 0, 0, 0.2);
  box-shadow: inset 0 1px 5px rgba(0, 0, 0, 0.2);
}

/* 霓虹主题的响应区域 */
:root[data-theme="neon"] .response-content {
  border-color: rgba(var(--primary-rgb), 0.2);
  background-color: rgba(0, 0, 0, 0.15);
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  line-height: 1.6;
  color: var(--text-primary);
}

/* 霓虹主题特殊样式 */
:root[data-theme="neon"] .send-button {
  box-shadow: var(--glow-primary);
}

:root[data-theme="neon"] .model-select:focus,
:root[data-theme="neon"] .prompt-input:focus {
  box-shadow: var(--glow-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    gap: 10px;
  }
  
  .reset-button, 
  .send-button {
    width: 100%;
  }
}
</style> 