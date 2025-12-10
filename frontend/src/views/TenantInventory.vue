<template>
  <div class="tenant-inventory-container">
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
            <div class="nav-item" :class="{ active: activeNav === 'circulation' }" @click="navigateTo('circulation')">流通监测</div>
            <div v-if="canViewAnalysis" class="nav-item" :class="{ active: activeNav === 'analysis' }" @click="navigateTo('analysis')">监管分析</div>
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
            <button v-else class="login-btn" @click="handleLogout">退出登录</button>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div class="back-row">
        <button class="ghost-btn" @click="goBack">← 返回药店列表</button>
        <span class="tenant-id">ID: {{ routeTenantId }}</span>
      </div>

      <div class="tenant-section">
        <div v-if="detailLoading" class="info-placeholder">正在加载药店信息...</div>
        <div v-else-if="detailError" class="info-placeholder error">{{ detailError }}</div>
        <div v-else-if="tenant" class="tenant-card">
          <div class="tenant-header">
            <div>
              <h2>{{ tenant.name }}</h2>
              <p class="tenant-address">{{ tenant.address }}</p>
            </div>
            <div class="tenant-tags">
              <span class="tag">{{ tenant.type }}</span>
              <span class="status" :class="{ active: tenant.is_active }">{{ tenant.is_active ? '在营' : '停业' }}</span>
            </div>
          </div>
          <div class="tenant-details">
            <div>
              <div class="tuple-box">
                <span class="label">统一社会信用代码</span>
                <strong>{{ tenant.unified_social_credit_code }}</strong>
              </div>
            </div>
            <div>
              <div class="tuple-box">
                <span class="label">法人代表</span>
                <strong>{{ tenant.legal_representative }}</strong>
              </div>
            </div>
            <div>
              <div class="tuple-box">
                <span class="label">业务范围</span>
                <strong>{{ tenant.business_scope }}</strong>
              </div>
            </div>
          </div>
          <div class="tenant-contact">
            <div>
              <div class="tuple-box small">联系人：{{ tenant.contact_person }}</div>
            </div>
            <div>
              <div class="tuple-box small">电话：{{ tenant.contact_phone }}</div>
            </div>
            <div>
              <div class="tuple-box small">邮箱：{{ tenant.contact_email }}</div>
            </div>
          </div>
          <div class="stats-grid">
            <div class="stat-card">
              <span class="stat-label">库存批次数</span>
              <span class="stat-value">{{ stats.total_batches }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">药品种类</span>
              <span class="stat-value">{{ stats.unique_drugs }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">总库存量</span>
              <span class="stat-value">{{ stats.total_quantity }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">最近更新</span>
              <span class="stat-value">{{ latestUpdateText }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="inventory-section">
        <div class="section-header">
          <div>
            <h3>库存批次</h3>
            <p>展示 {{ tenant?.name || '药店' }} 的全部库存批次，可按关键字筛选</p>
          </div>
          <div class="search-controls">
            <input
              type="text"
              placeholder="请输入批次号、药品或供应商"
              v-model="inventoryKeyword"
              @keyup.enter="searchInventory"
            />
            <button class="search-btn" :disabled="inventoryLoading" @click="searchInventory">搜索</button>
            <button class="ghost-btn" :disabled="inventoryLoading && !inventoryKeyword" @click="resetInventorySearch">重置</button>
          </div>
        </div>

        <div v-if="inventoryLoading" class="info-placeholder">正在加载库存...</div>
        <div v-else-if="inventoryError" class="info-placeholder error">{{ inventoryError }}</div>
        <div v-else-if="!inventory.length" class="info-placeholder">暂无库存数据</div>
        <div v-else class="table-wrapper">
          <table class="inventory-table">
            <thead>
              <tr>
                <th>批次号</th>
                <th>药品</th>
                <th>数量</th>
                <th>单价</th>
                <th>生产日期</th>
                <th>有效期</th>
                <th>更新时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in inventory" :key="item.id">
                <td>
                  <div class="tuple-box small">{{ item.batch_number }}</div>
                </td>
                <td>
                  <div class="tuple-box">
                    <div class="drug-name">{{ item.drug_name || '-' }}</div>
                    <div class="drug-brand">{{ item.drug_brand }}</div>
                  </div>
                </td>
                <td>
                  <div class="tuple-box small">{{ item.quantity }}</div>
                </td>
                <td>
                  <div class="tuple-box small">{{ formatPrice(item.unit_price) }}</div>
                </td>
                <td>
                  <div class="tuple-box small">{{ formatDate(item.production_date) }}</div>
                </td>
                <td>
                  <div class="tuple-box small">{{ formatDate(item.expiry_date) }}</div>
                </td>
                <td>
                  <div class="tuple-box small">{{ formatDateTime(item.updated_at) }}</div>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="pagination" v-if="inventoryPagination.total > inventoryPagination.per_page">
            <button class="ghost-btn" :disabled="inventoryPagination.page === 1" @click="changePage(inventoryPagination.page - 1)">
              上一页
            </button>
            <span>第 {{ inventoryPagination.page }} / {{ inventoryTotalPages }} 页 · 共 {{ inventoryPagination.total }} 条</span>
            <button
              class="ghost-btn"
              :disabled="inventoryPagination.page >= inventoryTotalPages"
              @click="changePage(inventoryPagination.page + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter, useRoute } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getCurrentUser, clearAuth } from '@/utils/authSession'
import { fetchInventory, fetchTenantDetail } from '@/api/catalog'
import { getRoleLabel } from '@/utils/roleLabel'
export default {
  name: 'TenantInventory',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const activeNav = ref('inventory')
    const currentUser = ref(getCurrentUser())
    const isLogistics = computed(() => currentUser.value?.role === 'logistics')
    const isSupplier = computed(() => currentUser.value?.role === 'supplier')
    const isPharmacy = computed(() => currentUser.value?.role === 'pharmacy')
    const isRegulator = computed(() => currentUser.value?.role === 'regulator')
    const isAdmin = computed(() => currentUser.value?.role === 'admin')
    const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
    const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
    const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))

    const tenant = ref(null)
    const stats = ref({ total_batches: 0, unique_drugs: 0, total_quantity: 0, latest_update: null })
    const detailLoading = ref(false)
    const detailError = ref('')

    const inventory = ref([])
    const inventoryKeyword = ref('')
    const inventoryPagination = ref({ page: 1, per_page: 10, total: 0 })
    const inventoryLoading = ref(false)
    const inventoryError = ref('')

    const routeTenantId = computed(() => Number(route.params.tenantId))

    const fetchTenant = async () => {
      if (!routeTenantId.value) {
        detailError.value = '参数缺失'
        return
      }
      detailLoading.value = true
      detailError.value = ''
      try {
        const response = await fetchTenantDetail(routeTenantId.value)
        tenant.value = response.tenant
        stats.value = response.stats || stats.value
      } catch (error) {
        detailError.value = error.message || '药店信息加载失败'
        tenant.value = null
      } finally {
        detailLoading.value = false
      }
    }

    const fetchInventoryData = async () => {
      if (!routeTenantId.value) return
      inventoryLoading.value = true
      inventoryError.value = ''
      try {
        const response = await fetchInventory({
          tenantId: routeTenantId.value,
          keyword: inventoryKeyword.value.trim(),
          page: inventoryPagination.value.page,
          perPage: inventoryPagination.value.per_page
        })
        inventory.value = response.items || []
        inventoryPagination.value = {
          page: response.page ?? inventoryPagination.value.page,
          per_page: response.per_page ?? inventoryPagination.value.per_page,
          total: typeof response.total === 'number' ? response.total : (response.items || []).length
        }
      } catch (error) {
        inventoryError.value = error.message || '库存加载失败'
        inventory.value = []
      } finally {
        inventoryLoading.value = false
      }
    }

    const searchInventory = () => {
      inventoryPagination.value = { ...inventoryPagination.value, page: 1 }
      fetchInventoryData()
    }

    const resetInventorySearch = () => {
      inventoryKeyword.value = ''
      inventoryPagination.value = { ...inventoryPagination.value, page: 1 }
      fetchInventoryData()
    }

    const changePage = (page) => {
      const total = Math.max(1, inventoryTotalPages.value)
      if (page < 1 || page > total || page === inventoryPagination.value.page) return
      inventoryPagination.value = { ...inventoryPagination.value, page }
      fetchInventoryData()
    }

    const inventoryTotalPages = computed(() => {
      const total = inventoryPagination.value.total || 0
      const size = inventoryPagination.value.per_page || 1
      return Math.max(1, Math.ceil(total / size))
    })

    const formatDate = (value) => {
      if (!value) return '—'
      return value.slice(0, 10)
    }

    const formatPrice = (value) => {
      if (value === null || value === undefined || value === '') return '—'
      return `¥${Number(value).toFixed(2)}`
    }

    const formatDateTime = (value) => {
      if (!value) return '—'
      return value.replace('T', ' ').replace('Z', '')
    }

    const latestUpdateText = computed(() => {
      if (!stats.value.latest_update) return '—'
      return formatDateTime(stats.value.latest_update)
    })

    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })

    const goToLogin = () => router.push('/login')
    const goToChangePassword = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/change-password' } })
        return
      }
      router.push({ name: 'change-password' })
    }
    const handleLogout = () => {
      clearAuth()
      currentUser.value = null
      router.push('/login')
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
    const goBack = () => router.push('/inventory')

    const refreshUser = () => {
      currentUser.value = getCurrentUser()
    }

    const navigateTo = (page) => {
      activeNav.value = page
      switch (page) {
        case 'home':
          router.push('/')
          break
        case 'inventory':
          router.push('/inventory')
          break
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
          break
        case 'b2b':
          router.push('/b2b')
          break
        case 'circulation':
          router.push('/circulation')
          break
        case 'analysis':
          router.push('/analysis')
          break
        case 'service':
          router.push('/service')
          break
        default:
          router.push('/')
      }
    }

    watch(() => route.params.tenantId, () => {
      inventoryPagination.value = { ...inventoryPagination.value, page: 1, total: 0 }
      fetchTenant()
      fetchInventoryData()
    })

    onMounted(() => {
      window.addEventListener('storage', refreshUser)
      fetchTenant()
      fetchInventoryData()
    })

    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
    })

    return {
      activeNav,
      currentUser,
      isRegulator,
      isAdmin,
      canViewAnalysis,
      userDisplayName,
      userRoleLabel,
      goToLogin,
      goToChangePassword,
      handleLogout,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      navigateTo,
      currentDate,
      tenant,
      stats,
      detailLoading,
      detailError,
      inventory,
      inventoryKeyword,
      inventoryPagination,
      inventoryLoading,
      inventoryError,
      inventoryTotalPages,
      latestUpdateText,
      searchInventory,
      resetInventorySearch,
      changePage,
      formatDate,
      formatPrice,
      formatDateTime,
      goBack,
      routeTenantId
      , isLogistics,
      isSupplier,
      isPharmacy
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.tenant-inventory-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  width: 100%;
}

.header-content {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 0 20px;
}

.platform-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.platform-title {
  font-size: 24px;
  font-weight: bold;
  color: #1a73e8;
  margin: 0;
}

.current-date {
  color: #666;
  font-size: 16px;
}

.nav-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-item {
  font-size: 16px;
  color: #333;
  cursor: pointer;
  padding: 5px 0;
  transition: color 0.3s;
}

.nav-item.active,
.nav-item:hover {
  color: #1a73e8;
}

.user-actions {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background-color: #f0f5ff;
  color: #1a73e8;
  font-size: 14px;
  font-weight: 600;
  margin-right: 10px;
  gap: 8px;
}

.user-name {
  white-space: nowrap;
}

.user-role {
  padding: 2px 10px;
  border-radius: 999px;
  background-color: #fff;
  border: 1px solid rgba(26, 115, 232, 0.2);
  font-size: 12px;
  color: #1a73e8;
}

.auth-btn {
  background-color: #fff;
  color: #1a73e8;
  border: 1px solid #1a73e8;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
}

.auth-btn:hover {
  background-color: rgba(26, 115, 232, 0.08);
}

.review-btn {
  background-color: #fff7e6;
  color: #b76c00;
  border: 1px solid #f3e5b8;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.review-btn:hover {
  background-color: #ffeccc;
}

.admin-btn {
  background-color: #f0f5ff;
  color: #1a73e8;
  border: 1px solid #d6e4ff;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.admin-btn:hover {
  background-color: #e5edff;
}

.change-btn {
  border: 1px solid #1a73e8;
  background-color: transparent;
  color: #1a73e8;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
  transition: background-color 0.3s;
}

.change-btn:hover {
  background-color: rgba(26, 115, 232, 0.08);
}

.login-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #0d62d9;
}

.main-content {
  flex: 1;
  width: 100%;
  margin: 0;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.back-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tenant-id {
  font-size: 13px;
  color: #6b7280;
}

.ghost-btn {
  background-color: transparent;
  border: 1px solid #1a73e8;
  color: #1a73e8;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.ghost-btn:hover {
  background-color: #e8f2ff;
}

.tenant-section,
.inventory-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.tenant-card h2 {
  margin-bottom: 6px;
}

.tenant-address {
  color: #6b7280;
}

.tenant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 16px;
}

.tenant-tags {
  display: flex;
  gap: 10px;
  align-items: center;
}

.tag {
  padding: 4px 12px;
  border-radius: 999px;
  background-color: #e8f0fe;
  color: #1a73e8;
  font-size: 13px;
}

.status {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 999px;
  background-color: #f5f5f5;
  color: #999;
}

.status.active {
  background-color: #e6f4ea;
  color: #1e8e3e;
}

.tenant-details,
.tenant-contact {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

/* 无填充的区块框：用于将若干元组信息视觉分组 */
.tuple-box {
  border: 1px solid rgba(26, 115, 232, 0.12);
  border-radius: 8px;
  padding: 10px;
  background-color: transparent;
  display: block;
}
.tuple-box.small {
  padding: 6px 8px;
  font-size: 13px;
}

.tenant-details .label {
  display: block;
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 15px;
}

.stat-card {
  background-color: #f7f9fc;
  border-radius: 8px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #1a73e8;
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.search-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.search-controls input {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 8px 12px;
  min-width: 240px;
}

.search-btn {
  background-color: #1a73e8;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.info-placeholder {
  text-align: center;
  color: #6b7280;
  padding: 30px 0;
}

.info-placeholder.error {
  color: #d93025;
}

.table-wrapper {
  overflow-x: auto;
}

.inventory-table {
  width: 100%;
  border-collapse: separate;
  /* vertical spacing between logical rows */
  border-spacing: 0 12px;
}

.inventory-table th,
.inventory-table td {
  text-align: left;
  padding: 0; /* td 内使用 .tuple-box 控制内边距 */
  border-bottom: none;
  font-size: 14px;
  vertical-align: middle;
}

/* 让每行的 tuple-box 占满单元格宽度，并在整行 hover 时强调 */
.inventory-table tbody tr .tuple-box {
  width: 100%;
}
.inventory-table tbody tr:hover .tuple-box {
  border-color: rgba(26, 115, 232, 0.22);
  box-shadow: 0 6px 18px rgba(26,115,232,0.06);
}

.drug-brand {
  font-size: 12px;
  color: #6b7280;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .nav-menu {
    flex-wrap: wrap;
  }
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .search-controls {
    width: 100%;
  }
  .search-controls input {
    flex: 1;
    min-width: 0;
    width: 100%;
  }
}
</style>
