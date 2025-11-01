/**
 * 图像保存 Web Worker
 * 在后台线程处理图像保存请求，避免阻塞主线程的渲染
 */

// Worker 中不能直接使用 import，需要使用 importScripts
// 但现代浏览器支持 ES6 模块，我们使用 fetch API

/**
 * 发送 HTTP 请求
 * @param {string} url 请求地址
 * @param {object} options 请求选项
 * @returns {Promise} 请求结果
 */
async function sendRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: JSON.stringify(options.data),
      ...options
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    throw new Error(`请求失败: ${error.message}`);
  }
}

/**
 * 保存单张图片
 * @param {object} data 图片数据
 * @param {object} options 选项
 */
async function saveImage(data, options = {}) {
  const baseURL = options.baseURL || 'http://localhost:8080/api';
  const url = `${baseURL}/images/save-image`;
  
  // 添加认证 token
  const headers = { ...options.headers };
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  return await sendRequest(url, {
    data,
    headers,
    timeout: 30000
  });
}

/**
 * 保存多张图片
 * @param {object} data 图片数据
 * @param {object} options 选项
 */
async function saveMultiImage(data, options = {}) {
  const baseURL = options.baseURL || 'http://localhost:8080/api';
  const url = `${baseURL}/images/save-multi-image`;
  
  // 添加认证 token
  const headers = { ...options.headers };
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  return await sendRequest(url, {
    data,
    headers,
    timeout: 30000
  });
}

/**
 * 获取用户 token
 * @returns {string|null} 用户 token
 */
function getUserToken() {
  try {
    // Worker 中无法访问 localStorage，需要从主线程传递
    return null;
  } catch (error) {
    return null;
  }
}

// 监听主线程消息
self.addEventListener('message', async (event) => {
  const { id, type, data, options = {} } = event.data;

  try {
    let result;

    switch (type) {
      case 'SAVE_IMAGE':
        console.log('🔧 Worker: 开始保存单张图片', { id, data });
        result = await saveImage(data, options);
        break;

      case 'SAVE_MULTI_IMAGE':
        console.log('🔧 Worker: 开始保存多张图片', { id, data });
        result = await saveMultiImage(data, options);
        break;

      default:
        throw new Error(`未知的操作类型: ${type}`);
    }

    // 发送成功结果到主线程
    self.postMessage({
      id,
      type: 'SUCCESS',
      result
    });

    console.log('✅ Worker: 图片保存成功', { id, type });

  } catch (error) {
    console.error('❌ Worker: 图片保存失败', { id, type, error: error.message });

    // 发送错误结果到主线程
    self.postMessage({
      id,
      type: 'ERROR',
      error: {
        message: error.message,
        stack: error.stack
      }
    });
  }
});

// Worker 启动日志
console.log('🚀 图像保存 Worker 已启动');