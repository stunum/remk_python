/**
 * 硬件控制相关API
 * 直接访问独立硬件服务（端口 25512）
 * Electron 环境不存在 CORS 跨域问题
 */

// 硬件服务地址
const HARDWARE_API_BASE = 'http://localhost:25512/api';



/**
 * 启动设备
 * @returns {Promise} 响应数据
 */
export function startDevice() {
  console.log('🔧 调用硬件服务API: 启动设备');
  const url = `${HARDWARE_API_BASE}/hardware/start`;
  
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 启动设备响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 启动设备失败:', error);
    throw new Error(`启动设备失败: ${error.message}`);
  });
}

/**
 * 停止设备
 * @returns {Promise} 响应数据
 */
export function stopDevice() {
  console.log('🔧 调用硬件服务API: 停止设备');
  const url = `${HARDWARE_API_BASE}/hardware/stop`;
  
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 停止设备响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 停止设备失败:', error);
    throw new Error(`停止设备失败: ${error.message}`);
  });
}

/**
 * 复位设备
 * @returns {Promise} 响应数据
 */
export function resetDevice() {
  console.log('🔧 调用硬件服务API: 复位设备');
  const url = `${HARDWARE_API_BASE}/hardware/reset`;
  
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 复位设备响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 复位设备失败:', error);
    throw new Error(`复位设备失败: ${error.message}`);
  });
}

/**
 * 获取设备状态
 * @returns {Promise} 响应数据
 */
export function getDeviceStatus() {
  console.log('🔧 调用硬件服务API: 获取设备状态');
  const url = `${HARDWARE_API_BASE}/hardware/status`;
  
  return fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 获取设备状态响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 获取设备状态失败:', error);
    throw new Error(`获取设备状态失败: ${error.message}`);
  });
}

/**
 * 获取设备信息
 * @returns {Promise} 响应数据
 */
export function getDeviceInfo() {
  console.log('🔧 调用硬件服务API: 获取设备信息');
  const url = `${HARDWARE_API_BASE}/hardware/info`;
  
  return fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 获取设备信息响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 获取设备信息失败:', error);
    throw new Error(`获取设备信息失败: ${error.message}`);
  });
}

/**
 * 设置相机增益
 * @param {number} analog - 亮度值
 * @param {number} digital - 微调值
 * @returns {Promise} 响应数据
 */
export function setCameraGain(analog, digital) {
  console.log('🔧 调用硬件服务API: 设置相机增益', { analog, digital });
  const url = `${HARDWARE_API_BASE}/hardware/camera/gain`;
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      analog: analog,
      digital: digital
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('📷 相机增益设置响应:', data);
    return data;
  })
  .catch(error => {
    console.error('📷 相机增益设置失败:', error);
    throw new Error(`设置相机增益失败: ${error.message}`);
  });
}

/**
 * 重启相机
 * @returns {Promise} 响应数据
 */
export function restartCamera() {
  console.log('🔧 调用硬件服务API: 重启相机');
  const url = `${HARDWARE_API_BASE}/hardware/camera/restart`;
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('📷 相机重启响应:', data);
    return data;
  })
  .catch(error => {
    console.error('📷 相机重启失败:', error);
    throw new Error(`重启相机失败: ${error.message}`);
  });
}

/**
 * 设置壁纸位置
 * @param {string} pos - 位置: "top"上, "bottom"下, "left"左, "right"右, "middle"中
 * @returns {Promise} 响应数据
 */
export function setWallpaperPosition(pos) {
  console.log('🔧 调用硬件服务API: 设置壁纸位置', { pos });
  const url = `${HARDWARE_API_BASE}/wallpaper`;
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      pos: pos
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 壁纸位置设置响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 壁纸位置设置失败:', error);
    throw new Error(`设置壁纸位置失败: ${error.message}`);
  });
}

/**
 * 拍照接口
 * @param {string} mode - 拍摄模式: "gray" 灰度模式, "color" 彩色模式
 * @param {string} folderpath - 保存目录路径
 * @param {Object} options - 选项参数，包含showLoading等
 * @returns {Promise} 响应数据
 */
export function captureImage(mode, folderpath, options = {}) {
  console.log('🔧 调用硬件服务API: 拍照', { mode, folderpath });
  const url = `${HARDWARE_API_BASE}/capture`;
  const { showLoading = true } = options;
  
  const requestBody = {
    mode: mode,
    folderpath: folderpath
  };
  
  // 如果需要显示loading，可以在这里添加loading逻辑
  // 由于这里使用的是原生fetch，showLoading参数主要用于与其他API保持一致
  // 实际的loading控制在调用方处理
  
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 拍照响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 拍照失败:', error);
    throw new Error(`拍照失败: ${error.message}`);
  });
}

/**
 * 获取眼睛左右状态
 * @returns {Promise} 响应数据，包含眼睛状态信息 "OD"(右眼) 或 "OS"(左眼)
 */
export function getEyeSideStatus() {
  console.log('🔧 调用硬件服务API: 获取眼睛左右状态');
  const url = `${HARDWARE_API_BASE}/hardware/status/osd`;
  
  return fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('✅ 获取眼睛左右状态响应:', data);
    return data;
  })
  .catch(error => {
    console.error('❌ 获取眼睛左右状态失败:', error);
    throw new Error(`获取眼睛左右状态失败: ${error.message}`);
  });
}

export default {
  startDevice,
  stopDevice,
  resetDevice,
  getDeviceStatus,
  getDeviceInfo,
  setCameraGain,
  restartCamera,
  captureImage,
  setWallpaperPosition,
  getEyeSideStatus
};

