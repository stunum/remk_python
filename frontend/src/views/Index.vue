<template>
  <a-layout class="main-layout">
    <!-- 侧边栏 -->
    <a-layout-sider theme="light" v-model:collapsed="collapsed" :trigger="null" collapsible>
      <div class="logo">
        <img src="@/assets/images/logo-y.png" alt="Eyes Remk" class="logo-img">
        <span v-show="!collapsed" class="logo-text">瑞尔明康</span>
      </div>
      <a-menu v-model:selectedKeys="selectedKeys" theme="light" mode="inline">
        <!-- <a-menu-item key="dashboard" @click="navigateTo('/index/dashboard')">
          <DashboardOutlined />
          <span>仪表盘</span>
        </a-menu-item> -->
        <a-menu-item key="visits" @click="navigateTo('/index/visits')">
          <EyeOutlined />
          <span>就诊管理</span>
        </a-menu-item>
        <a-menu-item key="patients" @click="navigateTo('/index/patients')">
          <UserOutlined />
          <span>病人管理</span>
        </a-menu-item>
        <a-menu-item key="settings" @click="navigateTo('/index/settings')">
          <SettingOutlined />
          <span>系统设置</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    
    <a-layout>
      <!-- 头部 -->
      <a-layout-header class="header">
        <div class="header-left">
          <MenuUnfoldOutlined
            v-if="collapsed"
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          <MenuFoldOutlined 
            v-else 
            class="trigger" 
            @click="() => (collapsed = !collapsed)" 
          />
        </div>
        
        <div class="header-right">
          <a-space>
            <!-- <a-badge count="5">
              <BellOutlined class="header-icon" />
            </a-badge> -->
            <a-dropdown>
              <a-avatar :size="32" :src="userStore.user?.avatar" style="background-color: #1890ff">
                {{ userStore.user?.fullName?.charAt(0) || 'U' }}
              </a-avatar>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="profile">
                    <UserOutlined />
                    个人资料
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item key="logout" @click="handleLogout">
                    <LogoutOutlined />
                    退出登录
                  </a-menu-item>
                  <a-menu-item v-if="isElectronApp" key="quit" @click="handleQuit">
                    <CloseCircleOutlined />
                    关闭程序
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </div>
      </a-layout-header>
      
      <!-- 主内容区 -->
      <a-layout-content class="content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>
<script setup scoped>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/store/modules/user';
import { isElectron, electronApp } from '@/utils/electron';
import {
  DashboardOutlined,
  EyeOutlined,
  SettingOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  CloseCircleOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

// 检查是否在 Electron 环境中
const isElectronApp = isElectron();

// 响应式数据
const selectedKeys = ref(['patients']);
const collapsed = ref(false);

// 根据当前路由设置选中的菜单项
const updateSelectedKeys = () => {
  const path = route.path;
  if (path.includes('/dashboard')) {
    selectedKeys.value = ['dashboard'];
  } else if (path.includes('/patients')) {
    selectedKeys.value = ['patients'];
  } else if (path.includes('/visits')) {
    selectedKeys.value = ['visits'];
  } else if (path.includes('/view-images')) {
    selectedKeys.value = ['view-images'];
  } else if (path.includes('/settings')) {
    selectedKeys.value = ['settings'];
  } else {
    selectedKeys.value = ['dashboard'];
  }
};

// 监听路由变化
watch(
  () => route.path,
  () => {
    updateSelectedKeys();
  },
  { immediate: true }
);

// 导航函数
const navigateTo = (path) => {
  router.push(path);
};

// 退出登录
const handleLogout = async () => {
  try {
    await userStore.logout();
    router.push('/login');
  } catch (error) {
    console.error('退出登录失败:', error);
  }
};

// 关闭程序（仅 Electron）
const handleQuit = async () => {
  try {
    await userStore.logout();
    await electronApp.quit();
  } catch (error) {
    console.error('关闭程序失败:', error);
  }
};

// 组件挂载时的操作
onMounted(() => {
  console.log('Index页面已加载');
  updateSelectedKeys();
});
</script>
<style scoped>
.main-layout {
  min-height: 100vh;
}

/* Logo样式 */
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.1);
  margin: 16px;
  border-radius: 8px;
}

.logo-img {
  height: 32px;
  width: auto;
}

.logo-text {
  color: white;
  font-weight: bold;
  font-size: 16px;
  margin-left: 8px;
}

/* 头部样式 */
.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
  margin-right: 16px;
}

.trigger:hover {
  color: #1890ff;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  color: #262626;
}

.header-right {
  display: flex;
  align-items: center;
}

.header-icon {
  font-size: 16px;
  cursor: pointer;
  color: #666;
  transition: color 0.3s;
}

.header-icon:hover {
  color: #1890ff;
}

/* 内容区样式 */
.content {
  background: #f0f2f5;
  min-height: calc(100vh - 112px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }
}
</style>