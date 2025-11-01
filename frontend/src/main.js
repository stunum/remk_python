import {createApp} from 'vue'
import App from './App.vue'
import './style.css';
import Antd from 'ant-design-vue';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router';
import store from './store';
import 'ant-design-vue/dist/reset.css';


createApp(App).use(ElementPlus).use(Antd).use(router).use(store).mount('#app');
