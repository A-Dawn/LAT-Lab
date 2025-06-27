<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { resendVerificationEmail } from '../services/api'

const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')
const needVerification = ref(false)
const successMsg = ref('')
const router = useRouter()
const route = useRoute()
const store = useStore()

// 添加重新发送验证邮件相关的状态
const showResendForm = ref(false)
const resendEmail = ref('')
const resendStatus = ref('') // 'success', 'error', ''
const resendMessage = ref('')
const isResending = ref(false)

// 检查URL中是否有错误消息
onMounted(() => {
  if (route.query.message) {
    errorMsg.value = route.query.message
  }
  
  // 检查是否刚刚完成邮箱验证
  if (route.query.verified === 'true') {
    successMsg.value = '邮箱验证成功，请登录'
  }
  
  // 检查本地存储中的验证状态
  const justVerified = localStorage.getItem('just_verified')
  if (justVerified) {
    successMsg.value = '邮箱验证成功，请登录'
    localStorage.removeItem('just_verified')
  }
})

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  
  try {
    isLoading.value = true
    errorMsg.value = ''
    successMsg.value = ''
    
    // 使用Vuex的login action
    await store.dispatch('login', {
      username: username.value,
      password: password.value
    })
    
    // 如果选择了"记住我"，可以设置更长的过期时间
    if (rememberMe.value) {
      localStorage.setItem('remember', 'true')
    }
    
    // 登录成功后跳转到首页或重定向页面
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (error) {
    console.error('登录失败:', error)
    
    // 检查是否是邮箱未验证错误
    if (error.response && error.response.status === 403 && 
        error.response.data.detail && error.response.data.detail.includes('验证您的邮箱')) {
      needVerification.value = true
      errorMsg.value = '请先验证您的邮箱后再登录'
      // 自动填充邮箱地址到重发验证邮件表单
      showResendForm.value = true
      // 尝试从用户名中提取邮箱
      if (username.value.includes('@')) {
        resendEmail.value = username.value
      }
    } else {
      needVerification.value = false
      errorMsg.value = error.response?.data?.detail || '登录失败，请检查用户名和密码'
    }
  } finally {
    isLoading.value = false
  }
}

// 重新发送验证邮件
const handleResendVerification = async () => {
  if (!resendEmail.value) {
    resendStatus.value = 'error'
    resendMessage.value = '请输入邮箱地址'
    return
  }
  
  isResending.value = true
  resendStatus.value = ''
  
  try {
    await resendVerificationEmail(resendEmail.value)
    resendStatus.value = 'success'
    resendMessage.value = '验证邮件已重新发送，请查收'
  } catch (error) {
    resendStatus.value = 'error'
    resendMessage.value = error.response?.data?.detail || '发送失败，请稍后重试'
  } finally {
    isResending.value = false
  }
}

// 切换重新发送表单的显示状态
const toggleResendForm = () => {
  showResendForm.value = !showResendForm.value
  if (!showResendForm.value) {
    resendEmail.value = ''
    resendStatus.value = ''
    resendMessage.value = ''
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box">
        <div class="login-header">
          <h2>登录</h2>
          <p>欢迎回来，请登录您的账号</p>
        </div>
        
        <form @submit.prevent="handleSubmit" class="login-form">
          <div v-if="errorMsg" class="error-message">
            {{ errorMsg }}
          </div>
          
          <div v-if="successMsg" class="success-message">
            {{ successMsg }}
          </div>
          
          <div class="form-group">
            <label for="username">用户名</label>
            <input 
              id="username"
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="请输入密码"
              required
            />
          </div>
          
          <div class="login-options">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe"> 记住我
            </label>
            <a href="#" class="forgot-password">忘记密码?</a>
          </div>
          
          <button 
            type="submit" 
            :disabled="isLoading" 
            class="login-button"
          >
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </form>
        
        <!-- 验证提醒区域优化 -->
        <div v-if="needVerification" class="verification-reminder">
          <div class="reminder-icon">!</div>
          <div class="reminder-content">
            <h3>邮箱未验证</h3>
            <p>您的邮箱尚未验证，请先验证邮箱后再登录。</p>
            <button @click="toggleResendForm" class="resend-button">
              {{ showResendForm ? '取消' : '重新发送验证邮件' }}
            </button>
          </div>
        </div>
        
        <!-- 重新发送验证邮件表单优化 -->
        <div v-if="showResendForm" class="resend-form">
          <div class="form-group">
            <label for="resendEmail">邮箱地址</label>
            <input
              type="email"
              id="resendEmail"
              v-model="resendEmail"
              placeholder="请输入您注册时使用的邮箱"
              required
            />
          </div>
          
          <div v-if="resendStatus === 'success'" class="resend-success">
            <div class="status-icon">✓</div>
            <p>{{ resendMessage }}</p>
          </div>
          
          <div v-if="resendStatus === 'error'" class="resend-error">
            <div class="status-icon">✗</div>
            <p>{{ resendMessage }}</p>
          </div>
          
          <button
            @click="handleResendVerification"
            :disabled="isResending"
            class="resend-button full-width"
          >
            {{ isResending ? '发送中...' : '重新发送验证邮件' }}
          </button>
        </div>
        
        <!-- 底部链接区域 -->
        <div class="register-link">
          <p>还没有账号? <router-link to="/register">立即注册</router-link></p>
        </div>
        
        <!-- 重新发送验证邮件链接 -->
        <div v-if="!needVerification && !showResendForm" class="resend-verification">
          <a href="#" @click.prevent="toggleResendForm">
            没有收到验证邮件？点击重新发送
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--hero-gradient, linear-gradient(135deg, #4c84ff 0%, #2861ff 100%));
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-box {
  background-color: var(--card-bg, #fff);
  color: var(--text-primary);
  border-radius: 10px;
  box-shadow: var(--card-shadow, 0 5px 20px rgba(0, 0, 0, 0.1));
  padding: 30px;
  border: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 2rem;
  color: var(--text-primary, #303133);
  margin-bottom: 10px;
}

.login-header p {
  color: var(--text-secondary, #909399);
  font-size: 1rem;
}

.error-message {
  background-color: rgba(245, 108, 108, 0.1);
  color: var(--error-color, #f56c6c);
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  text-align: center;
}

.success-message {
  background-color: rgba(76, 217, 100, 0.1);
  color: var(--success-color, #4cd964);
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  text-align: center;
}

.login-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: var(--text-secondary, #606266);
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: var(--input-padding, 10px);
  border: 1px solid var(--border-color, #dcdfe6);
  border-radius: var(--input-radius, 4px);
  font-size: 1rem;
  transition: border-color 0.3s;
  background-color: var(--input-bg, white);
  color: var(--text-primary, #303133);
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color, #409eff);
  box-shadow: 0 0 0 2px rgba(var(--primary-rgb, 64, 158, 255), 0.2);
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-secondary, #606266);
  cursor: pointer;
}

.forgot-password {
  color: var(--primary-color, #409eff);
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
  color: var(--secondary-color);
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 1rem;
  background-color: var(--primary-color, #409eff);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
}

.login-button:hover {
  background-color: var(--secondary-color, #66b1ff);
  transform: translateY(-2px);
}

.login-button:disabled {
  background-color: var(--button-bg-hover, #a0cfff);
  cursor: not-allowed;
  transform: none;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: var(--text-tertiary, #909399);
}

.register-link a {
  color: var(--primary-color, #409eff);
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  color: var(--secondary-color);
  text-decoration: underline;
}

/* 暗色主题特殊处理 */
:root[data-theme="dark"] .login-box {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

/* 霓虹主题特殊处理 */
:root[data-theme="neon"] .login-button {
  box-shadow: var(--glow-primary);
}

:root[data-theme="neon"] .login-button:hover {
  box-shadow: var(--glow-secondary);
}

/* 响应式调整 */
@media (max-width: 576px) {
  .login-box {
    padding: 20px;
  }
  
  .login-header h2 {
    font-size: 1.75rem;
  }
  
  .login-button {
    padding: 10px 0;
  }
}

.verification-reminder {
  background-color: rgba(255, 193, 7, 0.1);
  border-left: 4px solid #ffc107;
  padding: 15px;
  margin: 20px 0;
  border-radius: 4px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.reminder-icon {
  width: 24px;
  height: 24px;
  background-color: #ffc107;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}

.reminder-content {
  flex: 1;
}

.reminder-content h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #856404;
}

.reminder-content p {
  margin: 0 0 12px;
  color: #856404;
}

.resend-button {
  background-color: var(--primary-color, #409eff);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s, transform 0.2s;
}

.resend-button:hover {
  background-color: var(--secondary-color, #66b1ff);
  transform: translateY(-2px);
}

.resend-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
  transform: none;
}

.full-width {
  width: 100%;
}

/* 重新发送验证邮件相关样式 */
.resend-verification {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
}

.resend-verification a {
  color: var(--primary-color, #409eff);
  text-decoration: none;
}

.resend-verification a:hover {
  text-decoration: underline;
}

.resend-form {
  background-color: rgba(0, 0, 0, 0.02);
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  border: 1px solid var(--border-color, #ebeef5);
}

.resend-success,
.resend-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.resend-success {
  background-color: rgba(76, 217, 100, 0.1);
  color: #2c7a44;
}

.resend-error {
  background-color: rgba(245, 108, 108, 0.1);
  color: #c45656;
}

.status-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.resend-success .status-icon {
  background-color: #4cd964;
  color: white;
}

.resend-error .status-icon {
  background-color: #f56c6c;
  color: white;
}
</style> 