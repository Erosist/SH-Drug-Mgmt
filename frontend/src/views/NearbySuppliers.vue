<template>
  <div class="nearby-suppliers-container">
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
            >{{ isRegulator ? '药品追溯查询' : '流通数据上报' }}</div>
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

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 页面标题 -->
      <div class="page-header">
        <h2>就近供应商推荐</h2>
        <p class="subtitle">在地图上查看药店和供应商位置，搜索药品查找有库存的供应商</p>
      </div>

      <!-- 地图区域 - 始终显示 -->
      <el-card class="map-card">
        <template #header>
          <div class="card-header">
            <span>供应商地图</span>
            <div>
              <el-tag v-if="allSuppliers.length > 0" type="info">
                共 {{ allSuppliers.length }} 个供应商
              </el-tag>
              <el-tag v-if="searchResult && searchResult.filtered > 0" type="success" style="margin-left: 10px">
                匹配 {{ searchResult.filtered }} 个
              </el-tag>
            </div>
          </div>
        </template>

        <div class="map-container">
          <div id="amap-container" style="width: 100%; height: 600px;"></div>
          <div class="map-legend">
            <div class="legend-item">
                <img :src="pharmacyIcon" class="legend-img" alt="我的位置" />
                <span>我的位置</span>
            </div>
            <div class="legend-item">
              <img :src="supplierNormalIcon" class="legend-img" alt="普通供应商" />
              <span>普通供应商</span>
            </div>
            <div class="legend-item">
              <img :src="supplierMatchedIcon" class="legend-img" alt="匹配的供应商" />
              <span>匹配的供应商</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-section">
        <el-form :model="searchForm" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="药品名称" required>
                <el-autocomplete
                  v-model="searchForm.drugName" 
                  :fetch-suggestions="queryDrugSuggestions"
                  placeholder="请输入药品名称，如：阿莫西林"
                  clearable
                  :trigger-on-focus="false"
                  @select="handleDrugSelect"
                  style="width: 100%"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                  <template #default="{ item }">
                    <div class="drug-suggestion-item">
                      <span class="drug-name">{{ item.value }}</span>
                      <span class="drug-count">{{ item.supplier_count }} 个供应商</span>
                    </div>
                  </template>
                </el-autocomplete>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="搜索方式">
                <el-radio-group v-model="searchType">
                  <el-radio label="location">使用我的位置</el-radio>
                  <el-radio label="address">输入地址</el-radio>
                  <el-radio label="coords">输入坐标</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 地址搜索 -->
          <el-row :gutter="20" v-if="searchType === 'address'">
            <el-col :span="8">
              <el-form-item label="地址">
                <el-input 
                  v-model="searchForm.address" 
                  placeholder="请输入详细地址，如：北京市朝阳区望京SOHO"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item label="城市">
                <el-input 
                  v-model="searchForm.city" 
                  placeholder="北京市"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 坐标搜索 -->
          <el-row :gutter="20" v-if="searchType === 'coords'">
            <el-col :span="6">
              <el-form-item label="经度">
                <el-input-number 
                  v-model="searchForm.longitude" 
                  :precision="6"
                  :step="0.000001"
                  placeholder="116.470697"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="纬度">
                <el-input-number 
                  v-model="searchForm.latitude" 
                  :precision="6"
                  :step="0.000001"
                  placeholder="40.000565"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 搜索参数 -->
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="搜索半径">
                <el-select v-model="searchForm.maxDistance" placeholder="选择搜索半径">
                  <el-option label="不限制" :value="null" />
                  <el-option label="10公里" :value="10000" />
                  <el-option label="30公里" :value="30000" />
                  <el-option label="50公里" :value="50000" />
                  <el-option label="100公里" :value="100000" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="显示数量">
                <el-input-number 
                  v-model="searchForm.limit" 
                  :min="1" 
                  :max="50"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="距离计算">
                <el-switch
                  v-model="searchForm.useApi"
                  active-text="驾车距离"
                  inactive-text="直线距离"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item>
                <el-button type="primary" @click="searchNearbySuppliers" :loading="loading">
                  <el-icon><Search /></el-icon> 搜索供应商
                </el-button>
                <el-button @click="resetSearch">重置</el-button>
                <el-button 
                  v-if="searchType === 'location'" 
                  @click="updateMyLocation"
                  :loading="updatingLocation"
                >
                  <el-icon><Location /></el-icon> 更新我的位置
                </el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <!-- 我的位置信息 -->
      <div v-if="myLocation && searchType === 'location'" class="my-location-info">
        <el-alert type="info" :closable="false">
          <template #title>
            <div class="location-info-content">
              <span><strong>我的位置：</strong>{{ myLocation.name }}</span>
              <span style="margin-left: 20px;">
                <strong>地址：</strong>{{ myLocation.address }}
              </span>
              <span v-if="myLocation.has_location" style="margin-left: 20px;">
                <strong>坐标：</strong>({{ myLocation.longitude }}, {{ myLocation.latitude }})
              </span>
            </div>
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 搜索结果 -->
    <el-card class="result-card" v-if="searchResult && searchResult.suppliers.length > 0">
      <template #header>
        <div class="card-header">
          <span>搜索结果 - {{ searchResult.drug_name }}</span>
          <div>
            <el-tag type="success">找到 {{ searchResult.filtered }} 个供应商</el-tag>
            <el-tag v-if="searchResult.geocode_failed > 0" type="warning" style="margin-left: 10px;">
              {{ searchResult.geocode_failed }} 个供应商位置获取失败
            </el-tag>
          </div>
        </div>
      </template>

      <div class="result-summary">
        <el-descriptions :column="4" border size="small">
          <el-descriptions-item label="药品名称">
            <el-tag type="primary">{{ searchResult.drug_name }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="搜索位置">
            {{ searchResult.pharmacy_location.longitude.toFixed(6) }}, 
            {{ searchResult.pharmacy_location.latitude.toFixed(6) }}
          </el-descriptions-item>
          <el-descriptions-item label="符合条件">
            {{ searchResult.filtered }}
          </el-descriptions-item>
          <el-descriptions-item label="搜索半径">
            {{ searchResult.params.max_distance ? 
              (searchResult.params.max_distance / 1000) + 'km' : '不限制' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 供应商列表 -->
      <div class="suppliers-list">
        <el-table 
          :data="searchResult.suppliers" 
          stripe 
          style="width: 100%"
          :default-sort="{ prop: 'distance', order: 'ascending' }"
        >
          <el-table-column type="index" label="排名" width="60" />
          <el-table-column prop="name" label="供应商名称" min-width="180" />
          <el-table-column label="药品信息" min-width="200">
            <template #default="{ row }">
              <div v-if="row.inventory && row.inventory.drug_info">
                <div><strong>{{ row.inventory.drug_info.generic_name }}</strong></div>
                <div style="font-size: 12px; color: #666;">
                  {{ row.inventory.drug_info.brand_name }} | {{ row.inventory.drug_info.specification }}
                </div>
                <div style="font-size: 12px; color: #999;">
                  {{ row.inventory.drug_info.manufacturer }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="库存/价格" width="140" align="center">
            <template #default="{ row }">
              <div v-if="row.inventory">
                <el-tag type="success">库存: {{ row.inventory.quantity }}</el-tag>
                <div style="margin-top: 5px; color: #f56c6c; font-weight: bold;">
                  ¥{{ row.inventory.unit_price }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="distance_text" label="距离" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getDistanceType(row.distance)">
                {{ row.distance_text }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="address" label="地址" min-width="220" />
          <el-table-column prop="contact_person" label="联系人" width="100" />
          <el-table-column prop="contact_phone" label="联系电话" width="130" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="viewSupplierDetail(row)">
                查看详情
              </el-button>
              <el-button size="small" type="success" @click="contactSupplier(row)">
                联系
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="searchResult && searchResult.suppliers.length === 0"
        :description="searchResult.message || '未找到符合条件的供应商'"
      >
        <el-button type="primary" @click="resetSearch">重新搜索</el-button>
      </el-empty>
    </el-card>

    <!-- 供应商详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="供应商详情" 
      width="700px"
    >
      <div v-if="currentSupplier">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="供应商名称" :span="2">
            {{ currentSupplier.name }}
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag>{{ currentSupplier.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="距离">
            <el-tag type="success">{{ currentSupplier.distance_text }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">
            {{ currentSupplier.address }}
          </el-descriptions-item>
          <el-descriptions-item label="统一社会信用代码" :span="2">
            {{ currentSupplier.unified_social_credit_code }}
          </el-descriptions-item>
          <el-descriptions-item label="法定代表人">
            {{ currentSupplier.legal_representative }}
          </el-descriptions-item>
          <el-descriptions-item label="联系人">
            {{ currentSupplier.contact_person }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            {{ currentSupplier.contact_phone }}
          </el-descriptions-item>
          <el-descriptions-item label="联系邮箱">
            {{ currentSupplier.contact_email }}
          </el-descriptions-item>
          <el-descriptions-item label="经营范围" :span="2">
            {{ currentSupplier.business_scope }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 库存信息 -->
        <el-divider>库存信息</el-divider>
        <div v-if="currentSupplier.inventory" class="inventory-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="药品通用名">
              {{ currentSupplier.inventory.drug_info?.generic_name }}
            </el-descriptions-item>
            <el-descriptions-item label="商品名">
              {{ currentSupplier.inventory.drug_info?.brand_name }}
            </el-descriptions-item>
            <el-descriptions-item label="规格">
              {{ currentSupplier.inventory.drug_info?.specification }}
            </el-descriptions-item>
            <el-descriptions-item label="生产厂家">
              {{ currentSupplier.inventory.drug_info?.manufacturer }}
            </el-descriptions-item>
            <el-descriptions-item label="库存数量">
              <el-tag type="success" size="large">{{ currentSupplier.inventory.quantity }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="单价">
              <span style="color: #f56c6c; font-size: 18px; font-weight: bold;">
                ¥{{ currentSupplier.inventory.unit_price }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="最小订购量">
              {{ currentSupplier.inventory.min_order_quantity }}
            </el-descriptions-item>
            <el-descriptions-item label="有效期至">
              {{ currentSupplier.inventory.valid_until }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Location, MapLocation } from '@element-plus/icons-vue'
import { nearbyApi } from '@/api/nearby'
import { getCurrentUser, clearAuth } from '@/utils/authSession'
import { getRoleLabel } from '@/utils/roleLabel'

const router = useRouter()

// 用户信息
const currentUser = ref(getCurrentUser())
const isLogistics = computed(() => currentUser.value && currentUser.value.role === 'logistics')
const isSupplier = computed(() => currentUser.value && currentUser.value.role === 'supplier')
const isPharmacy = computed(() => currentUser.value && currentUser.value.role === 'pharmacy')
const isRegulator = computed(() => currentUser.value && currentUser.value.role === 'regulator')
const isAdmin = computed(() => currentUser.value && currentUser.value.role === 'admin')
const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))

// 当前导航
const activeNav = ref('nearby')

// 动态日期
const currentDate = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth() + 1
  const d = now.getDate()
  return `${y}年${m}月${d}日`
})

// 导航方法
const navigateTo = (page) => {
  switch(page) {
    case 'home':
      router.push('/'); break
    case 'inventory':
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/inventory' } })
        break
      }
      if (currentUser.value.role === 'unauth') {
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
    default:
      router.push('/');
  }
}

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

const handleLogout = () => {
  clearAuth()
  currentUser.value = null
  router.push('/login')
}

const refreshUser = () => {
  currentUser.value = getCurrentUser()
}

// 地图相关
let map = null
let markers = []
let polylines = [] // 存储路径线
const allSuppliers = ref([]) // 所有供应商

// 统一的药店图标（SVG -> base64 data URL），在地图 marker 和图例中复用
const pharmacyIconSvg = `<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="15" fill="#ef4444"/><circle cx="20" cy="20" r="10" fill="#fff"/><circle cx="20" cy="20" r="5" fill="#ef4444"/></svg>`
const pharmacyIcon = `data:image/svg+xml;base64,${btoa(pharmacyIconSvg)}`

// 供应商图标（普通 / 匹配），使用 base SVG 并在图例与 marker 中复用
const supplierNormalSvg = `<svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg"><circle cx="18" cy="18" r="16" fill="#999999"/><circle cx="18" cy="18" r="10" fill="#fff"/><circle cx="18" cy="18" r="6" fill="#999999"/></svg>`
const supplierMatchedSvg = `<svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg"><circle cx="18" cy="18" r="16" fill="#4096ff"/><circle cx="18" cy="18" r="10" fill="#fff"/><circle cx="18" cy="18" r="6" fill="#4096ff"/></svg>`

const supplierNormalIcon = `data:image/svg+xml;base64,${btoa(supplierNormalSvg)}`
const supplierMatchedIcon = `data:image/svg+xml;base64,${btoa(supplierMatchedSvg)}`

// 搜索类型
const searchType = ref('location') // location, address, coords

// 搜索表单
const searchForm = reactive({
  drugName: '', // 药品名称
  address: '',
  city: '',
  longitude: null,
  latitude: null,
  maxDistance: 50000, // 默认50公里
  limit: 10,
  useApi: false // 默认使用直线距离
})

// 状态
const loading = ref(false)
const updatingLocation = ref(false)
const myLocation = ref(null)
const searchResult = ref(null)

// 供应商详情对话框
const detailDialogVisible = ref(false)
const currentSupplier = ref(null)

// 获取我的位置
const loadMyLocation = async () => {
  try {
    console.log('Loading my location...')
    const response = await nearbyApi.getMyLocation()
    if (response.data.success) {
      myLocation.value = response.data.tenant
      console.log('My location loaded:', myLocation.value)
      
      // 如果有坐标，自动填充
      if (myLocation.value.has_location) {
        searchForm.longitude = myLocation.value.longitude
        searchForm.latitude = myLocation.value.latitude
      }
    }
  } catch (error) {
    console.error('获取位置失败:', error)
  }
}

// 获取所有供应商
const loadAllSuppliers = async () => {
  try {
    console.log('Loading all suppliers...')
    const response = await nearbyApi.getAllSuppliers()
    if (response.data.success) {
      allSuppliers.value = response.data.suppliers
      console.log('All suppliers loaded:', allSuppliers.value.length)
      
      // 提示地理编码失败的信息
      if (response.data.geocode_failed > 0) {
        ElMessage.warning(`已加载 ${allSuppliers.value.length} 个供应商，${response.data.geocode_failed} 个供应商位置获取失败`)
      }
    }
  } catch (error) {
    console.error('获取供应商失败:', error)
  }
}

// 更新我的位置 - 使用浏览器地理定位
const updateMyLocation = async () => {
  if (!navigator.geolocation) {
    ElMessage.error('您的浏览器不支持地理定位功能')
    return
  }

  try {
    updatingLocation.value = true
    ElMessage.info('正在获取您的位置，请允许浏览器访问位置信息...')
    
    // 使用浏览器的地理定位API
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const coords = position.coords
          console.log('获取到的位置:', coords)
          
          // GCJ-02坐标系转换（如果需要）
          // 浏览器返回的是WGS84坐标，而高德地图使用GCJ-02坐标
          // 这里直接使用，高德API会自动处理
          const response = await nearbyApi.updateMyLocation({
            longitude: coords.longitude,
            latitude: coords.latitude
          })
          
          if (response.data.success) {
            ElMessage.success('位置更新成功')
            await loadMyLocation()
            
            // 更新地图中心点
            if (map && response.data.tenant.longitude && response.data.tenant.latitude) {
              map.setCenter([response.data.tenant.longitude, response.data.tenant.latitude])
              updateMapMarkers()
            }
          }
        } catch (error) {
          ElMessage.error('位置更新失败: ' + (error.response?.data?.message || error.message))
        } finally {
          updatingLocation.value = false
        }
      },
      (error) => {
        updatingLocation.value = false
        let errorMsg = '获取位置失败'
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMsg = '您拒绝了位置访问请求，请在浏览器设置中允许位置访问'
            break
          case error.POSITION_UNAVAILABLE:
            errorMsg = '位置信息不可用，请检查您的设备设置'
            break
          case error.TIMEOUT:
            errorMsg = '获取位置超时，请重试'
            break
        }
        ElMessage.error(errorMsg)
        console.error('Geolocation error:', error)
      },
      {
        enableHighAccuracy: true, // 使用高精度
        timeout: 10000, // 10秒超时
        maximumAge: 0 // 不使用缓存的位置
      }
    )
  } catch (error) {
    updatingLocation.value = false
    ElMessage.error('位置更新失败: ' + (error.message || '未知错误'))
  }
}

// 搜索就近供应商
const searchNearbySuppliers = async () => {
  // 验证药品名称
  if (!searchForm.drugName || searchForm.drugName.trim() === '') {
    ElMessage.warning('请输入药品名称')
    return
  }

  loading.value = true
  
  try {
    let params = {
      drug_name: searchForm.drugName.trim(),
      max_distance: searchForm.maxDistance,
      limit: searchForm.limit,
      use_api: searchForm.useApi
    }

    // 根据搜索类型添加参数
    if (searchType.value === 'location') {
      if (!myLocation.value?.has_location) {
        ElMessage.warning('请先设置您的位置')
        return
      }
      params.longitude = myLocation.value.longitude
      params.latitude = myLocation.value.latitude
    } else if (searchType.value === 'address') {
      if (!searchForm.address) {
        ElMessage.warning('请输入地址')
        return
      }
      params.address = searchForm.address
      params.city = searchForm.city
    } else if (searchType.value === 'coords') {
      if (!searchForm.longitude || !searchForm.latitude) {
        ElMessage.warning('请输入经纬度')
        return
      }
      params.longitude = searchForm.longitude
      params.latitude = searchForm.latitude
    }

    const response = await nearbyApi.getNearbySuppliers(params)
    
    if (response.data.success) {
      searchResult.value = response.data
      
      // 更新地图标记，高亮匹配的供应商
      updateMapMarkers()
      
      if (response.data.filtered === 0) {
        ElMessage.info(response.data.message || '未找到符合条件的供应商，请尝试扩大搜索范围')
      } else {
        let successMsg = `找到 ${response.data.filtered} 个有 ${response.data.drug_name} 库存的供应商`
        if (response.data.geocode_failed > 0) {
          successMsg += `（${response.data.geocode_failed} 个供应商位置获取失败）`
        }
        ElMessage.success(successMsg)
      }
    }
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message
    ElMessage.error('搜索失败: ' + errorMsg)
    console.error('搜索错误:', error)
  } finally {
    loading.value = false
  }
}

// 查询药品候选项（用于自动完成下拉框）
const queryDrugSuggestions = async (queryString, callback) => {
  if (!queryString || queryString.trim() === '') {
    callback([])
    return
  }

  try {
    const response = await nearbyApi.getDrugSuggestions(queryString.trim(), 10)
    if (response.data.success) {
      // 将药品列表转换为 el-autocomplete 需要的格式
      const suggestions = response.data.drugs.map(drug => ({
        value: drug.generic_name,
        supplier_count: drug.supplier_count,
        brand_name: drug.brand_name,
        specification: drug.specification
      }))
      callback(suggestions)
    } else {
      callback([])
    }
  } catch (error) {
    console.error('获取药品候选项失败:', error)
    callback([])
  }
}

// 选择药品候选项时的处理
const handleDrugSelect = (item) => {
  console.log('选择了药品:', item)
  // 可以在这里添加额外的逻辑，比如自动搜索
}

// 重置搜索
const resetSearch = () => {
  searchForm.drugName = ''
  searchForm.address = ''
  searchForm.city = ''
  searchForm.longitude = null
  searchForm.latitude = null
  searchForm.maxDistance = 50000
  searchForm.limit = 10
  searchForm.useApi = false
  searchResult.value = null
  
  // 重置地图标记（显示所有供应商，无高亮）
  if (map) {
    updateMapMarkers()
  }
}

// 根据距离获取标签类型
const getDistanceType = (distance) => {
  if (distance < 5000) return 'success'
  if (distance < 20000) return 'warning'
  return 'info'
}

// 查看供应商详情
const viewSupplierDetail = (supplier) => {
  currentSupplier.value = supplier
  detailDialogVisible.value = true
}

// 联系供应商
const contactSupplier = (supplier) => {
  ElMessageBox.alert(
    `联系人：${supplier.contact_person}\n电话：${supplier.contact_phone}\n邮箱：${supplier.contact_email}`,
    '联系方式',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  )
}

// 初始化地图
const initMap = () => {
  if (!window.AMap) {
    ElMessage.error('地图加载失败，请刷新页面重试')
    return
  }

  // 创建地图实例
  map = new AMap.Map('amap-container', {
    zoom: 11,
    center: myLocation.value?.has_location 
      ? [myLocation.value.longitude, myLocation.value.latitude]
      : [116.397128, 39.916527], // 默认中心点
    viewMode: '2D'
  })

  // 添加缩放控件（有时部分高德控件在某些环境会抛错，使用 try/catch 保护）
  try {
    if (AMap.Scale) map.addControl(new AMap.Scale())
  } catch (err) {
    console.warn('AMap.Scale 控件初始化失败:', err)
  }

  try {
    if (AMap.ToolBar) map.addControl(new AMap.ToolBar())
  } catch (err) {
    console.warn('AMap.ToolBar 控件初始化失败:', err)
  }

  // 在地图完全初始化后触发一次标记更新，确保在地图 ready/complete 之后再添加 marker
  map.on && map.on('complete', () => {
    try {
      console.log('AMap complete event fired — map ready')
      updateMapMarkers()
    } catch (e) {
      console.error('updateMapMarkers 在 map.complete 回调中失败:', e)
    }
  })
}

// 清除所有标记和路径
const clearMarkers = () => {
  if (markers.length > 0) {
    map.remove(markers)
    markers = []
  }
  if (polylines.length > 0) {
    map.remove(polylines)
    polylines = []
  }
}

// 更新地图标记
const updateMapMarkers = () => {
  if (!map) {
    console.warn('Map not initialized yet')
    return
  }

  console.log('Starting updateMapMarkers...')
  clearMarkers()

  const allPoints = []
  const matchedSupplierIds = new Set(
    searchResult.value?.suppliers?.map(s => s.id) || []
  )

  // 添加药店标记（红色）
  if (myLocation.value?.has_location) {
    console.log('Adding pharmacy marker at:', myLocation.value.longitude, myLocation.value.latitude)
    const pharmacyMarker = new AMap.Marker({
      position: [myLocation.value.longitude, myLocation.value.latitude],
      title: '我的位置',
      icon: new AMap.Icon({
        size: new AMap.Size(40, 40),
        image: pharmacyIcon,
        imageSize: new AMap.Size(40, 40)
      }),
      offset: new AMap.Pixel(-20, -20),
      zIndex: 200
    })

    markers.push(pharmacyMarker)
    allPoints.push([myLocation.value.longitude, myLocation.value.latitude])

    // 添加药店信息窗口
    const pharmacyInfo = new AMap.InfoWindow({
      content: `
        <div style="padding: 12px;">
          <h4 style="margin: 0 0 10px 0; color: #ef4444; font-size: 16px;">📍 ${myLocation.value.name}</h4>
          <p style="margin: 5px 0;">地址: ${myLocation.value.address}</p>
          <p style="margin: 5px 0;">经度: ${myLocation.value.longitude.toFixed(6)}</p>
          <p style="margin: 5px 0;">纬度: ${myLocation.value.latitude.toFixed(6)}</p>
        </div>
      `
    })

    pharmacyMarker.on('click', () => {
      pharmacyInfo.open(map, pharmacyMarker.getPosition())
    })
  }

  // 添加供应商标记
  console.log('Adding supplier markers, total:', allSuppliers.value.length)
  allSuppliers.value.forEach((supplier, index) => {
    if (!supplier.longitude || !supplier.latitude) {
      console.warn('Supplier missing coordinates:', supplier.name)
      return
    }

    const isMatched = matchedSupplierIds.has(supplier.id)
    const matchedSupplier = searchResult.value?.suppliers?.find(s => s.id === supplier.id)

    // 根据是否匹配使用不同的图标和大小
    const iconSize = isMatched ? 36 : 28
    const iconColor = isMatched ? '#4096ff' : '#999999'
    const zIndex = isMatched ? 150 : 100

    const supplierMarker = new AMap.Marker({
      position: [supplier.longitude, supplier.latitude],
      title: supplier.name,
      icon: new AMap.Icon({
        size: new AMap.Size(iconSize, iconSize),
        // 使用预生成的 data URL，根据是否匹配选择图标
        image: isMatched ? supplierMatchedIcon : supplierNormalIcon,
        imageSize: new AMap.Size(iconSize, iconSize)
      }),
      offset: new AMap.Pixel(-iconSize/2, -iconSize/2),
      zIndex: zIndex
    })

    markers.push(supplierMarker)
    allPoints.push([supplier.longitude, supplier.latitude])

    // 构建信息窗口内容
    let inventoryHtml = ''
    if (isMatched && matchedSupplier?.inventory) {
      const inv = matchedSupplier.inventory
      inventoryHtml = `
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;">
          <p style="margin: 5px 0; font-weight: bold; color: #4096ff;">💊 库存药品</p>
          <p style="margin: 5px 0; padding-left: 10px;">${inv.drug_info?.generic_name || ''} (${inv.drug_info?.brand_name || ''})</p>
          <p style="margin: 5px 0; padding-left: 10px; font-size: 12px;">${inv.drug_info?.specification || ''}</p>
          <p style="margin: 5px 0;"><strong>库存:</strong> <span style="color: #67c23a;">${inv.quantity}</span></p>
          <p style="margin: 5px 0;"><strong>价格:</strong> <span style="color: #f56c6c; font-weight: bold;">¥${inv.unit_price}</span></p>
          <p style="margin: 5px 0;"><strong>距离:</strong> <span style="color: #409eff;">${matchedSupplier.distance_text}</span></p>
        </div>
      `
    }

    // 地理编码标识
    const geocodedBadge = supplier.geocoded 
      ? '<span style="background: #fef0c7; color: #9c6400; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px;">📍 地址解析</span>' 
      : ''

    // 添加供应商信息窗口
    const supplierInfo = new AMap.InfoWindow({
      content: `
        <div style="padding: 12px; min-width: 260px;">
          <h4 style="margin: 0 0 10px 0; color: ${iconColor}; font-size: 16px;">
            ${isMatched ? '🏭' : '⚪'} ${supplier.name} ${geocodedBadge}
          </h4>
          <p style="margin: 5px 0;"><strong>地址:</strong> ${supplier.address}</p>
          <p style="margin: 5px 0;"><strong>联系人:</strong> ${supplier.contact_person}</p>
          <p style="margin: 5px 0;"><strong>电话:</strong> ${supplier.contact_phone}</p>
          ${inventoryHtml}
        </div>
      `
    })

    supplierMarker.on('click', () => {
      supplierInfo.open(map, supplierMarker.getPosition())
    })

    // 如果是匹配的供应商且有药店位置，绘制路径
    if (isMatched && myLocation.value?.has_location && matchedSupplier) {
      const path = [
        [myLocation.value.longitude, myLocation.value.latitude],
        [supplier.longitude, supplier.latitude]
      ]

      const polyline = new AMap.Polyline({
        path: path,
        strokeColor: '#4096ff',
        strokeWeight: 3,
        strokeOpacity: 0.6,
        strokeStyle: 'solid',
        zIndex: 50
      })

      polylines.push(polyline)
    }
  })

  // 将所有标记和路径添加到地图
  console.log('Adding markers to map, total markers:', markers.length)
  console.log('Adding polylines to map, total polylines:', polylines.length)
  
  if (markers.length > 0) {
    map.add(markers)
  }
  
  if (polylines.length > 0) {
    map.add(polylines)
  }

  // 自动调整视野以包含所有标记
  if (allPoints.length > 0) {
    console.log('Setting fit view for', allPoints.length, 'points')
    // 如果只有一个点（一般是只有我的位置），更友好地居中并设置合适缩放
    if (allPoints.length === 1) {
      try {
        map.setCenter(allPoints[0])
        map.setZoom(14)
      } catch (e) {
        console.warn('单点居中失败，回退到 setFitView:', e)
        map.setFitView(markers, false, [50, 50, 50, 50])
      }
    } else {
      map.setFitView(markers, false, [50, 50, 50, 50])
    }
  }
  
  console.log('Map markers updated successfully')
}

// 页面加载时初始化
onMounted(async () => {
  window.addEventListener('storage', refreshUser)
  
  // 加载我的位置和所有供应商
  await Promise.all([
    loadMyLocation(),
    loadAllSuppliers()
  ])
  
  // 等待DOM渲染后初始化地图，并依赖 map.complete 事件进行标记更新
  await nextTick()
  initMap()

  // 作为容错回退：如果 map 在短时间内没有触发 complete，我们在 800ms 后再尝试一次更新标记
  setTimeout(() => {
    try {
      console.log('Fallback updateMapMarkers check — myLocation:', myLocation.value)
      updateMapMarkers()
    } catch (e) {
      console.warn('Fallback updateMapMarkers 失败:', e)
    }
  }, 800)
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', refreshUser)
  
  // 销毁地图
  if (map) {
    map.destroy()
    map = null
  }
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.nearby-suppliers-container {
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

/* 主内容区域 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-header h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.map-card {
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-section {
  margin-bottom: 20px;
}

.my-location-info {
  margin-top: 20px;
}

.location-info-content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.result-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-summary {
  margin-bottom: 20px;
}

.suppliers-list {
  margin-top: 20px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
}

.inventory-info {
  margin-top: 15px;
}

.map-container {
  margin: 20px 0;
}

.map-legend {
  margin-top: 10px;
  display: flex;
  gap: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-icon {
  font-size: 20px;
}

.legend-img {
  width: 20px;
  height: 20px;
  display: inline-block;
  vertical-align: middle;
  border-radius: 50%;
}

/* 药品候选项样式 */
.drug-suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.drug-name {
  flex: 1;
  color: #303133;
  font-size: 14px;
}

.drug-count {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}
</style>
