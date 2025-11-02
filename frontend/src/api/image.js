/**
 * 眼底图像相关API
 * 适配后端 FastAPI 接口
 */

import { http } from '@/utils/request';

const fundusImageAPI = {
  /**
   * 获取眼底图像列表（分页）
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码（从1开始）
   * @param {number} params.pageSize - 每页数量
   * @param {number} params.examinationId - 按检查记录ID筛选
   * @param {string} params.eyeSide - 按眼别筛选 (OS/OD)
   * @param {string} params.captureMode - 按拍摄模式筛选 (gray/color)
   * @param {string} params.imageQuality - 按影像质量筛选 (excellent/good/fair/poor)
   * @param {string} params.uploadStatus - 按上传状态筛选 (uploading/uploaded/failed/processing)
   * @param {boolean} params.isPrimary - 按是否主图筛选
   * @param {boolean} params.includeDeleted - 是否包含已删除记录
   */
  getFundusImages(params = {}) {
    const queryParams = {
      page: params.page || 1,
      page_size: params.pageSize || 10
    };
    
    // 添加可选参数
    if (params.examinationId) queryParams.examination_id = params.examinationId;
    if (params.eyeSide) queryParams.eye_side = params.eyeSide;
    if (params.captureMode) queryParams.capture_mode = params.captureMode;
    if (params.imageQuality) queryParams.image_quality = params.imageQuality;
    if (params.uploadStatus) queryParams.upload_status = params.uploadStatus;
    if (params.isPrimary !== undefined) queryParams.is_primary = params.isPrimary;
    if (params.includeDeleted) queryParams.include_deleted = params.includeDeleted;
    
    return http.get('/fundus-images', queryParams);
  },

  /**
   * 获取单个眼底图像
   * @param {number} id - 图像ID
   */
  getFundusImage(id) {
    return http.get(`/fundus-images/${id}`);
  },

  /**
   * 创建眼底图像记录
   * @param {Object} data - 图像数据
   */
  createFundusImage(data) {
    return http.post('/fundus-images', data);
  },

  /**
   * 更新眼底图像信息
   * @param {number} id - 图像ID
   * @param {Object} data - 更新数据
   */
  updateFundusImage(id, data) {
    return http.put(`/fundus-images/${id}`, data);
  },

  /**
   * 批量删除眼底图像（软删除）
   * @param {Array} imageIds - 图像ID列表
   */
  deleteFundusImages(imageIds) {
    return http.delete('/fundus-images', {
      data: {
        ids: imageIds
      }
    });
  },

  /**
   * 删除单个眼底图像（软删除）
   * @param {number} id - 图像ID
   */
  deleteFundusImage(id) {
    return this.deleteFundusImages([id]);
  },

  /**
   * 保存图片到本地和数据库（自定义接口，如果后端有提供）
   * @param {Object} data - 图片数据
   * @param {number} data.examination_id - 检查记录ID
   * @param {Array} data.images - 图片路径数组
   * @param {string} data.eye_side - 眼别 (OD/OS)
   * @param {string} data.image_type - 影像类型
   * @param {string} data.resolution - 分辨率
   * @param {string} data.file_format - 文件格式
   * @param {string} data.acquisition_device - 采集设备
   */
  saveImage(data) {
    return http.post('/fundus-images/save-image', data, {
      timeout: 30000
    });
  },

  /**
   * 批量保存图片
   * @param {Object} data - 图片数据
   */
  saveMultiImage(data) {
    return http.post('/fundus-images/save-multi-image', data, {
      timeout: 30000
    });
  },

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
  saveVideo(data) {
    return http.post('/fundus-images/save-video', data, {
      timeout: 60000
    });
  }
};

export default fundusImageAPI;

// 兼容旧的导出方式
export const getFundusImages = fundusImageAPI.getFundusImages;
export const getFundusImage = fundusImageAPI.getFundusImage;
export const deleteFundusImage = fundusImageAPI.deleteFundusImage;
export const saveImage = fundusImageAPI.saveImage;
export const saveMultiImage = fundusImageAPI.saveMultiImage;
export const saveVideo = fundusImageAPI.saveVideo;

