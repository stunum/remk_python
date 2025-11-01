/**
 * 用户管理相关API
 */

import { http } from '@/utils/request';

const userAPI = {
  // 获取用户列表
  getUsers(params = {}) {
    return http.get('/users', {
      page: params.page || 1,
      page_size: params.pageSize || 10,
      search: params.search || '',
      role: params.role || '',
      roles: params.roles || '',
      department: params.department || '',
      status: params.status || 'active',
      order_by: params.orderBy || 'full_name',
      order: params.order || 'asc'
    });
  },

  // 创建用户
  createUser(data) {
    return http.post('/users', data);
  },

  // 获取单个用户信息
  getUser(id) {
    return http.get(`/users/${id}`);
  },

  // 更新用户信息
  updateUser(id, data) {
    return http.put(`/users/${id}`, data);
  },

  // 删除用户
  deleteUser(id) {
    return http.delete(`/users/${id}`);
  },

  // 更新用户状态
  updateUserStatus(id, status) {
    return http.patch(`/users/${id}/status`, { status });
  },

  // 获取用户角色
  getUserRoles(id) {
    return http.get(`/users/${id}/roles`);
  },

  // 更新用户角色
  updateUserRoles(id, roleIds) {
    return http.put(`/users/${id}/roles`, { role_ids: roleIds });
  }
};

export default userAPI;
