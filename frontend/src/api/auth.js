/**
 * 认证相关API接口
 */

import { http } from '@/utils/request';

// 认证API
export const authAPI = {
  /**
   * 用户登录
   * @param {string} username 用户名
   * @param {string} password 密码（已加密）
   */
  login(username, password) {
    return http.post('/auth/login', {
      username,
      password,
    }, {
      showLoading: true,
      loadingText: '登录中...',
    });
  },

  /**
   * 刷新令牌
   * @param {string} refreshToken 刷新令牌
   */
  refreshToken(refreshToken) {
    return http.post('/auth/refresh', {
      refresh_token: refreshToken,
    }, {
      showLoading: false, // 刷新令牌时不显示加载
    });
  },

  /**
   * 验证令牌
   * @param {string} token 访问令牌
   */
  validateToken(token) {
    return http.post('/auth/validate', {
      token,
    }, {
      showLoading: false, // 验证令牌时不显示加载
    });
  },

  /**
   * 用户退出登录
   */
  logout() {
    return http.post('/auth/logout', {}, {
      showLoading: true,
      loadingText: '退出中...',
    });
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser() {
    return http.get('/auth/user', {}, {
      showLoading: false,
    });
  },

  /**
   * 修改密码
   * @param {string} oldPassword 旧密码（已加密）
   * @param {string} newPassword 新密码（已加密）
   */
  changePassword(oldPassword, newPassword) {
    return http.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    }, {
      showLoading: true,
      loadingText: '修改中...',
    });
  },
};
