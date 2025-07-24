// 安全加密工具库
// 提供密码派生函数和安全存储功能

/**
 * 这个文件提供安全的加密和哈希功能，用于前端数据存储
 * 使用PBKDF2算法进行密码派生，提高计算成本和安全性
 */

// 派生密钥所需的迭代次数
const PBKDF2_ITERATIONS = 10000;
// 派生密钥长度
const KEY_LENGTH = 256;
// 哈希算法
const HASH_ALGORITHM = 'SHA-256';
// 安全存储的盐值，在实际使用时应该从服务器获取
const SALT = 'DSBlog_SecureSaltValue_7821';

/**
 * 使用密码派生函数生成安全密钥
 * @param {string} data 原始数据
 * @param {string} salt 盐值
 * @returns {Promise<ArrayBuffer>} 派生出的密钥
 */
async function deriveKey(data, salt = SALT) {
  // 将数据转换为编码
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);
  const saltBuffer = encoder.encode(salt);
  
  // 导入密钥材料
  const keyMaterial = await window.crypto.subtle.importKey(
    'raw',
    dataBuffer,
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );
  
  // 派生密钥
  return window.crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: saltBuffer,
      iterations: PBKDF2_ITERATIONS,
      hash: HASH_ALGORITHM
    },
    keyMaterial,
    { name: 'AES-GCM', length: KEY_LENGTH },
    true,
    ['encrypt', 'decrypt']
  );
}

/**
 * 安全地将数据存储在会话存储中
 * @param {string} key 存储键名
 * @param {any} data 要存储的数据
 */
export async function secureSessionStore(key, data) {
  try {
    // 转换数据为字符串
    const dataString = JSON.stringify(data);
    
    // 计算此数据的HMAC以确保完整性
    const encoder = new TextEncoder();
    const derivedKey = await deriveKey(key + '_integrity_check');
    
    // 创建HMAC
    const signature = await window.crypto.subtle.sign(
      { name: 'HMAC' },
      derivedKey,
      encoder.encode(dataString)
    );
    
    // 将签名转换为Base64
    const signatureBase64 = btoa(String.fromCharCode.apply(null, new Uint8Array(signature)));
    
    // 存储数据和签名
    const storageData = {
      data: dataString,
      signature: signatureBase64,
      timestamp: Date.now()
    };
    
    // 保存到会话存储
    sessionStorage.setItem(key, JSON.stringify(storageData));
    
    return true;
  } catch (error) {
    console.error('安全存储失败:', error);
    // 降级到普通存储
    sessionStorage.setItem(key, JSON.stringify(data));
    return false;
  }
}

/**
 * 从会话存储中安全地获取数据
 * @param {string} key 存储键名
 * @returns {any} 存储的数据，如果验证失败返回null
 */
export async function secureSessionRetrieve(key) {
  try {
    // 获取存储的数据
    const storedJson = sessionStorage.getItem(key);
    if (!storedJson) return null;
    
    let storageData;
    try {
      storageData = JSON.parse(storedJson);
    } catch (e) {
      // 可能是旧格式数据，尝试直接解析
      return JSON.parse(storedJson);
    }
    
    // 检查是否是新格式
    if (!storageData.data || !storageData.signature) {
      // 可能是旧格式数据，直接返回
      return JSON.parse(storedJson);
    }
    
    // 验证数据完整性
    const encoder = new TextEncoder();
    const derivedKey = await deriveKey(key + '_integrity_check');
    
    // 解码签名
    const signature = new Uint8Array(
      atob(storageData.signature)
        .split('')
        .map(char => char.charCodeAt(0))
    );
    
    // 验证签名
    const isValid = await window.crypto.subtle.verify(
      { name: 'HMAC' },
      derivedKey,
      signature,
      encoder.encode(storageData.data)
    );
    
    if (!isValid) {
      console.error('数据完整性验证失败');
      return null;
    }
    
    // 返回数据
    return JSON.parse(storageData.data);
  } catch (error) {
    console.error('安全检索失败:', error);
    // 尝试降级获取
    const data = sessionStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  }
}

// 导出便利的工具对象
export const secureStorage = {
  setItem: secureSessionStore,
  getItem: secureSessionRetrieve
}; 