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
  background: var(--hero-gradient);
  padding: 20px;
}

.not-found-container {
  text-align: center;
  background-color: var(--bg-primary);
  border-radius: 10px;
  padding: 40px;
  box-shadow: var(--shadow-medium);
  max-width: 500px;
  width: 100%;
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: var(--primary-color);
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(var(--text-primary-rgb), 0.1);
}

h1 {
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 15px;
}

p {
  color: var(--text-secondary);
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.home-button {
  display: inline-block;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.home-button:hover {
  background-color: var(--primary-hover);
}
</style> 