/**
 * 系统相关API接口
 */

import { http } from '@/utils/request';

// 系统API
export const systemAPI = {
  /**
   * 获取系统信息
   */
  getSystemInfo() {
    return http.get('/system/info', {}, {
      showLoading: false,
    });
  },

  /**
   * 获取系统统计信息
   */
  getSystemStats() {
    return http.get('/system/stats', {}, {
      showLoading: false,
    });
  },

  /**
   * 显示消息对话框
   * @param {string} title 标题
   * @param {string} message 消息内容
   */
  showMessageDialog(title, message) {
    return http.post('/proxy/system/dialog/message', {
      title,
      message,
    });
  },

  /**
   * 显示文件选择对话框
   */
  showOpenFileDialog() {
    return http.post('/proxy/system/dialog/open');
  },

  /**
   * 显示文件保存对话框
   * @param {string} filename 默认文件名
   */
  showSaveFileDialog(filename) {
    return http.post('/proxy/system/dialog/save', {
      default_filename: filename,
    });
  },

  /**
   * 获取系统日志
   * @param {object} params 查询参数
   */
  getSystemLogs(params = {}) {
    return http.get('/system/logs', params, {
      showLoading: true,
      loadingText: '加载日志...',
    });
  },

  /**
   * 清理系统日志
   */
  clearSystemLogs() {
    return http.delete('/system/logs', {
      showLoading: true,
      loadingText: '清理中...',
    });
  },
};
