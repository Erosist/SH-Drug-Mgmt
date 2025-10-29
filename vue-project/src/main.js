import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'  // 添加这一行

createApp(App).use(router).mount('#app')