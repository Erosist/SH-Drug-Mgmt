<template>
  <div class="analysis-container">
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
            <div 
              v-if="isPharmacy"
              class="nav-item" 
              :class="{ active: activeNav === 'nearby' }"
              @click="navigateTo('nearby')"
            >就近推荐</div>
            <div 
              v-if="!isLogistics"
              class="nav-item" 
              :class="{ active: activeNav === 'b2b' }"
              @click="navigateTo('b2b')"
            >B2B供求平台</div>
            <div 
              v-if="isLogistics || isRegulator"
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
            <div 
              v-if="isRegulator"
              class="nav-item" 
              :class="{ active: activeNav === 'compliance' }"
              @click="navigateTo('compliance')"
            >合规分析报告</div>
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

    <div class="main-content">
      <div class="filters-card section">
        <div class="filters-left">
          <div class="filter-item">
            <label>时间范围</label>
            <select v-model="filters.range" @change="handleFiltersChange">
              <option value="7d">近7天</option>
              <option value="30d">近30天</option>
              <option value="90d">近90天</option>
            </select>
          </div>
          <div class="filter-item">
            <label>区域范围</label>
            <select v-model="filters.region" @change="handleFiltersChange">
              <option value="all">全部区域</option>
              <option v-for="region in regionOptions" :key="region" :value="region">
                {{ region }}
              </option>
            </select>
          </div>
        </div>
        <div class="filters-right">
          <div class="refresh-info">
            <span>上次更新：{{ lastUpdatedText }}</span>
            <span class="auto-refresh">自动刷新：5分钟</span>
          </div>
          <button class="refresh-btn" :disabled="loading" @click="refreshDashboard">
            {{ loading ? '刷新中...' : '手动刷新' }}
          </button>
        </div>
      </div>

      <div class="metrics-grid">
        <div class="metric-card primary">
          <div class="metric-title">当前药品总库存量</div>
          <div class="metric-value">{{ formatNumber(metrics.total_inventory) }}</div>
          <div class="metric-subtitle">来自库存中心</div>
        </div>
        <div class="metric-card">
          <div class="metric-title">在途药品数量</div>
          <div class="metric-value">{{ formatNumber(metrics.in_transit) }}</div>
          <div class="metric-trend up">运输中</div>
        </div>
        <div class="metric-card">
          <div class="metric-title">异常上报数量</div>
          <div class="metric-value">{{ formatNumber(metrics.abnormal_reports) }}</div>
          <div class="metric-trend down">需要复核</div>
        </div>
        <div class="metric-card">
          <div class="metric-title">覆盖区域数</div>
          <div class="metric-value">{{ formatNumber(metrics.regions) }}</div>
          <div class="metric-subtitle">统计范围：省级行政区</div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="section chart-card">
          <div class="chart-header">
            <div>
              <h3>药品状态时间序列</h3>
              <p>近 {{ rangeLabel }} 状态变化趋势</p>
            </div>
          </div>
          <div ref="trendChart" class="chart"></div>
        </div>

        <div class="section chart-card">
          <div class="chart-header">
            <div>
              <h3>区域流通量对比</h3>
              <p>按省份统计的流通数量</p>
            </div>
          </div>
          <div ref="regionChart" class="chart"></div>
        </div>

        <div class="section chart-card full-width">
          <div class="chart-header">
            <div>
              <h3>流通热点地图</h3>
              <p>按地区的流通热度分布</p>
            </div>
          </div>
          <div ref="mapChart" class="chart map-chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getCurrentUser, isAuthenticated } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'
import { getRoleLabel } from '@/utils/roleLabel'
import { getDashboard } from '@/api/circulation'

export default {
  name: 'Analysis',
  setup() {
    const router = useRouter()
    const currentUser = ref(getCurrentUser())
    const activeNav = ref('analysis')
    const isLogistics = computed(() => currentUser.value && currentUser.value.role === 'logistics')
    const isSupplier = computed(() => currentUser.value && currentUser.value.role === 'supplier')
    const isPharmacy = computed(() => currentUser.value && currentUser.value.role === 'pharmacy')
    const isRegulator = computed(() => currentUser.value && currentUser.value.role === 'regulator')
    const isAdmin = computed(() => currentUser.value && currentUser.value.role === 'admin')
    const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
    const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
    const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))
    
    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })

    const filters = reactive({
      range: '7d',
      region: 'all'
    })
    const regionOptions = ['北京', '上海', '广东', '浙江', '江苏', '四川', '湖北', '湖南', '山东']

    const metrics = reactive({
      total_inventory: 0,
      in_transit: 0,
      abnormal_reports: 0,
      regions: 0
    })

    const lastUpdated = ref('')
    const loading = ref(false)
    const autoRefreshTimer = ref(null)

    const dashboardData = ref({
      trend: [],
      region_flow: [],
      map: []
    })

    const trendChart = ref(null)
    const regionChart = ref(null)
    const mapChart = ref(null)
    let chinaMapRegistered = false
    let chinaMapData = null
    let trendChartInstance = null
    let regionChartInstance = null
    let mapChartInstance = null

    const rangeLabel = computed(() => {
      switch (filters.range) {
        case '30d':
          return '30天'
        case '90d':
          return '90天'
        default:
          return '7天'
      }
    })

    const lastUpdatedText = computed(() => {
      if (!lastUpdated.value) return '尚未获取数据'
      const date = new Date(lastUpdated.value)
      return date.toLocaleString('zh-CN')
    })

    const formatNumber = (value) => {
      if (value === null || value === undefined) return '--'
      if (value > 10000) {
        return `${(value / 10000).toFixed(1)} 万`
      }
      return value.toLocaleString()
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
        case 'service':
          router.push('/service')
          break
        default:
          router.push('/')
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
      const user = currentUser.value
      if (!user) return router.push('/login')
      router.push(roleToRoute(user.role))
    }

    const refreshUser = () => { currentUser.value = getCurrentUser() }

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

    const handleFiltersChange = () => {
      refreshDashboard()
    }

    const resizeHandler = () => {
      trendChartInstance?.resize()
      regionChartInstance?.resize()
      mapChartInstance?.resize()
    }

    const refreshDashboard = async () => {
      if (!isAuthenticated()) {
        ElMessage.warning('请先登录后查看监管看板')
        return router.push({ name: 'login', query: { redirect: '/analysis' } })
      }
      if (currentUser.value?.role !== 'regulator') {
        ElMessage.error('仅监管用户可以查看监管看板')
        return
      }

      loading.value = true
      try {
        const data = await getDashboard({
          range: filters.range,
          region: filters.region
        })
        dashboardData.value = data
        metrics.total_inventory = data.metrics.total_inventory
        metrics.in_transit = data.metrics.in_transit
        metrics.abnormal_reports = data.metrics.abnormal_reports
        metrics.regions = data.metrics.regions
        lastUpdated.value = data.last_updated

        await nextTick()
        renderTrendChart()
        renderRegionChart()
        renderMapChart()
      } catch (error) {
        console.error('加载看板数据失败:', error)
        ElMessage.error(error.message || '加载看板数据失败')
      } finally {
        loading.value = false
      }
    }

    const disposeCharts = () => {
      if (trendChartInstance) {
        trendChartInstance.dispose()
        trendChartInstance = null
      }
      if (regionChartInstance) {
        regionChartInstance.dispose()
        regionChartInstance = null
      }
      if (mapChartInstance) {
        mapChartInstance.dispose()
        mapChartInstance = null
      }
    }

    const renderTrendChart = () => {
      if (!trendChart.value) return
      if (trendChartInstance) trendChartInstance.dispose()
      trendChartInstance = echarts.init(trendChart.value)

      const trend = dashboardData.value.trend || []
      const dates = trend.map(item => item.date)
      const shipped = trend.map(item => item.shipped)
      const inTransit = trend.map(item => item.in_transit)
      const delivered = trend.map(item => item.delivered)

      trendChartInstance.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['已发货', '运输中', '已送达'] },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value' },
        series: [
          { name: '已发货', type: 'line', smooth: true, data: shipped },
          { name: '运输中', type: 'line', smooth: true, data: inTransit },
          { name: '已送达', type: 'line', smooth: true, data: delivered }
        ]
      })
    }

    const renderRegionChart = () => {
      if (!regionChart.value) return
      if (regionChartInstance) regionChartInstance.dispose()
      regionChartInstance = echarts.init(regionChart.value)

      const regionFlow = (dashboardData.value.region_flow || []).slice(0, 10)
      regionChartInstance.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value' },
        yAxis: {
          type: 'category',
          data: regionFlow.map(item => item.region),
          inverse: true
        },
        series: [
          {
            name: '流通量',
            type: 'bar',
            data: regionFlow.map(item => item.count),
            itemStyle: {
              color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                { offset: 0, color: '#5B8FF9' },
                { offset: 1, color: '#61D9A3' }
              ])
            }
          }
        ]
      })
    }

    const loadChinaMap = async () => {
      if (chinaMapRegistered) return
      if (!chinaMapData) {
        const response = await fetch('/maps/china.json')
        if (!response.ok) {
          throw new Error('加载中国地图数据失败')
        }
        chinaMapData = await response.json()
      }
      echarts.registerMap('china', chinaMapData)
      chinaMapRegistered = true
    }

    const renderMapChart = async () => {
      if (!mapChart.value) return
      if (mapChartInstance) mapChartInstance.dispose()
      mapChartInstance = echarts.init(mapChart.value)

      if (!chinaMapRegistered) {
        try {
          await loadChinaMap()
        } catch (error) {
          console.warn('地图数据加载失败，使用简化版本:', error)
          // 如果地图数据加载失败，可以显示一个提示
          return
        }
      }

      mapChartInstance.setOption({
        tooltip: { trigger: 'item' },
        visualMap: {
          type: 'continuous',
          min: 0,
          max: Math.max(...(dashboardData.value.map || []).map(item => item.value), 10),
          left: 'left',
          bottom: '10%',
          text: ['高', '低'],
          inRange: {
            color: ['#cfe8ff', '#1a73e8']
          }
        },
        series: [{
          name: '流通热度',
          type: 'map',
          map: 'china',
          roam: true,
          label: { show: false },
          data: dashboardData.value.map || []
        }]
      })
    }

    const setupAutoRefresh = () => {
      if (autoRefreshTimer.value) clearInterval(autoRefreshTimer.value)
      autoRefreshTimer.value = setInterval(() => {
        refreshDashboard()
      }, 5 * 60 * 1000)
    }

    onMounted(() => {
      window.addEventListener('storage', refreshUser)
      window.addEventListener('resize', resizeHandler)
      refreshDashboard()
      setupAutoRefresh()
    })

    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
      window.removeEventListener('resize', resizeHandler)
      if (autoRefreshTimer.value) clearInterval(autoRefreshTimer.value)
      disposeCharts()
    })

    return {
      navItems: [
        { key: 'home', label: '首页' },
        { key: 'inventory', label: '库存管理' },
        { key: 'b2b', label: 'B2B供求平台' },
        { key: 'circulation', label: '流通监管' },
        { key: 'analysis', label: '监管分析' },
        { key: 'service', label: '智能调度' }
      ],
      activeNav,
      currentDate,
      isLogistics,
      isSupplier,
      isPharmacy,
      isRegulator,
      isAdmin,
      canViewAnalysis,
      currentUser,
      filters,
      regionOptions,
      metrics,
      lastUpdatedText,
      loading,
      trendChart,
      regionChart,
      mapChart,
      rangeLabel,
      navigateTo,
      goToLogin,
      goToChangePassword,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      goToUserHome,
      handleFiltersChange,
      refreshDashboard,
      formatNumber,
      userDisplayName,
      userRoleLabel
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

.analysis-container {
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

.user-info {
  display: flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 999px;
  background-color: #f0f5ff;
  color: #1a73e8;
  font-size: 14px;
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
  padding: 24px;
  flex: 1;
}

.section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.filters-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters-left {
  display: flex;
  gap: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-item label {
  font-size: 14px;
  color: #666;
}

.filter-item select {
  width: 160px;
  padding: 8px;
  border: 1px solid #dfe3e8;
  border-radius: 6px;
}

.filters-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.refresh-info {
  display: flex;
  flex-direction: column;
  font-size: 13px;
  color: #666;
}

.auto-refresh {
  color: #1a73e8;
}

.refresh-btn {
  padding: 10px 20px;
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.metric-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03);
}

.metric-card.primary {
  background: linear-gradient(135deg, #1a73e8 0%, #4facfe 100%);
  color: #fff;
}

.metric-title {
  font-size: 14px;
  color: inherit;
  opacity: 0.8;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  margin: 12px 0;
}

.metric-subtitle {
  font-size: 13px;
  opacity: 0.7;
}

.metric-trend {
  font-size: 13px;
  font-weight: 600;
}

.metric-trend.up {
  color: #16a34a;
}

.metric-trend.down {
  color: #dc2626;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.chart-card h3 {
  font-size: 18px;
  margin-bottom: 4px;
  color: #1f2937;
}

.chart-header p {
  color: #6b7280;
  font-size: 13px;
}

.chart {
  width: 100%;
  height: 320px;
}

.map-chart {
  height: 420px;
}

.chart-card.full-width {
  grid-column: 1 / -1;
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


/* 区块样式 */
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

/* 筛选条件样式 */
.filter-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.checkbox-item input {
  margin: 0;
}

/* 百分比条样式 */
.percentage-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.percentage-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.percentage-label {
  font-size: 14px;
  color: #666;
  width: 80px;
}

.percentage-bar {
  flex-grow: 1;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.percentage-fill {
  height: 100%;
  background-color: #1a73e8;
  border-radius: 4px;
}

.percentage-value {
  font-size: 14px;
  color: #333;
  width: 30px;
  text-align: right;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.reset-btn {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #495057;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.reset-btn:hover {
  background-color: #e9ecef;
}

/* 趋势分析图表 */
.trend-chart {
  margin-bottom: 15px;
}

.chart-placeholder {
  height: 200px;
  background-color: #f8f9fa;
  border-radius: 4px;
  position: relative;
  display: flex;
  align-items: flex-end;
  padding: 10px;
}

.chart-lines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding: 0 20px;
}

.chart-line {
  width: 2px;
  background-color: #e8e8e8;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  width: 100%;
  height: 100%;
  padding: 0 20px;
}

.chart-bar {
  width: 30px;
  background-color: #1a73e8;
  border-radius: 2px 2px 0 0;
  margin: 0 10px;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
  font-size: 12px;
  color: #666;
}

.coverage-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

/* 区域对比图表 */
.comparison-chart {
  margin-bottom: 15px;
}

.chart-bars-horizontal {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.city-name {
  font-size: 14px;
  color: #333;
  width: 50px;
}

.bar-container {
  flex-grow: 1;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background-color: #1a73e8;
  border-radius: 10px;
}

.bar-value {
  font-size: 14px;
  color: #333;
  width: 30px;
  text-align: right;
}

.chart-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

/* 数据表格样式 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-container {
  overflow-x: auto;
}

.analysis-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.analysis-table th,
.analysis-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.analysis-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.analysis-table tbody tr:hover {
  background-color: #f5f7fa;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status.通过 {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status.违规 {
  background-color: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.status.未通过 {
  background-color: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .data-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .analysis-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 992px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .nav-menu {
    gap: 15px;
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
  
  .data-overview {
    grid-template-columns: 1fr;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
