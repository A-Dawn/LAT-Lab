<template>
  <Teleport to="body">
    <div v-if="visible" class="toast-container" :class="typeClass">
      <div class="toast-content">
        <div class="toast-icon">
          <span v-if="type === 'success'">✓</span>
          <span v-else-if="type === 'error'">✗</span>
          <span v-else-if="type === 'warning'">!</span>
          <span v-else>ℹ</span>
        </div>
        <div class="toast-message">{{ message }}</div>
        <button v-if="closable" @click="close" class="toast-close" aria-label="关闭">×</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  duration: {
    type: Number,
    default: 3000
  },
  closable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)

const typeClass = computed(() => `toast-${props.type}`)

const close = () => {
  visible.value = false
  emit('close')
}

onMounted(() => {
  visible.value = true
  
  if (props.duration > 0) {
    setTimeout(() => {
      close()
    }, props.duration)
  }
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  animation: toast-slide-in 0.3s ease;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 500px;
}

.toast-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
}

.toast-message {
  flex: 1;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.4;
}

.toast-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: var(--text-tertiary);
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.toast-close:hover {
  background-color: var(--hover-color);
  color: var(--text-secondary);
}

/* 成功类型 */
.toast-success .toast-icon {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.toast-success .toast-content {
  border-left: 4px solid #22c55e;
}

/* 错误类型 */
.toast-error .toast-icon {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.toast-error .toast-content {
  border-left: 4px solid #ef4444;
}

/* 警告类型 */
.toast-warning .toast-icon {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.toast-warning .toast-content {
  border-left: 4px solid #f59e0b;
}

/* 信息类型 */
.toast-info .toast-icon {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.toast-info .toast-content {
  border-left: 4px solid #3b82f6;
}

@keyframes toast-slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .toast-success .toast-icon {
    color: #4ade80;
  }
  
  .toast-success .toast-content {
    border-left-color: #4ade80;
  }
  
  .toast-error .toast-icon {
    color: #f87171;
  }
  
  .toast-error .toast-content {
    border-left-color: #f87171;
  }
  
  .toast-warning .toast-icon {
    color: #fbbf24;
  }
  
  .toast-warning .toast-content {
    border-left-color: #fbbf24;
  }
  
  .toast-info .toast-icon {
    color: #60a5fa;
  }
  
  .toast-info .toast-content {
    border-left-color: #60a5fa;
  }
}
</style> 