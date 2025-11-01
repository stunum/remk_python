/**
 * 医生相关API
 */

import { http } from '@/utils/request';

const doctorAPI = {
  // 获取医生列表
  getDoctors(params = {}) {
    return http.get('/users', {
      role: 'doctor',
      page: params.page || 1,
      page_size: params.pageSize || 100,
      search: params.search || '',
      department: params.department || '',
      status: params.status || 'active',
      order_by: params.orderBy || 'full_name',
      order: params.order || 'asc'
    });
  },

  // 获取单个医生信息
  getDoctor(id) {
    return http.get(`/users/${id}`);
  }
};

export default doctorAPI;