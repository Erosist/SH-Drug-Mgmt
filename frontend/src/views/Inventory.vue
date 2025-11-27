<template>
  <div class="inventory-container">
    <!-- 顶部导航栏 - 与Home.vue保持一致 -->
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
              class="nav-item" 
              :class="{ active: activeNav === 'inventory' }"
              @click="navigateTo('inventory')"
            >库存管理</div>
            <div 
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
              class="nav-item" 
              :class="{ active: activeNav === 'analysis' }"
              @click="navigateTo('analysis')"
            >监管分析</div>
            <div 
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
      <div v-if="myTenantId" class="section my-tenant-overview">
        <div class="section-header">
          <div>
            <h2 class="section-title">我的企业库存概览</h2>
            <p class="section-subtitle">聚焦当前登录用户所在企业的主体信息与库存统计</p>
          </div>
          <button class="ghost-btn" @click="goToMyTenantInventory">查看全部明细</button>
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
          <div class="tenant-details-grid">
            <div>
              <span class="info-label">统一社会信用代码</span>
              <strong>{{ myTenantDetail.unified_social_credit_code }}</strong>
            </div>
            <div>
              <span class="info-label">法人代表</span>
              <strong>{{ myTenantDetail.legal_representative }}</strong>
            </div>
            <div>
              <span class="info-label">联系人</span>
              <strong>{{ myTenantDetail.contact_person }}</strong>
            </div>
            <div>
              <span class="info-label">联系电话</span>
              <strong>{{ myTenantDetail.contact_phone }}</strong>
            </div>
          </div>
          <div class="tenant-contact-grid">
            <div>业务范围：{{ myTenantDetail.business_scope }}</div>
            <div>邮箱：{{ myTenantDetail.contact_email }}</div>
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

      <div v-if="myTenantId" class="section my-tenant-inventory">
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
                <td>{{ item.batch_number }}</td>
                <td>
                  <div class="drug-name">{{ item.drug_name || '—' }}</div>
                  <div class="drug-brand">{{ item.drug_brand }}</div>
                </td>
                <td>{{ item.quantity }}</td>
                <td>{{ formatPrice(item.unit_price) }}</td>
                <td>{{ formatDate(item.production_date) }}</td>
                <td>{{ formatDate(item.expiry_date) }}</td>
                <td>{{ formatDateTime(item.updated_at) }}</td>
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

      <div class="content-wrapper">
        <!-- 左侧主要内容 -->
        <div class="left-content">
          <!-- 库存预警管理 -->
          <div class="section inventory-warning-section">
            <h2 class="section-title">库存预警管理</h2>
            <div style="padding: 10px 0">
              <InventoryWarning />
            </div>
          </div>
          
          <!-- 药品定位与就近推荐 -->
          <div class="section drug-location">
            <h2 class="section-title">药品定位与就近推荐</h2>
            
            <!-- 搜索筛选区域 -->
            <div class="search-filters">
              <div class="filter-row">
                <div class="filter-group">
                  <label>药品名称/ID</label>
                  <div class="search-input-group">
                    <input type="text" placeholder="输入药品名称或ID" class="search-field">
                    <button class="search-btn">搜索</button>
                  </div>
                </div>
                
                <div class="filter-group">
                  <label>供应商类型</label>
                  <select class="filter-select">
                    <option>全部</option>
                    <option>医院药房</option>
                    <option>连锁药店</option>
                    <option>个体药店</option>
                  </select>
                </div>
              </div>
              
              <div class="filter-row">
                <div class="filter-group">
                  <label>金额</label>
                  <input type="text" placeholder="输入金额范围" class="filter-field">
                </div>
                
                <div class="filter-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="within5km">
                    <span class="checkmark"></span>
                    5公里内
                  </label>
                </div>
              </div>
            </div>
            
            <!-- 推荐供应商列表 -->
            <div class="recommended-suppliers">
              <h3 class="subsection-title">推荐供应商</h3>
              
              <div class="supplier-list">
                <div 
                  class="supplier-card" 
                  :class="{ active: selectedSupplier === 'renji' }"
                  @click="selectSupplier('renji')"
                >
                  <div class="supplier-name">仁济医院药房</div>
                  <div class="supplier-info">
                    <span class="medical-insurance">医保</span>
                    <span class="distance">1.2公里</span>
                  </div>
                </div>
                
                <div 
                  class="supplier-card" 
                  :class="{ active: selectedSupplier === 'baixin' }"
                  @click="selectSupplier('baixin')"
                >
                  <div class="supplier-name">百信连锁药店</div>
                  <div class="supplier-info">
                    <span class="medical-insurance">医保</span>
                    <span class="distance">3.5公里</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧供应商详情 -->
        <div class="right-content">
          <!-- 供应商详情 -->
          <div class="section supplier-detail">
            <h2 class="section-title">供应商详情</h2>
            
            <div v-if="selectedSupplier === 'renji'" class="supplier-info-panel">
              <div class="supplier-header">
                <h3 class="supplier-title">仁济医院药房</h3>
              </div>
              
              <div class="supplier-metrics">
                <div class="metric-item">
                  <span class="metric-label">有效率</span>
                  <span class="metric-value">4.9</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">配送时间</span>
                  <span class="metric-value">1.2公里</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">库存用量</span>
                  <span class="metric-value">充足</span>
                </div>
              </div>
            </div>
            
            <div v-if="selectedSupplier === 'baixin'" class="supplier-info-panel">
              <div class="supplier-header">
                <h3 class="supplier-title">百信连锁药店</h3>
              </div>
              
              <div class="supplier-metrics">
                <div class="metric-item">
                  <span class="metric-label">有效率</span>
                  <span class="metric-value">4.7</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">配送时间</span>
                  <span class="metric-value">3.5公里</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">库存用量</span>
                  <span class="metric-value">一般</span>
                </div>
              </div>
            </div>
            
            <div v-if="!selectedSupplier" class="no-supplier-selected">
              请选择左侧的供应商查看详情
            </div>
          </div>
          
          <!-- 供应商位置分布 -->
          <div class="section supplier-distribution">
            <h2 class="section-title">供应商位置分布</h2>
            
            <div class="distribution-metrics">
              <div class="distribution-item">
                <span class="distribution-label">有效率</span>
                <span class="distribution-value">0.8</span>
              </div>
              <div class="distribution-item">
                <span class="distribution-label">库存数量</span>
                <span class="distribution-value">1.6</span>
              </div>
              <div class="distribution-item">
                <span class="distribution-label">运输时间</span>
                <span class="distribution-value">1.7</span>
              </div>
            </div>
            
            <!-- 订单信息 -->
            <div class="order-info">
              <div class="order-code">平码至36开间</div>
              <div class="order-time">23分钟</div>
              <div class="order-status">当前订单</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getCurrentUser } from '@/utils/authSession'
import { getRoleLabel } from '@/utils/roleLabel'
import { roleToRoute } from '@/utils/roleRoute'
import { fetchInventory, fetchTenantDetail } from '@/api/catalog'
import InventoryWarning from '@/component/InventoryWarning.vue'

export default {
  name: 'Inventory',
  components: { InventoryWarning },
  setup() {
    const router = useRouter()
    const activeNav = ref('inventory')
    const selectedSupplier = ref('renji')
    const within5km = ref(true)
    const currentUser = ref(getCurrentUser())
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

    const refreshUser = () => {
      currentUser.value = getCurrentUser()
    }

    const goToUserHome = () => {
      const u = currentUser.value
      if (!u) return router.push('/login')
      router.push(roleToRoute(u.role))
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

    const selectSupplier = (supplier) => {
      selectedSupplier.value = supplier
    }

    const goToMyTenantInventory = () => {
      if (!myTenantId.value) return
      router.push({ name: 'tenant-inventory', params: { tenantId: myTenantId.value } })
    }

    onMounted(() => {
      window.addEventListener('storage', refreshUser)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
    })

    return {
      goToLogin,
      goToUserHome,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      navigateTo,
      activeNav,
      selectedSupplier,
      selectSupplier,
      within5km,
      currentDate,
      currentUser,
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
}

/* 顶部导航栏样式 - 与Home.vue保持一致 */
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
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
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

/* 主内容区域样式 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  height: 100%;
}

.section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
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
  border-collapse: collapse;
}

.result-table th,
.result-table td {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.result-table th {
  background-color: #f7f9fc;
  color: #555;
}

.info-placeholder {
  text-align: center;
  color: #6b7280;
  padding: 20px 0;
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

.tenant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.tenant-address {
  color: #6b7280;
  margin-top: 4px;
}

.tenant-tags {
  display: flex;
  gap: 10px;
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

.tenant-details-grid,
.tenant-contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.info-label {
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

/* 搜索筛选区域样式 */
.search-filters {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.filter-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.search-input-group {
  display: flex;
}

.search-field {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  outline: none;
}

.search-field:focus {
  border-color: #1a73e8;
}

.search-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.filter-select, .filter-field {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

.filter-select:focus, .filter-field:focus {
  border-color: #1a73e8;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-top: 8px;
}

.checkbox-label input {
  margin-right: 8px;
}

/* 推荐供应商样式 */
.subsection-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.supplier-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.supplier-card {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.supplier-card:hover {
  border-color: #1a73e8;
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.1);
}

.supplier-card.active {
  border-color: #1a73e8;
  background-color: #f0f7ff;
}

.supplier-name {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.supplier-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.medical-insurance {
  color: #27ae60;
  font-weight: bold;
}

.distance {
  color: #666;
}

/* 供应商详情样式 */
.supplier-info-panel {
  padding: 10px 0;
}

.supplier-header {
  margin-bottom: 20px;
}

.supplier-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.supplier-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-label {
  color: #666;
  font-size: 14px;
}

.metric-value {
  font-weight: bold;
  color: #333;
}

.no-supplier-selected {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-style: italic;
}

/* 供应商位置分布样式 */
.distribution-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.distribution-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.distribution-label {
  color: #666;
  font-size: 14px;
}

.distribution-value {
  font-weight: bold;
  color: #333;
}

.order-info {
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  text-align: center;
}

.order-code {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.order-time {
  color: #1a73e8;
  font-weight: bold;
  margin-bottom: 5px;
}

.order-status {
  color: #666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .filter-row {
    flex-direction: column;
    gap: 10px;
  }
}

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


