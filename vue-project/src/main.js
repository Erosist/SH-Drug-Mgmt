import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

const app = createApp(App)

// 配置 axios
axios.defaults.baseURL = "http://localhost:8880"

// 设置全局属性
app.config.globalProperties.$http = axios

// 使用插件
app.use(router)
app.use(ElementPlus)

// 最后挂载
app.mount('#app')