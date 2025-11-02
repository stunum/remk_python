/**
 * 前端加密工具
 * 提供密码加密、数据加密等功能
 */

import CryptoJS from 'crypto-js';
import { PASSWORD_SALT } from '@/config/security';

// 加密密钥（实际项目中应该从配置获取）
const SECRET_KEY = 'eyes_remk_crypto_key_2024';
const IV_LENGTH = 16; // AES块大小

/**
 * MD5哈希
 * @param {string} data 要哈希的数据
 * @returns {string} MD5哈希值
 */
export function md5Hash(data) {
  return CryptoJS.MD5(data).toString();
}

/**
 * SHA256哈希
 * @param {string} data 要哈希的数据
 * @returns {string} SHA256哈希值
 */
export function sha256Hash(data) {
  return CryptoJS.SHA256(data).toString();
}

/**
 * 密码加密（用于登录）
 * 使用时间戳和随机数增加安全性
 * @param {string} password 原始密码
 * @returns {object} 加密后的密码信息
 */
export function encryptPassword(password) {
  const timestamp = Date.now().toString();
  const random = Math.random().toString(36).substring(2);
  const salt = timestamp + random;
  
  // 组合密码和盐值
  const combinedPassword = password + salt;
  
  // 使用SHA256进行哈希
  const hashedPassword = sha256Hash(combinedPassword);
  
  return {
    password: hashedPassword,
    salt: salt,
    timestamp: timestamp
  };
}

/**
 * 简单密码哈希（用于登录）
 * 注意：必须与后端的 PASSWORD_SALT 保持一致
 * @param {string} password 原始密码
 * @returns {string} 哈希后的密码
 */
export function hashPassword(password) {
  // 使用与后端相同的盐值（从配置文件导入）
  const saltedPassword = password + PASSWORD_SALT;
  return sha256Hash(saltedPassword);
}

/**
 * AES加密
 * @param {string} text 要加密的文本
 * @param {string} key 加密密钥（可选，使用默认密钥）
 * @returns {string} 加密后的文本
 */
export function aesEncrypt(text, key = SECRET_KEY) {
  try {
    const encrypted = CryptoJS.AES.encrypt(text, key).toString();
    return encrypted;
  } catch (error) {
    console.error('AES加密失败:', error);
    return text;
  }
}

/**
 * AES解密
 * @param {string} encryptedText 加密的文本
 * @param {string} key 解密密钥（可选，使用默认密钥）
 * @returns {string} 解密后的文本
 */
export function aesDecrypt(encryptedText, key = SECRET_KEY) {
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedText, key);
    const decrypted = bytes.toString(CryptoJS.enc.Utf8);
    return decrypted;
  } catch (error) {
    console.error('AES解密失败:', error);
    return encryptedText;
  }
}

/**
 * Base64编码
 * @param {string} text 要编码的文本
 * @returns {string} Base64编码后的文本
 */
export function base64Encode(text) {
  try {
    return btoa(unescape(encodeURIComponent(text)));
  } catch (error) {
    console.error('Base64编码失败:', error);
    return text;
  }
}

/**
 * Base64解码
 * @param {string} encodedText Base64编码的文本
 * @returns {string} 解码后的文本
 */
export function base64Decode(encodedText) {
  try {
    return decodeURIComponent(escape(atob(encodedText)));
  } catch (error) {
    console.error('Base64解码失败:', error);
    return encodedText;
  }
}

/**
 * 生成随机字符串
 * @param {number} length 字符串长度
 * @returns {string} 随机字符串
 */
export function generateRandomString(length = 16) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * 生成UUID
 * @returns {string} UUID字符串
 */
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * 验证密码强度
 * @param {string} password 密码
 * @returns {object} 密码强度信息
 */
export function validatePasswordStrength(password) {
  const result = {
    score: 0,
    level: 'weak',
    suggestions: []
  };
  
  if (!password) {
    result.suggestions.push('密码不能为空');
    return result;
  }
  
  // 长度检查
  if (password.length < 8) {
    result.suggestions.push('密码长度至少8位');
  } else if (password.length >= 8) {
    result.score += 1;
  }
  
  // 包含小写字母
  if (/[a-z]/.test(password)) {
    result.score += 1;
  } else {
    result.suggestions.push('密码应包含小写字母');
  }
  
  // 包含大写字母
  if (/[A-Z]/.test(password)) {
    result.score += 1;
  } else {
    result.suggestions.push('密码应包含大写字母');
  }
  
  // 包含数字
  if (/\d/.test(password)) {
    result.score += 1;
  } else {
    result.suggestions.push('密码应包含数字');
  }
  
  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    result.score += 1;
  } else {
    result.suggestions.push('密码应包含特殊字符');
  }
  
  // 确定强度等级
  if (result.score >= 4) {
    result.level = 'strong';
  } else if (result.score >= 3) {
    result.level = 'medium';
  } else {
    result.level = 'weak';
  }
  
  return result;
}

/**
 * 敏感数据加密存储
 * @param {object} data 要存储的数据
 * @returns {string} 加密后的数据字符串
 */
export function encryptSensitiveData(data) {
  try {
    const jsonString = JSON.stringify(data);
    const encrypted = aesEncrypt(jsonString);
    return base64Encode(encrypted);
  } catch (error) {
    console.error('敏感数据加密失败:', error);
    return null;
  }
}

/**
 * 敏感数据解密
 * @param {string} encryptedData 加密的数据字符串
 * @returns {object} 解密后的数据对象
 */
export function decryptSensitiveData(encryptedData) {
  try {
    const decoded = base64Decode(encryptedData);
    const decrypted = aesDecrypt(decoded);
    return JSON.parse(decrypted);
  } catch (error) {
    console.error('敏感数据解密失败:', error);
    return null;
  }
}

/**
 * 数据完整性验证
 * @param {string} data 原始数据
 * @param {string} hash 哈希值
 * @returns {boolean} 是否完整
 */
export function verifyDataIntegrity(data, hash) {
  const computedHash = sha256Hash(data);
  return computedHash === hash;
}

/**
 * 生成数据签名
 * @param {string} data 要签名的数据
 * @param {string} key 签名密钥
 * @returns {string} 签名
 */
export function generateSignature(data, key = SECRET_KEY) {
  const message = data + key;
  return sha256Hash(message);
}

/**
 * 验证数据签名
 * @param {string} data 原始数据
 * @param {string} signature 签名
 * @param {string} key 验证密钥
 * @returns {boolean} 签名是否有效
 */
export function verifySignature(data, signature, key = SECRET_KEY) {
  const expectedSignature = generateSignature(data, key);
  return expectedSignature === signature;
}

// 默认导出所有函数
export default {
  md5Hash,
  sha256Hash,
  encryptPassword,
  hashPassword,
  aesEncrypt,
  aesDecrypt,
  base64Encode,
  base64Decode,
  generateRandomString,
  generateUUID,
  validatePasswordStrength,
  encryptSensitiveData,
  decryptSensitiveData,
  verifyDataIntegrity,
  generateSignature,
  verifySignature
};
