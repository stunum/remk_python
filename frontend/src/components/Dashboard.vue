<template>
  <div class="dashboard-container">
    <!-- 欢迎卡片 -->
    <a-row :gutter="24" class="welcome-row">
      <a-col :span="24">
        <a-card class="welcome-card">
          <div class="welcome-content">
            <div class="welcome-info">
              <h2>欢迎回来，{{ userStore.user?.fullName || '用户' }}！</h2>
              <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
            </div>
            <div class="welcome-avatar">
              <a-avatar :size="64" :src="userStore.user?.avatar" style="background-color: #1890ff">
                {{ userStore.user?.fullName?.charAt(0) || 'U' }}
              </a-avatar>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 统计卡片 -->
    <a-row :gutter="24" class="stats-row">
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card">
          <a-statistic
            title="今日检查"
            :value="stats.todayExams"
            :prefix="h(EyeOutlined)"
            :value-style="{ color: '#1890ff' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card">
          <a-statistic
            title="本月检查"
            :value="stats.monthlyExams"
            :prefix="h(CalendarOutlined)"
            :value-style="{ color: '#52c41a' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card">
          <a-statistic
            title="异常检出"
            :value="stats.abnormalCases"
            :prefix="h(ExclamationCircleOutlined)"
            :value-style="{ color: '#faad14' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card">
          <a-statistic
            title="系统在线"
            :value="stats.uptime"
            suffix="小时"
            :prefix="h(ClockCircleOutlined)"
            :value-style="{ color: '#722ed1' }"
          />
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 快速操作 -->
    <a-row :gutter="24" class="actions-row">
      <a-col :xs="24" :lg="12">
        <a-card title="快速操作" class="action-card">
          <div class="quick-actions">
            <a-button type="primary" size="large" @click="navigateTo('/view-images')">
              <EyeOutlined />
              开始检查
            </a-button>
            <a-button size="large" @click="navigateTo('/index/settings')">
              <SettingOutlined />
              系统设置
            </a-button>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :lg="12">
        <a-card title="系统状态" class="status-card">
          <div class="system-status">
            <a-row :gutter="16">
              <a-col :span="12">
                <div class="status-item">
                  <a-badge status="processing" text="数据库连接" />
                </div>
              </a-col>
              <a-col :span="12">
                <div class="status-item">
                  <a-badge status="success" text="图像服务" />
                </div>
              </a-col>
              <a-col :span="12">
                <div class="status-item">
                  <a-badge status="success" text="网络连接" />
                </div>
              </a-col>
              <a-col :span="12">
                <div class="status-item">
                  <a-badge status="warning" text="存储空间" />
                </div>
              </a-col>
            </a-row>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/modules/user';
import { isResponseSuccess, getResponseMessage } from '@/utils/request';
import { examinationAPI } from '@/api';
import {
  EyeOutlined,
  SettingOutlined,
  CalendarOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const userStore = useUserStore();

// 统计数据
const stats = ref({
  todayExams: 0,
  monthlyExams: 0,
  abnormalCases: 0,
  uptime: 0
});

const loading = ref(false);

// 获取统计数据
const fetchStats = async () => {
  if (loading.value) return; // 防止重复调用
  
  loading.value = true;
  try {
    const response = await examinationAPI.getExaminationStats();
    if (isResponseSuccess(response)) {
      stats.value = {
        todayExams: response.data.today_examinations || 0,
        monthlyExams: response.data.monthly_examinations || 0,
        abnormalCases: response.data.abnormal_cases || 0,
        uptime: response.data.system_uptime || 0
      };
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
    // 显示错误提示，但保持界面稳定
  } finally {
    loading.value = false;
  }
};

// 当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });
});

// 导航函数
const navigateTo = (path) => {
  router.push(path);
};

// 生命周期
onMounted(() => {
  console.log('Dashboard组件已加载');
  // 直接获取统计数据
  fetchStats();
});
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
}

/* 欢迎卡片 */
.welcome-row {
  margin-bottom: 24px;
}

.welcome-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-info h2 {
  margin: 0 0 8px 0;
  color: #262626;
  font-size: 24px;
}

.welcome-info p {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

/* 操作区域 */
.actions-row {
  margin-bottom: 24px;
}

.action-card,
.status-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  height: 100%;
}

.quick-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.quick-actions .ant-btn {
  height: 48px;
  border-radius: 8px;
  font-weight: 500;
}

.quick-actions .ant-btn-primary {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  border: none;
}

.system-status {
  padding: 8px 0;
}

.status-item {
  margin-bottom: 12px;
}

.status-item:last-child {
  margin-bottom: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
  }
  
  .welcome-avatar {
    margin-top: 16px;
  }
  
  .dashboard-container {
    padding: 16px;
  }
  
  .quick-actions {
    justify-content: center;
  }
  
  .quick-actions .ant-btn {
    flex: 1;
    min-width: 120px;
  }
}
</style>
