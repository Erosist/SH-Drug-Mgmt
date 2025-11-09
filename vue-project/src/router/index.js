import { createRouter, createWebHistory } from 'vue-router'
import login from '../views/Login.vue'
import home from '../views/Home.vue'
import register from '../views/Register.vue'
import inventory from '../views/Inventory.vue'
import circulation from '../views/Circulation.vue'
import analysis from '../views/Analysis.vue'
import service from '../views/SmartDispatch.vue'
import b2b from '../views/B2B.vue'
import PharmacyUser from '../views/PharmacyUser.vue'
import SupplierUser from '../views/SupplierUser.vue'
import LogisticsUser from '../views/LogisticsUser.vue'
import RegulatorUser from '../views/RegulatorUser.vue'
import UnauthenticatedUser from '../views/UnauthenticatedUser.vue'
import { getCurrentUser } from '../mocks/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: home },
    { path: '/login', name: 'login', component: login },
    { path: '/register', name: 'register', component: register },
    { path: '/inventory', name: 'inventory', component: inventory },
    { path: '/b2b', name: 'b2b', component: b2b },
    { path: '/circulation', name: 'circulation', component: circulation },
    { path: '/analysis', name: 'analysis', component: analysis },
    { path: '/service', name: 'service', component: service },

    // 基于角色的用户界面（无后端，使用前端mock登录）
    { path: '/pharmacy', name: 'pharmacy', component: PharmacyUser, meta: { requiresAuth: true } },
    { path: '/supplier', name: 'supplier', component: SupplierUser, meta: { requiresAuth: true } },
    { path: '/logistics', name: 'logistics', component: LogisticsUser, meta: { requiresAuth: true } },
    { path: '/regulator', name: 'regulator', component: RegulatorUser, meta: { requiresAuth: true } },
    { path: '/unauth', name: 'unauth', component: UnauthenticatedUser, meta: { requiresAuth: true } },
  ],
})

// 简单的前置守卫：访问需要认证的页面时，检查是否已登录
router.beforeEach((to, from, next) => {
  if (to.meta && to.meta.requiresAuth) {
    const user = getCurrentUser()
    if (!user) {
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router
//import.meta.env.BASE_URL