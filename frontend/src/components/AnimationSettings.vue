<template>
  <div class="animation-settings">
    <h3 class="settings-title">🎨 动画设置</h3>
    
    <div class="setting-group">
      <label class="setting-label">
        <input 
          type="checkbox" 
          v-model="localPreferences.enableAnimations"
          @change="updateSettings"
          class="setting-checkbox"
        />
        <span>启用页面切换动画</span>
      </label>
    </div>

    <div class="setting-group" v-if="localPreferences.enableAnimations">
      <label class="setting-label">动画速度</label>
      <select 
        v-model="localPreferences.animationSpeed" 
        @change="updateSettings"
        class="setting-select"
      >
        <option value="slow">慢速 (500ms)</option>
        <option value="normal">正常 (300ms)</option>
        <option value="fast">快速 (200ms)</option>
      </select>
    </div>

    <div class="performance-info" v-if="showPerformanceInfo">
      <h4>性能信息</h4>
      <ul>
        <li>减少动画偏好: {{ performanceInfo.prefersReducedMotion ? '是' : '否' }}</li>
        <li>低性能设备: {{ performanceInfo.isSlowDevice ? '是' : '否' }}</li>
        <li>当前动画: {{ performanceInfo.currentTransition }}</li>
        <li>动画时长: {{ performanceInfo.duration }}ms</li>
      </ul>
    </div>

    <button 
      @click="showPerformanceInfo = !showPerformanceInfo"
      class="toggle-info-btn"
    >
      {{ showPerformanceInfo ? '隐藏' : '显示' }}性能信息
    </button>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { usePageTransition } from '../composables/usePageTransition'

const { 
  userPreferences, 
  updatePreferences, 
  getPerformanceInfo 
} = usePageTransition()

const showPerformanceInfo = ref(false)
const performanceInfo = ref({})
const localPreferences = reactive({
  enableAnimations: true,
  animationSpeed: 'normal'
})

onMounted(() => {
  // 同步本地状态
  Object.assign(localPreferences, userPreferences.value)
  performanceInfo.value = getPerformanceInfo()
})

const updateSettings = () => {
  updatePreferences(localPreferences)
  performanceInfo.value = getPerformanceInfo()
}
</script>

<style scoped>
.animation-settings {
  padding: 20px;
  background: var(--bg-elevated, #fff);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-width: 400px;
}

.settings-title {
  margin: 0 0 20px 0;
  color: var(--text-primary, #333);
  font-size: 1.2rem;
  font-weight: 600;
}

.setting-group {
  margin-bottom: 16px;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  color: var(--text-primary, #333);
  cursor: pointer;
}

.setting-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color, #4c84ff);
}

.setting-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 6px;
  background: var(--bg-primary, #fff);
  color: var(--text-primary, #333);
  font-size: 0.9rem;
  margin-top: 5px;
}

.performance-info {
  margin-top: 20px;
  padding: 15px;
  background: var(--bg-secondary, #f8f9fa);
  border-radius: 8px;
  border-left: 3px solid var(--primary-color, #4c84ff);
}

.performance-info h4 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: var(--text-primary, #333);
}

.performance-info ul {
  margin: 0;
  padding-left: 20px;
  font-size: 0.85rem;
  color: var(--text-secondary, #666);
}

.performance-info li {
  margin-bottom: 5px;
}

.toggle-info-btn {
  background: var(--primary-color, #4c84ff);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  margin-top: 15px;
  transition: background-color 0.2s ease;
}

.toggle-info-btn:hover {
  background: var(--primary-hover, #3b73e6);
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .animation-settings {
    background: var(--bg-elevated, #2d3748);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  }
  
  .setting-select {
    background: var(--bg-primary, #1a202c);
    border-color: var(--border-color, #4a5568);
    color: var(--text-primary, #e2e8f0);
  }
  
  .performance-info {
    background: var(--bg-secondary, #1a202c);
  }
}
</style>
