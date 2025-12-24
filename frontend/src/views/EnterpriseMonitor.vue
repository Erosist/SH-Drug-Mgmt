<template>
  <div class="enterprise-monitor">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>企业监控中心</h2>
          <p class="subtitle">监控所有企业的库存和订单情况</p>
        </div>
        <el-button type="primary" @click="goHome">返回首页</el-button>
      </div>
    </el-card>

    <!-- 仪表盘统计 -->
    <el-row :gutter="20" class="dashboard-stats">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#409EFF"><OfficeBuilding /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.enterprises?.total || 0 }}</div>
              <div class="stat-label">企业总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#67C23A"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.orders?.total || 0 }}</div>
              <div class="stat-label">订单总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#E6A23C"><Box /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.inventory?.total_records || 0 }}</div>
              <div class="stat-label">库存记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#F56C6C"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.inventory?.low_stock_alerts || 0 }}</div>
              <div class="stat-label">低库存预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 标签页切换 -->
    <el-card class="main-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 企业列表 -->
        <el-tab-pane label="企业列表" name="enterprises">
          <div class="filter-bar">
            <el-select v-model="enterpriseFilter.type" placeholder="企业类型" clearable style="width: 200px">
              <el-option label="全部" value=""></el-option>
              <el-option label="药店" value="PHARMACY"></el-option>
              <el-option label="供应商" value="SUPPLIER"></el-option>
              <el-option label="物流商" value="LOGISTICS"></el-option>
            </el-select>
            <el-button type="primary" @click="loadEnterprises">
              <el-icon><Search /></el-icon> 查询
            </el-button>
          </div>

          <el-table :data="enterprises" stripe v-loading="loading">
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="name" label="企业名称" min-width="200"></el-table-column>
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getEnterpriseTypeTag(row.type)">
                  {{ getEnterpriseTypeLabel(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="contact_person" label="联系人" width="120"></el-table-column>
            <el-table-column prop="contact_phone" label="联系电话" width="150"></el-table-column>
            <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip></el-table-column>
            <el-table-column prop="user_count" label="用户数" width="80"></el-table-column>
            <el-table-column prop="supply_count" label="供应品种" width="100"></el-table-column>
            <el-table-column label="订单统计" width="120">
              <template #default="{ row }">
                买: {{ row.order_count_as_buyer || 0 }} / 卖: {{ row.order_count_as_supplier || 0 }}
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                  {{ row.is_active ? '激活' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="enterprisePagination.page"
            v-model:page-size="enterprisePagination.per_page"
            :total="enterprisePagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadEnterprises"
            @size-change="loadEnterprises"
            style="margin-top: 20px; justify-content: center"
          />
        </el-tab-pane>

        <!-- 库存概览 -->
        <el-tab-pane label="库存概览" name="inventory">
          <div class="filter-bar">
            <el-input
              v-model="inventoryFilter.drug_name"
              placeholder="药品名称"
              clearable
              style="width: 200px"
            ></el-input>
            <el-select v-model="inventoryFilter.tenant_id" placeholder="选择企业" clearable filterable style="width: 250px">
              <el-option
                v-for="ent in enterpriseOptions"
                :key="ent.id"
                :label="ent.name"
                :value="ent.id"
              ></el-option>
            </el-select>
            <el-button type="primary" @click="loadInventory">
              <el-icon><Search /></el-icon> 查询
            </el-button>
          </div>

          <el-table :data="inventory" stripe v-loading="loading">
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column label="企业" min-width="180">
              <template #default="{ row }">
                <div>{{ row.tenant?.name }}</div>
                <div class="text-secondary" style="font-size: 12px">{{ row.tenant?.type }}</div>
              </template>
            </el-table-column>
            <el-table-column label="药品信息" min-width="250">
              <template #default="{ row }">
                <div><strong>{{ row.drug?.brand_name }}</strong></div>
                <div class="text-secondary" style="font-size: 12px">{{ row.drug?.generic_name }}</div>
                <div class="text-secondary" style="font-size: 12px">{{ row.drug?.specification }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="drug.manufacturer" label="生产厂家" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="available_quantity" label="可用数量" width="100" sortable>
              <template #default="{ row }">
                <el-tag :type="row.available_quantity < 10 ? 'danger' : 'success'">
                  {{ row.available_quantity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="unit_price" label="单价" width="100" sortable>
              <template #default="{ row }">
                ¥{{ row.unit_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="valid_until" label="有效期至" width="120"></el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'info'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.updated_at) }}
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="inventoryPagination.page"
            v-model:page-size="inventoryPagination.per_page"
            :total="inventoryPagination.total"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadInventory"
            @size-change="loadInventory"
            style="margin-top: 20px; justify-content: center"
          />
        </el-tab-pane>

        <!-- 订单概览 -->
        <el-tab-pane label="订单概览" name="orders">
          <div class="filter-bar">
            <el-select v-model="orderFilter.status" placeholder="订单状态" clearable style="width: 150px">
              <el-option label="全部" value=""></el-option>
              <el-option label="待确认" value="PENDING"></el-option>
              <el-option label="已确认" value="CONFIRMED"></el-option>
              <el-option label="已发货" value="SHIPPED"></el-option>
              <el-option label="已送达" value="DELIVERED"></el-option>
              <el-option label="已完成" value="COMPLETED"></el-option>
              <el-option label="已取消" value="CANCELLED"></el-option>
            </el-select>
            <el-select v-model="orderFilter.buyer_id" placeholder="采购方" clearable filterable style="width: 200px">
              <el-option
                v-for="ent in enterpriseOptions"
                :key="ent.id"
                :label="ent.name"
                :value="ent.id"
              ></el-option>
            </el-select>
            <el-select v-model="orderFilter.supplier_id" placeholder="供应方" clearable filterable style="width: 200px">
              <el-option
                v-for="ent in enterpriseOptions"
                :key="ent.id"
                :label="ent.name"
                :value="ent.id"
              ></el-option>
            </el-select>
            <el-button type="primary" @click="loadOrders">
              <el-icon><Search /></el-icon> 查询
            </el-button>
          </div>

          <el-table :data="orders" stripe v-loading="loading">
            <el-table-column prop="order_number" label="订单号" width="150"></el-table-column>
            <el-table-column label="采购方" min-width="150">
              <template #default="{ row }">
                {{ row.buyer?.name }}
              </template>
            </el-table-column>
            <el-table-column label="供应方" min-width="150">
              <template #default="{ row }">
                {{ row.supplier?.name }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getOrderStatusTag(row.status)">
                  {{ getOrderStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="订单金额" width="120" sortable>
              <template #default="{ row }">
                ¥{{ row.total_amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_quantity" label="总数量" width="100"></el-table-column>
            <el-table-column prop="items_count" label="明细数" width="80"></el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewOrderDetail(row.id)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="orderPagination.page"
            v-model:page-size="orderPagination.per_page"
            :total="orderPagination.total"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadOrders"
            @size-change="loadOrders"
            style="margin-top: 20px; justify-content: center"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="orderDetailVisible" title="订单详情" width="800px">
      <div v-if="currentOrder" v-loading="orderDetailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getOrderStatusTag(currentOrder.status)">
              {{ getOrderStatusLabel(currentOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="采购方">{{ currentOrder.buyer?.name }}</el-descriptions-item>
          <el-descriptions-item label="供应方">{{ currentOrder.supplier?.name }}</el-descriptions-item>
          <el-descriptions-item label="订单金额" :span="2">¥{{ currentOrder.total_amount?.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentOrder.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="确认时间">{{ formatDateTime(currentOrder.confirmed_at) }}</el-descriptions-item>
          <el-descriptions-item label="发货时间">{{ formatDateTime(currentOrder.shipped_at) }}</el-descriptions-item>
          <el-descriptions-item label="送达时间">{{ formatDateTime(currentOrder.delivered_at) }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentOrder.notes || '无' }}</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px">订单明细</h3>
        <el-table :data="currentOrder.items" border stripe>
          <el-table-column label="药品名称" min-width="200">
            <template #default="{ row }">
              <div><strong>{{ row.drug?.brand_name }}</strong></div>
              <div style="font-size: 12px; color: #909399">{{ row.drug?.generic_name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="drug.specification" label="规格" width="120"></el-table-column>
          <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
          <el-table-column prop="unit_price" label="单价" width="100">
            <template #default="{ row }">
              ¥{{ row.unit_price }}
            </template>
          </el-table-column>
          <el-table-column prop="subtotal" label="小计" width="120">
            <template #default="{ row }">
              ¥{{ row.subtotal.toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Document, Box, Warning, Search } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5000'

// 状态
const activeTab = ref('enterprises')
const loading = ref(false)
const statistics = ref({})

// 企业列表
const enterprises = ref([])
const enterpriseOptions = ref([])
const enterpriseFilter = ref({ type: '' })
const enterprisePagination = ref({ page: 1, per_page: 20, total: 0 })

// 库存列表
const inventory = ref([])
const inventoryFilter = ref({ drug_name: '', tenant_id: null })
const inventoryPagination = ref({ page: 1, per_page: 50, total: 0 })

// 订单列表
const orders = ref([])
const orderFilter = ref({ status: '', buyer_id: null, supplier_id: null })
const orderPagination = ref({ page: 1, per_page: 50, total: 0 })

// 订单详情
const orderDetailVisible = ref(false)
const orderDetailLoading = ref(false)
const currentOrder = ref(null)

// 获取token
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token')
  return { headers: { Authorization: `Bearer ${token}` } }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/regulator/statistics/dashboard`,
      getAuthHeaders()
    )
    statistics.value = response.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error(error.response?.data?.error || '加载统计数据失败')
  }
}

// 加载企业列表
const loadEnterprises = async () => {
  loading.value = true
  try {
    const params = {
      page: enterprisePagination.value.page,
      per_page: enterprisePagination.value.per_page,
      type: enterpriseFilter.value.type
    }
    const response = await axios.get(
      `${API_BASE_URL}/api/regulator/enterprises`,
      { ...getAuthHeaders(), params }
    )
    enterprises.value = response.data.enterprises
    enterprisePagination.value.total = response.data.total
    
    // 更新企业选项
    if (enterpriseOptions.value.length === 0) {
      enterpriseOptions.value = response.data.enterprises
    }
  } catch (error) {
    console.error('加载企业列表失败:', error)
    ElMessage.error(error.response?.data?.error || '加载企业列表失败')
  } finally {
    loading.value = false
  }
}

// 加载库存数据
const loadInventory = async () => {
  loading.value = true
  try {
    const params = {
      page: inventoryPagination.value.page,
      per_page: inventoryPagination.value.per_page,
      tenant_id: inventoryFilter.value.tenant_id,
      drug_name: inventoryFilter.value.drug_name
    }
    const response = await axios.get(
      `${API_BASE_URL}/api/regulator/inventory/overview`,
      { ...getAuthHeaders(), params }
    )
    inventory.value = response.data.inventory
    inventoryPagination.value.total = response.data.total
  } catch (error) {
    console.error('加载库存数据失败:', error)
    ElMessage.error(error.response?.data?.error || '加载库存数据失败')
  } finally {
    loading.value = false
  }
}

// 加载订单数据
const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: orderPagination.value.page,
      per_page: orderPagination.value.per_page,
      status: orderFilter.value.status,
      buyer_id: orderFilter.value.buyer_id,
      supplier_id: orderFilter.value.supplier_id
    }
    const response = await axios.get(
      `${API_BASE_URL}/api/regulator/orders/overview`,
      { ...getAuthHeaders(), params }
    )
    orders.value = response.data.orders
    orderPagination.value.total = response.data.total
  } catch (error) {
    console.error('加载订单数据失败:', error)
    ElMessage.error(error.response?.data?.error || '加载订单数据失败')
  } finally {
    loading.value = false
  }
}

// 查看订单详情
const viewOrderDetail = async (orderId) => {
  orderDetailVisible.value = true
  orderDetailLoading.value = true
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/regulator/orders/${orderId}`,
      getAuthHeaders()
    )
    currentOrder.value = response.data.order
  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error(error.response?.data?.error || '加载订单详情失败')
  } finally {
    orderDetailLoading.value = false
  }
}

// 标签页切换
const handleTabChange = (tabName) => {
  if (tabName === 'enterprises' && enterprises.value.length === 0) {
    loadEnterprises()
  } else if (tabName === 'inventory' && inventory.value.length === 0) {
    loadInventory()
  } else if (tabName === 'orders' && orders.value.length === 0) {
    loadOrders()
  }
}

// 工具函数
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getEnterpriseTypeLabel = (type) => {
  const labels = {
    PHARMACY: '药店',
    SUPPLIER: '供应商',
    LOGISTICS: '物流商',
    REGULATOR: '监管'
  }
  return labels[type] || type
}

const getEnterpriseTypeTag = (type) => {
  const tags = {
    PHARMACY: 'primary',
    SUPPLIER: 'success',
    LOGISTICS: 'warning',
    REGULATOR: 'danger'
  }
  return tags[type] || ''
}

const getOrderStatusLabel = (status) => {
  const labels = {
    PENDING: '待确认',
    CONFIRMED: '已确认',
    SHIPPED: '已发货',
    DELIVERED: '已送达',
    COMPLETED: '已完成',
    CANCELLED: '已取消'
  }
  return labels[status] || status
}

const getOrderStatusTag = (status) => {
  const tags = {
    PENDING: 'warning',
    CONFIRMED: 'primary',
    SHIPPED: 'info',
    DELIVERED: 'success',
    COMPLETED: 'success',
    CANCELLED: 'danger'
  }
  return tags[status] || ''
}

const goHome = () => {
  router.push({ name: 'home' })
}

// 初始化
onMounted(() => {
  loadStatistics()
  loadEnterprises()
})
</script>

<style scoped>
.enterprise-monitor {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-card h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.dashboard-stats {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.main-card {
  min-height: 600px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.text-secondary {
  color: #909399;
}

:deep(.el-pagination) {
  display: flex;
  justify-content: center;
}
</style>
