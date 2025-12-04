<template>
  <div class="inventory-container">
    <!-- 顶部导航栏 - 直接复制自 Home.vue，确保结构与样式完全一致 -->
    <div class="header">
      <div class="header-content">
        <div class="platform-info">
          <h1 class="platform-title">上海药品监管信息平台</h1>
          <div class="current-date">{{ currentDate }}</div>
        </div>
        
        <div class="nav-section">
          <div class="nav-menu">
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'home' }"
              @click="navigateTo('home')"
            >首页</div>
            <div 
              v-if="!isLogistics && !isRegulator"
              class="nav-item" 
              :class="{ active: activeNav === 'inventory' }"
              @click="navigateTo('inventory')"
            >库存管理</div>
            <div v-if="isPharmacy" class="nav-item" :class="{ active: activeNav === 'nearby' }" @click="navigateTo('nearby')">就近推荐</div>
            <div 
              v-if="!isLogistics"
              class="nav-item" 
              :class="{ active: activeNav === 'b2b' }"
              @click="navigateTo('b2b')"
            >B2B供求平台</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'circulation' }"
              @click="navigateTo('circulation')"
            >流通监管</div>
            <div 
              v-if="canViewAnalysis"
              class="nav-item" 
              :class="{ active: activeNav === 'analysis' }"
              @click="navigateTo('analysis')"
            >监管分析</div>
            <div v-if="isLogistics"
              class="nav-item" 
              :class="{ active: activeNav === 'service' }"
              @click="navigateTo('service')"
            >智能调度</div>
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

    <!-- 库存管理主内容区域 -->
    <div class="main-content">
      <div class="inventory-tabs">
        <div
          v-for="tab in inventoryTabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeInventoryTab === tab.key }"
          @click="setActiveInventoryTab(tab.key)"
        >
          {{ tab.label }}
        </div>
      </div>

      <div v-if="activeInventoryTab === 'overview'" class="tab-panel">
        <div v-if="myTenantId">
          <div class="section my-tenant-overview">
            <div class="section-header">
              <div>
                <h2 class="section-title">我的企业库存概览</h2>
                <p class="section-subtitle">聚焦当前登录用户所在企业的主体信息与库存统计</p>
              </div>
              <button v-if="!isLogistics" class="ghost-btn" @click="goToMyTenantInventory">查看全部明细</button>
            </div>
            <div v-if="myTenantLoading" class="info-placeholder">正在加载企业信息...</div>
            <div v-else-if="myTenantError" class="info-placeholder error">
              {{ myTenantError }}
              <button class="ghost-btn retry-btn" @click="reloadMyTenant">重新加载</button>
            </div>
            <div v-else-if="myTenantDetail" class="tenant-overview-content">
              <div class="tenant-header">
                <div>
                  <h3>{{ myTenantDetail.name }}</h3>
                  <p class="tenant-address">{{ myTenantDetail.address }}</p>
                </div>
                <div class="tenant-tags">
                  <span class="tag">{{ myTenantDetail.type }}</span>
                  <span class="status" :class="{ active: myTenantDetail.is_active }">
                    {{ myTenantDetail.is_active ? '在营' : '停业' }}
                  </span>
                </div>
              </div>
              <div class="stats-grid">
                <div class="stat-card">
                  <span class="stat-label">库存批次</span>
                  <span class="stat-value">{{ myTenantStats.total_batches }}</span>
                </div>
                <div class="stat-card">
                  <span class="stat-label">药品种类</span>
                  <span class="stat-value">{{ myTenantStats.unique_drugs }}</span>
                </div>
                <div class="stat-card">
                  <span class="stat-label">总库存量</span>
                  <span class="stat-value">{{ myTenantStats.total_quantity }}</span>
                </div>
                <div class="stat-card">
                  <span class="stat-label">最近更新</span>
                  <span class="stat-value">{{ myLatestUpdateText }}</span>
                </div>
              </div>
            </div>
            <div v-else class="info-placeholder">暂无企业信息</div>
          </div>

          <div class="section my-tenant-inventory">
            <div class="section-header">
              <div>
                <h2 class="section-title">企业库存明细</h2>
                <p class="section-subtitle">仅展示当前企业的库存批次</p>
              </div>
              <div class="search-controls">
                <input
                  type="text"
                  placeholder="输入批次号、药品或供应商"
                  v-model="myInventoryKeyword"
                  @keyup.enter="searchMyInventory"
                />
                <button class="search-btn" :disabled="myInventoryLoading" @click="searchMyInventory">搜索</button>
                <button
                  class="ghost-btn"
                  :disabled="!myInventoryKeyword || myInventoryLoading"
                  @click="resetMyInventorySearch"
                >
                  重置
                </button>
              </div>
            </div>
            <div v-if="myInventoryLoading" class="info-placeholder">正在加载库存...</div>
            <div v-else-if="myInventoryError" class="info-placeholder error">{{ myInventoryError }}</div>
            <div v-else-if="!myInventory.length" class="info-placeholder">暂无库存数据</div>
            <div v-else class="table-wrapper">
              <table class="result-table my-inventory-table">
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
                  <tr v-for="item in myInventory" :key="item.id">
                    <td>
                      <div class="tuple-box small">
                        <template v-if="isAuthenticatedViewer">{{ item.batch_number }}</template>
                        <template v-else>—</template>
                      </div>
                    </td>
                    <td>
                      <div class="tuple-box">
                        <div class="drug-name">{{ item.drug_name || '—' }}</div>
                        <div class="drug-brand">{{ item.drug_brand }}</div>
                      </div>
                    </td>
                    <td>
                      <div class="tuple-box small">
                        <template v-if="isAuthenticatedViewer">{{ item.quantity }}</template>
                        <template v-else>需认证后查看</template>
                      </div>
                    </td>
                    <td>
                      <div class="tuple-box small">
                        <template v-if="isAuthenticatedViewer">{{ formatPrice(item.unit_price) }}</template>
                        <template v-else>—</template>
                      </div>
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
              <div class="pagination" v-if="myInventoryPagination.total > myInventoryPagination.per_page">
                <button class="ghost-btn" :disabled="myInventoryPagination.page === 1" @click="changeMyInventoryPage(myInventoryPagination.page - 1)">
                  上一页
                </button>
                <span>第 {{ myInventoryPagination.page }} / {{ myInventoryTotalPages }} 页 · 共 {{ myInventoryPagination.total }} 条</span>
                <button
                  class="ghost-btn"
                  :disabled="myInventoryPagination.page >= myInventoryTotalPages"
                  @click="changeMyInventoryPage(myInventoryPagination.page + 1)"
                >
                  下一页
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="info-placeholder">
          当前账号未关联企业，无法展示库存概览。
        </div>
      </div>

      <div v-else-if="activeInventoryTab === 'maintenance'" class="tab-panel">
        <div v-if="myTenantId && canManageInventory" class="section manual-inventory-section">
          <div class="section-header">
            <div>
              <h2 class="section-title">库存维护</h2>
              <p class="section-subtitle">通过标准化操作板维护库存批次与补货计划</p>
            </div>
          </div>
          <InventoryManagePanel />
        </div>
        <div v-else class="info-placeholder">
          该功能仅对已认证企业开放，请先完成企业认证或切换具备权限的账户。
        </div>
      </div>

      <div v-else class="tab-panel">
        <div class="section inventory-warning-section">
          <div class="section-header">
            <div>
              <h2 class="section-title">库存预警管理</h2>
              <p class="section-subtitle">实时监测低库存、临期批次并给出调拨建议</p>
            </div>
          </div>
          <div style="padding: 10px 0">
            <InventoryWarning />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { useRouter, useRoute } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getCurrentUser } from '@/utils/authSession'
import { getRoleLabel } from '@/utils/roleLabel'
import { roleToRoute } from '@/utils/roleRoute'
import { fetchInventory, fetchTenantDetail } from '@/api/catalog'
import InventoryWarning from '@/component/InventoryWarning.vue'
import InventoryManagePanel from '@/component/InventoryManagePanel.vue'

export default {
  name: 'Inventory',
  components: { InventoryWarning, InventoryManagePanel },
  setup() {
    const router = useRouter()
    const activeNav = ref('inventory')
    const route = useRoute()

    const mapRouteToNav = (name) => {
      switch (name) {
        case 'home':
          return 'home'
        case 'inventory':
        case 'tenant-inventory':
          return 'inventory'
        case 'b2b':
          return 'b2b'
        case 'circulation':
          return 'circulation'
        case 'nearby-suppliers':
          return 'nearby'
        case 'analysis':
          return 'analysis'
        case 'service':
          return 'service'
        default:
          return 'home'
      }
    }
    const currentUser = ref(getCurrentUser())
    const inventoryTabs = [
      { key: 'overview', label: '我的企业库存概览' },
      { key: 'maintenance', label: '库存维护' },
      { key: 'warning', label: '库存预警管理' }
    ]
    const activeInventoryTab = ref('overview')
    const isLogistics = computed(() => currentUser.value && currentUser.value.role === 'logistics')
    const isSupplier = computed(() => currentUser.value && currentUser.value.role === 'supplier')
    const isPharmacy = computed(() => currentUser.value && currentUser.value.role === 'pharmacy')
    const isRegulator = computed(() => currentUser.value && currentUser.value.role === 'regulator')
    const isAdmin = computed(() => currentUser.value && currentUser.value.role === 'admin')
    const isAuthenticatedViewer = computed(() => Boolean(currentUser.value && currentUser.value.role && currentUser.value.role !== 'unauth'))
    const canManageInventory = computed(() => isPharmacy.value || isSupplier.value || isAdmin.value)
    const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
    const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
    const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))
    const myTenantId = computed(() => currentUser.value?.tenant_id || null)
    const createDefaultStats = () => ({
      total_batches: 0,
      unique_drugs: 0,
      total_quantity: 0,
      latest_update: null
    })
    const myTenantDetail = ref(null)
    const myTenantStats = ref(createDefaultStats())
    const myTenantLoading = ref(false)
    const myTenantError = ref('')
    const myInventory = ref([])
    const myInventoryKeyword = ref('')
    const myInventoryPagination = ref({ page: 1, per_page: 10, total: 0 })
    const myInventoryLoading = ref(false)
    const myInventoryError = ref('')

    const myInventoryTotalPages = computed(() => {
      const total = myInventoryPagination.value.total || 0
      const size = myInventoryPagination.value.per_page || 1
      return Math.max(1, Math.ceil(total / size))
    })

    const fetchMyTenantInfo = async () => {
      if (!myTenantId.value) return
      myTenantLoading.value = true
      myTenantError.value = ''
      try {
        const response = await fetchTenantDetail(myTenantId.value)
        myTenantDetail.value = response.tenant
        myTenantStats.value = response.stats || createDefaultStats()
      } catch (error) {
        myTenantError.value = error.message || '企业信息加载失败'
        myTenantDetail.value = null
        myTenantStats.value = createDefaultStats()
      } finally {
        myTenantLoading.value = false
      }
    }

    const fetchMyInventoryData = async () => {
      if (!myTenantId.value) return
      myInventoryLoading.value = true
      myInventoryError.value = ''
      try {
        const response = await fetchInventory({
          tenantId: myTenantId.value,
          keyword: myInventoryKeyword.value.trim(),
          page: myInventoryPagination.value.page,
          perPage: myInventoryPagination.value.per_page
        })
        myInventory.value = response.items || []
        myInventoryPagination.value = {
          page: response.page ?? myInventoryPagination.value.page,
          per_page: response.per_page ?? myInventoryPagination.value.per_page,
          total: typeof response.total === 'number' ? response.total : (response.items || []).length
        }
      } catch (error) {
        myInventoryError.value = error.message || '库存加载失败'
        myInventory.value = []
      } finally {
        myInventoryLoading.value = false
      }
    }

    const searchMyInventory = () => {
      myInventoryPagination.value = { ...myInventoryPagination.value, page: 1, total: 0 }
      fetchMyInventoryData()
    }

    const resetMyInventorySearch = () => {
      myInventoryKeyword.value = ''
      myInventoryPagination.value = { ...myInventoryPagination.value, page: 1, total: 0 }
      fetchMyInventoryData()
    }

    const changeMyInventoryPage = (page) => {
      const total = Math.max(1, myInventoryTotalPages.value)
      if (page < 1 || page > total || page === myInventoryPagination.value.page) return
      myInventoryPagination.value = { ...myInventoryPagination.value, page }
      fetchMyInventoryData()
    }

    const formatDate = (value) => {
      if (!value) return '—'
      return String(value).slice(0, 10)
    }

    const formatPrice = (value) => {
      if (value === null || value === undefined || value === '') return '—'
      return `¥${Number(value).toFixed(2)}`
    }

    const formatDateTime = (value) => {
      if (!value) return '—'
      return String(value).replace('T', ' ').replace('Z', '')
    }

    const myLatestUpdateText = computed(() => {
      if (!myTenantStats.value.latest_update) return '—'
      return formatDateTime(myTenantStats.value.latest_update)
    })

    const reloadMyTenant = () => {
      if (!myTenantId.value) return
      fetchMyTenantInfo()
      fetchMyInventoryData()
    }

    watch(myTenantId, (tenantId) => {
      if (!tenantId) {
        myTenantDetail.value = null
        myTenantError.value = ''
        myTenantStats.value = createDefaultStats()
        myInventory.value = []
        return
      }
      myInventoryPagination.value = { ...myInventoryPagination.value, page: 1, total: 0 }
      fetchMyTenantInfo()
      fetchMyInventoryData()
    }, { immediate: true })

    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })

    const goToLogin = () => {
      router.push('/login')
    }
      const goToChangePassword = () => {
        if (!currentUser.value) {
          router.push({ name: 'login', query: { redirect: '/change-password' } })
          return
        }
        router.push({ name: 'change-password' })
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
    const setActiveInventoryTab = (tab) => {
      activeInventoryTab.value = tab
    }

    const refreshUser = () => {
      currentUser.value = getCurrentUser()
    }

    const goToUserHome = () => {
      const u = currentUser.value
      if (!u) return router.push('/login')
      router.push(roleToRoute(u.role))
    }

    const navigateTo = (page) => {
      switch (page) {
        case 'home':
          router.push('/')
          break
        case 'inventory':
          // 已登录但未认证用户：若关联企业则跳转企业明细页，否则去企业认证页；未登录跳登录
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/inventory' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            // 显示未认证提示页，但保留用户的点击意图（active=inventory）用于 nav 高亮
            router.push({ name: 'unauth', query: { active: 'inventory' } })
            break
          }
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
        case 'b2b':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/b2b' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'b2b' } })
            break
          }
          router.push('/b2b')
          break
        case 'circulation':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/circulation' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'circulation' } })
            break
          }
          router.push('/circulation')
          break
        case 'analysis':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/analysis' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'analysis' } })
            break
          }
          router.push('/analysis')
          break
        case 'service':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/service' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'service' } })
            break
          }
          router.push('/service')
          break
        default:
          router.push('/')
      }
    }

    const goToMyTenantInventory = () => {
      if (!myTenantId.value) return
      router.push({ name: 'tenant-inventory', params: { tenantId: myTenantId.value } })
    }

    onMounted(() => {
      activeNav.value = mapRouteToNav(route.name)
      window.addEventListener('storage', refreshUser)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
    })

    watch(() => route.name, (name) => {
      activeNav.value = mapRouteToNav(name)
    })

    return {
      goToLogin,
      goToChangePassword,
      goToUserHome,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      inventoryTabs,
      activeInventoryTab,
      setActiveInventoryTab,
      navigateTo,
      activeNav,
      currentDate,
      currentUser,
      isAuthenticatedViewer,
      isLogistics,
      isSupplier,
      isRegulator,
      isAdmin,
      isPharmacy,
      canViewAnalysis,
      canManageInventory,
      userDisplayName,
      userRoleLabel,
      myTenantId,
      myTenantDetail,
      myTenantStats,
      myTenantLoading,
      myTenantError,
      myLatestUpdateText,
      reloadMyTenant,
      myInventory,
      myInventoryKeyword,
      myInventoryPagination,
      myInventoryLoading,
      myInventoryError,
      myInventoryTotalPages,
      searchMyInventory,
      resetMyInventorySearch,
      changeMyInventoryPage,
      goToMyTenantInventory,
      formatDate,
      formatPrice,
      formatDateTime
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

.inventory-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
  line-height: 1.6;
}

/* 顶部导航栏样式 - 与Home.vue保持一致 */
.header {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  width: 100%;
}

/* 确保 header 内部不受父容器 line-height 影响 */
.header {
  line-height: normal;
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

.nav-item:hover {
  color: #1a73e8;
}

.nav-item.active {
  color: #1a73e8;
  border-bottom: 2px solid #1a73e8;
}

.user-actions {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 999px;
  background-color: #f0f5ff;
  color: #1a73e8;
  font-size: 14px;
  font-weight: 600;
  margin-right: 10px;
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

/* 精确覆盖：确保库存页面顶栏行距与 Home.vue 完全一致 */
.header .platform-title {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
  margin: 0;
}
.header .platform-info {
  margin-bottom: 15px;
}
.header {
  padding: 15px 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
.nav-section {
  padding-top: 15px;
}
.nav-menu {
  gap: 30px;
}
.nav-item {
  padding: 5px 0;
}

/* 按钮垂直间距调整，增加上下呼吸感 */
.user-actions button,
.search-controls button,
.filters > button,
.ghost-btn,
.auth-btn,
.review-btn,
.admin-btn,
.login-btn,
.search-btn {
  margin-top: 8px;
  margin-bottom: 8px;
}

/* 主内容区域样式 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}


.inventory-tabs {
  display: flex;
  gap: 40px;
  padding: 0 8px;
  border-bottom: 1px solid #e5e5e5;
  background: transparent;
}

.tab-item {
  position: relative;
  padding: 10px 0;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  transition: color 0.2s ease;
}

.tab-item::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  width: 100%;
  background-color: transparent;
  transition: background-color 0.2s ease;
}

.tab-item.active {
  color: #1a73e8;
  font-weight: 600;
}

.tab-item.active::after {
  background-color: #1a73e8;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 6px rgba(10, 20, 30, 0.04);
  padding: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #222;
}

.section-subtitle {
  margin-top: 6px;
  color: #6b7280;
  font-size: 14px;
}

.tag {
  padding: 4px 12px;
  border-radius: 999px;
  background-color: #e8f0fe;
  color: #1a73e8;
  font-size: 13px;
  height: fit-content;
}

.ghost-btn {
  background-color: transparent;
  border: 1px solid #1a73e8;
  color: #1a73e8;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.ghost-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ghost-btn:not(:disabled):hover {
  background-color: #e8f2ff;
}

.table-wrapper {
  overflow-x: auto;
}

.result-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 12px;
}

.result-table th,
.result-table td {
  text-align: left;
  padding: 0; /* 内边距由 .tuple-box 控制 */
  border-bottom: none;
  font-size: 14px;
  vertical-align: middle;
}

.result-table tbody tr .tuple-box {
  width: 100%;
}
.result-table tbody tr:hover .tuple-box {
  border-color: rgba(26, 115, 232, 0.22);
  box-shadow: 0 6px 18px rgba(26,115,232,0.06);
}

.result-table th {
  background-color: #f7f9fc;
  color: #555;
}

.info-placeholder {
  text-align: center;
  color: #6b7280;
  padding: 28px 0;
}

.info-placeholder.error {
  color: #d93025;
}

.retry-btn {
  margin-left: 12px;
}

.tenant-overview-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.tenant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.tenant-address {
  color: #6b7280;
  margin-top: 4px;
}

.tenant-tags {
  display: flex;
  gap: 12px;
  align-items: center;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
}

.stat-card {
  background-color: #fbfdff;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.my-inventory-table .drug-name {
  font-weight: 600;
}

.my-inventory-table .drug-brand {
  font-size: 12px;
  color: #6b7280;
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .platform-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .nav-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .nav-menu {
    flex-wrap: wrap;
  }
  
  .main-content {
    padding: 10px;
  }
}
</style>


