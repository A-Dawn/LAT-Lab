// 认证相关的工具函数

// 保存token到localStorage
export const saveToken = (token) => {
  localStorage.setItem('token', token);
};

// 从localStorage获取token
export const getToken = () => {
  return localStorage.getItem('token');
};

// 清除token
export const clearToken = () => {
  localStorage.removeItem('token');
};

// 检查是否已登录
export const isLoggedIn = () => {
  return !!getToken();
};

// 解析JWT令牌(不验证签名)
export const parseJwt = (token) => {
  try {
    if (!token) return null;
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('解析JWT失败:', e);
    return null;
  }
};

// 检查token是否过期
export const isTokenExpired = () => {
  const token = getToken();
  if (!token) return true;
  
  try {
    const decoded = parseJwt(token);
    if (!decoded || !decoded.exp) return true;
    
    // exp是Unix时间戳(秒)
    const expirationDate = new Date(decoded.exp * 1000);
    const currentDate = new Date();
    
    return currentDate >= expirationDate;
  } catch (e) {
    console.error('检查token过期失败:', e);
    return true;
  }
}; 