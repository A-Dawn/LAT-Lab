<template>
  <div class="not-found-page">
    <div class="not-found-container">
      <div class="error-code">404</div>
      <h1>页面不存在</h1>
      <p>抱歉，您访问的页面不存在或已被删除。</p>
      <router-link to="/" class="home-button">返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #4c84ff 0%, #2861ff 100%);
  padding: 20px;
}

.not-found-container {
  text-align: center;
  background-color: white;
  border-radius: 10px;
  padding: 40px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: #4c84ff;
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 15px;
}

p {
  color: #606266;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.home-button {
  display: inline-block;
  background-color: #4c84ff;
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.home-button:hover {
  background-color: #2861ff;
}
</style> 