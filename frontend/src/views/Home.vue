<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="header-content">
        <div class="platform-info">
          <h1 class="platform-title">上海药品监管信息平台</h1>
          <div class="current-date">{{ currentDate }}</div>
        </div>
        
        <div class="nav-section">
          <div class="nav-menu" v-if="!isAdmin">
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
            <div v-if="isLogistics"
              class="nav-item"
              :class="{ active: activeNav === 'orders' }"
              @click="navigateTo('logistics-orders')"
            >订单查看</div>
          </div>
          <div v-else class="nav-menu disabled-nav">
            <span class="nav-disabled-text">管理员账号无法访问业务功能</span>
          </div>
          
          <div class="user-actions">
            <div v-if="currentUser" class="user-info">
              <span class="user-name">{{ userDisplayName }}</span>
              <span class="user-role">{{ userRoleLabel }}</span>
            </div>
            <button
              v-if="currentUser"
              class="admin-btn"
              @click="goToChangePassword"
            >修改密码</button>
            <button v-if="!currentUser || currentUser.role==='unauth'" class="auth-btn" @click="goToEnterpriseAuth">企业认证</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToEnterpriseReview">认证审核</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToSystemStatus">系统状态</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToAdminUsers">用户管理</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToAuditLogs">审计日志</button>
            <button v-if="!currentUser" class="login-btn" @click="goToLogin">登录</button>
            <button v-else class="login-btn" @click="handleLogout">退出登录</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 左侧主要内容 -->
        <div class="left-content">
          <!-- 核心功能服务 - 一行三列 -->
          <div class="section core-functions">
            <h2 class="section-title">核心功能服务</h2>
            <div class="function-cards three-columns">
              <!-- 药品信息查询 -->
              <div class="function-card drug-search-card">
                <h3>药品信息查询</h3>
                <div class="drug-search-box">
                  <input type="text" v-model="drugSearchKeyword" placeholder="输入药品名称或厂家" class="drug-search-input" @keyup.enter="handleDrugSearch" />
                  <button class="drug-search-btn" @click="handleDrugSearch" :disabled="drugSearching">{{ drugSearching ? '搜索中...' : '搜索' }}</button>
                </div>
                <div class="drug-search-results">
                  <div v-if="drugSearchResults.length > 0" class="drug-list">
                    <div v-for="drug in drugSearchResults" :key="drug.id" class="drug-item" @click="showDrugDetail(drug)">
                      <div class="drug-name">{{ drug.generic_name }}</div>
                      <div class="drug-brand">{{ drug.brand_name }}</div>
                    </div>
                  </div>
                  <div v-else-if="drugSearched && !drugSearching" class="no-drug-result">未找到相关药品</div>
                  <div v-else class="drug-search-hint">支持按药品名称、厂家搜索</div>
                </div>
              </div>
              
              <!-- 附近药房定位 -->
              <div class="function-card nearby-pharmacy-card">
                <h3>附近药房定位</h3>
                <p>基于地理位置查找附近药房，实时获取库存信息</p>
                <div class="mini-map-container">
                  <div id="home-mini-map" class="mini-map"></div>
                  <div v-if="nearbyLoading" class="map-loading">
                    <span>加载中...</span>
                  </div>
                </div>
                <div class="nearby-pharmacy-list">
                  <div v-if="nearbyPharmacies.length > 0">
                    <div v-for="pharmacy in nearbyPharmacies" :key="pharmacy.id" class="pharmacy-item">
                      <div class="pharmacy-name">{{ pharmacy.name }}</div>
                      <div class="pharmacy-distance">{{ pharmacy.distance_text || '计算中...' }}</div>
                    </div>
                  </div>
                  <div v-else-if="!nearbyLoading" class="no-pharmacy">
                    <span v-if="!currentUser">请登录查看附近药房</span>
                    <span v-else>暂无附近药房数据</span>
                  </div>
                </div>
                <button class="action-btn" @click="goToNearbySuppliers">查看更多</button>
              </div>
              
              <!-- 健康资讯中心 -->
              <div class="function-card health-news-card">
                <h3>健康资讯中心</h3>
                <p>获取最新健康资讯、疾病预防知识和健康生活方式建议</p>
                <div class="health-news-list">
                  <div v-for="news in healthNewsList" :key="news.id" class="news-item">
                    <span class="news-title">{{ news.title }}</span>
                    <span class="news-date">{{ formatNewsDate(news.publish_date) }}</span>
                  </div>
                  <div v-if="healthNewsList.length === 0" class="news-item">
                    <span class="news-title" style="color: #999;">暂无资讯</span>
                  </div>
                </div>
                <button class="action-btn" @click="loadMoreNews">更多资讯</button>
              </div>
            </div>
          </div>
          
          <!-- 就近供应商推荐（已移除） -->
          
          <!-- 重要提醒与公告 -->
          <div class="section notices">
            <h2 class="section-title">重要提醒与公告</h2>
            <div class="notice-content">
              <div v-if="urgentNotice" class="urgent-notice">
                <div class="notice-title">{{ urgentNotice.title }}</div>
                <div class="notice-desc">{{ urgentNotice.content }}</div>
              </div>
              <div v-else class="urgent-notice">
                <div class="notice-title" style="color: #999;">暂无紧急通知</div>
              </div>
              
              <div class="report-input">
                <input type="text" v-model="reportText" placeholder="本市2024年度报告请输入" class="report-field">
                <button class="submit-btn" @click="submitReport">提交</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧特色服务 -->
        <div class="right-content">
          <div class="section feature-services">
            <h2 class="section-title">特色服务</h2>
            <div class="feature-list">
              <div class="feature-item reminder-card">
                <div class="feature-icon">⏰</div>
                <div class="feature-content">
                  <h3>个性化用药提醒</h3>
                  <div class="today-reminders" v-if="currentUser">
                    <div v-if="todayRemindersLoading" class="reminder-loading">加载中...</div>
                    <div v-else-if="todayReminders.length > 0" class="reminder-preview">
                      <div class="reminder-count">今日待提醒: <strong>{{ todayReminders.length }}</strong> 条</div>
                      <div v-for="item in todayReminders.slice(0, 2)" :key="item.id + item.remind_time" class="reminder-item">
                        <span class="time">{{ item.remind_time }}</span>
                        <span class="drug">{{ item.drug_name }}</span>
                      </div>
                    </div>
                    <div v-else class="no-reminders">暂无今日提醒</div>
                  </div>
                  <div v-else class="login-hint">登录后可创建用药提醒</div>
                  <button class="feature-btn" @click="goToReminders">创建提醒</button>
                </div>
              </div>
              
              <div class="feature-item price-compare-card">
                <div class="feature-icon">💰</div>
                <div class="feature-content">
                  <h3>药品价格对比</h3>
                  <div class="price-search-box">
                    <input type="text" v-model="priceSearchKeyword" placeholder="输入药品名称" class="price-search-input" @keyup.enter="handlePriceCompare" />
                    <button class="price-search-btn" @click="handlePriceCompare" :disabled="priceSearching">{{ priceSearching ? '查询中...' : '比价' }}</button>
                  </div>
                  <div class="price-sort-toggle" v-if="priceResults.length > 0">
                    <span @click="togglePriceSort" class="sort-link">{{ priceSort === 'price_asc' ? '价格 ↑' : '价格 ↓' }}</span>
                  </div>
                  <div class="price-results">
                    <div v-if="priceResults.length > 0" class="price-list">
                      <div v-for="(item, index) in priceResults" :key="item.supply_id" class="price-item" :class="{ 'lowest-price': index === 0 && priceSort === 'price_asc' }">
                        <div class="price-supplier">{{ item.supplier_name }}</div>
                        <div class="price-value">¥{{ item.unit_price.toFixed(2) }}</div>
                        <div class="price-stock">库存: {{ item.available_quantity }}</div>
                      </div>
                    </div>
                    <div v-else-if="priceSearched && !priceSearching" class="no-price-result">未找到价格信息</div>
                  </div>
                </div>
              </div>
              
              <div class="feature-item">
                <div class="feature-icon">💬</div>
                <div class="feature-content">
                  <h3>药物在线咨询</h3>
                  <p>专业的药7x24小时在线，随时解答关于用药安全的疑问</p>
                  <button class="feature-btn">咨询指南</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 药品详情对话框 -->
  <el-dialog v-model="drugDetailVisible" :title="currentDrug?.generic_name || '药品详情'" width="500px">
    <div v-if="drugDetailLoading" class="drug-detail-loading">加载中...</div>
    <div v-else-if="currentDrugDetail" class="drug-detail-content">
      <div class="detail-row"><span class="label">通用名：</span><span>{{ currentDrugDetail.generic_name }}</span></div>
      <div class="detail-row"><span class="label">商品名：</span><span>{{ currentDrugDetail.brand_name || '-' }}</span></div>
      <div class="detail-row"><span class="label">制造商：</span><span>{{ currentDrugDetail.manufacturer || '-' }}</span></div>
      <div class="detail-row"><span class="label">剖型：</span><span>{{ currentDrugDetail.dosage_form || '-' }}</span></div>
      <div class="detail-row"><span class="label">规格：</span><span>{{ currentDrugDetail.specification || '-' }}</span></div>
      <div class="detail-row"><span class="label">批准文号：</span><span>{{ currentDrugDetail.approval_number || '-' }}</span></div>
      <div class="detail-row"><span class="label">分类：</span><span>{{ currentDrugDetail.category || '-' }}</span></div>
      <div class="detail-row"><span class="label">OTC类型：</span><span>{{ currentDrugDetail.otc_type || '-' }}</span></div>
      <div class="detail-row" v-if="currentDrugDetail.description"><span class="label">说明：</span><span>{{ currentDrugDetail.description }}</span></div>
    </div>
    <template #footer>
      <el-button @click="drugDetailVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script>
import { useRouter, useRoute } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { getCurrentUser, clearAuth } from '@/utils/authSession'
import { getRoleLabel } from '@/utils/roleLabel'
import { ElMessage, ElMessageBox } from 'element-plus'
import { homeApi } from '@/api/home'
import { nearbyApi } from '@/api/nearby'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const route = useRoute()

    const mapRouteToNav = (name) => {
      if (!name) return 'home'
      if (name === 'home') return 'home'
      if (name === 'inventory' || name === 'tenant-inventory') return 'inventory'
      if (name === 'nearby-suppliers') return 'nearby'
      if (name === 'b2b') return 'b2b'
      if (name === 'circulation') return 'circulation'
      if (name === 'analysis') return 'analysis'
      if (name === 'service') return 'service'
      if (name === 'logistics-orders') return 'orders'
      return 'home'
    }

    const activeNav = ref(mapRouteToNav(route.name))
    watch(() => route.name, (n) => { activeNav.value = mapRouteToNav(n) }, { immediate: true })
    const currentUser = ref(getCurrentUser())
    const isLogistics = computed(() => currentUser.value && currentUser.value.role === 'logistics')
    const isSupplier = computed(() => currentUser.value && currentUser.value.role === 'supplier')
    const isPharmacy = computed(() => currentUser.value && currentUser.value.role === 'pharmacy')
    const isRegulator = computed(() => currentUser.value && currentUser.value.role === 'regulator')
    const isAdmin = computed(() => currentUser.value && currentUser.value.role === 'admin')
    const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
    const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
    const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))

    // 主页数据
    const platformStats = ref({})
    const healthNewsList = ref([])
    const urgentNotice = ref(null)
    const userStats = ref({})
    const reportText = ref('')

    // 附近药房数据
    const nearbyPharmacies = ref([])
    const nearbyLoading = ref(false)
    let miniMap = null

    // 药品搜索数据
    const drugSearchKeyword = ref('')
    const drugSearchResults = ref([])
    const drugSearching = ref(false)
    const drugSearched = ref(false)
    const drugDetailVisible = ref(false)
    const drugDetailLoading = ref(false)
    const currentDrug = ref(null)
    const currentDrugDetail = ref(null)

    // 药品价格对比数据
    const priceSearchKeyword = ref('')
    const priceResults = ref([])
    const priceSearching = ref(false)
    const priceSearched = ref(false)
    const priceSort = ref('price_asc')

    // 今日用药提醒数据
    const todayReminders = ref([])
    const todayRemindersLoading = ref(false)
    const isNotificationSupported = ref('Notification' in window)

    // 动态日期
    const currentDate = computed(() => {
      const now = new Date()
      const y = now.getFullYear()
      const m = now.getMonth() + 1
      const d = now.getDate()
      return `${y}年${m}月${d}日`
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
      router.push({ name: 'admin-users' })
    }

    const goToAuditLogs = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push({ name: 'admin-audit-logs' })
    }

    const refreshUser = () => {
      currentUser.value = getCurrentUser()
    }

    const handleLogout = () => {
      clearAuth()
      currentUser.value = null
      router.push('/login')
    }
    
    const navigateTo = (page) => {
      // rely on route watcher to update activeNav after navigation/possible redirect
      switch(page) {
        case 'home':
          router.push('/'); break
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
          router.push('/inventory'); break
        case 'nearby':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/nearby-suppliers' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'nearby' } })
            break
          }
          router.push('/nearby-suppliers'); break
        case 'b2b':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/b2b' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'b2b' } })
            break
          }
          router.push('/b2b'); break
        case 'circulation':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/circulation' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'circulation' } })
            break
          }
          router.push('/circulation'); break
        case 'analysis':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/analysis' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'analysis' } })
            break
          }
          router.push('/analysis'); break
        case 'service':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/service' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'service' } })
            break
          }
          router.push('/service'); break
        case 'logistics-orders':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/logistics-orders' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'orders' } })
            break
          }
          router.push('/logistics-orders'); break
        case 'compliance':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/compliance-report' } })
            break
          }
          if (currentUser.value.role !== 'regulator') {
            // 非监管用户无权访问，统一回首页
            router.push('/')
            break
          }
          router.push({ name: 'compliance-report' }); break
        default:
          router.push('/');
      }
    }

    // 加载平台统计数据
    const loadPlatformStats = async () => {
      try {
        const response = await homeApi.getPlatformStats()
        if (response.data?.data) {
          platformStats.value = response.data.data
        }
      } catch (error) {
        console.error('加载平台统计失败:', error)
      }
    }

    // 加载健康资讯
    const loadHealthNews = async () => {
      try {
        const response = await homeApi.getHealthNews({ limit: 3 })
        if (response.data?.data) {
          healthNewsList.value = response.data.data
        }
      } catch (error) {
        console.error('加载健康资讯失败:', error)
      }
    }

    // 加载紧急通知
    const loadUrgentNotices = async () => {
      try {
        const response = await homeApi.getUrgentNotices({ limit: 1 })
        if (response.data?.data && response.data.data.length > 0) {
          urgentNotice.value = response.data.data[0]
        }
      } catch (error) {
        console.error('加载紧急通知失败:', error)
      }
    }

    // 加载用户统计数据
    const loadUserStats = async () => {
      if (!currentUser.value) return
      try {
        const response = await homeApi.getUserStats()
        if (response.data?.data) {
          userStats.value = response.data.data
        }
      } catch (error) {
        console.error('加载用户统计失败:', error)
      }
    }

    // 格式化新闻日期
    const formatNewsDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const month = date.getMonth() + 1
      const day = date.getDate()
      return `${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
    }

    // 加载更多资讯
    const loadMoreNews = () => {
      router.push({ name: 'health-news' })
    }

    // 提交报告
    const submitReport = () => {
      if (!reportText.value.trim()) {
        ElMessage.warning('请输入报告内容')
        return
      }
      ElMessage.success('报告提交成功')
      reportText.value = ''
    }

    // 跳转到就近推荐页面
    const goToNearbySuppliers = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/nearby-suppliers' } })
        return
      }
      router.push('/nearby-suppliers')
    }

    // 初始化迷你地图
    const initMiniMap = async () => {
      await nextTick()
      const container = document.getElementById('home-mini-map')
      if (!container || !window.AMap) {
        console.warn('地图容器或AMap未加载')
        return
      }

      try {
        miniMap = new AMap.Map('home-mini-map', {
          zoom: 12,
          center: [121.4737, 31.2304], // 默认上海中心
          viewMode: '2D',
          dragEnable: false,
          zoomEnable: false,
          doubleClickZoom: false
        })
      } catch (error) {
        console.error('初始化迷你地图失败:', error)
      }
    }

    // 加载附近药房
    const loadNearbyPharmacies = async () => {
      if (!currentUser.value) return
      
      nearbyLoading.value = true
      try {
        // 获取所有供应商（这里简化处理，取前3个）
        const response = await nearbyApi.getAllSuppliers()
        if (response.data?.success && response.data.suppliers) {
          const suppliers = response.data.suppliers.slice(0, 3)
          
          // 计算与默认中心点的距离
          const centerLng = 121.4737
          const centerLat = 31.2304
          
          nearbyPharmacies.value = suppliers.map(s => ({
            ...s,
            distance_text: formatDistance(calculateHaversine(centerLng, centerLat, s.longitude, s.latitude))
          }))

          // 在地图上添加标记
          if (miniMap && suppliers.length > 0) {
            suppliers.forEach(supplier => {
              if (supplier.longitude && supplier.latitude) {
                new AMap.Marker({
                  position: [supplier.longitude, supplier.latitude],
                  map: miniMap,
                  title: supplier.name
                })
              }
            })
            // 调整视图到第一个供应商
            if (suppliers[0]?.longitude && suppliers[0]?.latitude) {
              miniMap.setCenter([suppliers[0].longitude, suppliers[0].latitude])
            }
          }
        }
      } catch (error) {
        console.error('加载附近药房失败:', error)
      } finally {
        nearbyLoading.value = false
      }
    }

    // Haversine公式计算距离（米）
    const calculateHaversine = (lng1, lat1, lng2, lat2) => {
      const R = 6371000
      const toRad = (deg) => deg * Math.PI / 180
      const dLat = toRad(lat2 - lat1)
      const dLng = toRad(lng2 - lng1)
      const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
                Math.sin(dLng/2) * Math.sin(dLng/2)
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
      return R * c
    }

    // 格式化距离
    const formatDistance = (meters) => {
      if (meters < 1000) return `${Math.round(meters)}m`
      return `${(meters / 1000).toFixed(1)}km`
    }

    // 药品搜索
    const handleDrugSearch = async () => {
      const keyword = drugSearchKeyword.value.trim()
      if (!keyword) {
        ElMessage.warning('请输入药品名称或厂家')
        return
      }
      drugSearching.value = true
      drugSearched.value = false
      try {
        const response = await homeApi.searchDrugs(keyword)
        if (response.data?.success) {
          drugSearchResults.value = response.data.items || []
        } else {
          drugSearchResults.value = []
        }
      } catch (error) {
        console.error('药品搜索失败:', error)
        drugSearchResults.value = []
        ElMessage.error('搜索失败，请重试')
      } finally {
        drugSearching.value = false
        drugSearched.value = true
      }
    }

    // 显示药品详情
    const showDrugDetail = async (drug) => {
      currentDrug.value = drug
      drugDetailVisible.value = true
      drugDetailLoading.value = true
      try {
        const response = await homeApi.getDrugDetail(drug.id)
        if (response.data?.success) {
          currentDrugDetail.value = response.data.data
        } else {
          currentDrugDetail.value = drug
        }
      } catch (error) {
        console.error('获取药品详情失败:', error)
        currentDrugDetail.value = drug
      } finally {
        drugDetailLoading.value = false
      }
    }

    // 药品价格对比
    const handlePriceCompare = async () => {
      const keyword = priceSearchKeyword.value.trim()
      if (!keyword) {
        ElMessage.warning('请输入药品名称')
        return
      }
      priceSearching.value = true
      priceSearched.value = false
      try {
        const response = await homeApi.compareDrugPrices(keyword, priceSort.value)
        if (response.data?.success) {
          priceResults.value = response.data.items || []
        } else {
          priceResults.value = []
        }
      } catch (error) {
        console.error('价格查询失败:', error)
        priceResults.value = []
        ElMessage.error('查询失败，请重试')
      } finally {
        priceSearching.value = false
        priceSearched.value = true
      }
    }

    // 切换价格排序
    const togglePriceSort = () => {
      priceSort.value = priceSort.value === 'price_asc' ? 'price_desc' : 'price_asc'
      if (priceSearchKeyword.value.trim()) {
        handlePriceCompare()
      }
    }

    // 加载今日用药提醒
    const loadTodayReminders = async () => {
      if (!currentUser.value) return
      todayRemindersLoading.value = true
      try {
        const response = await homeApi.getTodayReminders()
        if (response.data?.success) {
          todayReminders.value = response.data.items || []
        }
      } catch (error) {
        console.error('加载今日提醒失败:', error)
      } finally {
        todayRemindersLoading.value = false
      }
    }

    // 跳转到用药提醒页面
    const goToReminders = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/medication-reminders' } })
        return
      }
      router.push({ name: 'medication-reminders' })
    }

    onMounted(() => {
      window.addEventListener('storage', refreshUser)
      // 加载主页数据
      loadPlatformStats()
      loadHealthNews()
      loadUrgentNotices()
      loadUserStats()
      // 初始化迷你地图并加载附近药房
      initMiniMap()
      loadNearbyPharmacies()
      // 加载今日用药提醒
      loadTodayReminders()
    })
    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
      // 清理地图实例
      if (miniMap) {
        miniMap.destroy()
        miniMap = null
      }
    })

    return {
      goToLogin,
      goToChangePassword,
      handleLogout,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      goToAuditLogs,
      navigateTo,
      activeNav,
      currentUser,
      isLogistics,
      isSupplier,
      isPharmacy,
      isRegulator,
      isAdmin,
      canViewAnalysis,
      userDisplayName,
      userRoleLabel,
      currentDate,
      // 主页数据
      platformStats,
      healthNewsList,
      urgentNotice,
      userStats,
      reportText,
      // 附近药房
      nearbyPharmacies,
      nearbyLoading,
      goToNearbySuppliers,
      // 药品搜索
      drugSearchKeyword,
      drugSearchResults,
      drugSearching,
      drugSearched,
      drugDetailVisible,
      drugDetailLoading,
      currentDrug,
      currentDrugDetail,
      handleDrugSearch,
      showDrugDetail,
      // 药品价格对比
      priceSearchKeyword,
      priceResults,
      priceSearching,
      priceSearched,
      priceSort,
      handlePriceCompare,
      togglePriceSort,
      // 用药提醒
      todayReminders,
      todayRemindersLoading,
      goToReminders,
      // 主页方法
      formatNewsDate,
      loadMoreNews,
      submitReport
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

.home-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 */
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

.nav-menu.disabled-nav {
  flex: 1;
  align-items: center;
  gap: 0;
  color: #999;
  font-size: 14px;
}

.nav-disabled-text {
  color: #999;
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

/* 核心功能服务样式 - 三列布局 */
.function-cards.three-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.function-card {
  display: flex;
  flex-direction: column;
  height: 320px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.function-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.function-card h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.function-card p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 15px;
  flex-grow: 1;
}

.action-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  align-self: flex-start;
  transition: background-color 0.3s;
  margin-top: auto;
}

.action-btn:hover {
  background-color: #0d62d9;
}

.map-container {
  height: 120px;
  background-color: #f0f2f5;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px 0;
}

.map-placeholder {
  color: #999;
}

.pharmacy-info {
  font-weight: bold;
  text-align: center;
  color: #333;
  margin-top: 10px;
}

/* 附近药房卡片样式 */
.nearby-pharmacy-card {
  background-color: #f8fafc;
}

.nearby-pharmacy-card p {
  flex-grow: 0;
  margin-bottom: 10px;
}

.mini-map-container {
  position: relative;
  height: 100px;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 10px;
}

.mini-map {
  width: 100%;
  height: 100%;
  background-color: #e8f4f8;
}

.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 13px;
}

.nearby-pharmacy-list {
  flex: 1;
  min-height: 80px;
  overflow-y: auto;
}

.pharmacy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #eee;
}

.pharmacy-item:last-child {
  border-bottom: none;
}

.pharmacy-name {
  font-size: 13px;
  color: #333;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 10px;
}

.pharmacy-distance {
  font-size: 12px;
  color: #1a73e8;
  background-color: #e6f0ff;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
}

.no-pharmacy {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 13px;
}

/* 健康资讯中心样式 */
.health-news-card {
  background-color: #f8fafc;
}

.health-news-list {
  margin: 15px 0;
}

.news-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.news-item:last-child {
  border-bottom: none;
}

.news-title {
  color: #333;
  font-size: 14px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.news-date {
  color: #999;
  font-size: 12px;
  margin-left: 10px;
}

/* 重要提醒与公告样式 */
.urgent-notice {
  margin-bottom: 20px;
}

.notice-title {
  font-weight: bold;
  color: #e74c3c;
  margin-bottom: 8px;
}

.notice-desc {
  color: #666;
  line-height: 1.5;
}

.report-input {
  display: flex;
  margin-top: 15px;
}

.report-field {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  outline: none;
}

.report-field:focus {
  border-color: #1a73e8;
}

.submit-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #0d62d9;
}

/* 特色服务样式 */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  gap: 15px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.feature-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.feature-icon {
  width: 40px;
  height: 40px;
  background-color: #f0f9ff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  color: #1a73e8;
  flex-shrink: 0;
}

.feature-content {
  flex-grow: 1;
}

.feature-content h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: #333;
}

.feature-content p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 10px;
  font-size: 14px;
}

.feature-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.feature-btn:hover {
  background-color: #0d62d9;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .function-cards.three-columns {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 就近供应商推荐样式 */
.nearby-suppliers {
  margin-top: 20px;
}

.nearby-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.nearby-intro {
  display: flex;
  gap: 15px;
  align-items: center;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #1a73e8;
}

.intro-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.intro-text h3 {
  font-size: 18px;
  color: #1a73e8;
  margin-bottom: 8px;
  font-weight: 600;
}

.intro-text p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.nearby-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.stat-item {
  background-color: #f8fafc;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.1);
  border-color: #1a73e8;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #1a73e8;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.nearby-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.primary-action-btn {
  background: linear-gradient(135deg, #1a73e8 0%, #0d62d9 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
}

.primary-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.4);
}

.primary-action-btn:active {
  transform: translateY(0);
}

.secondary-action-btn {
  background-color: white;
  color: #1a73e8;
  border: 2px solid #1a73e8;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.secondary-action-btn:hover {
  background-color: #f0f9ff;
  transform: translateY(-2px);
}

.secondary-action-btn:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 18px;
}

.location-preview {
  background-color: #f8fafc;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.location-label {
  color: #666;
  font-weight: 600;
}

.location-name {
  color: #333;
  font-weight: bold;
}

.location-coords {
  color: #999;
  font-size: 12px;
  font-family: monospace;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .function-cards.three-columns {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .nearby-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 992px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .function-cards.three-columns {
    grid-template-columns: 1fr;
  }
  
  .nav-menu {
    gap: 15px;
  }
  
  .nearby-stats {
    grid-template-columns: 1fr;
  }
  
  .nearby-actions {
    flex-direction: column;
  }
  
  .primary-action-btn,
  .secondary-action-btn {
    width: 100%;
    justify-content: center;
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

/* 药品搜索样式 */
.drug-search-card .drug-search-box {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.drug-search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.drug-search-btn {
  padding: 8px 16px;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.drug-search-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.drug-search-results {
  max-height: 200px;
  overflow-y: auto;
}

.drug-list .drug-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.drug-list .drug-item:hover {
  background: #f5f5f5;
}

.drug-name {
  font-weight: 500;
  color: #333;
}

.drug-brand {
  color: #999;
  font-size: 12px;
}

.no-drug-result,
.drug-search-hint {
  padding: 12px;
  text-align: center;
  color: #999;
}

/* 药品详情弹窗样式 */
.drug-detail-loading {
  padding: 20px;
  text-align: center;
  color: #999;
}

.drug-detail-content .detail-row {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.drug-detail-content .detail-row .label {
  width: 90px;
  color: #666;
  flex-shrink: 0;
}

/* 价格对比样式 */
.price-compare-card .price-search-box {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.price-search-input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.price-search-btn {
  padding: 6px 12px;
  background: #e67e22;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.price-search-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.price-sort-toggle {
  margin-bottom: 8px;
}

.sort-link {
  color: #3498db;
  cursor: pointer;
  font-size: 12px;
}

.price-results {
  max-height: 180px;
  overflow-y: auto;
}

.price-list .price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.price-item.lowest-price {
  background: #e8f8f0;
  border-left: 3px solid #27ae60;
}

.price-supplier {
  flex: 1;
  font-size: 13px;
}

.price-value {
  color: #e74c3c;
  font-weight: bold;
  margin: 0 12px;
}

.price-stock {
  color: #999;
  font-size: 12px;
}

.no-price-result {
  padding: 12px;
  text-align: center;
  color: #999;
}

/* 用药提醒卡片样式 */
.reminder-card .today-reminders {
  margin: 10px 0;
  min-height: 60px;
}

.reminder-loading {
  color: #999;
  font-size: 13px;
}

.reminder-preview {
  background: #f0f7ff;
  border-radius: 6px;
  padding: 10px;
}

.reminder-count {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.reminder-count strong {
  color: #1a73e8;
  font-size: 16px;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 0;
  font-size: 13px;
}

.reminder-item .time {
  background: #1a73e8;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.reminder-item .drug {
  color: #333;
}

.no-reminders {
  color: #999;
  font-size: 13px;
}

.login-hint {
  color: #999;
  font-size: 13px;
  margin: 10px 0;
}
</style>
