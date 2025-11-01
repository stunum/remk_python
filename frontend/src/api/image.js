import request from '@/utils/request';

/**
 * 保存图片到本地和数据库
 * @param {Object} data - 图片数据
 * @param {number} data.examination_id - 检查记录ID
 * @param {number} data.registration_id - 注册记录ID
 * @param {string} data.patient_id - 患者ID
 * @param {string} data.file_dir - 文件夹
 * @param {Array} data.images - 图片路径数组
 * @param {string} data.eye_side - 眼别 (OD/OS)
 * @param {string} data.image_type - 影像类型
 * @param {string} data.resolution - 分辨率
 * @param {string} data.file_format - 文件格式
 * @param {string} data.acquisition_device - 采集设备
 * @param {Object} options - 选项参数，包含showLoading等
 */
export function saveImage(data, options = {}) {
  const { showLoading = true, ...otherOptions } = options;
  return request({
    url: '/images/save-image',  // 去掉 /api 前缀，baseURL已经包含了
    method: 'POST',
    data,
    timeout: 30000,  // 30秒超时，图片数据可能较大
    showLoading: showLoading,
    ...otherOptions
  });
}

/**
 * 保存图片到本地和数据库
 * @param {Object} data - 图片数据
 * @param {number} data.examination_id - 检查记录ID
 * @param {number} data.registration_id - 注册记录ID
 * @param {string} data.patient_id - 患者ID
 * @param {string} data.file_dir - 文件夹
 * @param {Array} data.images - 图片路径数组
 * @param {string} data.eye_side - 眼别 (OD/OS)
 * @param {string} data.image_type - 影像类型
 * @param {string} data.resolution - 分辨率
 * @param {string} data.file_format - 文件格式
 * @param {string} data.acquisition_device - 采集设备
 * @param {Object} options - 选项参数，包含showLoading等
 */
export function saveMultiImage(data, options = {}) {
  const { showLoading = true, ...otherOptions } = options;
  return request({
    url: '/images/save-multi-image',  // 去掉 /api 前缀，baseURL已经包含了
    method: 'POST',
    data,
    timeout: 30000,  // 30秒超时，图片数据可能较大
    showLoading: showLoading,
    ...otherOptions
  });
}
/**
 * 保存视频到本地和数据库
 * @param {Object} data - 视频数据
 * @param {number} data.examination_id - 检查记录ID
 * @param {string} data.video_data - base64视频数据
 * @param {string} data.cover_image_data - base64封面图片数据
 * @param {string} data.eye_side - 眼别 (left/right)
 * @param {number} data.duration - 视频时长（秒）
 * @param {string} data.file_format - 文件格式 (webm/mp4)
 * @param {string} data.acquisition_device - 采集设备
 */
export function saveVideo(data) {
  return request({
    url: '/images/save-video',  // 去掉 /api 前缀，baseURL已经包含了
    method: 'POST',
    data,
    timeout: 60000  // 60秒超时，视频数据较大
  });
}

/**
 * 获取眼底图像列表
 */
export function getFundusImages(params) {
  return request({
    url: '/images',  // 去掉 /api 前缀，baseURL已经包含了
    method: 'GET',
    params
  });
}

/**
 * 获取单个眼底图像
 */
export function getFundusImage(id) {
  return request({
    url: `/images/${id}`,  // 去掉 /api 前缀，baseURL已经包含了
    method: 'GET'
  });
}

/**
 * 删除眼底图像
 */
export function deleteFundusImage(id) {
  return request({
    url: `/images/${id}`,  // 去掉 /api 前缀，baseURL已经包含了
    method: 'DELETE'
  });
}

