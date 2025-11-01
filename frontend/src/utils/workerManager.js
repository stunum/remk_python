/**
 * Web Worker 管理器
 * 提供简单的 API 来使用图像保存 Worker
 */

class WorkerManager {
  constructor() {
    this.worker = null;
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.isInitialized = false;
  }

  /**
   * 初始化 Worker
   */
  async init() {
    if (this.isInitialized) {
      return;
    }

    try {
      // 创建 Worker
      this.worker = new Worker(
        new URL('../workers/imageSaveWorker.js', import.meta.url),
        { type: 'module' }
      );

      // 监听 Worker 消息
      this.worker.addEventListener('message', this.handleWorkerMessage.bind(this));
      
      // 监听 Worker 错误
      this.worker.addEventListener('error', this.handleWorkerError.bind(this));

      this.isInitialized = true;
      console.log('✅ Worker 管理器初始化成功');
    } catch (error) {
      console.error('❌ Worker 管理器初始化失败:', error);
      throw error;
    }
  }

  /**
   * 处理 Worker 消息
   * @param {MessageEvent} event 消息事件
   */
  handleWorkerMessage(event) {
    const { id, type, result, error } = event.data;
    const request = this.pendingRequests.get(id);

    if (!request) {
      console.warn('⚠️ 收到未知请求的响应:', id);
      return;
    }

    // 从待处理请求中移除
    this.pendingRequests.delete(id);

    if (type === 'SUCCESS') {
      request.resolve(result);
    } else if (type === 'ERROR') {
      request.reject(new Error(error.message));
    }
  }

  /**
   * 处理 Worker 错误
   * @param {ErrorEvent} event 错误事件
   */
  handleWorkerError(event) {
    console.error('❌ Worker 发生错误:', event);
    
    // 拒绝所有待处理的请求
    for (const [id, request] of this.pendingRequests) {
      request.reject(new Error('Worker 发生错误'));
    }
    this.pendingRequests.clear();
  }

  /**
   * 获取用户 token
   * @returns {string|null} 用户 token
   */
  getUserToken() {
    try {
      const userInfo = localStorage.getItem('eyes_remk_user');
      if (userInfo) {
        const parsed = JSON.parse(userInfo);
        return parsed.token;
      }
    } catch (error) {
      console.warn('获取 token 失败:', error);
    }
    return null;
  }

  /**
   * 发送请求到 Worker
   * @param {string} type 请求类型
   * @param {object} data 请求数据
   * @param {object} options 选项
   * @returns {Promise} 请求结果
   */
  async sendRequest(type, data, options = {}) {
    if (!this.isInitialized) {
      await this.init();
    }

    const id = ++this.requestId;
    
    // 添加认证 token
    const requestOptions = {
      ...options,
      token: this.getUserToken(),
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
    };

    return new Promise((resolve, reject) => {
      // 存储请求回调
      this.pendingRequests.set(id, { resolve, reject });

      // 设置超时
      const timeout = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error('请求超时'));
      }, requestOptions.timeout || 30000);

      // 修改 resolve 和 reject 以清除超时
      const originalResolve = resolve;
      const originalReject = reject;
      
      this.pendingRequests.set(id, {
        resolve: (result) => {
          clearTimeout(timeout);
          originalResolve(result);
        },
        reject: (error) => {
          clearTimeout(timeout);
          originalReject(error);
        }
      });

      // 发送消息到 Worker
      this.worker.postMessage({
        id,
        type,
        data,
        options: requestOptions
      });
    });
  }

  /**
   * 保存单张图片
   * @param {object} data 图片数据
   * @param {object} options 选项
   * @returns {Promise} 保存结果
   */
  async saveImage(data, options = {}) {
    return await this.sendRequest('SAVE_IMAGE', data, options);
  }

  /**
   * 保存多张图片
   * @param {object} data 图片数据
   * @param {object} options 选项
   * @returns {Promise} 保存结果
   */
  async saveMultiImage(data, options = {}) {
    return await this.sendRequest('SAVE_MULTI_IMAGE', data, options);
  }

  /**
   * 销毁 Worker
   */
  destroy() {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
    
    // 拒绝所有待处理的请求
    for (const [id, request] of this.pendingRequests) {
      request.reject(new Error('Worker 已销毁'));
    }
    this.pendingRequests.clear();
    
    this.isInitialized = false;
    console.log('🔧 Worker 管理器已销毁');
  }
}

// 创建单例实例
const workerManager = new WorkerManager();

// 页面卸载时销毁 Worker
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    workerManager.destroy();
  });
}

export default workerManager;