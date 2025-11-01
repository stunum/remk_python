/**
 * 自动路由生成工具
 * 根据文件夹结构自动生成路由配置
 */

/**
 * 自动导入所有视图文件并生成路由
 * @returns {Array} 路由配置数组
 */
export function generateAutoRoutes() {
  // 使用 Vite 的 import.meta.glob 功能自动导入所有 .vue 文件
  const modules = import.meta.glob('../views/**/*.vue', { eager: false });
  const routes = [];

  Object.keys(modules).forEach((path) => {
    // 提取文件路径信息
    const routePath = getRoutePathFromFile(path);
    const routeName = getRouteNameFromFile(path);
    const component = modules[path];

    // 跳过以 _ 开头的文件（私有组件）
    if (routeName.startsWith('_')) {
      return;
    }

    routes.push({
      path: routePath,
      name: routeName,
      component: component,
      meta: {
        // 从文件路径中提取元信息
        title: formatTitle(routeName),
        requiresAuth: checkAuthRequired(path),
        layout: getLayoutFromPath(path)
      }
    });
  });

  return routes;
}

/**
 * 从文件路径生成路由路径
 * @param {string} filePath 文件路径
 * @returns {string} 路由路径
 */
function getRoutePathFromFile(filePath) {
  // ../views/User/Profile.vue -> /user/profile
  // ../views/Index.vue -> /
  // ../views/Login.vue -> /login
  
  let path = filePath
    .replace('../views/', '')
    .replace('.vue', '')
    .toLowerCase();

  // 处理嵌套路由
  if (path.includes('/')) {
    path = '/' + path.replace(/\//g, '/').toLowerCase();
  } else {
    path = path === 'index' ? '/' : '/' + path;
  }

  // 处理动态路由 [id].vue -> /:id
  path = path.replace(/\[([^\]]+)\]/g, ':$1');

  return path;
}

/**
 * 从文件路径生成路由名称
 * @param {string} filePath 文件路径
 * @returns {string} 路由名称
 */
function getRouteNameFromFile(filePath) {
  return filePath
    .replace('../views/', '')
    .replace('.vue', '')
    .replace(/\//g, '-')
    .toLowerCase();
}

/**
 * 格式化标题
 * @param {string} name 路由名称
 * @returns {string} 格式化后的标题
 */
function formatTitle(name) {
  return name
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * 检查是否需要认证
 * @param {string} path 文件路径
 * @returns {boolean} 是否需要认证
 */
function checkAuthRequired(path) {
  // 登录页面不需要认证
  if (path.includes('Login') || path.includes('login')) {
    return false;
  }
  
  // 公共页面不需要认证
  const publicPages = ['Index', 'About', 'Help'];
  const fileName = path.split('/').pop().replace('.vue', '');
  
  return !publicPages.includes(fileName);
}

/**
 * 从路径获取布局信息
 * @param {string} path 文件路径
 * @returns {string} 布局名称
 */
function getLayoutFromPath(path) {
  // 根据文件路径确定使用的布局
  if (path.includes('Login') || path.includes('login')) {
    return 'auth';
  }
  
  if (path.includes('Admin') || path.includes('admin')) {
    return 'admin';
  }
  
  return 'default';
}

/**
 * 生成嵌套路由
 * @param {Array} routes 路由数组
 * @returns {Array} 嵌套路由数组
 */
export function generateNestedRoutes(routes) {
  const nestedRoutes = [];
  const routeMap = new Map();

  routes.forEach(route => {
    const pathParts = route.path.split('/').filter(part => part);
    
    if (pathParts.length === 1) {
      // 顶级路由
      nestedRoutes.push(route);
    } else {
      // 嵌套路由
      const parentPath = '/' + pathParts[0];
      
      if (!routeMap.has(parentPath)) {
        routeMap.set(parentPath, {
          path: parentPath,
          name: pathParts[0],
          component: () => import('../layouts/NestedLayout.vue'),
          children: []
        });
        nestedRoutes.push(routeMap.get(parentPath));
      }
      
      const parentRoute = routeMap.get(parentPath);
      parentRoute.children.push({
        ...route,
        path: pathParts.slice(1).join('/')
      });
    }
  });

  return nestedRoutes;
}
