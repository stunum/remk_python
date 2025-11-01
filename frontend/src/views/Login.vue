<template>
  <div class="login-container">
    <!-- 背景图片 -->
    <div class="login-background"></div>
    
    <!-- 登录窗口 -->
    <div class="login-window">
      <!-- 登录标题 -->
      <div class="login-header">
        <h2 class="login-title">系统登录</h2>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <!-- 用户名输入框 -->
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            clearable
            maxlength="20"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon class="input-icon"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            clearable
            show-password
            maxlength="20"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon class="input-icon"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item class="login-button-item">
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loginLoading"
            @click="handleLogin"
          >
            {{ loginLoading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部信息 -->
      <div class="login-footer">
        <p class="copyright">© 2025 瑞尔明康眼底检查系统</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { User, Lock } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/modules/user';
import { authAPI } from '@/api/auth';
import { hashPassword } from '@/utils/crypto';

const router = useRouter();
const userStore = useUserStore();

// 响应式数据
const loginFormRef = ref(null);
const loginLoading = ref(false);

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
});

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 5, max: 20, message: '用户名长度应在5-20个字符之间', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度应在8-20个字符之间', trigger: 'blur' }
  ]
};

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  try {
    // 表单验证
    const valid = await loginFormRef.value.validate();
    if (!valid) return;

    loginLoading.value = true;

    // 对密码进行客户端加密
    const encryptedPassword = hashPassword(loginForm.password);

    // 调用后端登录API
    const response = await authAPI.login(loginForm.username, encryptedPassword);
    
    // 根据新的响应格式判断成功（2xx状态码为成功）
    if (response.success || (response.code && response.code >= 200 && response.code < 300)) {
      console.log('登录成功，响应数据:', response);
      
      // 从新格式中提取数据
      const loginData = response.data || response;
      
      // 保存用户信息和令牌
      await userStore.setUserInfo({
        token: loginData.token || response.token,
        refreshToken: loginData.refresh_token || response.refresh_token,
        user: loginData.user || response.user,
        permissions: loginData.permissions || response.permissions,
        expiresAt: loginData.expires_at || response.expires_at
      });

      console.log('用户信息已保存到store');
      console.log('用户认证状态:', userStore.isAuthenticated);
      console.log('用户登录状态:', userStore.isLoggedIn);
      console.log('令牌信息:', userStore.token ? '存在' : '不存在');

      message.success(response.message || '登录成功');
      
      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        console.log('准备跳转到/index页面');
        console.log('当前认证状态:', userStore.isAuthenticated);
        console.log('当前路由:', router.currentRoute.value.path);
        console.log('路由器实例:', router);
        console.log('所有路由:', router.getRoutes().map(r => ({ path: r.path, name: r.name })));
        
        router.push('/index').then(() => {
          console.log('跳转成功，当前路由:', router.currentRoute.value.path);
        }).catch(error => {
          console.error('跳转失败:', error);
        });
      }, 500);
      
    } else {
      message.error(response.message || '登录失败');
    }
    
  } catch (error) {
    console.error('登录错误:', error);
    message.error('登录失败，请检查网络连接或稍后重试');
  } finally {
    loginLoading.value = false;
  }
};

// 生命周期
onMounted(() => {
  // 检查是否已登录
  if (userStore.isLoggedIn) {
    router.push('/index');
    return;
  }

  // 聚焦到用户名输入框
  setTimeout(() => {
    const firstInput = document.querySelector('.login-form input');
    if (firstInput) {
      firstInput.focus();
    }
  }, 100);
});
</script>

<style lang="scss" scoped>
.login-container {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10%;
}

// 背景图片
.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/images/login-bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 0;
  
  // 添加一个半透明遮罩层，提高登录窗口的可读性
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.3);
    z-index: 1;
  }
}

// 登录窗口
.login-window {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  z-index: 2;
  position: relative;
}

// 登录头部
.login-header {
  text-align: center;
  margin-bottom: 32px;

  .login-title {
    font-size: 28px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0;
    letter-spacing: 1px;
  }
}

// 登录表单
.login-form {
  .el-form-item {
    margin-bottom: 24px;

    :deep(.el-input__wrapper) {
      padding: 12px 16px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      border: 1px solid #e1e8ed;
      transition: all 0.3s ease;

      &:hover {
        border-color: #409eff;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
      }

      &.is-focus {
        border-color: #409eff;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
    }

    :deep(.el-input__inner) {
      font-size: 16px;
      color: #2c3e50;
    }

    .input-icon {
      color: #8c9aab;
      font-size: 18px;
    }
  }

  .login-button-item {
    margin-bottom: 0;

    .login-button {
      width: 100%;
      height: 48px;
      font-size: 16px;
      font-weight: 500;
      border-radius: 8px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
      }

      &:active {
        transform: translateY(0);
      }

      &.is-loading {
        background: linear-gradient(135deg, #a0a0a0, #808080);
      }
    }
  }
}

// 登录底部
.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e1e8ed;

  .copyright {
    font-size: 14px;
    color: #8c9aab;
    margin: 0;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .login-container {
    padding: 20px;
    justify-content: center;
  }

  .login-window {
    width: 100%;
    max-width: 400px;
    padding: 32px 24px;
  }

  .login-header .login-title {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .login-window {
    padding: 24px 20px;
  }

  .login-header .login-title {
    font-size: 22px;
  }

  .login-form {
    .login-button-item .login-button {
      height: 44px;
      font-size: 15px;
    }
  }
}

// 高分辨率屏幕适配
@media (min-width: 1920px) {
  .login-container {
    padding-right: 15%;
  }

  .login-window {
    width: 450px;
    padding: 48px;
  }

  .login-header .login-title {
    font-size: 32px;
  }
}
</style>
