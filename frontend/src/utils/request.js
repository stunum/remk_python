/**
 * Axios 请求封装
 * 统一处理请求和响应，包括错误处理、认证等
 */

import axios from 'axios';
import { message } from 'ant-design-vue';

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  timeout: 60000, // 60秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求加载状态管理
let loadingInstance = null;
let requestCount = 0;

// 显示加载
const showLoading = (config) => {
  if (config.showLoading !== false) {
    requestCount++;
    if (requestCount === 1) {
      // 使用ant-design-vue的loading
      loadingInstance = message.loading(config.loadingText || '加载中...', 0);
    }
  }
};

// 隐藏加载
const hideLoading = () => {
  requestCount--;
  if (requestCount <= 0) {
    requestCount = 0;
    if (loadingInstance) {
      loadingInstance();
      loadingInstance = null;
    }
  }
};

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 显示加载状态
    showLoading(config);

    // 添加认证token
    let token = null;
    try {
      const userInfo = localStorage.getItem('eyes_remk_user');
      if (userInfo) {
        const parsed = JSON.parse(userInfo);
        token = parsed.token;
      }
    } catch (error) {
      console.warn('获取token失败:', error);
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加请求ID用于调试
    config.headers['X-Request-ID'] = Date.now().toString();

    console.log('发送请求:', {
      url: config.url,
      method: config.method,
      data: config.data,
      params: config.params,
    });

    return config;
  },
  (error) => {
    hideLoading();
    console.error('请求配置错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    hideLoading();

    console.log('收到响应:', {
      url: response.config.url,
      status: response.status,
      data: response.data,
    });

    // 检查响应数据格式
    const { data } = response;
    
    // 标准格式 {code, msg, data}
    if (typeof data === 'object' && data !== null && typeof data.code === 'number') {
      // 检查状态码（2xx为成功）
      if (data.code < 200 || data.code >= 300) {
        const errorMessage = data.msg || data.message || '请求失败';
        message.error(errorMessage);
        return Promise.reject(new Error(errorMessage));
      }
      
      // 直接返回标准格式
      return data;
    }

    // 兼容旧格式 {success, message, data}
    if (typeof data === 'object' && data !== null && 'success' in data) {
      if (!data.success) {
        const errorMessage = data.message || '请求失败';
        message.error(errorMessage);
        return Promise.reject(new Error(errorMessage));
      }
      return data;
    }

    // 直接返回数据
    return data;
  },
  (error) => {
    hideLoading();

    console.error('请求错误:', error);

    // 处理不同类型的错误
    let errorMessage = '请求失败';
    
    if (error.response) {
      // 服务器响应了错误状态码
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          errorMessage = data?.message || '请求参数错误';
          break;
        case 401:
          errorMessage = '未授权，请重新登录';
          // 清除token并跳转到登录页
          localStorage.removeItem('eyes_remk_user');
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          break;
        case 403:
          errorMessage = '权限不足';
          break;
        case 404:
          errorMessage = '请求的资源不存在';
          break;
        case 500:
          errorMessage = '服务器内部错误';
          break;
        case 502:
          errorMessage = '网关错误';
          break;
        case 503:
          errorMessage = '服务暂时不可用';
          break;
        default:
          errorMessage = data?.message || `请求失败 (${status})`;
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '网络连接失败，请检查网络设置';
    } else {
      // 其他错误
      errorMessage = error.message || '请求配置错误';
    }

    // 显示错误消息
    message.error(errorMessage);

    return Promise.reject(error);
  }
);

/**
 * 检查响应是否成功
 * @param {Object} response - API响应对象
 * @returns {boolean} - 是否成功
 */
export const isResponseSuccess = (response) => {
  if (!response) return false;
  
  // 新格式: {code, msg, data}
  if (typeof response.code === 'number') {
    return response.code >= 200 && response.code < 300;
  }
  return false;
};

/**
 * 获取响应消息
 * @param {Object} response - API响应对象
 * @returns {string} - 响应消息
 */
export const getResponseMessage = (response) => {
  if (!response) return '';
  return response.msg || response.message || '';
};

// 封装常用的请求方法
export const http = {
  /**
   * GET请求
   * @param {string} url 请求地址
   * @param {object} params 请求参数
   * @param {object} config 请求配置
   */
  get(url, params = {}, config = {}) {
    return request({
      method: 'GET',
      url,
      params,
      ...config,
    });
  },

  /**
   * POST请求
   * @param {string} url 请求地址
   * @param {object} data 请求数据
   * @param {object} config 请求配置
   */
  post(url, data = {}, config = {}) {
    return request({
      method: 'POST',
      url,
      data,
      ...config,
    });
  },

  /**
   * PUT请求
   * @param {string} url 请求地址
   * @param {object} data 请求数据
   * @param {object} config 请求配置
   */
  put(url, data = {}, config = {}) {
    return request({
      method: 'PUT',
      url,
      data,
      ...config,
    });
  },

  /**
   * DELETE请求
   * @param {string} url 请求地址
   * @param {object} config 请求配置
   */
  delete(url, config = {}) {
    return request({
      method: 'DELETE',
      url,
      ...config,
    });
  },

  /**
   * PATCH请求
   * @param {string} url 请求地址
   * @param {object} data 请求数据
   * @param {object} config 请求配置
   */
  patch(url, data = {}, config = {}) {
    return request({
      method: 'PATCH',
      url,
      data,
      ...config,
    });
  },

  /**
   * 上传文件
   * @param {string} url 上传地址
   * @param {FormData} formData 文件数据
   * @param {object} config 请求配置
   */
  upload(url, formData, config = {}) {
    return request({
      method: 'POST',
      url,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      ...config,
    });
  },

  /**
   * 下载文件
   * @param {string} url 下载地址
   * @param {object} params 请求参数
   * @param {string} filename 文件名
   */
  async download(url, params = {}, filename = 'download') {
    try {
      const response = await request({
        method: 'GET',
        url,
        params,
        responseType: 'blob',
        showLoading: true,
        loadingText: '下载中...',
      });

      // 创建下载链接
      const blob = new Blob([response]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      message.success('下载成功');
    } catch (error) {
      console.error('下载失败:', error);
      message.error('下载失败');
    }
  },
};

// 导出axios实例供高级用法
export default request;