/**
 * 检查记录相关API
 */

import { http } from '@/utils/request';

const examinationAPI = {
  // 获取检查记录列表
  getExaminations(params = {}) {
    return http.get('/examinations', {
      page: params.page || 1,
      page_size: params.pageSize || 10,
      search: params.search || '',
      status: params.status || '',
      patient_id: params.patientId || '',
      examination_date: params.examinationDate || '',
      order_by: params.orderBy || 'examination_date',
      order: params.order || 'desc',
      include: params.include || ''
    });
  },

  // 获取病人检查记录（包含病人信息）
  getPatientExaminations(params = {}) {
    return http.get('/examinations/with-patients', {
      page: params.page || 1,
      page_size: params.pageSize || 10,
      search: params.search || '',
      status: params.status || '',
      examination_date: params.examinationDate || '',
      order_by: params.orderBy || 'examination_date',
      order: params.order || 'desc'
    });
  },

  // 获取单个检查记录
  getExamination(id) {
    return http.get(`/examinations/${id}`);
  },

  // 创建检查记录
  createExamination(data) {
    return http.post('/examinations', data);
  },

  // 更新检查记录
  updateExamination(id, data) {
    return http.put(`/examinations/${id}`, data);
  },

  // 更新检查状态
  updateExaminationStatus(id, status) {
    return http.patch(`/examinations/${id}/status`, { status });
  },

  // 删除检查记录
  deleteExamination(id) {
    return http.delete(`/examinations/${id}`);
  },

  // 获取检查统计数据
  getExaminationStats(params = {}) {
    return http.get('/examinations/stats', params);
  }
};

export default examinationAPI;
