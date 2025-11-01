/**
 * 挂号管理相关API
 */

import { http } from '@/utils/request';

const registrationAPI = {
  // 获取挂号记录列表
  getRegistrations(params = {}) {
    const queryParams = {
      page: params.page || 1,
      page_size: params.pageSize || 10,
      search: params.search || '',
      scheduled_date: params.scheduledDate || '',
      department: params.department || '',
      order_by: params.orderBy || 'scheduled_date',
      order: params.order || 'desc'
    };

    // 透传患者ID与队列模式
    if (params.patientId) {
      queryParams.patient_id = params.patientId;
    }
    if (params.patient_id) {
      queryParams.patient_id = params.patient_id;
    }
    if (params.queue_mode === true) {
      queryParams.queue_mode = true;
    }

    // 处理单个状态或多个状态
    if (params.statuses && Array.isArray(params.statuses)) {
      // 多状态查询，将数组转换为逗号分隔的字符串
      queryParams.statuses = params.statuses.join(',');
    } else if (params.status) {
      queryParams.status = params.status;
    }

    return http.get('/registrations', queryParams);
  },

  // 获取单个挂号记录
  getRegistration(id) {
    return http.get(`/registrations/${id}`);
  },

  // 创建挂号记录
  createRegistration(data) {
    return http.post('/registrations', data);
  },

  // 更新挂号状态
  updateRegistrationStatus(id, status) {
    return http.patch(`/registrations/${id}/status`, { status });
  },

  // 获取挂号统计数据
  getRegistrationStats(params = {}) {
    return http.get('/registrations/stats', params);
  }
};

export default registrationAPI;
