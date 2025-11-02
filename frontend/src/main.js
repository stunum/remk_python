import {createApp} from 'vue'
import App from './App.vue'
import './style.css';
import Antd from 'ant-design-vue';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router';
import store from './store';
import 'ant-design-vue/dist/reset.css';

// 开发环境加载密码测试工具
if (import.meta.env.DEV) {
  import('./utils/password-test').then(module => {
    console.log('🔐 密码测试工具已加载');
    console.log('使用方法: window.passwordTest.test("你的密码")');
  });
}

createApp(App).use(ElementPlus).use(Antd).use(router).use(store).mount('#app');
