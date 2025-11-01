/**
 * 检查类型相关API
 */

import { http } from '@/utils/request';

const examinationTypeAPI = {
  // 获取检查类型列表
  getExaminationTypes(params = {}) {
    return http.get('/examinations/types', {
      page: params.page || 1,
      page_size: params.pageSize || 100,
      search: params.search || '',
      is_active: params.isActive !== undefined ? params.isActive : true,
      order_by: params.orderBy || 'type_name',
      order: params.order || 'asc'
    });
  },

  // 获取单个检查类型
  getExaminationType(id) {
    return http.get(`/examinations/types/${id}`);
  }
};

export default examinationTypeAPI;