<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { resendVerificationEmail } from '../services/api'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMsg = ref('')
const isLoading = ref(false)
const isRegistered = ref(false)
const registeredEmail = ref('')
const isResending = ref(false)
const resendStatus = ref('')
const resendMessage = ref('')

const register = async () => {
  // 清除之前的错误信息
  errorMsg.value = ''
  
  // 表单验证
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    errorMsg.value = '请填写所有字段'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }
  
  // 设置加载状态
  isLoading.value = true
  
  try {
    // 发送注册请求
    const response = await axios.post('http://localhost:8000/api/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    
    // 注册成功
    isRegistered.value = true
    registeredEmail.value = email.value
    
  } catch (error) {
    // 处理错误
    if (error.response && error.response.data) {
      errorMsg.value = error.response.data.detail || '注册失败，请稍后再试'
    } else {
      errorMsg.value = '网络错误，请检查您的连接'
    }
  } finally {
    // 取消加载状态
    isLoading.value = false
  }
}

// 重新发送验证邮件
const handleResendVerification = async () => {
  isResending.value = true
  resendStatus.value = ''
  resendMessage.value = ''
  
  try {
    await resendVerificationEmail(registeredEmail.value)
    resendStatus.value = 'success'
    resendMessage.value = '验证邮件已重新发送，请查收'
  } catch (error) {
    resendStatus.value = 'error'
    resendMessage.value = error.response?.data?.detail || '发送失败，请稍后重试'
  } finally {
    isResending.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-container">
      <!-- 注册表单 -->
      <div v-if="!isRegistered" class="register-box">
        <h2>注册账号</h2>
        
        <div v-if="errorMsg" class="error-message">
          {{ errorMsg }}
        </div>
        
        <form @submit.prevent="register">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              type="text"
              id="username"
              v-model="username"
              placeholder="请输入用户名"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              type="email"
              id="email"
              v-model="email"
              placeholder="请输入邮箱"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <input
              type="password"
              id="password"
              v-model="password"
              placeholder="请输入密码"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              placeholder="请再次输入密码"
              required
            />
          </div>
          
          <button type="submit" :disabled="isLoading" class="register-button">
            {{ isLoading ? '注册中...' : '注册' }}
          </button>
        </form>
        
        <div class="login-link">
          已有账号？ <router-link to="/login">登录</router-link>
        </div>
      </div>
      
      <!-- 注册成功提示 -->
      <div v-if="isRegistered" class="success-message">
        <div class="success-icon">✓</div>
        <h3>注册成功！</h3>
        <p>我们已向 <strong>{{ registeredEmail }}</strong> 发送了一封验证邮件。</p>
        <p>请查收邮件并点击验证链接以激活您的账号。</p>
        <p class="note">如果没有收到邮件，请检查垃圾邮件文件夹，或者点击下方按钮重新发送验证邮件。</p>
        
        <!-- 重新发送验证邮件按钮 -->
        <div class="resend-section">
          <button 
            @click="handleResendVerification" 
            :disabled="isResending" 
            class="resend-button"
          >
            {{ isResending ? '发送中...' : '重新发送验证邮件' }}
          </button>
          
          <div v-if="resendStatus === 'success'" class="resend-success">
            {{ resendMessage }}
          </div>
          
          <div v-if="resendStatus === 'error'" class="resend-error">
            {{ resendMessage }}
          </div>
        </div>
        
        <div class="warning-note">
          <p><strong>注意：</strong>如果您长时间未收到邮件，可能是由于以下原因：</p>
          <ul>
            <li>邮件可能被归类到垃圾邮件文件夹</li>
            <li>邮件服务器可能暂时不可用</li>
            <li>您的邮箱提供商可能阻止了此类邮件</li>
          </ul>
          <p>您可以在登录页面尝试"重新发送验证邮件"功能。</p>
        </div>
        <div class="actions">
          <router-link to="/login" class="login-link-button">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #4c84ff 0%, #2861ff 100%);
}

.register-container {
  width: 100%;
  max-width: 450px;
  padding: 20px;
}

.register-box {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 10px;
}

.register-header p {
  color: #909399;
  font-size: 1rem;
}

.error-message {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  text-align: center;
}

.register-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #606266;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #409eff;
}

.register-button {
  width: 100%;
  padding: 12px 0;
  font-size: 1rem;
  background-color: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-button:hover {
  background-color: #66b1ff;
}

.register-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #909399;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}

.success-message {
  text-align: center;
  padding: 20px;
}

.success-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #4cd964;
  color: white;
  font-size: 30px;
  line-height: 60px;
  margin: 0 auto 20px;
}

.success-message h3 {
  font-size: 22px;
  margin-bottom: 15px;
  color: #333;
}

.success-message p {
  color: #666;
  margin-bottom: 10px;
}

.success-message .note {
  font-size: 14px;
  color: #999;
  margin: 20px 0;
}

.login-link-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.3s;
}

.login-link-button:hover {
  background-color: #66b1ff;
}

.warning-note {
  background-color: #fff8e1;
  border-left: 4px solid #ffc107;
  padding: 15px;
  margin: 20px 0;
  border-radius: 4px;
  text-align: left;
}

.warning-note ul {
  margin: 10px 0 10px 20px;
  padding: 0;
}

.warning-note li {
  margin-bottom: 5px;
}

.resend-section {
  margin: 20px 0;
}

.resend-button {
  padding: 10px 20px;
  background-color: #4c84ff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.resend-button:hover {
  background-color: #3a70e0;
}

.resend-button:disabled {
  background-color: #a0c0ff;
  cursor: not-allowed;
}

.resend-success {
  color: #4cd964;
  margin-top: 10px;
}

.resend-error {
  color: #ff3b30;
  margin-top: 10px;
}
</style> 