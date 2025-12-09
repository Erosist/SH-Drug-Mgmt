<template>
  <div class="orders-container">
    <!-- 顶部导航栏 - 与Circulation.vue完全一致的结构与样式 -->
    <div class="header">
      <div class="header-content">
        <div class="platform-info">
          <h1 class="platform-title">上海药品监管信息平台</h1>
          <div class="current-date">{{ currentDate }}</div>
        </div>

        <div class="nav-section">
          <div class="nav-menu">
            <div class="nav-item" :class="{ active: activeNav === 'home' }" @click="navigateTo('home')">首页</div>
            <div v-if="!isLogistics && !isRegulator" class="nav-item" :class="{ active: activeNav === 'inventory' }" @click="navigateTo('inventory')">库存管理</div>
            <div v-if="isPharmacy" class="nav-item" :class="{ active: activeNav === 'nearby' }" @click="navigateTo('nearby')">就近推荐</div>
            <div v-if="!isLogistics" class="nav-item" :class="{ active: activeNav === 'b2b' }" @click="navigateTo('b2b')">B2B供求平台</div>
            <div v-if="isLogistics || isRegulator" class="nav-item" :class="{ active: activeNav === 'circulation' }" @click="navigateTo('circulation')">{{ isRegulator ? '药品追溯查询' : '流通数据上报' }}</div>
            <div v-if="canViewAnalysis" class="nav-item" :class="{ active: activeNav === 'analysis' }" @click="navigateTo('analysis')">监管分析</div>
            <div v-if="isRegulator" class="nav-item" :class="{ active: activeNav === 'compliance' }" @click="navigateTo('compliance')">合规分析报告</div>
            <div v-if="isLogistics" class="nav-item" :class="{ active: activeNav === 'service' }" @click="navigateTo('service')">智能调度</div>
            <div v-if="isLogistics" class="nav-item" :class="{ active: activeNav === 'orders' }" @click="navigateTo('logistics-orders')">订单查看</div>
          </div>

          <div class="user-actions">
            <div v-if="currentUser" class="user-info">
              <span class="user-name">{{ userDisplayName }}</span>
              <span class="user-role">{{ userRoleLabel }}</span>
            </div>
            <button v-if="currentUser" class="change-btn" @click="goToChangePassword">修改密码</button>
            <button v-if="!currentUser || currentUser.role==='unauth'" class="auth-btn" @click="goToEnterpriseAuth">企业认证</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="review-btn" @click="goToEnterpriseReview">认证审核</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToSystemStatus">系统状态</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToAdminUsers">用户管理</button>
            <button v-if="!currentUser" class="login-btn" @click="goToLogin">登录</button>
            <button v-else class="login-btn" @click="goToUserHome">我的主页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <div class="section">
          <div class="page-header">
            <h2 class="page-title">物流订单列表</h2>
            <div class="page-date">当前时间：{{ currentTimestamp }}</div>
          </div>

          <!-- 权限提示 -->
          <div v-if="!isAuthenticated" class="permission-notice warning">
            <div class="notice-icon">⚠️</div>
            <div class="notice-text">请先登录后查看物流订单</div>
          </div>
          <div v-else-if="!isLogistics" class="permission-notice warning">
            <div class="notice-icon">⚠️</div>
            <div class="notice-text">当前角色无权查看物流订单，仅物流公司用户可访问该页面</div>
          </div>

          <div v-else>
            <div class="filters">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">订单号</label>
                  <input type="text" class="form-input" v-model="filters.order_no" placeholder="按订单号搜索" @keyup.enter="fetchOrders" />
                </div>
                <div class="form-group">
                  <label class="form-label">运单号</label>
                  <input type="text" class="form-input" v-model="filters.tracking_number" placeholder="按运单号搜索" @keyup.enter="fetchOrders" />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">状态</label>
                  <select class="form-select" v-model="filters.status">
                    <option value="">全部</option>
                    <option value="SHIPPED">已发货</option>
                    <option value="IN_TRANSIT">运输中</option>
                    <option value="DELIVERED">已送达</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">更新时间起</label>
                  <input type="date" class="form-input" v-model="filters.start_date" />
                </div>
                <div class="form-group">
                  <label class="form-label">更新时间止</label>
                  <input type="date" class="form-input" v-model="filters.end_date" />
                </div>
                <div class="form-group" style="align-self: end;">
                  <button class="query-btn" :disabled="loading" @click="fetchOrders">{{ loading ? '查询中...' : '查询' }}</button>
                </div>
              </div>
            </div>

            <!-- 列表 -->
            <div class="table-wrapper">
              <table class="orders-table">
                <thead>
                  <tr>
                    <th>订单号</th>
                    <th>运单号</th>
                    <th>药品批号</th>
                    <th>状态</th>
                    <th>收货地址</th>
                    <th>更新时间</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="orders.length === 0">
                    <td colspan="6" class="empty">暂无数据</td>
                  </tr>
                  <tr v-for="item in orders" :key="item.id">
                    <td>{{ item.order_no }}</td>
                    <td>{{ item.tracking_number || '-' }}</td>
                    <td>{{ item.batch_number || '-' }}</td>
                    <td>
                      <span class="status-badge" :class="'status-' + (item.status || '').toLowerCase()">{{ statusText(item.status) }}</span>
                    </td>
                    <td>{{ item.address || '-' }}</td>
                    <td>{{ formatTime(item.updated_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 分页（简单占位） -->
            <div class="action-buttons">
              <button class="reset-btn" :disabled="loading" @click="resetFilters">重置</button>
              <button class="submit-btn" :disabled="loading" @click="fetchOrders">刷新</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </template>

<script>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { logisticsApi } from '@/api/logistics'
import { getCurrentUser, isAuthenticated as checkAuth } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'
import { getRoleLabel } from '@/utils/roleLabel'

export default {
  name: 'LogisticsOrders',
  setup() {
    const router = useRouter()
    const activeNav = ref('orders')
    const currentUser = ref(getCurrentUser())
    const isLogistics = computed(() => currentUser.value && currentUser.value.role === 'logistics')
    const isPharmacy = computed(() => currentUser.value && currentUser.value.role === 'pharmacy')
    const isRegulator = computed(() => currentUser.value && currentUser.value.role === 'regulator')
    const isAdmin = computed(() => currentUser.value && currentUser.value.role === 'admin')
    const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
    const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
    const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))
    const loading = ref(false)

    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })
    const currentTimestamp = ref('')
    const updateTimestamp = () => {
      const now = new Date()
      currentTimestamp.value = now.toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit'
      })
    }

    const isAuthenticated = computed(() => checkAuth())

    const orders = ref([])
    const filters = ref({ order_no: '', tracking_number: '', status: '', start_date: '', end_date: '' })

    const fetchOrders = async () => {
      if (!isAuthenticated.value) {
        ElMessage.warning('请先登录后再查询')
        router.push({ name: 'login', query: { redirect: '/logistics-orders' } })
        return
      }
      if (!isLogistics.value) {
        ElMessage.error('只有物流用户才能查看物流订单')
        return
      }
      
      loading.value = true
      try {
        // 准备查询参数
        const params = {}
        
        if (filters.value.order_no) {
          params.order_no = filters.value.order_no
        }
        if (filters.value.tracking_number) {
          params.tracking_number = filters.value.tracking_number
        }
        if (filters.value.status) {
          params.status = filters.value.status
        }
        if (filters.value.start_date) {
          const d = new Date(filters.value.start_date)
          d.setHours(0, 0, 0, 0)
          params.start_date = d.toISOString()
        }
        if (filters.value.end_date) {
          const d = new Date(filters.value.end_date)
          d.setHours(23, 59, 59, 999)
          params.end_date = d.toISOString()
        }
        
        // 调用后端API
        const response = await logisticsApi.getOrders(params)
        
        // 处理响应数据
        if (response.data.success) {
          orders.value = Array.isArray(response.data.data) ? response.data.data : []
          
          if (orders.value.length === 0) {
            ElMessage.info('暂无符合条件的订单')
          }
        } else {
          ElMessage.error(response.data.message || '获取订单列表失败')
          orders.value = []
        }
      } catch (error) {
        console.error('获取订单失败:', error)
        
        // 根据错误类型显示不同的提示
        if (error.response) {
          // 服务器返回了错误响应
          const status = error.response.status
          const message = error.response.data?.message || error.response.data?.msg
          
          if (status === 401) {
            ElMessage.error('登录已过期，请重新登录')
            router.push({ name: 'login', query: { redirect: '/logistics-orders' } })
          } else if (status === 403) {
            ElMessage.error(message || '权限不足，无法访问物流订单')
          } else if (status === 500) {
            ElMessage.error('服务器错误，请稍后重试')
          } else {
            ElMessage.error(message || '获取订单列表失败')
          }
        } else if (error.request) {
          // 请求已发出但没有收到响应
          ElMessage.error('网络连接失败，请检查网络设置')
        } else {
          // 其他错误
          ElMessage.error('请求失败: ' + (error.message || '未知错误'))
        }
        
        orders.value = []
      } finally {
        loading.value = false
      }
    }

    const resetFilters = () => {
      filters.value = { order_no: '', tracking_number: '', status: '', start_date: '', end_date: '' }
      fetchOrders()
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }

    const statusText = (s) => {
      const map = { SHIPPED: '已发货', IN_TRANSIT: '运输中', DELIVERED: '已送达' }
      return map[s] || s || '-'
    }

    const goToLogin = () => { router.push('/login') }
    const goToChangePassword = () => {
      if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/change-password' } }); return }
      router.push({ name: 'change-password' })
    }
    const goToEnterpriseAuth = () => {
      if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/enterprise-auth' } }); return }
      if ([ 'regulator','admin' ].includes(currentUser.value.role)) return
      router.push('/enterprise-auth')
    }
    const goToEnterpriseReview = () => { if (!currentUser.value) return router.push('/login'); if (currentUser.value.role !== 'admin') return; router.push('/enterprise-review') }
    const goToSystemStatus = () => { if (!currentUser.value) return router.push('/login'); if (currentUser.value.role !== 'admin') return; router.push('/admin/status') }
    const goToAdminUsers = () => { if (!currentUser.value) return router.push('/login'); if (currentUser.value.role !== 'admin') return; router.push('/admin/users') }
    const refreshUser = () => { currentUser.value = getCurrentUser() }
    const goToUserHome = () => { const u = currentUser.value; if (!u) return router.push('/login'); router.push(roleToRoute(u.role)) }

    const navigateTo = (page) => {
      activeNav.value = page
      switch(page) {
        case 'home': router.push('/'); break
        case 'inventory': router.push('/inventory'); break
        case 'nearby':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/nearby-suppliers' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'nearby' } }); break }
          router.push('/nearby-suppliers'); break
        case 'b2b': router.push('/b2b'); break
        case 'circulation': router.push('/circulation'); break
        case 'analysis': router.push('/analysis'); break
        case 'service': router.push('/service'); break
        case 'compliance':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/compliance-report' } }); break }
          if (currentUser.value.role !== 'regulator') { router.push('/'); break }
          router.push({ name: 'compliance-report' }); break
        case 'logistics-orders': router.push('/logistics-orders'); break
        default: router.push('/')
      }
    }

    onMounted(() => {
      updateTimestamp()
      window.addEventListener('storage', refreshUser)
      fetchOrders()
      // 每秒更新时间
      const timer = setInterval(updateTimestamp, 1000)
      // 保存到实例以便清理（用闭包变量即可）
      // 这里简单保留，unmount时不需要访问timer变量
    })
    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
    })

    return {
      activeNav,
      currentDate,
      currentTimestamp,
      currentUser,
      isLogistics,
      isPharmacy,
      isRegulator,
      isAdmin,
      canViewAnalysis,
      userDisplayName,
      userRoleLabel,
      isAuthenticated,
      orders,
      filters,
      loading,
      fetchOrders,
      resetFilters,
      statusText,
      formatTime,
      navigateTo,
      goToLogin,
      goToUserHome,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      goToChangePassword,
    }
  }
}
</script>

<style scoped>
/* 复用 Circulation.vue 的样式定义（拷贝必要部分以保持一致外观） */
* { margin: 0; padding: 0; box-sizing: border-box; }
.orders-container { min-height: 100vh; background-color: #f5f7fa; font-family: "Microsoft YaHei", Arial, sans-serif; display: flex; flex-direction: column; }
.header { background-color: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 15px 0; width: 100%; }
.header-content { width: 100%; max-width: 100%; margin: 0 auto; padding: 0 20px; }
.platform-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.platform-title { font-size: 24px; font-weight: bold; color: #1a73e8; margin: 0; }
.current-date { color: #666; font-size: 16px; }
.nav-section { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 15px; flex-wrap: wrap; gap: 15px; }
.nav-menu { display: flex; gap: 30px; flex-wrap: wrap; }
.nav-item { font-size: 16px; color: #333; cursor: pointer; padding: 5px 0; transition: color 0.3s; }
.nav-item:hover { color: #1a73e8; }
.nav-item.active { color: #1a73e8; border-bottom: 2px solid #1a73e8; }
.user-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.user-info { display: flex; align-items: center; padding: 6px 16px; border-radius: 999px; background-color: #f0f5ff; color: #1a73e8; font-size: 14px; font-weight: 600; gap: 8px; }
.user-role { padding: 2px 10px; border-radius: 999px; background-color: #fff; border: 1px solid rgba(26,115,232,0.2); font-size: 12px; color: #1a73e8; }
.auth-btn, .review-btn, .admin-btn, .change-btn, .login-btn { font-size: 14px; }
.change-btn { border: 1px solid #1a73e8; background-color: transparent; color: #1a73e8; padding: 6px 14px; border-radius: 4px; cursor: pointer; margin-right: 10px; transition: background-color 0.3s; }
.change-btn:hover { background-color: rgba(26,115,232,0.08); }
.auth-btn { background-color: #fff; color: #1a73e8; border: 1px solid #1a73e8; padding: 8px 14px; border-radius: 4px; cursor: pointer; }
.auth-btn:hover { background-color: rgba(26,115,232,0.08); }
.review-btn { background-color: #fff7e6; color: #b76c00; border: 1px solid #f3e5b8; padding: 8px 14px; border-radius: 4px; cursor: pointer; }
.review-btn:hover { background-color: #ffeccc; }
.admin-btn { background-color: #f0f5ff; color: #1a73e8; border: 1px solid #d6e4ff; padding: 8px 14px; border-radius: 4px; cursor: pointer; }
.admin-btn:hover { background-color: #e5edff; }
.login-btn { background-color: #1a73e8; color: white; border: none; padding: 8px 20px; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
.login-btn:hover { background-color: #0d62d9; }
.main-content { flex: 1; width: 100%; max-width: 100%; margin: 0; padding: 20px; }
.content-wrapper { display: grid; grid-template-columns: 1fr; gap: 20px; height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.page-title { font-size: 24px; font-weight: bold; color: #333; }
.page-date { color: #666; font-size: 16px; }
.section { background-color: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin-bottom: 0; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.form-group { margin-bottom: 15px; }
.form-label { display: block; font-size: 14px; color: #666; margin-bottom: 5px; }
.form-input, .form-select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; outline: none; font-size: 14px; }
.form-input:focus, .form-select:focus { border-color: #1a73e8; }
.query-btn { background-color: #1a73e8; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
.query-btn:hover { background-color: #0d62d9; }
.table-wrapper { overflow-x: auto; }
.orders-table { width: 100%; border-collapse: collapse; }
.orders-table th, .orders-table td { padding: 10px; border-bottom: 1px solid #eee; text-align: left; font-size: 14px; }
.orders-table th { background: #f8f9fa; color: #333; }
.orders-table .empty { text-align: center; color: #888; }
.status-badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; color: #fff; }
.status-shipped { background-color: #91cc75; }
.status-in_transit { background-color: #fac858; color: #333; }
.status-delivered { background-color: #ee6666; }
.action-buttons { display: flex; justify-content: flex-end; gap: 15px; padding: 20px 0; }
.reset-btn { background-color: #f8f9fa; border: 1px solid #dee2e6; color: #495057; padding: 10px 25px; border-radius: 4px; cursor: pointer; }
.reset-btn:hover { background-color: #e9ecef; }
.submit-btn { background-color: #1a73e8; color: white; border: none; padding: 10px 25px; border-radius: 4px; cursor: pointer; }
.submit-btn:hover { background-color: #0d62d9; }

@media (max-width: 992px) { .form-row { grid-template-columns: 1fr; } }
</style>