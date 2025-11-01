/**
 * 用户状态管理
 */

import { defineStore } from 'pinia';
import { authAPI } from '@/api/auth';
import { defaultTokenManager, isTokenExpired, isTokenExpiringSoon, extractUserFromToken } from '@/utils/jwt';

export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息
    user: null,
    // 访问令牌
    token: null,
    // 刷新令牌
    refreshToken: null,
    // 令牌过期时间
    expiresAt: null,
    // 用户权限
    permissions: [],
    // 登录状态
    isLoggedIn: false,
    // 令牌刷新中
    isRefreshing: false,
    // JWT管理器
    tokenManager: defaultTokenManager
  }),

  getters: {
    // 获取用户信息
    getUserInfo: (state) => state.user,
    
    // 获取用户权限
    getUserPermissions: (state) => state.permissions,
    
    // 检查是否有特定权限
    hasPermission: (state) => (permission) => {
      return state.permissions.includes(permission);
    },
    
    // 检查是否有任意一个权限
    hasAnyPermission: (state) => (permissions) => {
      return permissions.some(permission => state.permissions.includes(permission));
    },
    
    // 检查是否有所有权限
    hasAllPermissions: (state) => (permissions) => {
      return permissions.every(permission => state.permissions.includes(permission));
    },
    
    // 检查用户类型
    isUserType: (state) => (userType) => {
      return state.user?.user_type === userType;
    },
    
    // 检查是否为管理员
    isAdmin: (state) => state.user?.user_type === 'admin',
    
    // 检查是否为医生
    isDoctor: (state) => state.user?.user_type === 'doctor',
    
    // 检查是否为技师
    isTechnician: (state) => state.user?.user_type === 'technician',
    
    // 检查令牌是否即将过期（30分钟内）
    isTokenExpiringSoon: (state) => {
      if (!state.token) return false;
      return isTokenExpiringSoon(state.token, 30);
    },
    
    // 检查令牌是否已过期
    isTokenExpired: (state) => {
      if (!state.token) return true;
      return isTokenExpired(state.token);
    },

    // 获取用户ID
    userId: (state) => state.user?.id || null,

    // 获取用户名
    username: (state) => state.user?.username || '',

    // 获取用户邮箱
    email: (state) => state.user?.email || '',

    // 获取用户全名
    fullName: (state) => state.user?.full_name || '',

    // 检查是否已登录且令牌有效
    isAuthenticated: (state) => {
      const result = state.isLoggedIn && state.token && !state.isTokenExpired;
      console.log('认证状态检查 - 结果:', result, {
        isLoggedIn: state.isLoggedIn,
        hasToken: !!state.token,
        isTokenExpired: state.isTokenExpired
      });
      return result;
    }
  },

  actions: {
    // 设置用户信息
    async setUserInfo(userInfo) {
      this.user = userInfo.user;
      this.token = userInfo.token;
      this.refreshToken = userInfo.refreshToken;
      this.expiresAt = userInfo.expiresAt;
      this.permissions = userInfo.permissions || [];
      this.isLoggedIn = true;
      
      // 使用JWT管理器保存令牌
      this.tokenManager.saveTokens(
        userInfo.token,
        userInfo.refreshToken,
        userInfo.expiresAt
      );
      
      // 设置令牌自动刷新回调
      this.tokenManager.setRefreshCallback(() => {
        this.refreshAccessToken();
      });
      
      // 保存到本地存储（兼容旧版本）
      this.saveToLocalStorage();
    },
    
    // 清除用户信息
    clearUserInfo() {
      this.user = null;
      this.token = null;
      this.refreshToken = null;
      this.expiresAt = null;
      this.permissions = [];
      this.isLoggedIn = false;
      this.isRefreshing = false;
      
      // 使用JWT管理器清除令牌
      this.tokenManager.clearTokens();
      
      // 清除本地存储（兼容旧版本）
      this.clearLocalStorage();
    },
    
    // 验证令牌
    async validateToken() {
      if (!this.token) {
        return false;
      }
      
      try {
        const response = await authAPI.validateToken(this.token);
        if (response.success || (response.code && response.code >= 200 && response.code < 300)) {
          // 从新格式中提取数据
          const tokenData = response.data || response;
          // 更新权限信息（可能有变化）
          this.permissions = tokenData.permissions || response.permissions || [];
          return true;
        } else {
          // 令牌无效，尝试刷新
          return await this.attemptTokenRefresh();
        }
      } catch (error) {
        console.error('令牌验证失败:', error);
        return await this.attemptTokenRefresh();
      }
    },
    
    // 刷新访问令牌
    async refreshAccessToken() {
      if (!this.refreshToken || this.isRefreshing) {
        return false;
      }
      
      this.isRefreshing = true;
      
      try {
        const response = await authAPI.refreshToken(this.refreshToken);
        
        if (response.success || (response.code && response.code >= 200 && response.code < 300)) {
          // 从新格式中提取数据
          const tokenData = response.data || response;
          // 更新令牌信息
          this.token = tokenData.token || response.token;
          this.refreshToken = tokenData.refresh_token || response.refresh_token;
          this.expiresAt = tokenData.expires_at || response.expires_at;
          this.user = tokenData.user || response.user;
          this.permissions = tokenData.permissions || response.permissions || [];
          
          // 保存到本地存储
          this.saveToLocalStorage();
          
          // 重新设置自动刷新
          this.setupTokenRefresh();
          
          console.log('令牌刷新成功');
          return true;
        } else {
          console.error('令牌刷新失败:', response.message);
          this.logout();
          return false;
        }
      } catch (error) {
        console.error('令牌刷新异常:', error);
        this.logout();
        return false;
      } finally {
        this.isRefreshing = false;
      }
    },
    
    // 尝试刷新令牌
    async attemptTokenRefresh() {
      if (this.isTokenExpired) {
        // 如果访问令牌已过期，尝试使用刷新令牌
        return await this.refreshAccessToken();
      }
      return false;
    },
    
    
    // 获取当前用户信息
    async getCurrentUser() {
      if (!this.token) {
        return null;
      }
      
      try {
        const response = await authAPI.getCurrentUser();
        if (response.success || (response.code && response.code >= 200 && response.code < 300)) {
          // 从新格式中提取数据
          const userData = response.data || response;
          this.user = userData.user || response.user;
          this.permissions = userData.permissions || response.permissions || [];
          this.saveToLocalStorage();
          return this.user;
        }
      } catch (error) {
        console.error('获取当前用户信息失败:', error);
      }
      
      return null;
    },
    
    // 登出
    logout() {
      this.clearUserInfo();
      
      // 跳转到登录页面（在路由守卫中处理）
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    },
    
    // 保存到本地存储
    saveToLocalStorage() {
      if (typeof window === 'undefined') return;
      
      const userInfo = {
        user: this.user,
        token: this.token,
        refreshToken: this.refreshToken,
        expiresAt: this.expiresAt,
        permissions: this.permissions,
        isLoggedIn: this.isLoggedIn
      };
      
      try {
        localStorage.setItem('eyes_remk_user', JSON.stringify(userInfo));
      } catch (error) {
        console.error('保存用户信息到本地存储失败:', error);
      }
    },
    
    // 从本地存储加载
    loadFromLocalStorage() {
      if (typeof window === 'undefined') return false;
      
      try {
        const stored = localStorage.getItem('eyes_remk_user');
        if (stored) {
          const userInfo = JSON.parse(stored);
          
          // 检查是否过期
          if (userInfo.expiresAt && Date.now() / 1000 < userInfo.expiresAt) {
            this.user = userInfo.user;
            this.token = userInfo.token;
            this.refreshToken = userInfo.refreshToken;
            this.expiresAt = userInfo.expiresAt;
            this.permissions = userInfo.permissions || [];
            this.isLoggedIn = userInfo.isLoggedIn;
            
            // 设置自动刷新
            this.setupTokenRefresh();
            
            return true;
          } else {
            // 过期了，清除存储
            this.clearLocalStorage();
          }
        }
      } catch (error) {
        console.error('从本地存储加载用户信息失败:', error);
        this.clearLocalStorage();
      }
      
      return false;
    },
    
    // 清除本地存储
    clearLocalStorage() {
      if (typeof window === 'undefined') return;
      
      try {
        localStorage.removeItem('eyes_remk_user');
      } catch (error) {
        console.error('清除本地存储失败:', error);
      }
    },
    
    // 设置令牌自动刷新
    setupTokenRefresh() {
      if (!this.token || !this.refreshToken) {
        return;
      }
      
      // 使用JWT管理器设置自动刷新
      this.tokenManager.setRefreshCallback(() => {
        return this.refreshAccessToken();
      });
      
      // 安排自动刷新（scheduleRefresh已经在saveTokens中调用）
      this.tokenManager.scheduleRefresh(this.token);
    },
    
    // 初始化用户状态
    async initializeUserState() {
      // 从本地存储加载
      const loaded = this.loadFromLocalStorage();
      
      if (loaded && this.token) {
        // 验证令牌是否仍然有效
        const isValid = await this.validateToken();
        if (!isValid) {
          this.clearUserInfo();
          return false;
        }
        return true;
      }
      
      return false;
    },

    // 兼容原有的方法名
    setToken(token, refreshToken) {
      this.token = token;
      this.refreshToken = refreshToken;
      this.saveToLocalStorage();
    },

    clearUserData() {
      this.clearUserInfo();
    },

    restoreUserState() {
      return this.loadFromLocalStorage();
    }
  }
});