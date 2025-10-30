import { createRouter, createWebHistory } from 'vue-router'
import login from '../views/Login.vue'
import home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: home },
    { path: '/login', component: login },
  ],
})

export default router
//import.meta.env.BASE_URL