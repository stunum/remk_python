export default [
  // 登录页面 - 独立页面
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '用户登录',
      requiresAuth: false
    }
  },
  // 主页面 - 包含嵌套路由
  {
    path: '/index',
    name: 'index',
    component: () => import('@/views/Index.vue'),
    redirect: '/index/dashboard',
    meta: {
      title: '首页',
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/components/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          requiresAuth: true
        }
      },
      {
        path: 'patients',
        name: 'patients',
        component: () => import('@/components/PatientManagement.vue'),
        meta: {
          title: '病人管理',
          requiresAuth: true
        }
      },
      {
        path: 'patients/:id/history',
        name: 'patient-history',
        component: () => import('@/components/PatientHistory.vue'),
        meta: {
          title: '历史病例',
          requiresAuth: true
        }
      },
      {
        path: 'visits',
        name: 'visits',
        component: () => import('@/components/VisitManagement.vue'),
        meta: {
          title: '就诊',
          requiresAuth: true
        }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/components/SystemSettings.vue'),
        meta: {
          title: '系统设置',
          requiresAuth: true
        }
      }
    ]
  },
  // 图像查看页面 - 独立页面
  {
    path: '/view-images',
    name: 'view-images',
    component: () => import('@/views/ViewImages.vue'),
    meta: {
      title: '图像查看',
      requiresAuth: true
    }
  },
  // AI诊断页面 - 独立页面
  {
    path: '/ai-diagnosis',
    name: 'ai-diagnosis',
    component: () => import('@/views/AIDiagnosis.vue'),
    meta: {
      title: 'AI辅助诊断',
      requiresAuth: true
    }
  }
];
