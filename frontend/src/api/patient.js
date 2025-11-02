/**
 * 病人管理相关API
 * 适配后端 FastAPI 接口
 */

import { http } from '@/utils/request';

const patientAPI = {
  /**
   * 获取病人列表（分页）
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码（从1开始）
   * @param {number} params.pageSize - 每页数量
   * @param {string} params.name - 姓名模糊查询
   * @param {string} params.patient_id - 患者编号模糊查询
   * @param {string} params.status - 状态筛选 (active/inactive/deceased)
   * @param {string} params.gender - 性别筛选 (male/female/other)
   */
  getPatients(params = {}) {
    const queryParams = {
      page: params.page || 1,
      page_size: params.pageSize || 10
    };
    
    // 添加可选参数
    if (params.name) queryParams.name = params.name;
    if (params.patient_id) queryParams.patient_id = params.patient_id;
    if (params.status) queryParams.status = params.status;
    if (params.gender) queryParams.gender = params.gender;
    
    return http.get('/patients', queryParams);
  },

  /**
   * 获取单个病人信息
   * @param {number} id - 患者ID
   */
  getPatient(id) {
    return http.get(`/patients/${id}`);
  },

  /**
   * 根据患者编号获取病人信息
   * @param {string} patientId - 患者编号
   */
  getPatientByPatientId(patientId) {
    return http.get(`/patients/by-patient-id/${patientId}`);
  },

  /**
   * 创建病人
   * @param {Object} data - 患者数据
   */
  createPatient(data) {
    return http.post('/patients', data);
  },

  /**
   * 更新病人信息
   * @param {number} id - 患者ID
   * @param {Object} data - 更新数据
   */
  updatePatient(id, data) {
    return http.put(`/patients/${id}`, data);
  },

  /**
   * 批量删除病人（软删除）
   * @param {Array} patientIds - 患者ID列表
   * @param {number} deletedBy - 删除操作人ID
   */
  deletePatients(patientIds, deletedBy = null) {
    return http.delete('/patients', {
      data: {
        patient_ids: patientIds,
        deleted_by: deletedBy
      }
    });
  },

  /**
   * 删除单个病人（软删除）
   * @param {number} id - 患者ID
   */
  deletePatient(id) {
    return this.deletePatients([id]);
  }
};

export default patientAPI;
