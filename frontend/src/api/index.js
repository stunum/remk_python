/**
 * API接口统一入口
 * 导出所有API模块
 */

// 导出认证相关API
export { authAPI } from './auth';

// 导出系统相关API
export { systemAPI } from './system';

// 导出病人管理相关API
export { default as patientAPI } from './patient';

// 导出检查记录相关API
export { default as examinationAPI } from './examination';

// 导出硬件控制相关API
export { default as hardwareAPI } from './hardware';

// 导出挂号管理相关API
export { default as registrationAPI } from './registration';

// 导出医生相关API
export { default as doctorAPI } from './doctor';

// 导出检查类型相关API
export { default as examinationTypeAPI } from './examinationType';

// 导出请求工具
export { http } from '@/utils/request';

// 默认导出所有API
export default {
  auth: () => import('./auth').then(m => m.authAPI),
  system: () => import('./system').then(m => m.systemAPI),
  patient: () => import('./patient').then(m => m.default),
  examination: () => import('./examination').then(m => m.default),
  registration: () => import('./registration').then(m => m.default),
  doctor: () => import('./doctor').then(m => m.default),
  examinationType: () => import('./examinationType').then(m => m.default),
};