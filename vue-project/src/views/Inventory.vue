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
            <button v-if="!currentUser || currentUser.role!=='regulator'" class="auth-btn" @click="goToEnterpriseAuth">企业认证</button>
            <button v-if="currentUser && currentUser.role==='regulator'" class="review-btn" @click="goToEnterpriseReview">认证审核</button>
            <button v-if="currentUser && currentUser.role==='regulator'" class="admin-btn" @click="goToAdminUsers">用户管理</button>
            <button v-if="!currentUser" class="login-btn" @click="goToLogin">登录</button>
            <button v-else class="login-btn" @click="goToUserHome">我的主页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 库存管理主内容区域 -->
    <div class="main-content">
      <div class="section data-query">
        <div class="data-query-header">
          <div>
            <h2 class="section-title">真实数据查询</h2>
            <p class="section-subtitle">直连后端数据库，支持药品、药店与库存批次的关键字检索</p>
          </div>
          <div class="tag">实时数据</div>
        </div>
        <div class="query-controls">
          <div class="query-field">
            <label>查询类型</label>
            <select v-model="queryType">
              <option value="drugs">药品</option>
              <option value="tenants">药店/机构</option>
            </select>
          </div>
          <div class="query-field flex-1">
            <label>关键字</label>
            <div class="query-input-group">
              <input
                type="text"
                :placeholder="queryPlaceholder"
                v-model="queryKeyword"
                @keyup.enter="performQuery"
              />
              <button class="search-btn" :disabled="dataLoading" @click="performQuery">查询</button>
              <button class="ghost-btn" :disabled="!queryKeyword || dataLoading" @click="resetQuery">重置</button>
            </div>
          </div>
        </div>
        <div class="query-results">
          <div v-if="dataLoading" class="query-feedback">正在查询...</div>
          <div v-else-if="dataError" class="query-feedback error">{{ dataError }}</div>
          <div v-else-if="!results.length" class="query-feedback">暂无数据，请调整筛选条件</div>
          <div v-else class="table-wrapper">
            <table class="result-table">
              <thead>
                <tr>
                  <th v-for="col in activeColumns" :key="col.key">{{ col.label }}</th>
                  <th v-if="queryType === 'tenants'">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in results" :key="`${queryType}-${row.id}`">
                  <td v-for="col in activeColumns" :key="col.key">{{ formatCell(row, col.key) }}</td>
                  <td v-if="queryType === 'tenants'">
                    <button class="link-btn" @click="viewTenantInventory(row.id)">查看库存</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="queryType === 'tenants'" class="hint-text">
              点击“查看库存”即可进入该药店的库存明细（二级页面）
            </div>
            <div class="pagination" v-if="pagination.total > pagination.per_page">
              <button
                class="ghost-btn"
                :disabled="pagination.page === 1 || dataLoading"
                @click="goToPage(pagination.page - 1)"
              >
                上一页
              </button>
              <span>第 {{ pagination.page }} / {{ totalPages }} 页 · 共 {{ pagination.total }} 条</span>
              <button
                class="ghost-btn"
                :disabled="pagination.page >= totalPages || dataLoading"
                @click="goToPage(pagination.page + 1)"
              >
                下一页
              </button>
            </div>
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
import { roleToRoute } from '@/utils/roleRoute'
import { fetchDrugs, fetchTenants } from '@/api/catalog'
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

    const queryType = ref('tenants')
    const queryKeyword = ref('')
    const results = ref([])
    const dataLoading = ref(false)
    const dataError = ref('')
    const pagination = ref({ page: 1, per_page: 10, total: 0 })

    const queryConfigs = {
      drugs: {
        placeholder: '输入通用名、商品名或批准文号',
        fetcher: fetchDrugs,
        columns: [
          { key: 'generic_name', label: '通用名' },
          { key: 'brand_name', label: '商品名' },
          { key: 'dosage_form', label: '剂型' },
          { key: 'specification', label: '规格' },
          { key: 'manufacturer', label: '生产企业' }
        ]
      },
      tenants: {
        placeholder: '输入药店名称、地址或统一社会信用代码',
        fetcher: fetchTenants,
        columns: [
          { key: 'name', label: '药店名称' },
          { key: 'type', label: '类型' },
          { key: 'contact_person', label: '联系人' },
          { key: 'contact_phone', label: '联系电话' },
          { key: 'address', label: '地址' },
          { key: 'is_active', label: '状态' }
        ]
      }
    }

    const activeColumns = computed(() => queryConfigs[queryType.value].columns)
    const queryPlaceholder = computed(() => queryConfigs[queryType.value].placeholder)

    const totalPages = computed(() => {
      const total = pagination.value.total || 0
      const size = pagination.value.per_page || 1
      return Math.max(1, Math.ceil(total / size))
    })

    const fetchCurrentData = async () => {
      const config = queryConfigs[queryType.value]
      if (!config) return
      dataLoading.value = true
      dataError.value = ''
      try {
        const response = await config.fetcher({
          keyword: queryKeyword.value.trim(),
          page: pagination.value.page,
          perPage: pagination.value.per_page
        })
        results.value = response.items || []
        pagination.value = {
          page: response.page ?? pagination.value.page,
          per_page: response.per_page ?? pagination.value.per_page,
          total: typeof response.total === 'number' ? response.total : (response.items || []).length
        }
      } catch (error) {
        dataError.value = error.message || '查询失败，请稍后重试'
        results.value = []
      } finally {
        dataLoading.value = false
      }
    }

    const performQuery = () => {
      pagination.value = { ...pagination.value, page: 1 }
      fetchCurrentData()
    }

    const resetQuery = () => {
      queryKeyword.value = ''
      pagination.value = { ...pagination.value, page: 1, total: 0 }
      fetchCurrentData()
    }

    const goToPage = (page) => {
      const maxPage = totalPages.value
      if (page < 1 || page > maxPage || page === pagination.value.page) return
      pagination.value = { ...pagination.value, page }
      fetchCurrentData()
    }

    const formatCell = (row, key) => {
      const value = row[key]
      if (value === null || value === undefined || value === '') return '—'
      if (typeof value === 'boolean') return value ? '在营' : '停业'
      if (typeof value === 'number') {
        if (key.includes('price')) return `¥${value.toFixed(2)}`
        return value
      }
      return value
    }

    watch(queryType, () => {
      queryKeyword.value = ''
      pagination.value = { ...pagination.value, page: 1, total: 0 }
      fetchCurrentData()
    })

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
      if (currentUser.value.role === 'regulator') return
      router.push('/enterprise-auth')
    }

    const goToEnterpriseReview = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'regulator') return
      router.push('/enterprise-review')
    }

    const goToAdminUsers = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'regulator') return
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

    const viewTenantInventory = (tenantId) => {
      if (!tenantId) return
      router.push({ name: 'tenant-inventory', params: { tenantId } })
    }

    onMounted(() => {
      window.addEventListener('storage', refreshUser)
      fetchCurrentData()
    })
    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
    })

    return {
      goToLogin,
      goToUserHome,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToAdminUsers,
      navigateTo,
      activeNav,
      selectedSupplier,
      selectSupplier,
      within5km,
      currentDate,
      currentUser,
      queryType,
      queryKeyword,
      queryPlaceholder,
      results,
      dataLoading,
      dataError,
      pagination,
      activeColumns,
      totalPages,
      performQuery,
      resetQuery,
      goToPage,
      formatCell,
      viewTenantInventory
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

.data-query-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.tag {
  padding: 4px 12px;
  border-radius: 999px;
  background-color: #e8f0fe;
  color: #1a73e8;
  font-size: 13px;
  height: fit-content;
}

.query-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 15px;
  align-items: flex-end;
}

.query-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 220px;
}

.query-field label {
  font-size: 14px;
  color: #555;
}

.query-field select,
.query-field input {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.query-field select:focus,
.query-field input:focus {
  border-color: #1a73e8;
}

.query-field.flex-1 {
  flex: 1;
}

.flex-1 {
  flex: 1;
}

.query-input-group {
  display: flex;
  gap: 10px;
  align-items: center;
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

.link-btn {
  background: none;
  border: none;
  color: #1a73e8;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.link-btn:hover {
  text-decoration: underline;
}

.hint-text {
  margin-top: 8px;
  color: #6b7280;
  font-size: 12px;
}

.query-results {
  min-height: 180px;
}

.query-feedback {
  text-align: center;
  color: #666;
  padding: 20px 0;
}

.query-feedback.error {
  color: #d93025;
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


