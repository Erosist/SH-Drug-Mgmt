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
      <div class="panel-grid">
        <aside class="control-panel">
          <h3>配送路径规划</h3>

          <div class="form-row">
            <label>起点（仓库坐标或地址）</label>
            <input v-model="start.input" placeholder="经度,纬度 或 地址文本" />
            <small class="muted">支持经纬度或地址，回车可尝试地理编码</small>
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
            <button class="primary" @click="geocodeAllAndOptimize" :disabled="computing">计算最优配送顺序</button>
            <button @click="clearRoute">清除地图</button>
          </div>

          <div class="form-row output">
            <label>配送顺序</label>
            <div class="order-list">
              <div v-if="deliveryOrder.length===0" class="muted">未计算</div>
              <ol v-else>
                <li v-for="(p, idx) in deliveryOrder" :key="idx">{{ p.name }} <span class="sub">({{ p.coordsText }})</span></li>
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
import { getCurrentUser, clearAuth } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'
import { getRoleLabel } from '@/utils/roleLabel'

let map = null
let markers = []
let polylines = []

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

    // 基本工具：解析 "lng,lat" 或 尝试地理编码
    const parseCoords = (text) => {
      if(!text) return null
      const parts = text.split(',').map(s=>s.trim())
      if(parts.length===2 && !isNaN(parseFloat(parts[0])) && !isNaN(parseFloat(parts[1]))) {
        return [parseFloat(parts[0]), parseFloat(parts[1])]
      }
      return null
    }

    

    // 计算两点直线距离（用于贪心近邻）
    const haversine = (a,b) => {
      const toRad = v => v * Math.PI / 180
      const R = 6371 // km
      const dLat = toRad(b[1]-a[1])
      const dLon = toRad(b[0]-a[0])
      const lat1 = toRad(a[1]); const lat2 = toRad(b[1])
      const sa = Math.sin(dLat/2)*Math.sin(dLat/2) + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)*Math.sin(dLon/2)
      const c = 2 * Math.atan2(Math.sqrt(sa), Math.sqrt(1-sa))
      return R * c
    }

    // 贪心最近邻求解顺序（快速、可解释）
    const optimizeOrder = (originCoords, destCoordsArray) => {
      const remaining = destCoordsArray.slice()
      const ordered = []
      let current = originCoords
      while(remaining.length>0) {
        let bestIdx = 0; let bestDist = Infinity
        for(let i=0;i<remaining.length;i++){
          const d = haversine(current, remaining[i].coords)
          if(d < bestDist) { bestDist = d; bestIdx = i }
        }
        ordered.push(remaining.splice(bestIdx,1)[0])
        current = ordered[ordered.length-1].coords
      }
      return ordered
    }

    // 地图辅助：清理
    const clearMapOverlays = () => {
      if(!map) return
      if(markers.length) { map.remove(markers); markers = [] }
      if(polylines.length) { map.remove(polylines); polylines = [] }
    }

    // 在地图上绘制节点和分段驾车路线（对每段调用 Driving）
    const drawRouteSegments = async (orderedPoints, startPoint) => {
      clearMapOverlays()
      if(!map) return

      // 添加起点标记
      const startMarker = new AMap.Marker({ position: startPoint, title: '起点', offset: new AMap.Pixel(-12,-24) })
      markers.push(startMarker)

      // 添加目的地标记
      orderedPoints.forEach((p, idx) => {
        const m = new AMap.Marker({ position: p.coords, title: `${idx+1}. ${p.name}`, offset: new AMap.Pixel(-12,-24) })
        markers.push(m)
      })

      map.add(markers)

      // 逐段调用驾车规划以获得实际道路 polyline
      for(let i=0;i<orderedPoints.length;i++){
        const origin = (i===0) ? startPoint : orderedPoints[i-1].coords
        const dest = orderedPoints[i].coords
        // eslint-disable-next-line no-await-in-loop
        await new Promise((resolve) => {
          const driving = new AMap.Driving({ map: map, policy: AMap.DrivingPolicy.LEAST_TIME })
          driving.search(origin, dest, (status, result) => {
            if(status === 'complete' && result.routes && result.routes.length>0) {
              const route = result.routes[0]
              // result.routes[0].paths[0].steps each may contain polyline (string) or path(array)
              const pathCoords = []
              (route.paths || []).forEach(pth => {
                (pth.steps || []).forEach(step => {
                  if(step.path && Array.isArray(step.path)) {
                    step.path.forEach(pt => pathCoords.push([pt.lng, pt.lat]))
                  } else if(step.polyline && typeof step.polyline === 'string') {
                    step.polyline.split(';').forEach(pair => {
                      if(!pair) return
                      const [lng, lat] = pair.split(',').map(Number)
                      pathCoords.push([lng, lat])
                    })
                  }
                })
              })

              if(pathCoords.length>0) {
                const pl = new AMap.Polyline({ path: pathCoords, strokeColor: '#2db7f5', strokeWeight: 6, strokeOpacity: 0.8 })
                polylines.push(pl)
                map.add(pl)
              }
            }
            // small delay to let map draw
            setTimeout(resolve, 120)
          })
        })
      }

      // fit view
      try { map.setFitView(markers.concat(polylines), false, [40,40,40,40]) } catch(e){}
    }

    // 主流程：地理编码所有输入 -> 优化顺序 -> 绘制路线
    const geocodeAllAndOptimize = async () => {
      computing.value = true
      deliveryOrder.value = []
      try {
        const startCoords = await geocode(start.value.input)
        if(!startCoords) {
          alert('无法解析起点，请检查输入（支持经度,纬度 或 可识别的地址）')
          computing.value = false
          return
        }
        start.value.coords = startCoords

        // geocode destinations
        const dests = []
        for(const d of destinations.value) {
          const c = await geocode(d.input || '')
          if(c) dests.push({ name: d.name || '未命名', coords: c })
        }
        if(dests.length===0) { alert('请至少填写一个可解析的目的地坐标或地址'); computing.value=false; return }

        // optimize by greedy NN
        const ordered = optimizeOrder(start.value.coords, dests)

        // set deliveryOrder for UI
        deliveryOrder.value = ordered.map(o => ({ name: o.name, coordsText: `${o.coords[0].toFixed(6)},${o.coords[1].toFixed(6)}` }))

        // draw on map
        await drawRouteSegments(ordered, start.value.coords)
      } finally {
        computing.value = false
      }
    }

    // helper geocode wrapper
    const geocode = async (inputText) => {
      const p = parseCoords(inputText)
      if(p) return p
      if(!window.AMap) return null
      return await new Promise((resolve) => {
        const geo = new AMap.Geocoder({ city: '' })
        geo.getLocation(inputText, (status, result) => {
          if(status==='complete' && result.geocodes && result.geocodes.length>0) {
            const loc = result.geocodes[0].location
            resolve([loc.lng, loc.lat])
          } else resolve(null)
        })
      })
    }

    const clearRoute = () => { clearMapOverlays(); deliveryOrder.value = [] }

    // 初始化地图（与 NearbySuppliers.vue 风格一致）
    const initMap = () => {
      if(!window.AMap) return
      map = new AMap.Map('dispatch-amap-container', { zoom: 12, center: [121.48,31.23], viewMode: '2D' })
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
      clearRoute
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
.small{background:#f3f3f3;border:none;padding:6px 8px;border-radius:4px}
.add-btn{background:transparent;border:1px dashed #ccc;padding:6px 10px;border-radius:4px;cursor:pointer}
.actions .primary{background:#1a73e8;color:#fff;padding:10px 14px;border:none;border-radius:6px;font-size:15px}
.output .order-list{max-height:220px;overflow:auto;padding:10px;border:1px dashed #eee;border-radius:6px;background:#fafafa}
.order-list ol{padding-left:18px}
.order-list .sub{color:#999;font-size:12px;margin-left:6px}

/* 减小地图高度并增强控制面板的可读性 */
.map-area .map-container{width:100%;height:520px;background:#f8f9fa;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.04);display:flex;align-items:center;justify-content:center}

@media (max-width:1000px){.panel-grid{grid-template-columns:1fr}.map-area .map-container{height:360px}}
</style>
