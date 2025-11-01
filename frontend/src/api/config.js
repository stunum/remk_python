/**
 * 配置相关API接口
 */

import { http } from '@/utils/request';

// 配置API
export const configAPI = {
  /**
   * 获取数据库配置
   */
  getDatabaseConfig() {
    return http.get('/configs/database', {}, {
      showLoading: false,
    });
  },

  /**
   * 更新数据库配置
   * @param {Object} config 数据库配置对象
   */
  updateDatabaseConfig(config) {
    return http.put('/configs/database', config, {
      showLoading: true,
    });
  },

  /**
   * 获取日志配置
   */
  getLoggingConfig() {
    return http.get('/configs/logging', {}, {
      showLoading: false,
    });
  },

  /**
   * 更新日志配置
   * @param {Object} config 日志配置对象
   */
  updateLoggingConfig(config) {
    return http.put('/configs/logging', config, {
      showLoading: true,
    });
  },

  /**
   * 获取其他配置（服务器、第三方、保存路径等）
   */
  getOtherConfig() {
    return http.get('/configs/other', {}, {
      showLoading: false,
    });
  },

  /**
   * 更新其他配置
   * @param {Object} config 其他配置对象
   */
  updateOtherConfig(config) {
    return http.put('/configs/other', config, {
      showLoading: true,
    });
  },

  /**
   * 测试数据库连接
   * @param {Object} config 数据库配置对象
   */
  testDatabaseConnection(config) {
    return http.post('/configs/database/test', config, {
      showLoading: true,
    });
  }
};