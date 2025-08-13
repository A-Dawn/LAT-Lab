<template>
  <div v-if="visible" class="modal-overlay" @click="handleCancel">
    <div class="confirm-dialog" @click.stop role="dialog" aria-labelledby="dialog-title">
      <h3 id="dialog-title">{{ title }}</h3>
      <p>{{ message }}</p>
      
      <div class="dialog-actions">
        <button 
          @click="handleConfirm" 
          class="dialog-button confirm-button"
          :aria-label="confirmText"
        >
          {{ confirmText }}
        </button>
        <button 
          @click="handleCancel" 
          class="dialog-button cancel-button"
          :aria-label="cancelText"
        >
          {{ cancelText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '确认'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: '确认'
  },
  cancelText: {
    type: String,
    default: '取消'
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
/* 删除确认对话框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fade-in 0.2s ease;
}

.confirm-dialog {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slide-up 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.confirm-dialog h3 {
  color: var(--text-primary);
  margin-top: 0;
  margin-bottom: 15px;
}

.confirm-dialog p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.dialog-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.confirm-button {
  background-color: #f56c6c;
  color: white;
}

.confirm-button:hover {
  background-color: #f78989;
}

.cancel-button {
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.cancel-button:hover {
  background-color: var(--bg-hover);
}
</style> 