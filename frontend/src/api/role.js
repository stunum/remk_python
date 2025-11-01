/**
 * 角色管理相关API
 */

import { http } from '@/utils/request';

const roleAPI = {
  // 获取角色列表
  getRoles(params = {}) {
    return http.get('/roles', params);
  },

  // 创建角色
  createRole(data) {
    return http.post('/roles', data);
  },

  // 获取单个角色信息
  getRole(id) {
    return http.get(`/roles/${id}`);
  },

  // 更新角色信息
  updateRole(id, data) {
    return http.put(`/roles/${id}`, data);
  },

  // 删除角色
  deleteRole(id) {
    return http.delete(`/roles/${id}`);
  },

  // 获取角色权限
  getRolePermissions(id) {
    return http.get(`/roles/${id}/permissions`);
  },

  // 更新角色权限
  updateRolePermissions(id, permissionIds) {
    return http.put(`/roles/${id}/permissions`, { permission_ids: permissionIds });
  }
};

export default roleAPI;
