const PBKDF2_ITERATIONS = 10000;
const KEY_LENGTH = 256;
const HASH_ALGORITHM = 'SHA-256';
const SESSION_ID = generateRandomString(32);

/**
 * 生成指定长度的安全随机字符串
 * @param {number} length 字符串长度
 * @returns {string} 随机字符串
 */
function generateRandomString(length) {
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * 获取当前用户唯一标识，用于增加密钥随机性
 * 结合多种因素形成用户"指纹"
 * @returns {string} 用户唯一标识
 */
function getUserFingerprint() {
  try {
    // 获取已登录用户ID（如果有）
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = userData.id || '';
    
    // 浏览器和设备信息
    const platform = navigator.platform || '';
    const userAgent = navigator.userAgent || '';
    const language = navigator.language || '';
    const screenInfo = `${screen.width}x${screen.height}`;
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
    
    // 创建一个日期范围，这样每个小时都会更新一次密钥
    // 但不至于太频繁导致数据丢失
    const hourStamp = Math.floor(Date.now() / (3600 * 1000));
    
    // 结合所有信息
    const fingerprint = `${userId}|${platform}|${screenInfo}|${timeZone}|${hourStamp}`;
    
    // 计算指纹的哈希值
    return hashString(fingerprint);
  } catch (e) {
    // 如果发生错误，至少返回一个随机字符串作为后备
    console.warn('生成用户指纹失败，使用随机值替代:', e);
    return generateRandomString(16);
  }
}

/**
 * 计算字符串的哈希值
 * @param {string} str 要哈希的字符串
 * @returns {string} 哈希值的十六进制表示
 */
async function hashString(str) {
  try {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  } catch (e) {
    // 如果Web Crypto不可用，使用简单的字符串处理作为后备
    console.warn('哈希计算失败，使用简化方法:', e);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转换为32位整数
    }
    return Math.abs(hash).toString(16);
  }
}

/**
 * 获取安全盐值 - 结合用户特定数据和会话ID
 * @param {string} purpose 盐值用途，增加针对性安全性
 * @returns {string} 动态生成的盐值
 */
async function getSalt(purpose = '') {
  // 获取或创建设备ID，存储在localStorage中作为设备标识
  let deviceId = localStorage.getItem('device_id');
  if (!deviceId) {
    deviceId = generateRandomString(24);
    try {
      localStorage.setItem('device_id', deviceId);
    } catch (e) {
      console.warn('无法保存设备ID:', e);
    }
  }
  
  // 获取用户指纹
  const fingerprint = await getUserFingerprint();
  
  // 结合多种因素形成盐值
  return `SALT_${purpose}_${fingerprint}_${deviceId}_${SESSION_ID}`;
}

/**
 * 获取系统密钥 - 动态生成，而非硬编码
 * @param {string} keyType 密钥类型，用于生成不同用途的密钥
 * @returns {string} 系统密钥
 */
async function getSystemKey(keyType = 'default') {
  // 获取设备ID
  const deviceId = localStorage.getItem('device_id') || generateRandomString(24);
  
  // 获取用户指纹
  const fingerprint = await getUserFingerprint();
  
  // 结合会话ID和密钥类型
  return `KEY_${keyType}_${fingerprint}_${deviceId.substring(0, 8)}_${SESSION_ID.substring(0, 8)}`;
}

/**
 * 使用密码派生函数生成安全密钥
 * @param {string} data 原始数据
 * @param {string} purpose 密钥用途，决定使用的盐值
 * @returns {Promise<CryptoKey>} 派生出的密钥
 */
async function deriveKey(data, purpose = 'default') {
  try {
    // 获取动态盐值
    const salt = await getSalt(purpose);
    
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
  } catch (error) {
    console.error('派生密钥失败:', error);
    return null;
  }
}

/**
 * 基本加密函数 - 不依赖于Web Crypto API，用于降级处理
 * 提供基本安全性，防止完全明文存储
 * @param {string|object} data 要加密的数据
 * @param {string} keyType 密钥类型
 * @returns {Promise<string>} 加密的Base64字符串
 */
async function basicEncrypt(data, keyType = 'default') {
  try {
    // 获取动态系统密钥
    const key = await getSystemKey(keyType);
    
    // 简单的XOR加密
    const dataStr = typeof data === 'string' ? data : JSON.stringify(data);
    const keyBytes = Array.from(key).map(char => char.charCodeAt(0));
    const dataBytes = Array.from(dataStr).map(char => char.charCodeAt(0));
    
    // XOR操作
    const encryptedBytes = dataBytes.map((byte, i) => 
      byte ^ keyBytes[i % keyBytes.length]
    );
    
    // 转换为Base64
    const byteString = String.fromCharCode.apply(null, encryptedBytes);
    return btoa(byteString);
  } catch (e) {
    console.error('基本加密失败:', e);
    // 极端情况下的降级 - 至少进行Base64编码，不要完全明文存储
    return btoa(JSON.stringify(data));
  }
}

/**
 * 基本解密函数 - 不依赖于Web Crypto API，用于降级处理
 * @param {string} encryptedData Base64加密字符串
 * @param {string} keyType 密钥类型
 * @returns {Promise<any>} 解密后的数据
 */
async function basicDecrypt(encryptedData, keyType = 'default') {
  try {
    // 获取动态系统密钥
    const key = await getSystemKey(keyType);
    
    // 解析Base64
    const byteString = atob(encryptedData);
    const encryptedBytes = Array.from(byteString).map(char => char.charCodeAt(0));
    const keyBytes = Array.from(key).map(char => char.charCodeAt(0));
    
    // XOR解密
    const decryptedBytes = encryptedBytes.map((byte, i) => 
      byte ^ keyBytes[i % keyBytes.length]
    );
    
    // 转换回字符串
    const decryptedStr = String.fromCharCode.apply(null, decryptedBytes);
    
    // 尝试解析JSON
    return JSON.parse(decryptedStr);
  } catch (e) {
    console.error('基本解密失败:', e);
    try {
      // 尝试直接解析Base64编码的JSON
      return JSON.parse(atob(encryptedData));
    } catch (e2) {
      console.error('解析备用格式失败:', e2);
      return null;
    }
  }
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
    const derivedKey = await deriveKey(key + '_integrity_check', 'hmac');
    
    // 如果无法派生密钥，使用基本加密
    if (!derivedKey) {
      console.warn('无法使用高级加密，回退到基本加密方式');
      const encryptedData = await basicEncrypt(data, key + '_basic');
      sessionStorage.setItem(key, JSON.stringify({
        data: encryptedData,
        isBasicEncryption: true,
        timestamp: Date.now()
      }));
      return true;
    }
    
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
      data: dataString, // 这里仍使用未加密的数据，后续改进
      signature: signatureBase64,
      timestamp: Date.now()
    };
    
    // 使用Web Crypto API加密整个数据包
    const encryptKey = await deriveKey(key + '_encryption', 'encryption');
    
    if (!encryptKey) {
      console.warn('无法创建加密密钥，回退到基本加密');
      const encryptedData = await basicEncrypt(storageData, key + '_storage');
      sessionStorage.setItem(key, JSON.stringify({
        data: encryptedData,
        isBasicEncryption: true,
        timestamp: Date.now()
      }));
      return true;
    }
    
    // 生成随机IV
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    
    // 加密数据
    const dataToEncrypt = encoder.encode(JSON.stringify(storageData));
    const encryptedBuffer = await window.crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      encryptKey,
      dataToEncrypt
    );
    
    // 将加密数据和IV转换为Base64
    const encryptedBase64 = btoa(String.fromCharCode.apply(null, new Uint8Array(encryptedBuffer)));
    const ivBase64 = btoa(String.fromCharCode.apply(null, iv));
    
    // 添加一个唯一的存储ID，帮助后续识别
    const storageId = generateRandomString(12);
    
    // 存储加密后的数据包
    sessionStorage.setItem(key, JSON.stringify({
      encrypted: encryptedBase64,
      iv: ivBase64,
      timestamp: Date.now(),
      storageId: storageId,
      version: 3  // 标记加密版本
    }));
    
    return true;
  } catch (error) {
    console.error('安全存储失败:', error);
    // 最终降级 - 使用基本加密，避免明文
    try {
      const encryptedData = await basicEncrypt(data, key + '_fallback');
      sessionStorage.setItem(key, JSON.stringify({
        data: encryptedData,
        isBasicEncryption: true,
        timestamp: Date.now()
      }));
      return true;
    } catch (finalError) {
      console.error('所有加密方法失败，无法安全存储数据:', finalError);
      return false;
    }
  }
}

/**
 * 从会话存储中安全地获取数据
 * @param {string} key 存储键名
 * @returns {Promise<any>} 存储的数据，如果验证失败返回null
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
      console.error('解析存储数据失败:', e);
      return null;
    }
    
    // 检查是否是基本加密格式
    if (storageData.isBasicEncryption && storageData.data) {
      return await basicDecrypt(storageData.data, key + '_basic');
    }
    
    // 检查是否是版本3加密格式 (随机密钥版本)
    if (storageData.version === 3 && storageData.encrypted && storageData.iv) {
      const encryptKey = await deriveKey(key + '_encryption', 'encryption');
      if (!encryptKey) {
        console.error('无法创建解密密钥');
        return null;
      }
      
      // 解码IV和加密数据
      const iv = new Uint8Array(
        atob(storageData.iv)
          .split('')
          .map(char => char.charCodeAt(0))
      );
      
      const encryptedData = new Uint8Array(
        atob(storageData.encrypted)
          .split('')
          .map(char => char.charCodeAt(0))
      );
      
      // 解密数据
      const decryptedBuffer = await window.crypto.subtle.decrypt(
        { name: 'AES-GCM', iv },
        encryptKey,
        encryptedData
      );
      
      // 解析解密后的数据
      const decoder = new TextDecoder();
      const decryptedJson = decoder.decode(decryptedBuffer);
      const decryptedData = JSON.parse(decryptedJson);
      
      // 检查是否有签名和数据
      if (decryptedData.signature && decryptedData.data) {
        // 验证签名
        const derivedKey = await deriveKey(key + '_integrity_check', 'hmac');
        if (!derivedKey) {
          console.warn('无法验证数据完整性');
          // 返回数据但不验证
          return JSON.parse(decryptedData.data);
        }
        
        const encoder = new TextEncoder();
        const isValid = await window.crypto.subtle.verify(
          { name: 'HMAC' },
          derivedKey,
          new Uint8Array(
            atob(decryptedData.signature)
              .split('')
              .map(char => char.charCodeAt(0))
          ),
          encoder.encode(decryptedData.data)
        );
        
        if (!isValid) {
          console.error('数据完整性验证失败');
          return null;
        }
        
        // 返回解析后的数据
        return JSON.parse(decryptedData.data);
      }
      
      return null;
    }
    
    // 检查是否是版本2加密格式
    if (storageData.version === 2 && storageData.encrypted && storageData.iv) {
      // 这里是与之前版本兼容的代码
      // ...省略，与上述代码类似，但使用旧的固定密钥方法
      console.warn('检测到v2格式加密，升级到v3格式');
      
      // 如果需要还原旧版本，复制v3的逻辑但使用固定盐值
      // 这里为简化，将直接尝试用新方法解密
      const encryptKey = await deriveKey(key + '_encryption', 'encryption');
      if (!encryptKey) {
        // 如果新方法失败，尝试旧方法的固定盐值
        console.warn('使用v3密钥失败，尝试v2兼容模式');
        
        // 这只是兼容代码示例，实际中可能需要更多逻辑
        try {
          // 解码数据
          const decryptedStr = atob(storageData.data || "");
          return JSON.parse(decryptedStr);
        } catch (e) {
          console.error('v2兼容模式失败:', e);
          return null;
        }
      }
    }
    
    // 检查是否是旧版格式
    if (storageData.data && storageData.signature) {
      // 验证数据完整性
      const encoder = new TextEncoder();
      const derivedKey = await deriveKey(key + '_integrity_check', 'hmac');
      
      if (!derivedKey) {
        console.warn('无法创建验证密钥，返回未验证数据');
        // 返回数据但不验证
        return JSON.parse(storageData.data);
      }
      
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
    }
    
    // 尝试解析旧格式数据（纯JSON）
    try {
      return JSON.parse(storedJson);
    } catch (e) {
      console.error('解析旧格式数据失败:', e);
      return null;
    }
  } catch (error) {
    console.error('安全检索失败:', error);
    return null;
  }
}

/**
 * 清除特定密钥或所有加密存储的数据
 * @param {string} key 可选，特定要清除的键，不提供则清除所有
 * @returns {boolean} 操作是否成功
 */
export async function clearSecureStorage(key = null) {
  try {
    if (key) {
      // 清除特定键
      sessionStorage.removeItem(key);
    } else {
      // 找出所有加密存储的键并清除
      const keys = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const k = sessionStorage.key(i);
        try {
          const data = JSON.parse(sessionStorage.getItem(k));
          if (data && (data.version === 3 || data.version === 2 || data.isBasicEncryption)) {
            keys.push(k);
          }
        } catch (e) {
          // 不是JSON格式，跳过
        }
      }
      
      // 清除找到的键
      keys.forEach(k => sessionStorage.removeItem(k));
    }
    return true;
  } catch (e) {
    console.error('清除安全存储失败:', e);
    return false;
  }
}

// 导出便利的工具对象
export const secureStorage = {
  setItem: secureSessionStore,
  getItem: secureSessionRetrieve,
  removeItem: key => clearSecureStorage(key),
  clear: () => clearSecureStorage()
}; 