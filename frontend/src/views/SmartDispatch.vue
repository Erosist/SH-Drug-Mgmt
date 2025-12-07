<template>
  <div class="smart-dispatch-container">
    <!-- header reuse (keeps style consistent) -->
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
            <div v-if="isLogistics"
              class="nav-item"
              :class="{ active: activeNav === 'orders' }"
              @click="navigateTo('logistics-orders')"
            >订单查看</div>
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
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToAuditLogs">审计日志</button>
            <button v-if="!currentUser" class="login-btn" @click="goToLogin">登录</button>
            <button v-else class="login-btn" @click="goToUserHome">我的主页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- main: left controls, right map -->
    <div class="main-content">
      <!-- 消息提示 -->
      <div v-if="successMessage" class="message success-message">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="message error-message">
        {{ errorMessage }}
      </div>

      <div class="panel-grid">
        <aside class="control-panel">
          <h3>配送路径规划</h3>

          <div class="form-row">
            <label>起点（仓库坐标或地址）</label>
            <input v-model="start.input" placeholder="经度,纬度 或 地址文本" />
            <small class="muted">支持经纬度（如 121.48,31.23）或地址</small>
          </div>

          <div class="form-row destinations">
            <label>目的地（配送点）</label>
            <div v-for="(d, i) in destinations" :key="d.id" class="dest-row">
              <input v-model="d.name" placeholder="名称（如 药店 A）" />
              <input v-model="d.input" placeholder="经度,纬度 或 地址" />
              <button class="small" @click="removeDestination(i)">删除</button>
            </div>
            <button @click="addDestination" class="add-btn">+ 添加目的地</button>
          </div>

          <div class="form-row actions">
            <button class="primary" @click="geocodeAllAndOptimize" :disabled="computing">
              {{ computing ? '计算中...' : '计算最优配送顺序' }}
            </button>
            <button @click="clearRoute" :disabled="computing">清除地图</button>
          </div>

          <div class="form-row output">
            <label>配送顺序</label>
            <div class="order-list">
              <div v-if="deliveryOrder.length===0" class="muted">未计算</div>
              <ol v-else>
                <li v-for="(p, idx) in deliveryOrder" :key="idx">
                  <strong>{{ p.order }}. {{ p.name }}</strong>
                  <div class="sub">坐标: {{ p.coordsText }}</div>
                  <div v-if="p.distanceFromPrev" class="sub">距上一点: {{ p.distanceFromPrev }}</div>
                </li>
              </ol>
            </div>
          </div>
        </aside>

        <section class="map-area">
          <div id="dispatch-amap-container" class="map-container">地图加载中...</div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getCurrentUser, clearAuth, getToken } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'
import { getRoleLabel } from '@/utils/roleLabel'
import axios from 'axios'

let map = null
let markers = []
let polylines = []

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

export default {
  name: 'SmartDispatch',
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
      if (name === 'compliance-report') return 'compliance'
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

    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日`
    })

    // 起点与目的地数据模型
    const start = ref({ input: '', coords: null })
    const destinations = ref([
      { id: 1, name: '药店 A', input: '121.48,31.23', coords: null },
      { id: 2, name: '药店 B', input: '121.50,31.22', coords: null }
    ])

    const computing = ref(false)
    const deliveryOrder = ref([])
    const errorMessage = ref('')
    const successMessage = ref('')

    const goToLogin = () => router.push('/login')
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
    const goToAuditLogs = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push('/admin/audit-logs')
    }
    const handleLogout = () => { clearAuth(); currentUser.value = null; router.push('/login') }
    const goToUserHome = () => { const u = currentUser.value; if(!u) return router.push('/login'); router.push(roleToRoute(u.role)) }

    const navigateTo = (page) => {
      switch(page) {
        case 'home': router.push('/'); break
        case 'inventory':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/inventory' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'inventory' } }); break }
          router.push('/inventory'); break
        case 'nearby':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/nearby-suppliers' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'nearby' } }); break }
          router.push('/nearby-suppliers'); break
        case 'b2b':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/b2b' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'b2b' } }); break }
          router.push('/b2b'); break
        case 'circulation':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/circulation' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'circulation' } }); break }
          router.push('/circulation'); break
        case 'analysis':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/analysis' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'analysis' } }); break }
          router.push('/analysis'); break
        case 'service':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/service' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'service' } }); break }
          router.push('/service'); break
        case 'logistics-orders':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/logistics-orders' } }); break }
          if (currentUser.value.role === 'unauth') { router.push({ name: 'unauth', query: { active: 'orders' } }); break }
          router.push('/logistics-orders'); break
        case 'compliance':
          if (!currentUser.value) { router.push({ name: 'login', query: { redirect: '/compliance-report' } }); break }
          if (currentUser.value.role !== 'regulator') { router.push('/'); break }
          router.push({ name: 'compliance-report' }); break
        default: router.push('/');
      }
    }

    const addDestination = () => destinations.value.push({ id: Date.now(), name: '', input: '', coords: null })
    const removeDestination = (i) => { destinations.value.splice(i,1) }

    // 获取 token（使用统一 authSession）
    const getAuthToken = () => {
      return getToken()
    }

    // 调用后端API进行路径优化
    const geocodeAllAndOptimize = async () => {
      computing.value = true
      deliveryOrder.value = []
      errorMessage.value = ''
      successMessage.value = ''
      
      try {
        const token = getAuthToken()
        if (!token) {
          errorMessage.value = '请先登录'
          alert('请先登录')
          router.push('/login')
          return
        }

        // 构建请求数据
        const requestData = {
          start: start.value.input,
          destinations: destinations.value.map(d => ({
            name: d.name || '未命名',
            location: d.input
          })),
          use_api: false,  // 使用直线距离（快速），如需驾车距离改为 true
          algorithm: 'greedy'  // 使用贪心算法（快速）
        }

        // 调用后端API
        const response = await axios.post(
          `${API_BASE_URL}/api/dispatch/optimize_route`,
          requestData,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )

        if (response.data.success) {
          const result = response.data
          
          // 更新起点坐标
          start.value.coords = [result.start.longitude, result.start.latitude]
          
          // 更新配送顺序
          deliveryOrder.value = result.route.map(r => ({
            name: r.name,
            coordsText: `${r.longitude.toFixed(6)},${r.latitude.toFixed(6)}`,
            order: r.order,
            distanceFromPrev: r.distance_from_prev_text
          }))
          
          // 在地图上绘制路线
          await drawRouteOnMap(result.start, result.route)
          
          successMessage.value = `路径优化成功！总距离：${result.total_distance_text}`
        } else {
          errorMessage.value = response.data.message || '路径优化失败'
          alert(errorMessage.value)
        }
      } catch (error) {
        console.error('路径优化错误:', error)
        if (error.response) {
          errorMessage.value = error.response.data?.message || '服务器错误'
        } else if (error.request) {
          errorMessage.value = '网络连接失败，请检查后端服务是否运行'
        } else {
          errorMessage.value = error.message || '未知错误'
        }
        alert(`路径优化失败：${errorMessage.value}`)
      } finally {
        computing.value = false
      }
    }

    // 在地图上绘制路线（调用高德地图驾车规划API）
    let _drivingPluginLoaded = false
    const ensureDrivingPlugin = () => {
      return new Promise((resolve) => {
        if (!window.AMap) return resolve(false)
        // 如果已经存在 Driving 类或之前已加载插件，直接返回
        if (window.AMap.Driving || _drivingPluginLoaded) {
          _drivingPluginLoaded = true
          return resolve(true)
        }
        try {
          AMap.plugin(['AMap.Driving'], () => {
            _drivingPluginLoaded = true
            resolve(true)
          })
        } catch (e) {
          console.warn('加载 AMap.Driving 插件失败，后续将回退为直线段绘制', e)
          resolve(false)
        }
      })
    }

    const drawRouteOnMap = async (startPoint, orderedPoints) => {
      clearMapOverlays()
      if (!map || !window.AMap) return

      // 添加起点标记
      const startMarker = new AMap.Marker({
        position: [startPoint.longitude, startPoint.latitude],
        title: '起点（仓库）',
        icon: new AMap.Icon({
          size: new AMap.Size(32, 32),
          image: '//a.amap.com/jsapi_demos/static/demo-center/icons/dir-marker.png',
          imageSize: new AMap.Size(32, 32)
        }),
        offset: new AMap.Pixel(-16, -32)
      })
      markers.push(startMarker)

      // 添加目的地标记
      orderedPoints.forEach((p, idx) => {
        const m = new AMap.Marker({
          position: [p.longitude, p.latitude],
          title: `${idx + 1}. ${p.name}`,
          label: {
            content: `${idx + 1}`,
            offset: new AMap.Pixel(0, -5),
            direction: 'top'
          },
          offset: new AMap.Pixel(-12, -24)
        })
        markers.push(m)
      })

      map.add(markers)

      // 尝试加载驾车规划插件（若不可用则使用直线连线回退）
      const pluginReady = await ensureDrivingPlugin()

      // 逐段调用驾车规划以获得实际道路 polyline
      for (let i = 0; i < orderedPoints.length; i++) {
        const origin = (i === 0)
          ? [startPoint.longitude, startPoint.latitude]
          : [orderedPoints[i - 1].longitude, orderedPoints[i - 1].latitude]
        const dest = [orderedPoints[i].longitude, orderedPoints[i].latitude]

        if (pluginReady && window.AMap && AMap.Driving) {
          // eslint-disable-next-line no-await-in-loop
          await new Promise((resolve) => {
            const drivingOptions = { map: map, hideMarkers: true }
            if (AMap.DrivingPolicy && AMap.DrivingPolicy.LEAST_TIME !== undefined) {
              drivingOptions.policy = AMap.DrivingPolicy.LEAST_TIME
            }
            const driving = new AMap.Driving(drivingOptions)
            driving.search(origin, dest, (status, result) => {
              if (status === 'complete' && result.routes && result.routes.length > 0) {
                const route = result.routes[0]
                const pathCoords = []
                ;(route.paths || []).forEach(pth => {
                  (pth.steps || []).forEach(step => {
                    if (step.path && Array.isArray(step.path)) {
                      step.path.forEach(pt => pathCoords.push([pt.lng, pt.lat]))
                    } else if (step.polyline && typeof step.polyline === 'string') {
                      step.polyline.split(';').forEach(pair => {
                        if (!pair) return
                        const [lng, lat] = pair.split(',').map(Number)
                        pathCoords.push([lng, lat])
                      })
                    }
                  })
                })

                if (pathCoords.length > 0) {
                  const pl = new AMap.Polyline({
                    path: pathCoords,
                    strokeColor: '#2db7f5',
                    strokeWeight: 6,
                    strokeOpacity: 0.8
                  })
                  polylines.push(pl)
                  map.add(pl)
                }
              }
              setTimeout(resolve, 120)
            })
          })
        } else {
          // 回退：直接绘制起点到终点的直线段
          const pl = new AMap.Polyline({
            path: [origin, dest],
            strokeColor: '#2db7f5',
            strokeWeight: 4,
            strokeOpacity: 0.6,
            dashStyle: 'solid'
          })
          polylines.push(pl)
          map.add(pl)
        }
      }

      // 自适应视野
      try {
        map.setFitView(markers.concat(polylines), false, [40, 40, 40, 40])
      } catch (e) {
        console.error('地图视野调整失败:', e)
      }
    }

    // 基本工具：解析 "lng,lat"
    const parseCoords = (text) => {
      if (!text) return null
      const parts = text.split(',').map(s => s.trim())
      if (parts.length === 2 && !isNaN(parseFloat(parts[0])) && !isNaN(parseFloat(parts[1]))) {
        return [parseFloat(parts[0]), parseFloat(parts[1])]
      }
      return null
    }

    const clearRoute = () => { clearMapOverlays(); deliveryOrder.value = []; errorMessage.value = ''; successMessage.value = '' }

    // 地图辅助：清理
    const clearMapOverlays = () => {
      if (!map) return
      if (markers.length) { map.remove(markers); markers = [] }
      if (polylines.length) { map.remove(polylines); polylines = [] }
    }

    // 初始化地图
    const initMap = () => {
      if (!window.AMap) return
      map = new AMap.Map('dispatch-amap-container', { zoom: 12, center: [121.48, 31.23], viewMode: '2D' })
      map.addControl(new AMap.Scale())
      map.addControl(new AMap.ToolBar())
    }

    const refreshUser = () => { currentUser.value = getCurrentUser() }

    onMounted(async () => {
      window.addEventListener('storage', refreshUser)
      await nextTick()
      initMap()
    })

    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
      if(map) { map.destroy(); map = null }
    })

    return {
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
      navigateTo,
      goToLogin,
  goToChangePassword,
  goToEnterpriseAuth,
  goToEnterpriseReview,
  goToSystemStatus,
  goToAdminUsers,
      goToAuditLogs,
      handleLogout,
      goToUserHome,
      // inputs
      start,
      destinations,
      addDestination,
      removeDestination,
      geocodeAllAndOptimize,
      deliveryOrder,
      computing,
      clearRoute,
      errorMessage,
      successMessage
    }
  }
}
</script>

<style scoped>
*{box-sizing:border-box;margin:0;padding:0}
.smart-dispatch-container{min-height:100vh;background:#f5f7fa;font-family:"Microsoft YaHei",Arial,sans-serif}
.header{background:#fff;box-shadow:0 2px 10px rgba(0,0,0,0.1);padding:15px 0;width:100%}
.header-content{padding:0 20px;margin:0 auto;max-width:100%}
.platform-info{display:flex;justify-content:space-between;align-items:center}
.platform-title{color:#1a73e8;font-size:24px;font-weight:bold;margin:0}
.current-date{color:#666;font-size:16px}
.nav-section{display:flex;justify-content:space-between;align-items:center;border-top:1px solid #eee;padding-top:15px}
.nav-menu{display:flex;gap:30px}
.nav-item{cursor:pointer;color:#333;padding:5px 0;font-size:16px;transition:color .3s}
.nav-item.active{color:#1a73e8;border-bottom:2px solid #1a73e8}
.user-actions{display:flex;align-items:center;gap:8px}
.user-info{display:flex;align-items:center;padding:6px 12px;border-radius:999px;background-color:#f0f5ff;color:#1a73e8;font-size:14px;font-weight:600;margin-right:10px;gap:8px}
.user-name{white-space:nowrap}
.user-role{padding:2px 10px;border-radius:999px;background-color:#fff;border:1px solid rgba(26,115,232,0.2);font-size:12px;color:#1a73e8}
.change-btn{border:1px solid #1a73e8;background-color:transparent;color:#1a73e8;padding:6px 14px;border-radius:4px;cursor:pointer;margin-right:10px;transition:background-color .3s}
.change-btn:hover{background-color:rgba(26,115,232,0.08)}
.auth-btn{background-color:#fff;color:#1a73e8;border:1px solid #1a73e8;padding:8px 14px;border-radius:4px;cursor:pointer;margin-right:10px}
.auth-btn:hover{background-color:rgba(26,115,232,0.08)}
.review-btn{background-color:#fff7e6;color:#b76c00;border:1px solid #f3e5b8;padding:8px 14px;border-radius:4px;cursor:pointer;margin-right:10px}
.review-btn:hover{background-color:#ffeccc}
.admin-btn{background-color:#f0f5ff;color:#1a73e8;border:1px solid #d6e4ff;padding:8px 14px;border-radius:4px;cursor:pointer;margin-right:10px}
.admin-btn:hover{background-color:#e5edff}
.login-btn{background-color:#1a73e8;color:#fff;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;font-size:14px;transition:background-color .3s}
.login-btn:hover{background-color:#0d62d9}

.message {
  padding: 12px 20px;
  margin: 16px 18px;
  border-radius: 6px;
  font-size: 14px;
  animation: slideDown 0.3s ease;
}

.success-message {
  background-color: #f0f9ff;
  color: #0c66e4;
  border: 1px solid #d0e7ff;
}

.error-message {
  background-color: #fff5f5;
  color: #c53030;
  border: 1px solid #feb2b2;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.main-content{padding:18px}
.panel-grid{display:grid;grid-template-columns:360px 1fr;gap:18px}
.control-panel{background:#fff;padding:16px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.05)}
.control-panel h3{margin-bottom:10px;color:#333}
.form-row{margin-bottom:12px}
.form-row label{display:block;color:#333;margin-bottom:8px;font-size:15px;font-weight:600}
.form-row input{width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px}
.muted{color:#777;font-size:13px}
.destinations .dest-row{display:flex;gap:8px;margin-bottom:10px}
.dest-row input{flex:1;padding:10px 12px;font-size:14px}
.small{background:#f3f3f3;border:none;padding:6px 8px;border-radius:4px;cursor:pointer}
.small:hover{background:#e8e8e8}
.add-btn{background:transparent;border:1px dashed #ccc;padding:6px 10px;border-radius:4px;cursor:pointer;width:100%}
.add-btn:hover{border-color:#1a73e8;color:#1a73e8}
.actions{display:flex;gap:10px}
.actions .primary{background:#1a73e8;color:#fff;padding:10px 14px;border:none;border-radius:6px;font-size:15px;flex:1;cursor:pointer}
.actions .primary:hover{background:#0d62d9}
.actions .primary:disabled{background:#ccc;cursor:not-allowed}
.actions button:not(.primary){background:#f3f3f3;border:1px solid #ddd;padding:10px 14px;border-radius:6px;cursor:pointer}
.actions button:not(.primary):hover{background:#e8e8e8}
.actions button:not(.primary):disabled{background:#f9f9f9;cursor:not-allowed;color:#999}
.output .order-list{max-height:220px;overflow:auto;padding:10px;border:1px dashed #eee;border-radius:6px;background:#fafafa}
.order-list ol{padding-left:18px}
.order-list li{margin-bottom:8px;line-height:1.6}
.order-list .sub{color:#999;font-size:12px;margin-left:6px;margin-top:2px}

/* 减小地图高度并增强控制面板的可读性 */
.map-area .map-container{width:100%;height:520px;background:#f8f9fa;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.04);display:flex;align-items:center;justify-content:center}

@media (max-width:1000px){.panel-grid{grid-template-columns:1fr}.map-area .map-container{height:360px}}
</style>
