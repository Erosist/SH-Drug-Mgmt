<template>
  <div class="mock-order">
    <div class="header">
      <h3>药品采购下单</h3>
      <div class="header-actions">
        <el-button @click="refreshOrders" :loading="loading" icon="Refresh" circle />
<<<<<<< HEAD
        <el-tooltip v-if="!canUseRealApi" content="仅药店/管理员账号可以在此页面真实下单" placement="top">
=======
        <el-tooltip v-if="!canUseRealApi" content="仅药店/供应商/管理员账号可以在此页面真实下单" placement="top">
>>>>>>> feature/supplier-mock-order-permission
          <span>
            <el-button type="primary" :disabled="!canUseRealApi" icon="Plus">
              新建采购单
            </el-button>
          </span>
        </el-tooltip>
        <el-button
          v-else
          type="primary"
          @click="showCreateDialog = true"
          icon="Plus"
        >
          新建采购单
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="!canUseRealApi"
      type="info"
      show-icon
      :closable="false"
      class="auth-hint"
      title="当前仅供监管角色查看演示"
<<<<<<< HEAD
      description="如需真实下单或查看订单，请使用药店或管理员账号登录。监管账号不会请求后台接口。"
=======
      description="如需真实下单或查看订单，请使用药店、供应商或管理员账号登录。监管账号不会请求后台接口。"
>>>>>>> feature/supplier-mock-order-permission
    />

    <!-- 订单统计 -->
    <div class="stats-panel" v-if="canUseRealApi && orderStats">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8" :md="4">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.total || 0 }}</div>
              <div class="stats-label">总订单</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4">
          <el-card class="stats-card pending">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.pending || 0 }}</div>
              <div class="stats-label">待确认</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4">
          <el-card class="stats-card confirmed">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.confirmed || 0 }}</div>
              <div class="stats-label">已确认</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4">
          <el-card class="stats-card shipped">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.shipped || 0 }}</div>
              <div class="stats-label">已发货</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4">
          <el-card class="stats-card completed">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.completed || 0 }}</div>
              <div class="stats-label">已完成</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4">
          <el-card class="stats-card cancelled">
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.cancelled || 0 }}</div>
              <div class="stats-label">已取消</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选工具栏 -->
    <el-card v-if="canUseRealApi" class="filter-card" shadow="never">
      <div class="filter-toolbar">
        <el-input
          v-model="filters.orderNumber"
          placeholder="搜索订单号"
          style="width: 200px"
          clearable
          @input="handleFilter"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
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
          <el-option label="已取消" value="CANCELLED_BY_PHARMACY" />
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
    <el-card v-if="canUseRealApi" class="list-card" shadow="never">
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

          <el-table-column label="供应商" width="150">
            <template #default="{ row }">
              {{ row.supplier_tenant?.name || '-' }}
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

          <el-table-column label="操作" width="180" fixed="right">
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
                type="danger" 
                size="small"
                @click.stop="cancelOrder(row)"
              >
                取消订单
              </el-button>
              <el-button 
                v-if="row.status === 'DELIVERED'"
                type="success" 
                size="small"
                @click.stop="confirmReceipt(row)"
              >
                确认收货
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div v-if="ordersList.length > 0" class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.perPage"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>
    <el-card v-else class="list-card" shadow="never">
<<<<<<< HEAD
      <el-empty description="监管角色不加载真实订单，可切换到药店账号体验下单流程。" />
=======
      <el-empty description="监管角色不加载真实订单，可切换到药店或供应商账号体验下单流程。" />
>>>>>>> feature/supplier-mock-order-permission
    </el-card>

    <!-- 新建采购单对话框 -->
  <el-dialog
    v-model="showCreateDialog"
      title="新建采购单"
      width="600px"
      @closed="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="120px"
      >
        <el-form-item label="选择供应信息" prop="supply_info_id">
          <el-select
            v-model="createForm.supply_info_id"
            placeholder="请选择供应信息"
            filterable
            remote
            :remote-method="searchSupplyInfo"
            :loading="supplySearchLoading"
            style="width: 100%"
            @change="onSupplyInfoChange"
          >
            <el-option
              v-for="supply in supplyOptions"
              :key="supply.id"
              :label="`${supply.drug.generic_name} - ${supply.tenant.name} (¥${supply.unit_price})`"
              :value="supply.id"
            >
              <div class="supply-option">
                <div class="supply-drug">{{ supply.drug.generic_name }}</div>
                <div class="supply-info">
                  供应商: {{ supply.tenant.name }} | 
                  单价: ¥{{ supply.unit_price }} | 
                  可供: {{ supply.available_quantity }}
                </div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="采购数量" prop="quantity">
          <el-input-number
            v-model="createForm.quantity"
            :min="selectedSupplyInfo?.min_order_quantity || 1"
            :max="selectedSupplyInfo?.available_quantity || 9999"
            placeholder="请输入采购数量"
            style="width: 100%"
          />
          <div v-if="selectedSupplyInfo" class="quantity-tips">
            起订量: {{ selectedSupplyInfo.min_order_quantity }}，
            可供数量: {{ selectedSupplyInfo.available_quantity }}
          </div>
        </el-form-item>

        <el-form-item label="期望交付日期">
          <el-date-picker
            v-model="createForm.expected_delivery_date"
            type="date"
            placeholder="选择期望交付日期"
            style="width: 100%"
            :disabled-date="disabledDeliveryDate"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="createForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入订单备注（可选）"
          />
        </el-form-item>

        <el-form-item v-if="selectedSupplyInfo" label="订单预览">
          <div class="order-preview">
            <div class="preview-item">
              <span class="preview-label">药品:</span>
              <span class="preview-value">{{ selectedSupplyInfo.drug.generic_name }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">供应商:</span>
              <span class="preview-value">{{ selectedSupplyInfo.tenant.name }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">单价:</span>
              <span class="preview-value">¥{{ selectedSupplyInfo.unit_price }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">数量:</span>
              <span class="preview-value">{{ createForm.quantity || 0 }}</span>
            </div>
            <div class="preview-item total">
              <span class="preview-label">总金额:</span>
              <span class="preview-value">¥{{ calculatePreviewTotal() }}</span>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitOrder"
            :loading="submitLoading"
          >
            提交订单
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="订单详情"
      width="700px"
      @closed="selectedOrder = null"
    >
      <div v-if="selectedOrder" class="order-detail">
        <!-- 基本信息 -->
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
            <el-descriptions-item label="供应商">
              {{ selectedOrder.supplier_tenant?.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="订单总额">
              <span class="order-total">¥{{ calculateOrderTotal(selectedOrder) }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 药品明细 -->
        <div class="detail-section">
          <h4>药品明细</h4>
          <el-table :data="selectedOrder.items" border>
            <el-table-column prop="drug.generic_name" label="药品名称" />
            <el-table-column prop="drug.specification" label="规格" />
            <el-table-column prop="quantity" label="数量" align="right" />
            <el-table-column prop="unit_price" label="单价" align="right">
              <template #default="{ row }">
                ¥{{ row.unit_price }}
              </template>
            </el-table-column>
            <el-table-column label="小计" align="right">
              <template #default="{ row }">
                ¥{{ (row.quantity * row.unit_price).toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 物流信息 -->
        <div v-if="selectedOrder.tracking_number" class="detail-section">
          <h4>物流信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="运单号">
              {{ selectedOrder.tracking_number }}
            </el-descriptions-item>
            <el-descriptions-item label="物流公司">
              {{ selectedOrder.logistics_tenant?.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="发货时间">
              {{ selectedOrder.shipped_at ? formatDateTime(selectedOrder.shipped_at) : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="预计到达">
              {{ selectedOrder.delivered_at ? formatDateTime(selectedOrder.delivered_at) : '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 备注信息 -->
        <div v-if="selectedOrder.notes" class="detail-section">
          <h4>订单备注</h4>
          <div class="notes-content">
            {{ selectedOrder.notes }}
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button 
            v-if="selectedOrder && selectedOrder.status === 'PENDING'"
            type="danger" 
            @click="cancelOrder(selectedOrder)"
          >
            取消订单
          </el-button>
          <el-button 
            v-if="selectedOrder && selectedOrder.status === 'DELIVERED'"
            type="success" 
            @click="confirmReceipt(selectedOrder)"
          >
            确认收货
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Plus, Refresh
} from '@element-plus/icons-vue'
import { orderApi } from '@/api/orders'
import { supplyApi } from '@/api/supply'
import { formatDate } from '@/utils/date'
import { getCurrentUser } from '@/utils/authSession'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const supplySearchLoading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const selectedOrder = ref(null)
const createFormRef = ref(null)

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

// 创建订单表单
const createForm = reactive({
  supply_info_id: null,
  quantity: null,
  expected_delivery_date: null,
  notes: ''
})

// 供应信息选项
const supplyOptions = ref([])
const selectedSupplyInfo = computed(() => {
  return supplyOptions.value.find(s => s.id === createForm.supply_info_id)
})

const currentUser = ref(getCurrentUser())
<<<<<<< HEAD
const canUseRealApi = computed(() => {
  const role = currentUser.value?.role
  return role === 'pharmacy' || role === 'admin'
=======
const currentRole = computed(() => currentUser.value?.role)
const canUseRealApi = computed(() => {
  const role = currentRole.value
  return role === 'pharmacy' || role === 'supplier' || role === 'admin'
})
const orderRoleFilter = computed(() => {
  const role = currentRole.value
  if (role === 'supplier' || role === 'pharmacy') return 'my_purchases'
  return undefined
>>>>>>> feature/supplier-mock-order-permission
})
const syncUser = () => {
  currentUser.value = getCurrentUser()
}

// 表单验证规则
const createFormRules = {
  supply_info_id: [
    { required: true, message: '请选择供应信息', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入采购数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '采购数量必须大于0', trigger: 'blur' }
  ]
}

// 方法
const fetchOrders = async () => {
  if (!canUseRealApi.value) {
    ordersList.value = []
    pagination.total = 0
    return
  }
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage,
      order_number: filters.orderNumber || undefined,
      status: filters.status || undefined,
      drug_name: filters.drugName || undefined,
<<<<<<< HEAD
      role_filter: 'my_purchases' // 只显示我的采购订单
=======
      role_filter: orderRoleFilter.value
    }
    if (!params.role_filter) {
      delete params.role_filter
>>>>>>> feature/supplier-mock-order-permission
    }
    
    const response = await orderApi.getOrders(params)
    
    if (response.data && response.data.data) {
      ordersList.value = response.data.data.items || []
      pagination.total = response.data.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取订单列表失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config
    })
    ElMessage.error(`获取订单列表失败：${error.response?.data?.msg || error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}

const fetchOrderStats = async () => {
  if (!canUseRealApi.value) return
  try {
    const response = await orderApi.getOrderStats()
    
    if (response.data && response.data.data) {
      orderStats.value = response.data.data
    }
  } catch (error) {
    console.error('获取订单统计失败:', error)
  }
}

const refreshOrders = () => {
  if (!canUseRealApi.value) return
  fetchOrders()
  fetchOrderStats()
}

const handleFilter = () => {
  pagination.page = 1
  fetchOrders()
}

const resetFilters = () => {
  filters.orderNumber = ''
  filters.status = ''
  filters.drugName = ''
  handleFilter()
}

const handleSizeChange = (size) => {
  pagination.perPage = size
  pagination.page = 1
  fetchOrders()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchOrders()
}

const searchSupplyInfo = async (query) => {
  if (!canUseRealApi.value) {
    supplyOptions.value = []
    return
  }
  if (!query) {
    supplyOptions.value = []
    return
  }
  
  supplySearchLoading.value = true
  try {
    const response = await supplyApi.getSupplyList({
      drug_name: query,
      per_page: 20
    })
    
    if (response.data && response.data.data) {
      supplyOptions.value = response.data.data.items || []
    }
  } catch (error) {
    console.error('搜索供应信息失败:', error)
    ElMessage.error('搜索供应信息失败')
  } finally {
    supplySearchLoading.value = false
  }
}

const onSupplyInfoChange = () => {
  if (selectedSupplyInfo.value) {
    createForm.quantity = selectedSupplyInfo.value.min_order_quantity
  }
}

const resetCreateForm = () => {
  Object.assign(createForm, {
    supply_info_id: null,
    quantity: null,
    expected_delivery_date: null,
    notes: ''
  })
  supplyOptions.value = []
  
  if (createFormRef.value) {
    createFormRef.value.clearValidate()
  }
}

const submitOrder = async () => {
  if (!canUseRealApi.value) {
<<<<<<< HEAD
    ElMessage.warning('请使用药店或管理员账号登录后再下单')
=======
    ElMessage.warning('请使用药店、供应商或管理员账号登录后再下单')
>>>>>>> feature/supplier-mock-order-permission
    return
  }
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    
    submitLoading.value = true
    
    const orderData = {
      supply_info_id: createForm.supply_info_id,
      quantity: createForm.quantity,
      expected_delivery_date: createForm.expected_delivery_date ? 
        formatDate(createForm.expected_delivery_date) : undefined,
      notes: createForm.notes
    }
    
    await orderApi.createOrder(orderData)
    ElMessage.success('订单提交成功')
    
    showCreateDialog.value = false
    refreshOrders()
  } catch (error) {
    console.error('提交订单失败:', error)
    const message = error.response?.data?.msg || '订单提交失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    submitLoading.value = false
  }
}

const viewOrderDetail = (order) => {
  selectedOrder.value = order
  showDetailDialog.value = true
}

const cancelOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消此订单吗？取消后不可恢复！',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await orderApi.cancelOrder(order.id, {
      reason: '用户主动取消'
    })

    if (response.data) {
      ElMessage.success('订单取消成功')
      refreshOrders()
      showDetailDialog.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
      ElMessage.error('取消订单失败，请稍后重试')
    }
  }
}

const confirmReceipt = async (order) => {
  try {
    await ElMessageBox.confirm(
      '确认已收到货品？确认后订单将完成！',
      '确认收货',
      {
        confirmButtonText: '确认收货',
        cancelButtonText: '取消',
        type: 'success',
      }
    )

    const response = await orderApi.receiveOrder(order.id, {
      notes: '药店确认收货'
    })

    if (response.data) {
      ElMessage.success('确认收货成功，订单已完成')
      refreshOrders()
      showDetailDialog.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认收货失败:', error)
      ElMessage.error('确认收货失败，请稍后重试')
    }
  }
}

const calculateOrderTotal = (order) => {
  if (!order.items) return '0.00'
  return order.items.reduce((total, item) => {
    return total + (item.quantity * item.unit_price)
  }, 0).toFixed(2)
}

const calculatePreviewTotal = () => {
  if (!selectedSupplyInfo.value || !createForm.quantity) return '0.00'
  return (selectedSupplyInfo.value.unit_price * createForm.quantity).toFixed(2)
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
    'CANCELLED_BY_PHARMACY': '药店取消',
    'CANCELLED_BY_SUPPLIER': '供应商取消',
    'EXPIRED_CANCELLED': '超时取消'
  }
  return statusMap[status] || status
}

const disabledDeliveryDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 // 禁用今天之前的日期
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

watch(canUseRealApi, (authorized) => {
  if (authorized) {
    refreshOrders()
  } else {
    ordersList.value = []
    orderStats.value = {}
    pagination.total = 0
  }
})

// 生命周期
onMounted(() => {
  window.addEventListener('storage', syncUser)
  refreshOrders()
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', syncUser)
})
</script>

<style scoped>
.mock-order {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.auth-hint {
  margin-bottom: 16px;
}

.header h3 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 统计面板 */
.stats-panel {
  margin-bottom: 20px;
}

.stats-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
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

.stats-card.cancelled {
  border-left: 4px solid #f56c6c;
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

/* 列表 */
.list-card {
  min-height: 400px;
}

.orders-list-container {
  min-height: 300px;
}

.order-item {
  margin-bottom: 4px;
  line-height: 1.4;
}

.drug-name {
  font-weight: 600;
  color: #303133;
}

.drug-quantity {
  font-size: 12px;
  color: #909399;
}

.order-amount {
  font-weight: 600;
  color: #e6a23c;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 对话框 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 供应信息选项 */
.supply-option {
  line-height: 1.4;
}

.supply-drug {
  font-weight: 600;
  color: #303133;
}

.supply-info {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 数量提示 */
.quantity-tips {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 订单预览 */
.order-preview {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.preview-item.total {
  border-top: 1px solid #e4e7ed;
  padding-top: 8px;
  margin-top: 8px;
  font-weight: 600;
}

.preview-label {
  color: #606266;
}

.preview-value {
  color: #303133;
  font-weight: 500;
}

/* 订单详情 */
.order-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f2f5;
}

.order-total {
  color: #e6a23c;
  font-weight: 700;
  font-size: 16px;
}

.notes-content {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
  color: #606266;
  line-height: 1.5;
  border-left: 4px solid #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-toolbar > * {
    width: 100%;
  }
  
  .stats-panel .el-row {
    margin: 0 -4px;
  }
  
  .stats-panel .el-col {
    padding: 0 4px;
    margin-bottom: 8px;
  }
}

:deep(.el-card__body) {
  padding: 16px;
}

:deep(.el-descriptions__label) {
  color: #606266;
  font-weight: 600;
}

:deep(.el-descriptions__content) {
  color: #303133;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
