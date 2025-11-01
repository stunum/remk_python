/**
 * 权限管理相关API
 */

import { http } from '@/utils/request';

const permissionAPI = {
  // 获取权限列表
  getPermissions(params = {}) {
    return http.get('/permissions', params);
  }
};

export default permissionAPI;
