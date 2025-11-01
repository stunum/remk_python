/**
 * JWT令牌处理工具
 * 提供JWT令牌的解析、验证和管理功能
 */

/**
 * 解析JWT令牌（不验证签名）
 * @param {string} token JWT令牌
 * @returns {object|null} 解析后的payload，失败返回null
 */
export function parseJWT(token) {
  if (!token) return null;
  
  try {
    // JWT由三部分组成：header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.warn('Invalid JWT format');
      return null;
    }
    
    // 解码payload部分（Base64URL编码）
    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    
    return JSON.parse(decoded);
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
}

/**
 * 检查JWT令牌是否过期
 * @param {string} token JWT令牌
 * @returns {boolean} true表示已过期
 */
export function isTokenExpired(token) {
  const payload = parseJWT(token);
  if (!payload || !payload.exp) {
    return true;
  }
  
  // JWT的exp是以秒为单位的时间戳
  const now = Math.floor(Date.now() / 1000);
  return payload.exp <= now;
}

/**
 * 检查JWT令牌是否即将过期
 * @param {string} token JWT令牌
 * @param {number} thresholdMinutes 提前多少分钟算作即将过期，默认30分钟
 * @returns {boolean} true表示即将过期
 */
export function isTokenExpiringSoon(token, thresholdMinutes = 30) {
  const payload = parseJWT(token);
  if (!payload || !payload.exp) {
    return true;
  }
  
  const now = Math.floor(Date.now() / 1000);
  const threshold = thresholdMinutes * 60; // 转换为秒
  
  return (payload.exp - now) <= threshold;
}

/**
 * 获取JWT令牌的过期时间
 * @param {string} token JWT令牌
 * @returns {Date|null} 过期时间，失败返回null
 */
export function getTokenExpiry(token) {
  const payload = parseJWT(token);
  if (!payload || !payload.exp) {
    return null;
  }
  
  return new Date(payload.exp * 1000);
}

/**
 * 获取JWT令牌的剩余有效时间（毫秒）
 * @param {string} token JWT令牌
 * @returns {number} 剩余时间（毫秒），已过期返回0
 */
export function getTokenRemainingTime(token) {
  const payload = parseJWT(token);
  if (!payload || !payload.exp) {
    return 0;
  }
  
  const now = Date.now();
  const expiry = payload.exp * 1000;
  
  return Math.max(0, expiry - now);
}

/**
 * 从JWT令牌中提取用户信息
 * @param {string} token JWT令牌
 * @returns {object|null} 用户信息，失败返回null
 */
export function extractUserFromToken(token) {
  const payload = parseJWT(token);
  if (!payload) {
    return null;
  }
  
  return {
    userId: payload.user_id,
    username: payload.username,
    userType: payload.user_type,
    permissions: payload.permissions || [],
    issuer: payload.iss,
    subject: payload.sub,
    issuedAt: payload.iat ? new Date(payload.iat * 1000) : null,
    expiresAt: payload.exp ? new Date(payload.exp * 1000) : null
  };
}

/**
 * 验证JWT令牌格式
 * @param {string} token JWT令牌
 * @returns {boolean} true表示格式正确
 */
export function isValidJWTFormat(token) {
  if (!token || typeof token !== 'string') {
    return false;
  }
  
  // JWT应该有三个部分，用.分隔
  const parts = token.split('.');
  if (parts.length !== 3) {
    return false;
  }
  
  // 每个部分都应该是Base64URL编码
  const base64UrlRegex = /^[A-Za-z0-9_-]+$/;
  return parts.every(part => base64UrlRegex.test(part));
}

/**
 * 创建JWT令牌信息对象
 * @param {string} accessToken 访问令牌
 * @param {string} refreshToken 刷新令牌
 * @param {number} expiresAt 过期时间戳（秒）
 * @returns {object} 令牌信息对象
 */
export function createTokenInfo(accessToken, refreshToken, expiresAt) {
  const accessPayload = parseJWT(accessToken);
  const refreshPayload = parseJWT(refreshToken);
  
  return {
    accessToken,
    refreshToken,
    expiresAt,
    user: accessPayload ? {
      userId: accessPayload.user_id,
      username: accessPayload.username,
      userType: accessPayload.user_type,
      permissions: accessPayload.permissions || []
    } : null,
    isValid: !isTokenExpired(accessToken),
    isExpiringSoon: isTokenExpiringSoon(accessToken),
    remainingTime: getTokenRemainingTime(accessToken),
    refreshTokenValid: refreshToken ? !isTokenExpired(refreshToken) : false
  };
}

/**
 * 令牌管理器类
 */
export class TokenManager {
  constructor(storageKey = 'eyes_remk_tokens') {
    this.storageKey = storageKey;
    this.refreshTimer = null;
    this.refreshCallback = null;
  }
  
  /**
   * 保存令牌到本地存储
   * @param {string} accessToken 访问令牌
   * @param {string} refreshToken 刷新令牌
   * @param {number} expiresAt 过期时间戳
   */
  saveTokens(accessToken, refreshToken, expiresAt) {
    const tokenInfo = {
      accessToken,
      refreshToken,
      expiresAt,
      savedAt: Date.now()
    };
    
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(tokenInfo));
      this.scheduleRefresh(accessToken);
    } catch (error) {
      console.error('Failed to save tokens:', error);
    }
  }
  
  /**
   * 从本地存储加载令牌
   * @returns {object|null} 令牌信息，失败返回null
   */
  loadTokens() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) return null;
      
      const tokenInfo = JSON.parse(stored);
      
      // 检查访问令牌是否过期
      if (isTokenExpired(tokenInfo.accessToken)) {
        // 如果刷新令牌也过期了，清除存储
        if (!tokenInfo.refreshToken || isTokenExpired(tokenInfo.refreshToken)) {
          this.clearTokens();
          return null;
        }
      }
      
      // 设置自动刷新
      if (tokenInfo.accessToken) {
        this.scheduleRefresh(tokenInfo.accessToken);
      }
      
      return tokenInfo;
    } catch (error) {
      console.error('Failed to load tokens:', error);
      this.clearTokens();
      return null;
    }
  }
  
  /**
   * 清除本地存储的令牌
   */
  clearTokens() {
    try {
      localStorage.removeItem(this.storageKey);
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
    
    this.cancelRefresh();
  }
  
  /**
   * 设置令牌刷新回调
   * @param {Function} callback 刷新回调函数
   */
  setRefreshCallback(callback) {
    this.refreshCallback = callback;
  }
  
  /**
   * 安排令牌自动刷新
   * @param {string} accessToken 访问令牌
   */
  scheduleRefresh(accessToken) {
    this.cancelRefresh();
    
    if (!this.refreshCallback) return;
    
    const remainingTime = getTokenRemainingTime(accessToken);
    const refreshTime = Math.max(0, remainingTime - 5 * 60 * 1000); // 提前5分钟刷新
    
    if (refreshTime > 0) {
      this.refreshTimer = setTimeout(() => {
        if (this.refreshCallback) {
          this.refreshCallback();
        }
      }, refreshTime);
    }
  }
  
  /**
   * 取消令牌自动刷新
   */
  cancelRefresh() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
  }
  
  /**
   * 获取当前令牌状态
   * @returns {object} 令牌状态信息
   */
  getTokenStatus() {
    const tokens = this.loadTokens();
    if (!tokens) {
      return {
        hasTokens: false,
        isValid: false,
        isExpiringSoon: false,
        needsRefresh: true
      };
    }
    
    const isValid = !isTokenExpired(tokens.accessToken);
    const isExpiringSoon = isTokenExpiringSoon(tokens.accessToken);
    const needsRefresh = !isValid || isExpiringSoon;
    
    return {
      hasTokens: true,
      isValid,
      isExpiringSoon,
      needsRefresh,
      remainingTime: getTokenRemainingTime(tokens.accessToken),
      expiresAt: getTokenExpiry(tokens.accessToken)
    };
  }
}

// 默认令牌管理器实例
export const defaultTokenManager = new TokenManager();

// 默认导出
export default {
  parseJWT,
  isTokenExpired,
  isTokenExpiringSoon,
  getTokenExpiry,
  getTokenRemainingTime,
  extractUserFromToken,
  isValidJWTFormat,
  createTokenInfo,
  TokenManager,
  defaultTokenManager
};
