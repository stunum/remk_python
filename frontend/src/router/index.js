import { createRouter, createWebHistory } from 'vue-router';
import { generateAutoRoutes, generateNestedRoutes } from '@/utils/auto-router';
import { beforeEachGuard, afterEachGuard } from './guards';

// 手动配置的路由模块（保持向后兼容）
const files = import.meta.glob('./modules/*.js', {
  eager: true,
});

// 路由暂存
const routeModuleList = [];

// 遍历路由模块
Object.keys(files).forEach((key) => {
  const module = files[key].default || {};
  const moduleList = Array.isArray(module) ? [...module] : [module];
  routeModuleList.push(...moduleList);
});

// 暂时禁用自动路由生成，只使用手动配置的路由
console.log('手动配置的路由模块:', routeModuleList);

// 存放固定路由
const defaultRouterList = [
  {
    path: '/',
    redirect: '/login' // 默认跳转到登录页
  }
];

// 只使用手动配置的路由
const routes = [...defaultRouterList, ...routeModuleList];

// 调试：打印所有路由
console.log('所有路由配置:', routes.map(r => ({ path: r.path, name: r.name, component: r.component?.toString() })));

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return {
      el: '#app',
      top: 0,
      behavior: 'smooth',
    };
  },
});

// 添加路由守卫
router.beforeEach(beforeEachGuard);
router.afterEach(afterEachGuard);

export default router;
