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
import AdminAuditLogs from '../views/AdminAuditLogs.vue'
import AdminAnnouncements from '../views/AdminAnnouncements.vue'
import ChangePassword from '../views/ChangePassword.vue'
import ForgotPassword from '../views/ForgotPassword.vue'
import TenantInventory from '../views/TenantInventory.vue'
import NearbySuppliers from '../views/NearbySuppliers.vue'
import { getCurrentUser } from '@/utils/authSession'
import ComplianceReport from '../views/ComplianceReport.vue'
import LogisticsOrders from '../views/LogisticsOrders.vue'
import MedicationReminders from '../views/MedicationReminders.vue'
import HealthNewsList from '../views/HealthNewsList.vue'

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
  'tenant-inventory',
  'nearby-suppliers'
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
    { path: '/nearby-suppliers', name: 'nearby-suppliers', component: NearbySuppliers, meta: { requiresAuth: true } },
    { path: '/b2b', name: 'b2b', component: b2b, meta: { requiresAuth: true, requiresVerified: true } },
    { path: '/circulation', name: 'circulation', component: circulation },
    { path: '/analysis', name: 'analysis', component: analysis },
    { path: '/service', name: 'service', component: service, meta: { requiresAuth: true, requiresVerified: true } },
    { path: '/logistics-orders', name: 'logistics-orders', component: LogisticsOrders, meta: { requiresAuth: true, requiresRole: 'logistics' } },
    { path: '/medication-reminders', name: 'medication-reminders', component: MedicationReminders, meta: { requiresAuth: true } },
        { path: '/health-news', name: 'health-news', component: HealthNewsList },
  { path: '/compliance-report', name: 'compliance-report', component: ComplianceReport, meta: { requiresAuth: true, requiresRole: 'regulator' } },
  { path: '/enterprise-auth', name: 'enterprise-auth', component: EnterpriseAuth, meta: { requiresAuth: true } },
  { path: '/enterprise-review', name: 'enterprise-review', component: EnterpriseReview, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/users', name: 'admin-users', component: AdminUsers, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/status', name: 'admin-status', component: SystemStatus, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/audit-logs', name: 'admin-audit-logs', component: AdminAuditLogs, meta: { requiresAuth: true, requiresRole: 'admin' } },
    { path: '/admin/announcements', name: 'admin-announcements', component: AdminAnnouncements, meta: { requiresAuth: true, requiresRole: 'admin' } },

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

  // 管理员访问首页时直接跳转到用户管理界面
  if (user?.role === 'admin' && to.name === 'home') {
    next({ name: 'admin-users' })
    return
  }

  // 如果页面要求登录且用户未登录 -> 跳转登录
  // 将独立的合规报告路由统一折叠到 B2B 页的内联模式
  if (to.name === 'compliance-report') {
    // 若已在 b2b 页面则直接放行（避免循环）；否则重定向到 b2b 并携带 section 标记
    if (from.name !== 'b2b') {
      next({ name: 'b2b', query: { ...to.query, section: 'compliance' } })
      return
    }
  }

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
