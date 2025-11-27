<template>
  <div class="logistics-order-management">
    <div class="header">
      <h2>物流订单管理</h2>
      <div class="company-info">
        <el-tag type="primary" size="large">
          {{ currentUser?.tenant_name || '物流公司' }}
        </el-tag>
      </div>
    </div>

    <!-- 订单状态统计 -->
    <div class="order-statistics">
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-number">{{ statistics.shipped }}</div>
          <div class="stat-label">待揽收</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-number">{{ statistics.in_transit }}</div>
          <div class="stat-label">运输中</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-number">{{ statistics.delivered }}</div>
          <div class="stat-label">已送达</div>
        </div>
      </el-card>
    </div>

    <!-- 状态筛选 -->
    <div class="status-filter">
      <el-button-group>
        <el-button 
          :type="selectedStatus === 'shipped' ? 'primary' : ''"
          @click="filterByStatus('shipped')"
        >
          待揽收 ({{ statistics.shipped }})
        </el-button>
        <el-button 
          :type="selectedStatus === 'in_transit' ? 'primary' : ''"
          @click="filterByStatus('in_transit')"
        >
          运输中 ({{ statistics.in_transit }})
        </el-button>
        <el-button 
          :type="selectedStatus === 'delivered' ? 'primary' : ''"
          @click="filterByStatus('delivered')"
        >
          已送达 ({{ statistics.delivered }})
        </el-button>
        <el-button 
          :type="selectedStatus === 'all' ? 'primary' : ''"
          @click="filterByStatus('all')"
        >
          全部 ({{ filteredOrders.length }})
        </el-button>
      </el-button-group>
    </div>

    <!-- 订单列表 -->
    <el-table :data="filteredOrders" v-loading="loading" stripe>
      <el-table-column prop="order_id" label="订单号" width="120" />
      <el-table-column prop="pharmacy_name" label="目的药房" width="150" />
      <el-table-column prop="supplier_name" label="供应商" width="150" />
      <el-table-column label="药品信息" width="200">
        <template #default="scope">
          <div class="drug-info">
            <div>{{ scope.row.drug_name }}</div>
            <div class="drug-specs">{{ scope.row.specifications }} × {{ scope.row.quantity }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="total_amount" label="订单金额" width="100">
        <template #default="scope">
          ¥{{ scope.row.total_amount }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="订单状态" width="120">
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="下单时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <div class="action-buttons">
            <!-- 待揽收状态：可以揽收 -->
            <el-button 
              v-if="scope.row.status === 'shipped'"
              type="primary" 
              size="small"
              @click="pickupOrder(scope.row)"
            >
              确认揽收
            </el-button>
            <!-- 运输中状态：可以确认送达 -->
            <el-button 
              v-if="scope.row.status === 'in_transit'"
              type="success" 
              size="small"
              @click="deliverOrder(scope.row)"
            >
              确认送达
            </el-button>
            <!-- 查看详情按钮 -->
            <el-button 
              type="info" 
              size="small"
              @click="viewOrderDetail(scope.row)"
            >
              查看详情
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 订单详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="订单详情" 
      width="60%"
    >
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ selectedOrder.order_id }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="getStatusTagType(selectedOrder.status)">
              {{ getStatusText(selectedOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="药房">{{ selectedOrder.pharmacy_name }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ selectedOrder.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="药品名称">{{ selectedOrder.drug_name }}</el-descriptions-item>
          <el-descriptions-item label="规格数量">{{ selectedOrder.specifications }} × {{ selectedOrder.quantity }}</el-descriptions-item>
          <el-descriptions-item label="单价">¥{{ selectedOrder.unit_price }}</el-descriptions-item>
          <el-descriptions-item label="总金额">¥{{ selectedOrder.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="下单时间">{{ formatDate(selectedOrder.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(selectedOrder.updated_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 物流信息 -->
        <div v-if="selectedOrder.logistics_company_id" class="logistics-info">
          <h4>物流信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="物流公司">{{ selectedOrder.logistics_company_name }}</el-descriptions-item>
            <el-descriptions-item label="配送状态">
              <el-tag :type="getStatusTagType(selectedOrder.status)">
                {{ getStatusText(selectedOrder.status) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api/orders'

// 状态管理
const loading = ref(false)
const orders = ref([])
const selectedStatus = ref('all')
const detailDialogVisible = ref(false)
const selectedOrder = ref(null)

// 用户信息
const currentUser = ref(JSON.parse(localStorage.getItem('user') || '{}'))

// 统计数据
const statistics = computed(() => {
  return {
    shipped: orders.value.filter(order => order.status === 'shipped').length,
    in_transit: orders.value.filter(order => order.status === 'in_transit').length,
    delivered: orders.value.filter(order => order.status === 'delivered').length
  }
})

// 过滤后的订单
const filteredOrders = computed(() => {
  if (selectedStatus.value === 'all') {
    return orders.value
  }
  return orders.value.filter(order => order.status === selectedStatus.value)
})

// 加载物流公司的订单
const fetchLogisticsOrders = async () => {
  try {
    loading.value = true
    console.log('获取物流订单, 当前用户:', currentUser.value)
    
    const response = await orderApi.getLogisticsOrders()
    console.log('物流订单响应:', response)
    
    if (response.success) {
      orders.value = response.data || []
      console.log('物流订单数据:', orders.value)
    } else {
      ElMessage.error(response.message || '获取订单失败')
    }
  } catch (error) {
    console.error('获取物流订单失败:', error)
    ElMessage.error('获取订单失败')
  } finally {
    loading.value = false
  }
}

// 状态筛选
const filterByStatus = (status) => {
  selectedStatus.value = status
}

// 确认揽收
const pickupOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确认揽收订单 ${order.order_id}？`,
      '确认揽收',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    loading.value = true
    const response = await orderApi.updateOrderStatus(order.order_id, 'in_transit')
    
    if (response.success) {
      ElMessage.success('订单已确认揽收')
      await fetchLogisticsOrders()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认揽收失败:', error)
      ElMessage.error('操作失败')
    }
  } finally {
    loading.value = false
  }
}

// 确认送达
const deliverOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确认订单 ${order.order_id} 已送达？`,
      '确认送达',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    
    loading.value = true
    const response = await orderApi.updateOrderStatus(order.order_id, 'delivered')
    
    if (response.success) {
      ElMessage.success('订单已确认送达')
      await fetchLogisticsOrders()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认送达失败:', error)
      ElMessage.error('操作失败')
    }
  } finally {
    loading.value = false
  }
}

// 查看订单详情
const viewOrderDetail = (order) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const statusTypes = {
    'shipped': 'warning',
    'in_transit': 'primary',
    'delivered': 'success'
  }
  return statusTypes[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusTexts = {
    'shipped': '待揽收',
    'in_transit': '运输中',
    'delivered': '已送达'
  }
  return statusTexts[status] || status
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchLogisticsOrders()
})
</script>

<style scoped>
.logistics-order-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #303133;
}

.company-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.order-statistics {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.status-filter {
  margin-bottom: 20px;
}

.drug-info {
  line-height: 1.5;
}

.drug-specs {
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.order-detail {
  margin-top: 20px;
}

.logistics-info {
  margin-top: 20px;
}

.logistics-info h4 {
  margin-bottom: 10px;
  color: #303133;
}
</style>
