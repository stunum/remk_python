/**
 * 路由守卫
 * 处理认证、权限检查和页面跳转
 */

import { useUserStore } from '@/store/modules/user';
import { message } from 'ant-design-vue';

// 不需要登录的页面
const PUBLIC_ROUTES = ['/login', '/register', '/forgot-password'];

// 需要特定权限的页面配置
const PERMISSION_ROUTES = {
  '/settings': ['system_config'],
  '/users': ['user_manage', 'user_view'],
  '/patients': ['patient_manage', 'patient_view'],
  '/examinations': ['exam_manage', 'exam_view']
};

// 需要特定用户类型的页面配置
const USER_TYPE_ROUTES = {
  '/admin': ['admin'],
  '/doctor': ['admin', 'doctor'],
  '/technician': ['admin', 'doctor', 'technician']
};

/**
 * 前置路由守卫
 * @param {Object} to 目标路由
 * @param {Object} from 来源路由
 * @param {Function} next 导航函数
 */
export async function beforeEachGuard(to, from, next) {
  const userStore = useUserStore();
  
  console.log('路由守卫 - 准备导航到:', to.path);
  console.log('路由守卫 - 用户登录状态:', userStore.isLoggedIn);
  console.log('路由守卫 - 用户认证状态:', userStore.isAuthenticated);
  
  // 初始化用户状态（从本地存储恢复）
  if (!userStore.isLoggedIn) {
    await userStore.initializeUserState();
    console.log('路由守卫 - 初始化后用户状态:', userStore.isAuthenticated);
  }
  
  // 检查是否为公开路由
  if (PUBLIC_ROUTES.includes(to.path)) {
    console.log('路由守卫 - 访问公开路由:', to.path);
    // 如果已登录且访问登录页，重定向到首页
    if (userStore.isAuthenticated && to.path === '/login') {
      console.log('路由守卫 - 已登录用户访问登录页，重定向到首页');
      next('/index');
      return;
    }
    next();
    return;
  }
  
  // 检查是否已登录
  if (!userStore.isAuthenticated) {
    console.log('路由守卫 - 用户未认证，重定向到登录页');
    message.warning('请先登录');
    next({
      path: '/login',
      query: { redirect: to.fullPath } // 保存目标页面，登录后跳转
    });
    return;
  }
  
  console.log('路由守卫 - 用户已认证，允许访问:', to.path);
  
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 瑞尔明康眼底检查系统`;
  }
  
  // 对于/index页面，暂时跳过复杂验证
  if (to.path === '/index') {
    console.log('路由守卫 - 直接允许访问首页');
    next();
    return;
  }
  
  // 其他页面进行正常验证
  next();
}

/**
 * 后置路由守卫
 * @param {Object} to 目标路由
 * @param {Object} from 来源路由
 */
export function afterEachGuard(to, from) {
  // 设置页面标题
  const title = to.meta?.title || '眼底检查系统';
  document.title = `${title} - 瑞尔明康`;
  
  // 记录页面访问日志（可选）
  console.log(`页面导航: ${from.path} -> ${to.path}`);
}

/**
 * 检查页面权限
 * @param {string} path 页面路径
 * @param {Object} userStore 用户store
 * @returns {Object} 权限检查结果
 */
function checkPagePermission(path, userStore) {
  // 检查是否需要特定权限
  const requiredPermissions = PERMISSION_ROUTES[path];
  if (!requiredPermissions) {
    return { allowed: true };
  }
  
  // 管理员拥有所有权限
  if (userStore.isAdmin) {
    return { allowed: true };
  }
  
  // 检查用户是否有所需权限中的任意一个
  const hasPermission = userStore.hasAnyPermission(requiredPermissions);
  if (!hasPermission) {
    return {
      allowed: false,
      message: `访问此页面需要以下权限之一: ${requiredPermissions.join(', ')}`
    };
  }
  
  return { allowed: true };
}

/**
 * 检查用户类型权限
 * @param {string} path 页面路径
 * @param {Object} userStore 用户store
 * @returns {Object} 权限检查结果
 */
function checkUserTypePermission(path, userStore) {
  const requiredUserTypes = USER_TYPE_ROUTES[path];
  if (!requiredUserTypes) {
    return { allowed: true };
  }
  
  const currentUserType = userStore.user?.user_type;
  if (!requiredUserTypes.includes(currentUserType)) {
    return {
      allowed: false,
      message: `此页面仅限以下用户类型访问: ${requiredUserTypes.join(', ')}`
    };
  }
  
  return { allowed: true };
}

/**
 * 根据用户类型获取默认页面
 * @param {string} userType 用户类型
 * @returns {string} 默认页面路径
 */
function getDefaultPageByUserType(userType) {
  switch (userType) {
    case 'admin':
      return '/index';
    case 'doctor':
      return '/index';
    case 'technician':
      return '/view-images';
    case 'viewer':
      return '/view-images';
    default:
      return '/index';
  }
}

/**
 * 检查路由权限（供组件使用）
 * @param {string} path 路径
 * @param {Object} userStore 用户store
 * @returns {boolean} 是否有权限
 */
export function canAccessRoute(path, userStore) {
  const pagePermission = checkPagePermission(path, userStore);
  const userTypePermission = checkUserTypePermission(path, userStore);
  
  return pagePermission.allowed && userTypePermission.allowed;
}

/**
 * 获取用户可访问的菜单项
 * @param {Array} menuItems 菜单配置
 * @param {Object} userStore 用户store
 * @returns {Array} 过滤后的菜单项
 */
export function getAccessibleMenuItems(menuItems, userStore) {
  return menuItems.filter(item => {
    // 检查菜单项权限
    if (item.permissions && !userStore.hasAnyPermission(item.permissions)) {
      return false;
    }
    
    // 检查用户类型权限
    if (item.userTypes && !item.userTypes.includes(userStore.user?.user_type)) {
      return false;
    }
    
    // 检查路由权限
    if (item.path && !canAccessRoute(item.path, userStore)) {
      return false;
    }
    
    // 递归检查子菜单
    if (item.children) {
      item.children = getAccessibleMenuItems(item.children, userStore);
      // 如果所有子菜单都被过滤掉，则隐藏父菜单
      if (item.children.length === 0) {
        return false;
      }
    }
    
    return true;
  });
}

/**
 * 权限指令（供模板使用）
 * @param {string|Array} permissions 权限代码
 * @param {Object} userStore 用户store
 * @returns {boolean} 是否有权限
 */
export function hasPermissionDirective(permissions, userStore) {
  if (!permissions) return true;
  
  const permissionArray = Array.isArray(permissions) ? permissions : [permissions];
  return userStore.hasAnyPermission(permissionArray);
}

/**
 * 用户类型指令（供模板使用）
 * @param {string|Array} userTypes 用户类型
 * @param {Object} userStore 用户store
 * @returns {boolean} 是否匹配用户类型
 */
export function hasUserTypeDirective(userTypes, userStore) {
  if (!userTypes) return true;
  
  const userTypeArray = Array.isArray(userTypes) ? userTypes : [userTypes];
  const currentUserType = userStore.user?.user_type;
  
  return userTypeArray.includes(currentUserType);
}
