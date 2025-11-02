/**
 * 检查记录相关API
 * 适配后端 FastAPI 接口
 */

import { http } from '@/utils/request';

const examinationAPI = {
  /**
   * 获取检查记录列表（分页）
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码（从1开始）
   * @param {number} params.pageSize - 每页数量
   * @param {number} params.patientId - 按患者ID筛选
   * @param {number} params.doctorId - 按医生ID筛选
   * @param {number} params.examinationTypeId - 按检查类型ID筛选
   * @param {string} params.status - 按状态筛选 (pending/in_progress/completed/cancelled)
   * @param {string} params.examinationNumber - 按检查编号筛选
   * @param {string} params.startDate - 开始日期 (YYYY-MM-DD)
   * @param {string} params.endDate - 结束日期 (YYYY-MM-DD)
   * @param {boolean} params.includeDeleted - 是否包含已删除记录
   */
  getExaminations(params = {}) {
    const queryParams = {
      page: params.page || 1,
      page_size: params.pageSize || 10
    };
    
    // 添加可选参数
    if (params.patientId) queryParams.patient_id = params.patientId;
    if (params.doctorId) queryParams.doctor_id = params.doctorId;
    if (params.examinationTypeId) queryParams.examination_type_id = params.examinationTypeId;
    if (params.status) queryParams.status = params.status;
    if (params.examinationNumber) queryParams.examination_number = params.examinationNumber;
    if (params.startDate) queryParams.start_date = params.startDate;
    if (params.endDate) queryParams.end_date = params.endDate;
    if (params.includeDeleted) queryParams.include_deleted = params.includeDeleted;
    
    return http.get('/examinations', queryParams);
  },

  /**
   * 获取单个检查记录
   * @param {number} id - 检查记录ID
   */
  getExamination(id) {
    return http.get(`/examinations/${id}`);
  },

  /**
   * 根据检查编号获取检查记录
   * @param {string} examinationNumber - 检查编号
   */
  getExaminationByNumber(examinationNumber) {
    return http.get(`/examinations/by-number/${examinationNumber}`);
  },

  /**
   * 创建检查记录
   * @param {Object} data - 检查记录数据
   */
  createExamination(data) {
    return http.post('/examinations', data);
  },

  /**
   * 更新检查记录
   * @param {number} id - 检查记录ID
   * @param {Object} data - 更新数据
   */
  updateExamination(id, data) {
    return http.put(`/examinations/${id}`, data);
  },

  /**
   * 批量删除检查记录（软删除）
   * @param {Array} examinationIds - 检查记录ID列表
   */
  deleteExaminations(examinationIds) {
    return http.delete('/examinations', {
      data: {
        examination_ids: examinationIds
      }
    });
  },

  /**
   * 删除单个检查记录（软删除）
   * @param {number} id - 检查记录ID
   */
  deleteExamination(id) {
    return this.deleteExaminations([id]);
  }
};

export default examinationAPI;
