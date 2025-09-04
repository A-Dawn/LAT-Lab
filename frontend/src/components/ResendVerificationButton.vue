<template>
  <div class="resend-verification-container">
    <button 
      @click="handleResend" 
      :disabled="isResending || countdown > 0" 
      class="resend-button"
      :class="{ 'disabled': isResending || countdown > 0 }"
    >
      <span v-if="isResending">发送中...</span>
      <span v-else-if="countdown > 0">{{ countdown }}秒后可重发</span>
      <span v-else>{{ buttonText }}</span>
    </button>
    
    <div v-if="status === 'success'" class="status-message success">
      {{ successMessage }}
    </div>
    
    <div v-if="status === 'error'" class="status-message error">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { resendVerificationEmail } from '../services/api'

const props = defineProps({
  email: {
    type: String,
    required: true
  },
  buttonText: {
    type: String,
    default: '重新发送验证邮件'
  },
  successMessage: {
    type: String,
    default: '验证邮件已重新发送，请稍等片刻并查收'
  }
})

const emit = defineEmits(['success', 'error'])

const isResending = ref(false)
const countdown = ref(0)
const status = ref('')
const errorMessage = ref('')

let countdownTimer = null

// 从localStorage获取上次发送时间
const getLastSentTime = () => {
  const lastSent = localStorage.getItem(`verification_last_sent_${props.email}`)
  return lastSent ? parseInt(lastSent) : 0
}

// 保存发送时间到localStorage
const saveSentTime = () => {
  localStorage.setItem(`verification_last_sent_${props.email}`, Date.now().toString())
}

// 计算剩余倒计时时间
const calculateRemainingTime = () => {
  const lastSent = getLastSentTime()
  const now = Date.now()
  const elapsed = Math.floor((now - lastSent) / 1000)
  const remaining = Math.max(0, 180 - elapsed)
  return remaining
}

// 开始倒计时
const startCountdown = () => {
  countdown.value = 180
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

// 处理重发请求
const handleResend = async () => {
  if (isResending.value || countdown.value > 0) {
    return
  }

  isResending.value = true
  status.value = ''
  errorMessage.value = ''

  try {
    await resendVerificationEmail(props.email)
    status.value = 'success'
    saveSentTime()
    startCountdown()
    emit('success')
    
    // 3秒后清除成功消息
    setTimeout(() => {
      status.value = ''
    }, 3000)
  } catch (error) {
    status.value = 'error'
    errorMessage.value = error.response?.data?.detail || '发送失败，请稍后重试'
    emit('error', error)
  } finally {
    isResending.value = false
  }
}

// 组件挂载时检查是否需要倒计时
onMounted(() => {
  const remaining = calculateRemainingTime()
  if (remaining > 0) {
    countdown.value = remaining
    startCountdown()
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.resend-verification-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resend-button {
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  min-width: 200px;
}

.resend-button:hover:not(.disabled) {
  background-color: var(--primary-hover);
}

.resend-button.disabled {
  background-color: rgba(var(--primary-color-rgb), 0.5);
  cursor: not-allowed;
}

.status-message {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
}

.status-message.success {
  background-color: rgba(var(--success-color-rgb), 0.1);
  color: var(--success-color);
  border: 1px solid rgba(var(--success-color-rgb), 0.3);
}

.status-message.error {
  background-color: rgba(var(--error-color-rgb), 0.1);
  color: var(--error-color);
  border: 1px solid rgba(var(--error-color-rgb), 0.3);
}
</style> 