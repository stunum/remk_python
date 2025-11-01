/**
 * 就诊管理相关API
 */

import request from '@/utils/request';

export function getVisitManagementList(params = {}) {
  return request({
    url: '/visit-management',
    method: 'get',
    params
  });
}

export default {
  getVisitManagementList
};

