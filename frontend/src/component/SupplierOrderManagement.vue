<template>
  <div class="supplier-order-management">
    <!-- 订单统计 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.total || 0 }}</div>
              <div class="stats-label">总订单</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6">
          <el-card class="stats-card pending">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.pending || 0 }}</div>
              <div class="stats-label">待确认</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6">
          <el-card class="stats-card confirmed">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.confirmed || 0 }}</div>
              <div class="stats-label">已确认</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6">
          <el-card class="stats-card shipped">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.shipped || 0 }}</div>
              <div class="stats-label">已发货</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选工具栏 -->
    <el-card class="filter-card">
      <div class="filter-toolbar">
        <el-input
          v-model="filters.orderNumber"
          placeholder="订单号"
          style="width: 150px"
          clearable
          @input="handleFilter"
        />
        <el-select
          v-model="filters.status"
          placeholder="订单状态"
          style="width: 150px"
          clearable
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="待确认" value="PENDING" />
          <el-option label="已确认" value="CONFIRMED" />
          <el-option label="已发货" value="SHIPPED" />
          <el-option label="运输中" value="IN_TRANSIT" />
          <el-option label="已送达" value="DELIVERED" />
          <el-option label="已完成" value="COMPLETED" />
          <el-option label="已拒绝" value="CANCELLED_BY_SUPPLIER" />
        </el-select>
        <el-input
          v-model="filters.drugName"
          placeholder="搜索药品名称"
          style="width: 150px"
          clearable
          @input="handleFilter"
        />
        <el-button type="primary" @click="handleFilter" :loading="loading">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="list-card">
      <div v-loading="loading" class="orders-list-container">
        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && ordersList.length === 0" 
          description="暂无订单"
          :image-size="80"
        />
        
        <!-- 订单表格 -->
        <el-table
          v-else
          :data="ordersList"
          stripe
          @row-click="viewOrderDetail"
        >
          <el-table-column prop="order_number" label="订单号" width="160" />

          <el-table-column label="药品信息" width="200">
            <template #default="{ row }">
              <div v-for="item in row.items" :key="item.id" class="order-item">
                <div class="drug-name">{{ item.drug.generic_name }}</div>
                <div class="drug-quantity">数量: {{ item.quantity }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="采购商" width="150">
            <template #default="{ row }">
              {{ row.buyer_tenant?.name || '-' }}
            </template>
          </el-table-column>

          <el-table-column label="订单金额" width="120" align="right">
            <template #default="{ row }">
              <span class="order-amount">¥{{ calculateOrderTotal(row) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.status)"
                size="small"
              >
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="下单时间" width="150">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small"
                @click.stop="viewOrderDetail(row)"
              >
                查看详情
              </el-button>
              <el-button 
                v-if="row.status === 'PENDING'"
                type="success" 
                size="small"
                @click.stop="confirmOrder(row)"
              >
                确认订单
              </el-button>
              <el-button 
                v-if="row.status === 'PENDING'"
                type="danger" 
                size="small"
                @click.stop="rejectOrder(row)"
              >
                拒绝订单
              </el-button>
              <el-button 
                v-if="row.status === 'CONFIRMED'"
                type="warning" 
                size="small"
                @click.stop="shipOrder(row)"
              >
                发货
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <el-pagination
          v-if="pagination.total > 0"
          class="pagination"
          @current-change="handlePageChange"
          :current-page="pagination.page"
          :page-size="pagination.perPage"
          :total="pagination.total"
          layout="total, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 订单详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="订单详情"
      width="800px"
      @close="selectedOrder = null"
    >
      <div v-if="selectedOrder" class="order-detail">
        <div class="detail-section">
          <h4>订单信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="订单号">
              {{ selectedOrder.order_number }}
            </el-descriptions-item>
            <el-descriptions-item label="订单状态">
              <el-tag :type="getStatusType(selectedOrder.status)">
                {{ getStatusText(selectedOrder.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="下单时间">
              {{ formatDateTime(selectedOrder.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="期望交付时间">
              {{ selectedOrder.expected_delivery_date ? formatDate(selectedOrder.expected_delivery_date) : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="采购商">
              {{ selectedOrder.buyer_tenant?.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="订单总额">
              <span class="order-total">¥{{ calculateOrderTotal(selectedOrder) }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h4>药品明细</h4>
          <el-table :data="selectedOrder.items" border>
            <el-table-column prop="drug.generic_name" label="药品名称" />
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="unit_price" label="单价" width="100">
              <template #default="{ row }">
                ¥{{ row.unit_price }}
              </template>
            </el-table-column>
            <el-table-column label="小计" width="120">
              <template #default="{ row }">
                ¥{{ (row.quantity * row.unit_price).toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="selectedOrder.notes" class="detail-section">
          <h4>订单备注</h4>
          <p>{{ selectedOrder.notes }}</p>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button 
            v-if="selectedOrder && selectedOrder.status === 'PENDING'"
            type="success" 
            @click="confirmOrder(selectedOrder)"
          >
            确认订单
          </el-button>
          <el-button 
            v-if="selectedOrder && selectedOrder.status === 'PENDING'"
            type="danger" 
            @click="rejectOrder(selectedOrder)"
          >
            拒绝订单
          </el-button>
          <el-button 
            v-if="selectedOrder && selectedOrder.status === 'CONFIRMED'"
            type="warning" 
            @click="shipOrder(selectedOrder)"
          >
            发货
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 拒绝订单弹窗 -->
    <el-dialog
      v-model="showRejectDialog"
      title="拒绝订单"
      width="500px"
    >
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="拒绝原因" required>
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showRejectDialog = false">取消</el-button>
          <el-button 
            type="danger" 
            @click="submitReject"
            :loading="rejectLoading"
          >
            确认拒绝
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 发货弹窗 -->
    <el-dialog
      v-model="showShipDialog"
      title="发货"
      width="500px"
    >
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="运单号">
          <el-input
            v-model="shipForm.tracking_number"
            placeholder="请输入运单号（可选）"
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="shipForm.has_reported">
            已在「流通监管 - 流通数据上报」中完成该运单号的上报
          </el-checkbox>
          <div class="ship-hint">
            提示：未上报的运单号不可发货，请先到「流通监管」完成上报。
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showShipDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitShip"
            :loading="shipLoading"
          >
            确认发货
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { orderApi } from '@/api/orders'
import { formatDate, formatDateTime } from '@/utils/date'

// 响应式数据
const loading = ref(false)
const showDetailDialog = ref(false)
const showRejectDialog = ref(false)
const showShipDialog = ref(false)
const rejectLoading = ref(false)
const shipLoading = ref(false)
const selectedOrder = ref(null)

// 订单列表和统计
const ordersList = ref([])
const orderStats = ref({})

// 筛选条件
const filters = reactive({
  orderNumber: '',
  status: '',
  drugName: ''
})

// 分页
const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

// 拒绝表单
const rejectForm = reactive({
  reason: ''
})

// 发货表单
const shipForm = reactive({
  tracking_number: '',
  has_reported: false
})

// 计算属性
const shouldShowStats = computed(() => {
  return orderStats.value && Object.keys(orderStats.value).length > 0
})

// 方法
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage,
      order_number: filters.orderNumber || undefined,
      status: filters.status || undefined,
      drug_name: filters.drugName || undefined,
      role_filter: 'my_sales'  // 供应商查看销售订单
    }
    
    // 清理undefined参数
    Object.keys(params).forEach(key => {
      if (params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await orderApi.getOrders(params)
    
    if (response.data && response.data.data) {
      ordersList.value = response.data.data.items || []
      pagination.total = response.data.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchOrderStats = async () => {
  try {
    const response = await orderApi.getOrderStats()
    if (response.data && response.data.data) {
      orderStats.value = response.data.data
    }
  } catch (error) {
    console.error('获取订单统计失败:', error)
    // 不显示错误消息，因为这不是核心功能
  }
}

const handleFilter = () => {
  pagination.page = 1
  fetchOrders()
}

const resetFilters = () => {
  filters.orderNumber = ''
  filters.status = ''
  filters.drugName = ''
  pagination.page = 1
  fetchOrders()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchOrders()
}

const refreshOrders = () => {
  fetchOrders()
  fetchOrderStats()
}

const viewOrderDetail = (order) => {
  selectedOrder.value = order
  showDetailDialog.value = true
}

const confirmOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      '确定要确认此订单吗？确认后将进入待发货状态。',
      '确认订单',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await orderApi.confirmOrder(order.id, {
      action: 'accept'
    })

    if (response.data) {
      ElMessage.success('订单确认成功')
      refreshOrders()
      showDetailDialog.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认订单失败:', error)
      const message = error.response?.data?.msg || '确认订单失败'
      ElMessage.error(message)
    }
  }
}

const rejectOrder = (order) => {
  selectedOrder.value = order
  rejectForm.reason = ''
  showRejectDialog.value = true
  showDetailDialog.value = false
}

const submitReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }

  rejectLoading.value = true
  try {
    const response = await orderApi.confirmOrder(selectedOrder.value.id, {
      action: 'reject',
      reason: rejectForm.reason
    })

    if (response.data) {
      ElMessage.success('订单已拒绝')
      refreshOrders()
      showRejectDialog.value = false
    }
  } catch (error) {
    console.error('拒绝订单失败:', error)
    const message = error.response?.data?.msg || '拒绝订单失败'
    ElMessage.error(message)
  } finally {
    rejectLoading.value = false
  }
}

const shipOrder = (order) => {
  selectedOrder.value = order
  shipForm.tracking_number = ''
  shipForm.has_reported = false
  showShipDialog.value = true
  showDetailDialog.value = false
}

const submitShip = async () => {
  if (!shipForm.tracking_number?.trim()) {
    ElMessage.error('请输入运单号')
    return
  }
  if (!shipForm.has_reported) {
    ElMessage.error('请先在「流通监管」完成该运单号的上报后再发货')
    return
  }

  shipLoading.value = true
  try {
    const shipData = {}
    shipData.tracking_number = shipForm.tracking_number.trim()

    const response = await orderApi.shipOrder(selectedOrder.value.id, shipData)

    if (response.data) {
      ElMessage.success('发货成功')
      refreshOrders()
      showShipDialog.value = false
    }
  } catch (error) {
    console.error('发货失败:', error)
    const message = error.response?.data?.msg || '发货失败'
    ElMessage.error(message)
  } finally {
    shipLoading.value = false
  }
}

const calculateOrderTotal = (order) => {
  if (!order.items) return '0.00'
  return order.items.reduce((total, item) => {
    return total + (item.quantity * item.unit_price)
  }, 0).toFixed(2)
}

const getStatusType = (status) => {
  const statusMap = {
    'PENDING': 'warning',
    'CONFIRMED': 'primary',
    'SHIPPED': 'info',
    'IN_TRANSIT': 'info',
    'DELIVERED': 'success',
    'COMPLETED': 'success',
    'CANCELLED_BY_PHARMACY': 'danger',
    'CANCELLED_BY_SUPPLIER': 'danger',
    'EXPIRED_CANCELLED': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'PENDING': '待确认',
    'CONFIRMED': '已确认',
    'SHIPPED': '已发货',
    'IN_TRANSIT': '运输中',
    'DELIVERED': '已送达',
    'COMPLETED': '已完成',
    'CANCELLED_BY_PHARMACY': '买方取消',
    'CANCELLED_BY_SUPPLIER': '已拒绝',
    'EXPIRED_CANCELLED': '超时取消'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  refreshOrders()
})
</script>

<style scoped>
.supplier-order-management {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 16px;
}

.stats-card {
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stats-card.pending {
  border-left: 4px solid #e6a23c;
}

.stats-card.confirmed {
  border-left: 4px solid #409eff;
}

.stats-card.shipped {
  border-left: 4px solid #909399;
}

.stats-card.completed {
  border-left: 4px solid #67c23a;
}

.stats-content {
  padding: 10px;
}

.stats-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

/* 筛选工具栏 */
.filter-card {
  margin-bottom: 20px;
}

.filter-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* 订单列表 */
.list-card {
  flex: 1;
}

.orders-list-container {
  min-height: 300px;
}

.order-item {
  margin-bottom: 8px;
}

.order-item:last-child {
  margin-bottom: 0;
}

.drug-name {
  font-weight: 500;
  color: #303133;
}

.drug-quantity {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.order-amount {
  font-weight: bold;
  color: #E6A23C;
}

/* 分页 */
.pagination {
  margin-top: 20px;
  justify-content: center;
}

/* 订单详情 */
.order-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.order-total {
  font-weight: bold;
  color: #E6A23C;
  font-size: 16px;
}

/* 对话框 */
.dialog-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 响应式 */
@media (max-width: 768px) {
  .filter-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-section :deep(.el-row) {
    gap: 8px !important;
  }
}
</style>
