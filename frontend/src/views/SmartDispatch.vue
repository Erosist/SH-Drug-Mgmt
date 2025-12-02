<template>
  <div class="smart-dispatch-container">
    <!-- 顶部导航栏 -->
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
            <div v-if="!isLogistics && !isRegulator" 
              class="nav-item" 
              :class="{ active: activeNav === 'inventory' }"
              @click="navigateTo('inventory')"
            >库存管理</div>
            <div v-if="!isLogistics"
              class="nav-item" 
              :class="{ active: activeNav === 'b2b' }"
              @click="navigateTo('b2b')"
            >B2B供求平台</div>
            <div v-if="isPharmacy"
              class="nav-item" 
              :class="{ active: activeNav === 'nearby' }"
              @click="navigateTo('nearby')"
            >就近推荐</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'circulation' }"
              @click="navigateTo('circulation')"
            >流通监管</div>
            <div v-if="canViewAnalysis"
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

    <!-- 智能调度主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 左侧功能导航 -->
        <aside class="sidebar">
          <div class="section">
            <h3 class="section-title">功能导航</h3>
            <ul class="function-list">
              <li class="function-item">药品定位</li>
              <li class="function-item">药品分布</li>
              <li class="function-item">药品类别</li>
              <li class="function-item">药品库存</li>
              <li class="function-item">药品流通</li>
            </ul>
            <button class="new-task-btn">新建任务</button>
          </div>
        </aside>

        <!-- 右侧主内容 -->
        <div class="main-area">
          <!-- 顶部：搜索条件 + 地图 -->
          <div class="top-row">
            <div class="search-section">
              <h3 class="section-title">药品定位与就近推荐</h3>
              <div class="search-conditions">
                <div class="condition-item">
                  <label>经度</label>
                  <input v-model="lng" type="text" placeholder="例如：121.4737" class="text-input" />
                </div>
                <div class="condition-item">
                  <label>纬度</label>
                  <input v-model="lat" type="text" placeholder="例如：31.2304" class="text-input" />
                </div>
                <div class="condition-item">
                  <label>搜索半径 (km)：<b>{{ radius }}</b></label>
                  <input v-model.number="radius" type="range" min="1" max="50" step="1" />
                  <div class="range-marks">
                    <span>1km</span>
                    <span>10km</span>
                    <span>30km</span>
                    <span>50km</span>
                  </div>
                </div>
                <div class="condition-item">
                  <label>药品类型</label>
                  <div class="checkbox-group">
                    <label><input type="checkbox" value="常用药品" v-model="selectedTypes" /> 常用药品</label>
                    <label><input type="checkbox" value="冷链药品" v-model="selectedTypes" /> 冷链药品</label>
                    <label><input type="checkbox" value="急救药品" v-model="selectedTypes" /> 急救药品</label>
                    <label><input type="checkbox" value="特殊药品" v-model="selectedTypes" /> 特殊药品</label>
                  </div>
                </div>
                <div class="actions-inline">
                  <button class="search-btn" @click="handleSearch">搜索供应商</button>
                </div>
              </div>
            </div>

            <!-- 地图显示区域 -->
            <div class="map-section">
              <h3 class="section-title">药品分布地图</h3>
              <div class="map-container">
                <div class="map-placeholder">地图加载中...</div>
              </div>
            </div>
          </div>

          <!-- 中部：统计信息 -->
          <div class="statistics-section">
            <h3 class="section-title">统计信息</h3>
            <div class="statistics-container">
              <div class="stat-item">
                <div class="stat-title">符合条件的供应商</div>
                <div class="stat-value">{{ filteredSuppliers.length }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-title">总库存量</div>
                <div class="stat-value">{{ totalStock }}件</div>
              </div>
              <div class="stat-item">
                <div class="stat-title">平均距离</div>
                <div class="stat-value">{{ avgDistance }}km</div>
              </div>
            </div>
          </div>

          <!-- 操作区 -->
          <div class="action-section">
            <h3 class="section-title">操作</h3>
            <div class="action-buttons">
              <button class="export-btn" @click="exportData">导出数据</button>
              <button class="refresh-btn" @click="refreshList">刷新列表</button>
            </div>
          </div>

          <!-- 供应商列表 -->
          <div class="supplier-list">
            <h3 class="section-title">供应商列表</h3>
            <table class="supplier-table">
              <thead>
                <tr>
                  <th>供应商名称</th>
                  <th>药品类型</th>
                  <th>库存量</th>
                  <th>距离</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(s, idx) in filteredSuppliers" :key="idx">
                  <td>{{ s.name }}</td>
                  <td>{{ s.type }}</td>
                  <td>{{ s.stock.toLocaleString() }}件</td>
                  <td>{{ s.distance.toFixed(1) }}km</td>
                  <td :class="['status', getStatusClass(s.status)]">{{ s.status }}</td>
                  <td><button class="contact-btn">联系</button></td>
                </tr>
                <tr v-if="filteredSuppliers.length === 0">
                  <td colspan="6" style="text-align:center;color:#999;">暂无满足条件的供应商</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { getCurrentUser } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'
import { getRoleLabel } from '@/utils/roleLabel'

export default {
  name: 'SmartDispatch',
  setup() {
    const router = useRouter()
  const activeNav = ref('service')
  const currentUser = ref(getCurrentUser())
  const isLogistics = computed(() => currentUser.value?.role === 'logistics')
  const isSupplier = computed(() => currentUser.value?.role === 'supplier')
  const isPharmacy = computed(() => currentUser.value?.role === 'pharmacy')
  const isRegulator = computed(() => currentUser.value?.role === 'regulator')
  const isAdmin = computed(() => currentUser.value?.role === 'admin')
  const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
  const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
  const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))
    
    // 位置与筛选
    const lat = ref('')
    const lng = ref('')
    const radius = ref(10)
    const selectedTypes = ref(['常用药品','冷链药品','急救药品','特殊药品'])

    // 模拟供应商数据（真实项目中应来自后端）
    const suppliers = ref([
      { name: '仁和药业', type: '常用药品', stock: 1200, distance: 3.2, status: '充足' },
      { name: '生物制药链中心', type: '冷链药品', stock: 850, distance: 5.7, status: '中等' },
      { name: '急救医疗药库', type: '急救药品', stock: 320, distance: 2.1, status: '充足' },
      { name: '特殊药品供应站', type: '特殊药品', stock: 120, distance: 8.3, status: '紧缺' },
      { name: '华东药品配送中心', type: '常用药品', stock: 640, distance: 11.5, status: '中等' },
      { name: '冷链专线仓', type: '冷链药品', stock: 430, distance: 14.2, status: '紧缺' }
    ])

    // 过滤后的供应商
    const filteredSuppliers = computed(() => {
      return suppliers.value
        .filter(s => selectedTypes.value.includes(s.type))
        .filter(s => s.distance <= radius.value)
        .sort((a,b) => a.distance - b.distance)
    })

    const totalStock = computed(() => {
      return filteredSuppliers.value.reduce((sum, s) => sum + s.stock, 0).toLocaleString()
    })

    const avgDistance = computed(() => {
      if (filteredSuppliers.value.length === 0) return '—'
      const avg = filteredSuppliers.value.reduce((sum, s) => sum + s.distance, 0) / filteredSuppliers.value.length
      return avg.toFixed(1)
    })

    // 当前日期
    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })

    const navigateTo = (page) => {
      activeNav.value = page

      switch(page) {
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

    const goToLogin = () => { router.push('/login') }

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

    const refreshUser = () => { currentUser.value = getCurrentUser() }

    const goToUserHome = () => {
      const u = currentUser.value
      if (!u) return router.push('/login')
      router.push(roleToRoute(u.role))
    }

    const handleSearch = () => {
      // 这里可以接入真实地图/定位与后端查询，目前依赖前端筛选
      // 校验经纬度格式（简单校验）
      const num = (v) => v === '' || !isNaN(parseFloat(v))
      if (!num(lat.value) || !num(lng.value)) {
        console.warn('经纬度格式不正确')
      }
    }

    const getStatusClass = (status) => {
      switch(status) {
        case '充足': return 'status-green'
        case '中等': return 'status-yellow'
        case '紧缺': return 'status-red'
        default: return 'status-green'
      }
    }

    const exportData = () => {
      const rows = [['供应商名称','药品类型','库存量','距离(km)','状态']]
      filteredSuppliers.value.forEach(s => {
        rows.push([s.name, s.type, s.stock, s.distance, s.status])
      })
      const csv = rows.map(r => r.join(',')).join('\n')
      const blob = new Blob(["\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '供应商列表.csv'
      a.click()
      URL.revokeObjectURL(url)
    }

    const refreshList = () => {
      // 简单随机更新库存与距离，模拟刷新
      suppliers.value = suppliers.value.map(s => ({
        ...s,
        stock: Math.max(50, Math.round(s.stock * (0.8 + Math.random()*0.4))),
        distance: Math.max(0.5, +(s.distance * (0.9 + Math.random()*0.2)).toFixed(1))
      }))
    }

    onMounted(() => { window.addEventListener('storage', refreshUser) })
    onBeforeUnmount(() => { window.removeEventListener('storage', refreshUser) })

    return {
      navigateTo,
      activeNav,
      isLogistics,
      isSupplier,
      isPharmacy,
      currentDate,
      goToLogin,
      goToUserHome,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      currentUser,
      userDisplayName,
      userRoleLabel,
      // 搜索交互
      lat,
      lng,
      radius,
      selectedTypes,
      suppliers,
      filteredSuppliers,
      totalStock,
      avgDistance,
      handleSearch,
      getStatusClass,
      exportData,
      refreshList
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

.smart-dispatch-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 - 与Home.vue一致 */
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

/* 主内容区域样式 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 260px 1fr; /* 左侧窄侧边栏和右侧主内容区域 */
  gap: 20px;
  height: 100%;
}

.top-row {
  display: grid;
  grid-template-columns: 360px 1fr; /* 左侧筛选卡片 + 右侧大地图 */
  gap: 20px;
  margin-bottom: 20px;
}

/* 登录按钮样式（与 Home.vue 对齐） */
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

/* 左侧功能导航样式 */
.sidebar {
  align-self: start;
}

.function-list {
  list-style: none;
  margin: 20px 0;
}

.function-item {
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
  cursor: pointer;
}

.function-item:hover {
  color: #1a73e8;
}

.new-task-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.new-task-btn:hover {
  background-color: #0d62d9;
}

/* 搜索条件样式 */
.search-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.search-conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.condition-item {
  flex: 1;
  min-width: 200px;
}

.text-input {
  width: 100%;
  height: 34px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0 10px;
  outline: none;
}

.range-marks {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}

.actions-inline {
  width: 100%;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.search-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #0d62d9;
}

/* 供应商列表样式 */
.supplier-list {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.supplier-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.supplier-table th,
.supplier-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.supplier-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.supplier-table tbody tr:hover {
  background-color: #f5f7fa;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status-green {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-yellow {
  background-color: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.status-red {
  background-color: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.contact-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.contact-btn:hover {
  background-color: #0d62d9;
}

/* 地图显示区域样式 */
.map-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 0;
}

.map-container {
  height: 400px;
  background-color: #f8f9fa;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.map-placeholder {
  font-size: 16px;
  color: #666;
}

/* 统计信息样式 */
.statistics-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin: 20px 0;
}

.statistics-container {
  display: flex;
  gap: 20px;
}

.stat-item { flex: 1; text-align: center; }
.stat-title { font-size: 14px; color: #666; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: bold; color: #1a73e8; }

/* 操作按钮样式 */
.action-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.action-buttons { display: flex; gap: 12px; }
.export-btn, .refresh-btn {
  background-color: #1a73e8;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.export-btn:hover, .refresh-btn:hover { background-color: #0d62d9; }

/* 响应式 */
@media (max-width: 1200px) {
  .top-row { grid-template-columns: 1fr; }
}
</style>
