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
import EnterpriseAuth from '../views/EnterpriseAuth.vue'
import EnterpriseReview from '../views/EnterpriseReview.vue'
import AdminUsers from '../views/AdminUsers.vue'
import SystemStatus from '../views/SystemStatus.vue'
import ChangePassword from '../views/ChangePassword.vue'
import ForgotPassword from '../views/ForgotPassword.vue'
import TenantInventory from '../views/TenantInventory.vue'
import { getCurrentUser } from '@/utils/authSession'

// 允许未完成企业认证（role === 'unauth'）的登录用户仍可浏览的公共路由
// 若以后需要更精细的控制，可改为基于 route.meta 来判断
const UNAUDITED_ALLOWED_ROUTE_NAMES = new Set([
  'enterprise-auth',
  'unauth',
  'home',
  'inventory',
  'b2b',
  'circulation',
  'analysis',
  'service',
  'tenant-inventory'
])

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: home },
    { path: '/login', name: 'login', component: login },
    { path: '/register', name: 'register', component: register },
    { path: '/forgot-password', name: 'forgot-password', component: ForgotPassword },
    { path: '/change-password', name: 'change-password', component: ChangePassword, meta: { requiresAuth: true } },
    { path: '/inventory', name: 'inventory', component: inventory },
    { path: '/tenants/:tenantId', name: 'tenant-inventory', component: TenantInventory, props: true, meta: { requiresAuth: true, requiresVerified: true } },
    { path: '/b2b', name: 'b2b', component: b2b, meta: { requiresAuth: true, requiresVerified: true } },
    { path: '/circulation', name: 'circulation', component: circulation },
    { path: '/analysis', name: 'analysis', component: analysis },
    { path: '/service', name: 'service', component: service, meta: { requiresAuth: true, requiresVerified: true } },
  { path: '/enterprise-auth', name: 'enterprise-auth', component: EnterpriseAuth, meta: { requiresAuth: true } },
  { path: '/enterprise-review', name: 'enterprise-review', component: EnterpriseReview, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/users', name: 'admin-users', component: AdminUsers, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/status', name: 'admin-status', component: SystemStatus, meta: { requiresAuth: true, requiresRole: 'admin' } },

    // 基于角色的用户界面（无后端，使用前端mock登录）
    { path: '/pharmacy', name: 'pharmacy', component: PharmacyUser, meta: { requiresAuth: true } },
    { path: '/supplier', name: 'supplier', component: SupplierUser, meta: { requiresAuth: true } },
    { path: '/logistics', name: 'logistics', component: LogisticsUser, meta: { requiresAuth: true } },
    { path: '/regulator', name: 'regulator', component: RegulatorUser, meta: { requiresAuth: true } },
    { path: '/unauth', name: 'unauth', component: UnauthenticatedUser, meta: { requiresAuth: true } },
  ],
})

// 前置守卫：处理登录、基于角色的路由限制，以及“需要企业认证”的页面重定向
router.beforeEach((to, from, next) => {
  const user = getCurrentUser()

  // 如果页面要求登录且用户未登录 -> 跳转登录
  if (to.meta?.requiresAuth && !user) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // 如果页面要求特定角色且当前用户不满足 -> 回到首页
  if (to.meta?.requiresRole && user?.role !== to.meta.requiresRole) {
    next({ name: 'home' })
    return
  }

  // 对于已登录但企业未认证的用户（role === 'unauth'），允许访问首页、未认证提示页和企业认证页
  if (user?.role === 'unauth') {
    const allowNames = new Set(['home', 'unauth', 'enterprise-auth'])
    if (!allowNames.has(to.name)) {
      next({ name: 'unauth' })
      return
    }
  }

  // 其它情况正常路由
  next()
})

export default router
//import.meta.env.BASE_URL
