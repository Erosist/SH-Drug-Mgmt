<template>
  <div class="b2b-container">
    <!-- 顶部导航栏 -->
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
            <div class="nav-item" :class="{ active: activeNav === 'circulation' }" @click="navigateTo('circulation')">流通监管</div>
            <div v-if="canViewAnalysis" class="nav-item" :class="{ active: activeNav === 'analysis' }" @click="navigateTo('analysis')">监管分析</div>
            <div v-if="isRegulator" class="nav-item" :class="{ active: activeNav === 'compliance' }" @click="navigateTo('compliance')">合规分析报告</div>
            <div v-if="isLogistics" class="nav-item" :class="{ active: activeNav === 'service' }" @click="navigateTo('service')">智能调度</div>
          </div>
          <div class="user-actions">
            <div v-if="currentUser" class="user-info">
              <span class="user-name">{{ userDisplayName }}</span>
              <span class="user-role">{{ userRoleLabel }}</span>
            </div>
            <button
              v-if="currentUser"
              class="change-btn"
              @click="goToChangePassword"
            >修改密码</button>
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

      <!-- 标签切换（增加“查看供应信息”为第三个选项，点击只切换下方内容） -->
      <div class="tabs" @click="onTabsClick">
        <div
          v-for="tab in visibleTabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="setActiveTab(tab.key)"
        >
          {{ tab.label }}
        </div>
      </div>

      <div class="form-sections">
        <!-- 供给表单 -->
        <div v-if="activeTab==='supply'" class="card">
          <h3 class="card-title">发布药品供给信息</h3>
          <div style="padding:10px 0">
            <SupplyInfoManagement />
          </div>
        </div>


        
        <!-- 查看供应信息（内联组件） -->
        <div v-else-if="activeTab==='list'" class="card">
          <h3 class="card-title">查看供应信息</h3>
          <div style="padding:10px 0">
            <SupplierList />
          </div>
        </div>

        <!-- 下单（内联组件） -->
        <div v-else-if="activeTab==='order'" class="card">
          <h3 class="card-title">下单</h3>
          <div style="padding:10px 0">
            <MockOrder :selectedSupplyId="route.query.supplyId" />
          </div>
        </div>

        
      </div>

      <!-- 已发布记录列表 -->
      <div class="records-section">
        <h3 class="section-title">最新发布记录</h3>
        <div v-loading="recordsLoading" class="records-container">
          <table class="records-table" v-if="realRecords.length > 0">
            <thead>
              <tr>
                <th>类型</th>
                <th>药品名称</th>
                <th>数量/价格</th>
                <th>状态</th>
                <th>日期</th>
                <th>操作方</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in realRecords" :key="index">
                <td>
                  <el-tag 
                    :type="record.type === 'supply' ? 'success' : record.type === 'order' ? 'primary' : 'info'"
                    size="small"
                  >
                    {{ record.typeName }}
                  </el-tag>
                </td>
                <td>{{ record.drugName }}</td>
                <td>{{ record.quantityAndPrice }}</td>
                <td>
                  <el-tag 
                    :type="getRecordStatusType(record.status)" 
                    size="small"
                  >
                    {{ record.statusText }}
                  </el-tag>
                </td>
                <td>{{ record.date }}</td>
                <td>{{ record.operatorName }}</td>
              </tr>
            </tbody>
          </table>
          <el-empty 
            v-else-if="!recordsLoading"
            description="暂无记录" 
            :image-size="80"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
// 引入 SupplierList 以支持路由跳转到组件视图
import SupplierList from '@/component/SupplierList.vue'
import SupplyInfoManagement from '@/component/SupplyInfoManagement.vue'
import MockOrder from '@/views/MockOrder.vue'
import { getCurrentUser } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'
import { supplyApi } from '@/api/supply'
import { orderApi } from '@/api/orders'
import { getRoleLabel } from '@/utils/roleLabel'

export default {
  name: 'B2BPlatform',
  components: { SupplierList, SupplyInfoManagement, MockOrder },
  setup() {
    const router = useRouter()
    const route = useRoute()
  const activeNav = ref('b2b')
    const activeTab = ref('supply')
  const currentUser = ref(getCurrentUser())
  const isLogistics = computed(() => currentUser.value && currentUser.value.role === 'logistics')
  const isSupplier = computed(() => currentUser.value && currentUser.value.role === 'supplier')
  const isPharmacy = computed(() => currentUser.value && currentUser.value.role === 'pharmacy')
  const isRegulator = computed(() => currentUser.value && currentUser.value.role === 'regulator')
  const isAdmin = computed(() => currentUser.value && currentUser.value.role === 'admin')
  const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
  const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
  const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))
  const userRole = computed(() => currentUser.value?.role || '')

  const canAccessSupply = computed(() => userRole.value !== 'pharmacy' && userRole.value !== 'regulator')
  const canAccessSupplyList = computed(() => userRole.value !== 'supplier')

  const tabMatrix = [
    { key: 'supply', label: '供给信息发布', guard: canAccessSupply },
    { key: 'list', label: '查看供应信息', guard: canAccessSupplyList },
    { key: 'order', label: '下单', guard: computed(() => true) }
  ]

  const visibleTabs = computed(() => tabMatrix.filter(tab => tab.guard.value))

  watch(visibleTabs, (tabs) => {
    if (!tabs.some(tab => tab.key === activeTab.value)) {
      activeTab.value = tabs[0]?.key || ''
    }
  }, { immediate: true })

    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日`
    })

    const supplyForm = ref({
      drugId: '',
      manufacturer: '',
      drugName: '',
      spec: '',
      quantity: 0,
      prodDate: '',
      unitPrice: 0,
      expireDate: '',
      status: 'supplying'
    })

    const records = ref([])
    const realRecords = ref([])
    const recordsLoading = ref(false)

    const totalPrice = computed(() => {
      const q = supplyForm.value.quantity || 0
      const p = supplyForm.value.unitPrice || 0
      return (q * p).toFixed(2)
    })

    const resetSupplyForm = () => {
      supplyForm.value = { drugId:'', manufacturer:'', drugName:'', spec:'', quantity:0, prodDate:'', unitPrice:0, expireDate:'', status:'supplying' }
    }

    const validateSupply = () => {
      return supplyForm.value.drugName && supplyForm.value.quantity > 0 && supplyForm.value.unitPrice > 0
    }

    const submitSupply = () => {
      if (!validateSupply()) {
        alert('请填写完整供给关键信息')
        return
      }
      records.value.unshift({
        kind: '供给',
        drugName: supplyForm.value.drugName,
        quantity: supplyForm.value.quantity,
        priceInfo: `${supplyForm.value.unitPrice} / ${totalPrice.value}`,
        status: supplyForm.value.status,
        date: currentDate.value
      })
      resetSupplyForm()
    }

    

    const navigateTo = (page) => {
      activeNav.value = page
      switch(page) {
        case 'home': router.push('/') ; break
        case 'inventory': router.push('/inventory') ; break
        case 'nearby':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/nearby-suppliers' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'nearby' } })
            break
          }
            
            router.push('/nearby-suppliers')
            break
        case 'b2b': router.push('/b2b') ; break
        case 'circulation': router.push('/circulation') ; break
        case 'analysis': router.push('/analysis') ; break
        case 'service': router.push('/service') ; break
        case 'compliance':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/compliance-report' } })
            break
          }
          if (currentUser.value.role !== 'regulator') {
            router.push('/')
            break
          }
          router.push({ name: 'compliance-report' })
          break
        default: router.push('/')
      }
    }

    const goToLogin = () => router.push('/login')
    const goToChangePassword = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/change-password' } })
        return
      }
      router.push({ name: 'change-password' })
    }
    const goToUserHome = () => {
      const u = currentUser.value
      if (!u) return router.push('/login')
      router.push(roleToRoute(u.role))
    }

    const goToEnterpriseAuth = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/enterprise-auth' } })
        return
      }
      if (['regulator','admin'].includes(currentUser.value.role)) return
      router.push('/enterprise-auth')
    }

    const goToEnterpriseReview = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push('/enterprise-review')
    }

    const goToSystemStatus = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push('/admin/status')
    }

    const goToAdminUsers = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push('/admin/users')
    }

    function setActiveTab(tab) {
      if (!visibleTabs.value.some(t => t.key === tab)) return
      activeTab.value = tab
    }

    function onTabsClick(e) {
      console.log('[B2B] tabs click target:', e.target && e.target.tagName, 'text=', e.target && e.target.textContent && e.target.textContent.trim())
    }

    const refreshUser = () => { currentUser.value = getCurrentUser() }
    
    // 处理路由查询参数切换tab
    watch(() => route.query.tab, (newTab) => {
      if (newTab && visibleTabs.value.some(t => t.key === newTab)) {
        activeTab.value = newTab
      }
    }, { immediate: true })
    
    onMounted(() => { 
      window.addEventListener('storage', refreshUser)
      loadRecentRecords()
    })
    onBeforeUnmount(() => { window.removeEventListener('storage', refreshUser) })

    // 获取最新记录数据
    const loadRecentRecords = async () => {
      if (!currentUser.value || ['unauth', 'regulator'].includes(currentUser.value.role)) {
        realRecords.value = []
        return
      }

      recordsLoading.value = true
      try {
        const records = []

        // 获取最新供应信息
        try {
          const supplyResponse = await supplyApi.getSupplyList({ per_page: 5 })
          if (supplyResponse.data?.data?.items) {
            supplyResponse.data.data.items.forEach(item => {
              records.push({
                type: 'supply',
                typeName: '供应信息',
                drugName: item.drug?.generic_name || '未知药品',
                quantityAndPrice: `${item.available_quantity}个 / ¥${item.unit_price}`,
                status: item.status,
                statusText: item.status === 'ACTIVE' ? '有效' : '无效',
                date: formatDate(item.created_at),
                operatorName: item.tenant?.name || '未知',
                createdAt: item.created_at
              })
            })
          }
        } catch (error) {
          console.log('获取供应信息失败:', error)
        }

        // 获取最新订单
        try {
          const ordersResponse = await orderApi.getOrders({ per_page: 5 })
          if (ordersResponse.data?.data?.items) {
            ordersResponse.data.data.items.forEach(item => {
              const drugName = item.items?.[0]?.drug?.generic_name || '未知药品'
              const quantity = item.items?.[0]?.quantity || 0
              const unitPrice = item.items?.[0]?.unit_price || 0
              
              records.push({
                type: 'order',
                typeName: '采购订单',
                drugName: drugName,
                quantityAndPrice: `${quantity}个 / ¥${unitPrice}`,
                status: item.status,
                statusText: getOrderStatusText(item.status),
                date: formatDate(item.created_at),
                operatorName: item.buyer_tenant?.name || '未知',
                createdAt: item.created_at
              })
            })
          }
        } catch (error) {
          console.log('获取订单信息失败:', error)
        }

        // 按创建时间排序，最新的在前
        records.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        realRecords.value = records.slice(0, 10) // 只显示最新10条

      } catch (error) {
        console.error('加载记录失败:', error)
      } finally {
        recordsLoading.value = false
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getOrderStatusText = (status) => {
      const statusMap = {
        'PENDING': '待确认',
        'CONFIRMED': '已确认',
        'SHIPPED': '已发货',
        'IN_TRANSIT': '运输中',
        'DELIVERED': '已送达',
        'COMPLETED': '已完成',
        'CANCELLED_BY_PHARMACY': '药店取消',
        'CANCELLED_BY_SUPPLIER': '供应商取消',
        'EXPIRED_CANCELLED': '超时取消'
      }
      return statusMap[status] || status
    }

    const getRecordStatusType = (status) => {
      const statusTypeMap = {
        'ACTIVE': 'success',
        'PENDING': 'warning',
        'CONFIRMED': 'primary',
        'SHIPPED': 'info',
        'COMPLETED': 'success',
        'CANCELLED_BY_PHARMACY': 'danger',
        'CANCELLED_BY_SUPPLIER': 'danger',
        'EXPIRED_CANCELLED': 'danger'
      }
      return statusTypeMap[status] || 'info'
    }

  return { 
    activeNav, activeTab, currentUser, userDisplayName, userRoleLabel, visibleTabs, setActiveTab, onTabsClick, 
    navigateTo, goToLogin, goToUserHome, goToEnterpriseAuth, goToEnterpriseReview, 
    goToSystemStatus, goToAdminUsers, goToChangePassword, currentDate, supplyForm, totalPrice, 
    resetSupplyForm, submitSupply, records,
    realRecords, recordsLoading, loadRecentRecords, getRecordStatusType,
    isLogistics, isSupplier, isPharmacy, isRegulator, isAdmin, canViewAnalysis,
    route
  }
  }
}
</script>

<style scoped>
* { margin:0; padding:0; box-sizing:border-box; }
.b2b-container { min-height:100vh; background:#f5f7fa; font-family:'Microsoft YaHei', Arial, sans-serif; display:flex; flex-direction:column; }
.header { background:#fff; box-shadow:0 2px 10px rgba(0,0,0,.1); padding:15px 0; }
.header-content { padding:0 20px; }
.platform-info { display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; }
.platform-title { font-size:24px; font-weight:bold; color:#1a73e8; }
.current-date { color:#666; font-size:16px; }
.nav-section { display:flex; justify-content:space-between; align-items:center; border-top:1px solid #eee; padding-top:15px; }
.nav-menu { display:flex; gap:30px; }
.nav-item { font-size:16px; color:#333; cursor:pointer; padding:5px 0; transition:color .3s; }
.nav-item:hover { color:#1a73e8; }
.nav-item.active { color:#1a73e8; border-bottom:2px solid #1a73e8; }
.user-actions { display:flex; align-items:center; }
.user-info { display:flex; align-items:center; padding:6px 12px; border-radius:999px; background-color:#f0f5ff; color:#1a73e8; font-size:14px; font-weight:600; margin-right:10px; gap:8px; }
.user-name { white-space:nowrap; }
.user-role { padding:2px 10px; border-radius:999px; background-color:#fff; border:1px solid rgba(26,115,232,.2); font-size:12px; color:#1a73e8; }
.auth-btn { background-color: #fff; color: #1a73e8; border: 1px solid #1a73e8; padding: 6px 14px; border-radius: 4px; cursor: pointer; margin-right: 10px; font-size: 14px; }
.auth-btn:hover { background-color: rgba(26,115,232,0.06) }
.review-btn { background-color: #fff7e6; color: #b76c00; border: 1px solid #f3e5b8; padding: 6px 14px; border-radius: 4px; cursor: pointer; margin-right: 10px; font-size: 14px; }
.review-btn:hover { background-color: #ffeccc; }
.admin-btn { background-color: #f0f5ff; color: #1a73e8; border: 1px solid #d6e4ff; padding: 6px 14px; border-radius: 4px; cursor: pointer; margin-right: 10px; font-size: 14px; }
.admin-btn:hover { background-color: #e5edff; }
.change-btn { border: 1px solid #1a73e8; background: transparent; color: #1a73e8; padding: 6px 14px; border-radius: 4px; cursor: pointer; margin-right: 10px; }
.change-btn:hover { background-color: rgba(26,115,232,0.06); }
.login-btn { background:#1a73e8; color:#fff; border:none; padding:8px 20px; border-radius:4px; cursor:pointer; font-size:14px; }
.login-btn:hover { background:#0d62d9; }

.main-content { flex:1; padding:20px; }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; }
.page-title { font-size:20px; font-weight:bold; color:#333; }
.page-date { font-size:14px; color:#666; }

.tabs-row { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e5e5e5; margin-bottom:20px; }
.tabs { display:flex; gap:40px; position:relative; z-index:20; /* debug: outline to visualize clickable area */ outline: none }
.tabs.debug-outline { outline: 3px dashed rgba(255,0,0,0.35) }
.tabs-actions { margin-left:20px }
.tab-item { padding:10px 0; cursor:pointer; font-size:14px; color:#555; position:relative; }
.tab-item.active { color:#1a73e8; font-weight:600; }
.tab-item.active::after { content:''; position:absolute; left:0; bottom:0; height:2px; width:100%; background:#1a73e8; }

.form-sections { margin-bottom:30px; }
.card { background:#fff; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,.05); padding:20px; }
.card-title { font-size:16px; font-weight:bold; color:#333; margin-bottom:15px; }
.sub-card { border:1px solid #eef0f4; border-radius:6px; padding:15px 15px 10px; margin-bottom:20px; background:#fbfcfd; }
.sub-title { font-size:14px; font-weight:600; color:#1a1a1a; margin-bottom:12px; }
.form-grid { display:grid; grid-template-columns:repeat(2, 1fr); gap:16px 24px; }
.form-item { display:flex; flex-direction:column; }
.form-item label { font-size:12px; color:#555; margin-bottom:6px; }
.form-item input, .form-item select { height:36px; border:1px solid #d9d9d9; border-radius:4px; padding:0 10px; font-size:14px; outline:none; background:#fff; }
.form-item input:focus, .form-item select:focus { border-color:#1a73e8; box-shadow:0 0 0 2px rgba(26,115,232,.15); }
.form-actions { display:flex; justify-content:flex-end; gap:12px; margin-top:5px; }
.primary-btn { background:#1a73e8; color:#fff; border:none; padding:8px 18px; border-radius:4px; cursor:pointer; font-size:14px; }
.primary-btn:hover { background:#0d62d9; }
.secondary-btn { background:#fff; color:#333; border:1px solid #d9d9d9; padding:8px 18px; border-radius:4px; cursor:pointer; font-size:14px; }
.secondary-btn:hover { background:#f5f5f5; }

.records-section { background:#fff; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,.05); padding:20px; }
.section-title { font-size:16px; font-weight:bold; color:#333; margin-bottom:15px; padding-bottom:10px; border-bottom:1px solid #eee; }
.records-container { min-height: 200px; }
.records-table { width:100%; border-collapse:collapse; font-size:14px; }
.records-table th, .records-table td { padding:10px 8px; border-bottom:1px solid #eee; text-align:left; }
.records-table th { background:#f8f9fa; font-weight:600; }
.records-table tbody tr:hover { background:#f5f7fa; }
.empty { text-align:center; color:#999; }

@media (max-width: 992px) {
  .form-grid { grid-template-columns:1fr; }
}
</style>
