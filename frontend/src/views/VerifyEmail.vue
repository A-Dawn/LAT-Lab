<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { verifyEmail } from '../services/api'

const route = useRoute()
const router = useRouter()

const status = ref('verifying') // verifying, success, error
const message = ref('')
const countdown = ref(5)
const token = ref('')

onMounted(async () => {
  // 从URL获取验证令牌，并进行基本验证
  const rawToken = route.query.token;
  
  // 验证令牌格式 - 只允许字母数字和有限的特殊字符
  if (!rawToken || typeof rawToken !== 'string' || !/^[a-zA-Z0-9_\-\.]+$/.test(rawToken)) {
    status.value = 'error'
    message.value = '验证链接无效，缺少验证令牌或令牌格式错误'
    return
  }
  
  token.value = rawToken;
  console.log('获取到有效的验证令牌')
  
  try {
    // 调用验证API
    const response = await verifyEmail(token.value)
    console.log('验证响应:', response)
    
    // 验证成功
    status.value = 'success'
    message.value = '邮箱验证成功！'
    
    // 清除本地存储中可能存在的错误状态
    localStorage.removeItem('verification_error')
    
    // 设置刚刚验证成功的标记
    localStorage.setItem('just_verified', 'true')
    
    // 倒计时后跳转到登录页
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
        router.push('/login?verified=true')
      }
    }, 1000)
    
  } catch (error) {
    // 验证失败
    console.error('验证失败:', error)
    status.value = 'error'
    message.value = error.response?.data?.detail || '验证失败，请重试'
    
    // 存储错误状态到本地存储
    localStorage.setItem('verification_error', 'true')
  }
})
</script>

<template>
  <div class="verify-email-page">
    <div class="verify-container">
      <div class="verify-box">
        <!-- 验证中 -->
        <div v-if="status === 'verifying'" class="verifying">
          <div class="spinner-container">
            <div class="spinner"></div>
          </div>
          <h2>正在验证您的邮箱...</h2>
          <p>请稍候，这可能需要几秒钟时间。</p>
        </div>
        
        <!-- 验证成功 -->
        <div v-else-if="status === 'success'" class="success">
          <div class="icon-success">✓</div>
          <h2>邮箱验证成功！</h2>
          <p>您的账号已激活，现在可以登录使用所有功能。</p>
          <div class="progress-bar">
            <div class="progress" :style="{width: (countdown / 5 * 100) + '%'}"></div>
          </div>
          <p class="countdown">{{ countdown }}秒后自动跳转到登录页...</p>
          <button @click="router.push('/login')" class="login-button">立即登录</button>
        </div>
        
        <!-- 验证失败 -->
        <div v-else class="error">
          <div class="icon-error">✗</div>
          <h2>验证失败</h2>
          <p>{{ message }}</p>
          <div class="actions">
            <button @click="router.push('/login')" class="login-button">返回登录</button>
            <button @click="router.push('/')" class="home-button">返回首页</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.verify-email-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--hero-gradient);
}

.verify-container {
  width: 100%;
  max-width: 500px;
  padding: 20px;
}

.verify-box {
  background-color: var(--card-bg);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  padding: 40px;
  text-align: center;
}

.spinner-container {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  position: relative;
}

.spinner {
  width: 80px;
  height: 80px;
  border: 5px solid rgba(var(--primary-color-rgb, 76, 132, 255), 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  position: absolute;
  top: 0;
  left: 0;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.icon-success {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: var(--success-color);
  color: white;
  font-size: 40px;
  line-height: 70px;
  margin: 0 auto 20px;
}

.icon-error {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: var(--error-color);
  color: white;
  font-size: 40px;
  line-height: 70px;
  margin: 0 auto 20px;
}

h2 {
  font-size: 24px;
  margin-bottom: 15px;
  color: var(--text-primary);
}

p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.countdown {
  color: var(--text-tertiary);
  font-size: 14px;
  margin-bottom: 20px;
}

.progress-bar {
  height: 6px;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
  margin-bottom: 10px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: var(--primary-color);
  border-radius: 3px;
  transition: width 1s linear;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.login-button,
.home-button {
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.login-button {
  background-color: var(--primary-color);
  color: white;
}

.home-button {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.login-button:hover {
  background-color: var(--primary-hover);
}

.home-button:hover {
  background-color: var(--bg-tertiary);
}
</style> 