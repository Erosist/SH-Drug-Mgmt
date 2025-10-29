import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue') // 创建这个文件或使用临时组件
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router