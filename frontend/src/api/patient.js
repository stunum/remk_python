/**
 * 病人管理相关API
 */

import { http } from '@/utils/request';

const patientAPI = {
  // 获取病人列表
  getPatients(params = {}) {
    return http.get('/patients', {
      page: params.page || 1,
      page_size: params.pageSize || 10,
      search: params.search || '',
      status: params.status || '',
      order_by: params.orderBy || 'created_at',
      order: params.order || 'desc'
    });
  },

  // 获取单个病人信息
  getPatient(id) {
    return http.get(`/patients/${id}`);
  },

  // 创建病人
  createPatient(data) {
    return http.post('/patients', data);
  },

  // 更新病人信息
  updatePatient(id, data) {
    return http.put(`/patients/${id}`, data);
  },

  // 删除病人
  deletePatient(id) {
    return http.delete(`/patients/${id}`);
  }
};

export default patientAPI;
