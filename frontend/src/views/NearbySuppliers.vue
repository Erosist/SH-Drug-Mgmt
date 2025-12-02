<template>
  <div class="nearby-suppliers-container">
    <!-- 顶部标题 -->
    <div class="page-header">
      <h2>就近供应商推荐</h2>
      <p class="subtitle">根据您的位置查找最近的药品供应商</p>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-section">
        <el-form :model="searchForm" label-width="100px">
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
    <el-card class="result-card" v-if="searchResult">
      <template #header>
        <div class="card-header">
          <span>搜索结果</span>
          <div>
            <el-tag type="success">找到 {{ searchResult.filtered }} 个供应商</el-tag>
            <el-button 
              size="small" 
              :type="showMap ? 'primary' : ''"
              @click="showMap = !showMap"
              style="margin-left: 10px"
            >
              <el-icon><MapLocation /></el-icon>
              {{ showMap ? '隐藏地图' : '显示地图' }}
            </el-button>
          </div>
        </div>
      </template>

      <div class="result-summary">
        <el-descriptions :column="4" border size="small">
          <el-descriptions-item label="搜索位置">
            {{ searchResult.pharmacy_location.longitude.toFixed(6) }}, 
            {{ searchResult.pharmacy_location.latitude.toFixed(6) }}
          </el-descriptions-item>
          <el-descriptions-item label="总供应商数">
            {{ searchResult.total }}
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

      <!-- 地图容器 -->
      <div v-show="showMap" class="map-container">
        <div id="amap-container" style="width: 100%; height: 500px;"></div>
        <div class="map-legend">
          <div class="legend-item">
            <span class="legend-icon pharmacy">📍</span>
            <span>我的位置</span>
          </div>
          <div class="legend-item">
            <span class="legend-icon supplier">🏭</span>
            <span>供应商</span>
          </div>
        </div>
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
          <el-table-column prop="name" label="供应商名称" min-width="200" />
          <el-table-column prop="address" label="地址" min-width="250" />
          <el-table-column prop="distance_text" label="距离" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getDistanceType(row.distance)">
                {{ row.distance_text }}
              </el-tag>
            </template>
          </el-table-column>
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
        v-if="searchResult.suppliers.length === 0"
        description="未找到符合条件的供应商"
      >
        <el-button type="primary" @click="resetSearch">重新搜索</el-button>
      </el-empty>
    </el-card>

    <!-- 供应商详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="供应商详情" 
      width="600px"
    >
      <div v-if="currentSupplier">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="供应商名称">
            {{ currentSupplier.name }}
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag>{{ currentSupplier.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="距离">
            <el-tag type="success">{{ currentSupplier.distance_text }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="地址">
            {{ currentSupplier.address }}
          </el-descriptions-item>
          <el-descriptions-item label="统一社会信用代码">
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
          <el-descriptions-item label="经营范围">
            {{ currentSupplier.business_scope }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Location, MapLocation } from '@element-plus/icons-vue'
import { nearbyApi } from '@/api/nearby'

// 地图相关
let map = null
let markers = []
const showMap = ref(false)

// 搜索类型
const searchType = ref('location') // location, address, coords

// 搜索表单
const searchForm = reactive({
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
    const response = await nearbyApi.getMyLocation()
    if (response.data.success) {
      myLocation.value = response.data.tenant
      
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

// 更新我的位置
const updateMyLocation = async () => {
  try {
    await ElMessageBox.prompt('请输入您的详细地址', '更新位置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '例如：北京市朝阳区望京SOHO'
    }).then(async ({ value }) => {
      updatingLocation.value = true
      const response = await nearbyApi.updateMyLocation({
        address: value,
        city: searchForm.city || undefined
      })
      
      if (response.data.success) {
        ElMessage.success('位置更新成功')
        await loadMyLocation()
      }
    })
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('位置更新失败: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    updatingLocation.value = false
  }
}

// 搜索就近供应商
const searchNearbySuppliers = async () => {
  loading.value = true
  
  try {
    let params = {
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
      
      if (response.data.filtered === 0) {
        ElMessage.info('未找到符合条件的供应商，请尝试扩大搜索范围')
      } else {
        ElMessage.success(`找到 ${response.data.filtered} 个供应商`)
      }
    }
  } catch (error) {
    ElMessage.error('搜索失败: ' + (error.response?.data?.message || error.message))
    console.error('搜索错误:', error)
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.address = ''
  searchForm.city = ''
  searchForm.longitude = null
  searchForm.latitude = null
  searchForm.maxDistance = 50000
  searchForm.limit = 10
  searchForm.useApi = false
  searchResult.value = null
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
    center: [116.397128, 39.916527], // 默认中心点
    viewMode: '2D'
  })

  // 添加缩放控件
  map.addControl(new AMap.Scale())
  map.addControl(new AMap.ToolBar())
}

// 清除所有标记
const clearMarkers = () => {
  if (markers.length > 0) {
    map.remove(markers)
    markers = []
  }
}

// 添加标记到地图
const addMarkersToMap = () => {
  if (!map || !searchResult.value) return

  clearMarkers()

  const allPoints = []

  // 添加药店标记（红色）
  const pharmacyMarker = new AMap.Marker({
    position: [
      searchResult.value.pharmacy_location.longitude,
      searchResult.value.pharmacy_location.latitude
    ],
    title: '我的位置',
    icon: new AMap.Icon({
      size: new AMap.Size(32, 32),
      image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSIxMiIgZmlsbD0iI2VmNDQ0NCIvPjxjaXJjbGUgY3g9IjE2IiBjeT0iMTYiIHI9IjgiIGZpbGw9IiNmZmYiLz48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSI0IiBmaWxsPSIjZWY0NDQ0Ii8+PC9zdmc+',
      imageSize: new AMap.Size(32, 32)
    }),
    offset: new AMap.Pixel(-16, -16)
  })

  markers.push(pharmacyMarker)
  allPoints.push([
    searchResult.value.pharmacy_location.longitude,
    searchResult.value.pharmacy_location.latitude
  ])

  // 添加药店信息窗口
  const pharmacyInfo = new AMap.InfoWindow({
    content: `
      <div style="padding: 10px;">
        <h4 style="margin: 0 0 10px 0; color: #ef4444;">📍 我的位置</h4>
        <p style="margin: 5px 0;">经度: ${searchResult.value.pharmacy_location.longitude.toFixed(6)}</p>
        <p style="margin: 5px 0;">纬度: ${searchResult.value.pharmacy_location.latitude.toFixed(6)}</p>
      </div>
    `
  })

  pharmacyMarker.on('click', () => {
    pharmacyInfo.open(map, pharmacyMarker.getPosition())
  })

  // 添加供应商标记（蓝色）
  searchResult.value.suppliers.forEach((supplier, index) => {
    if (!supplier.longitude || !supplier.latitude) return

    const supplierMarker = new AMap.Marker({
      position: [supplier.longitude, supplier.latitude],
      title: supplier.name,
      label: {
        content: `${index + 1}`,
        direction: 'top',
        offset: new AMap.Pixel(0, -5)
      },
      icon: new AMap.Icon({
        size: new AMap.Size(32, 32),
        image: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSIxMiIgZmlsbD0iIzQwOTZmZiIvPjxjaXJjbGUgY3g9IjE2IiBjeT0iMTYiIHI9IjgiIGZpbGw9IiNmZmYiLz48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSI0IiBmaWxsPSIjNDA5NmZmIi8+PC9zdmc+',
        imageSize: new AMap.Size(32, 32)
      }),
      offset: new AMap.Pixel(-16, -16)
    })

    markers.push(supplierMarker)
    allPoints.push([supplier.longitude, supplier.latitude])

    // 添加供应商信息窗口
    const supplierInfo = new AMap.InfoWindow({
      content: `
        <div style="padding: 10px; min-width: 200px;">
          <h4 style="margin: 0 0 10px 0; color: #4096ff;">🏭 ${supplier.name}</h4>
          <p style="margin: 5px 0;"><strong>距离:</strong> ${supplier.distance_text}</p>
          <p style="margin: 5px 0;"><strong>地址:</strong> ${supplier.address}</p>
          <p style="margin: 5px 0;"><strong>联系人:</strong> ${supplier.contact_person}</p>
          <p style="margin: 5px 0;"><strong>电话:</strong> ${supplier.contact_phone}</p>
        </div>
      `
    })

    supplierMarker.on('click', () => {
      supplierInfo.open(map, supplierMarker.getPosition())
    })
  })

  // 将所有标记添加到地图
  map.add(markers)

  // 自动调整视野以包含所有标记
  if (allPoints.length > 0) {
    map.setFitView(markers, false, [50, 50, 50, 50])
  }
}

// 监听地图显示状态和搜索结果变化
watch([showMap, searchResult], async ([newShowMap, newSearchResult]) => {
  if (newShowMap && newSearchResult) {
    await nextTick()
    
    if (!map) {
      initMap()
    }
    
    // 延迟添加标记，确保地图已完全加载
    setTimeout(() => {
      addMarkersToMap()
    }, 100)
  }
})

// 页面加载时获取我的位置
onMounted(() => {
  loadMyLocation()
})
</script>

<style scoped>
.nearby-suppliers-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
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
</style>
