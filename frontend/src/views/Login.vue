<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'

const loginIdentifier = ref('')  // 支持邮箱或用户名登录
const password = ref('')
const rememberMe = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')
const needVerification = ref(false)
const successMsg = ref('')
const router = useRouter()
const route = useRoute()
const store = useStore()

onMounted(() => {
  if (route.query.message) {
    const validMessages = [
      '登录失败，请检查用户名和密码',
      '会话已过期，请重新登录',
      '请先登录后再访问',
      '您的账号已被禁用',
      '权限不足，请使用管理员账号'
    ];
    
    if (validMessages.includes(route.query.message)) {
      errorMsg.value = route.query.message;
    } else {
      console.warn('收到非预期的消息参数:', route.query.message);
      errorMsg.value = '登录时出现问题，请重试';
    }
  }
  
  if (route.query.verified === 'true') {
    successMsg.value = '邮箱验证成功，请登录'
  }
  
  const justVerified = localStorage.getItem('just_verified')
  if (justVerified) {
    successMsg.value = '邮箱验证成功，请登录'
    localStorage.removeItem('just_verified')
  }
})

const handleSubmit = async () => {
  if (!loginIdentifier.value || !password.value) {
    errorMsg.value = '请输入邮箱/用户名和密码'
    return
  }
  
  try {
    isLoading.value = true
    errorMsg.value = ''
    successMsg.value = ''
    
    const loginResult = await store.dispatch('login', {
      username: loginIdentifier.value,
      password: password.value
    })
    
    if (rememberMe.value) {
      localStorage.setItem('remember', 'true')
    }
    
    // 检查用户是否已验证邮箱
    if (loginResult && !loginResult.is_verified) {
      // 用户登录成功但邮箱未验证，显示提示信息
      needVerification.value = true
      successMsg.value = '登录成功！但您的邮箱尚未验证，部分功能将受限。'
      
      // 延迟跳转，让用户看到提示信息
      setTimeout(() => {
        router.push('/profile')
      }, 2000)
    } else {
      // 正常登录流程
      let redirectPath = '/';
      
      if (route.query.redirect && typeof route.query.redirect === 'string') {
        const redirectQuery = route.query.redirect;
        
        if (redirectQuery.startsWith('/') && 
            !redirectQuery.includes('://') &&
            !redirectQuery.includes('javascript:')) {
          redirectPath = redirectQuery;
        } else {
          console.warn('重定向参数可能不安全，已忽略:', redirectQuery);
        }
      }
      
      router.push(redirectPath)
    }
  } catch (error) {
    console.error('登录失败:', error)
    needVerification.value = false
    errorMsg.value = error.response?.data?.detail || '登录失败，请检查邮箱/用户名和密码'
  } finally {
    isLoading.value = false
  }
}

const enterGuestMode = () => {
  // 调用store的访客模式action
  store.dispatch('enterGuestMode')
  // 跳转到首页
  router.push('/')
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
            <label for="loginIdentifier">邮箱或用户名</label>
            <input 
              id="loginIdentifier"
              v-model="loginIdentifier"
              type="text"
              placeholder="请输入邮箱或用户名"
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
          
          <!-- 访客模式按钮 -->
          <div class="guest-mode-section">
            <div class="divider">
              <span>或者</span>
            </div>
            <button 
              type="button"
              @click="enterGuestMode"
              class="guest-button"
            >
              🚶 访客模式
            </button>
            <p class="guest-tip">以访客身份浏览网站，无需登录</p>
          </div>
        </form>
        
        <!-- 验证提醒区域优化 -->
        <div v-if="needVerification" class="verification-reminder">
          <div class="reminder-icon">✓</div>
          <div class="reminder-content">
            <h3>登录成功！</h3>
            <p>您的邮箱尚未验证，部分功能将受限。正在跳转到个人中心...</p>
            <p class="verification-tip">您可以在个人中心重新发送验证邮件。</p>
          </div>
        </div>
        
        <!-- 底部链接区域 -->
        <div class="register-link">
          <p>还没有账号? <router-link to="/register">立即注册</router-link></p>
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
  background-color: rgba(76, 217, 100, 0.1);
  border-left: 4px solid var(--success-color, #4cd964);
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
  background-color: var(--success-color, #4cd964);
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
  color: var(--text-primary);
}

.reminder-content p {
  margin: 0 0 12px;
  color: var(--text-secondary);
}

.verification-tip {
  font-size: 0.9rem;
  color: var(--primary-color, #409eff);
  font-style: italic;
  margin-top: 8px;
}

.guest-mode-section {
  margin-top: 20px;
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.divider {
  position: relative;
  margin: 15px 0;
  text-align: center;
}

.divider span {
  display: inline-block;
  position: relative;
  padding: 0 10px;
  background-color: var(--card-bg, #fff);
  color: var(--text-secondary);
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: var(--border-color, rgba(0, 0, 0, 0.08));
  z-index: -1;
}

.guest-button {
  width: 100%;
  padding: 10px 0;
  font-size: 1rem;
  background-color: var(--primary-color, #409eff);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
  margin-top: 10px;
}

.guest-button:hover {
  background-color: var(--secondary-color, #66b1ff);
  transform: translateY(-2px);
}

.guest-tip {
  margin-top: 5px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}
</style> 