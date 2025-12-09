<template>
  <div class="mock-order">
    <div class="header">
      <h3>药品采购下单</h3>
      <div class="header-actions">
        <el-button @click="refreshOrders" :loading="loading" icon="Refresh" circle />
        <el-tooltip v-if="!canUseRealApi" content="仅药店/供应商/管理员账号可以在此页面真实下单" placement="top">
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
      description="如需真实下单或查看订单，请使用药店、供应商或管理员账号登录。监管账号不会请求后台接口。"
    />
    
    <!-- 订单统计 -->
    <div class="stats-panel" v-if="canUseRealApi && orderStats">
      <!-- 物流用户只显示相关状态 -->
      <el-row v-if="currentRole === 'logistics'" :gutter="16">
        <el-col :span="6">
          <el-card 
            class="stats-card" 
            :class="{ active: currentStatusFilter === '' }"
            @click="filterByStatus('')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.total || 0 }}</div>
              <div class="stats-label">总订单</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card 
            class="stats-card shipped" 
            :class="{ active: currentStatusFilter === 'SHIPPED' }"
            @click="filterByStatus('SHIPPED')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.shipped || 0 }}</div>
              <div class="stats-label">待揽收</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card 
            class="stats-card in-transit" 
            :class="{ active: currentStatusFilter === 'IN_TRANSIT' }"
            @click="filterByStatus('IN_TRANSIT')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.in_transit || 0 }}</div>
              <div class="stats-label">运输中</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card 
            class="stats-card delivered" 
            :class="{ active: currentStatusFilter === 'DELIVERED' }"
            @click="filterByStatus('DELIVERED')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.delivered || 0 }}</div>
              <div class="stats-label">已送达</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 非物流用户显示完整状态（优化为单行布局） -->
      <el-row v-else :gutter="12" class="stats-row-normal">
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact" 
            :class="{ active: currentStatusFilter === '' }"
            @click="filterByStatus('')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.total || 0 }}</div>
              <div class="stats-label">总订单</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact pending" 
            :class="{ active: currentStatusFilter === 'PENDING' }"
            @click="filterByStatus('PENDING')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.pending || 0 }}</div>
              <div class="stats-label">待确认</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact confirmed" 
            :class="{ active: currentStatusFilter === 'CONFIRMED' }"
            @click="filterByStatus('CONFIRMED')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.confirmed || 0 }}</div>
              <div class="stats-label">已确认</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact shipped" 
            :class="{ active: currentStatusFilter === 'SHIPPED' }"
            @click="filterByStatus('SHIPPED')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.shipped || 0 }}</div>
              <div class="stats-label">已发货</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact in-transit" 
            :class="{ active: currentStatusFilter === 'IN_TRANSIT' }"
            @click="filterByStatus('IN_TRANSIT')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.in_transit || 0 }}</div>
              <div class="stats-label">运输中</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact delivered" 
            :class="{ active: currentStatusFilter === 'DELIVERED' }"
            @click="filterByStatus('DELIVERED')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.delivered || 0 }}</div>
              <div class="stats-label">已送达</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact completed" 
            :class="{ active: currentStatusFilter === 'COMPLETED' }"
            @click="filterByStatus('COMPLETED')"
          >
            <div class="stats-content">
              <div class="stats-number">{{ orderStats.completed || 0 }}</div>
              <div class="stats-label">已完成</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="6" :sm="4" :md="3" :lg="3" :xl="3">
          <el-card 
            class="stats-card compact cancelled" 
            :class="{ active: currentStatusFilter === 'CANCELLED' }"
            @click="filterByStatus('CANCELLED')"
          >
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

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <!-- 查看详情按钮（所有状态都有） -->
                <el-button 
                  type="primary" 
                  size="small"
                  @click.stop="viewOrderDetail(row)"
                >
                  查看详情
                </el-button>

                <!-- 供应商操作 -->
                <template v-if="currentRole === 'supplier'">
                  <!-- 待确认状态：供应商可以确认或取消 -->
                  <template v-if="row.status === 'PENDING'">
                    <el-button 
                      type="success" 
                      size="small"
                      @click.stop="confirmOrder(row)"
                    >
                      确认订单
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small"
                      @click.stop="rejectOrder(row)"
                    >
                      拒绝订单
                    </el-button>
                  </template>
                  <!-- 已确认状态：供应商可以发货 -->
                  <template v-if="row.status === 'CONFIRMED'">
                    <el-button 
                      type="warning" 
                      size="small"
                      @click.stop="shipOrder(row)"
                    >
                      发货
                    </el-button>
                  </template>
                </template>

                <!-- 物流公司操作 -->
                <template v-if="currentRole === 'logistics'">
                  <!-- 待揽收状态（SHIPPED）：物流公司可以标记为运输中 -->
                  <template v-if="row.status === 'SHIPPED'">
                    <el-button 
                      type="primary" 
                      size="small"
                      @click.stop="markAsInTransit(row)"
                    >
                      标记运输中
                    </el-button>
                  </template>
                  <!-- 运输中状态：物流公司可以标记为已送达 -->
                  <template v-if="row.status === 'IN_TRANSIT'">
                    <el-button 
                      type="success" 
                      size="small"
                      @click.stop="markAsDelivered(row)"
                    >
                      标记已送达
                    </el-button>
                  </template>
                </template>

                <!-- 药店操作 -->
                <template v-if="currentRole === 'pharmacy'">
                  <!-- 待确认状态：药店可以取消 -->
                  <template v-if="row.status === 'PENDING'">
                    <el-button 
                      type="danger" 
                      size="small"
                      @click.stop="cancelOrderByPharmacy(row)"
                    >
                      取消订单
                    </el-button>
                  </template>
                  <!-- 已送达状态：药店可以确认收货 -->
                  <template v-if="row.status === 'DELIVERED'">
                    <el-button 
                      type="success" 
                      size="small"
                      @click.stop="confirmReceipt(row)"
                    >
                      确认收货
                    </el-button>
                  </template>
                </template>

                <!-- 管理员可以进行任何操作 -->
                <template v-if="currentRole === 'admin'">
                  <el-dropdown trigger="click" @command="(command) => handleAdminAction(command, row)">
                    <el-button size="small" type="info">
                      管理操作 <el-icon><ArrowDown /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="confirm" v-if="row.status === 'PENDING'">确认订单</el-dropdown-item>
                        <el-dropdown-item command="reject" v-if="row.status === 'PENDING'">拒绝订单</el-dropdown-item>
                        <el-dropdown-item command="ship" v-if="row.status === 'CONFIRMED'">发货</el-dropdown-item>
                        <el-dropdown-item command="deliver" v-if="['SHIPPED', 'IN_TRANSIT'].includes(row.status)">标记为已送达</el-dropdown-item>
                        <el-dropdown-item command="receive" v-if="row.status === 'DELIVERED'">确认收货</el-dropdown-item>
                        <el-dropdown-item command="cancel" v-if="!['COMPLETED', 'CANCELLED_BY_PHARMACY', 'CANCELLED_BY_SUPPLIER', 'EXPIRED_CANCELLED'].includes(row.status)">取消订单</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </div>
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
      <el-empty description="监管角色不加载真实订单，可切换到药店或供应商账号体验下单流程。" />
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
            :max="9999"
            placeholder="请输入采购数量"
            style="width: 100%"
            @change="handleQuantityChange"
            @input="handleQuantityInput"
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

    <!-- 发货对话框 -->
    <el-dialog
      v-model="showShipDialog"
      title="订单发货"
      width="500px"
      @closed="shipForm.tracking_number = ''; shipForm.logistics_tenant_id = null; shipForm.notes = ''"
    >
      <div v-if="selectedOrder" class="ship-order-form">
        <div class="order-info">
          <h4>订单信息</h4>
          <p><strong>订单号：</strong>{{ selectedOrder.order_number }}</p>
          <p><strong>收货方：</strong>{{ selectedOrder.buyer_tenant?.name || '-' }}</p>
        </div>
        
        <el-form :model="shipForm" label-width="100px" style="margin-top: 20px;">
          <el-form-item label="运单号" required>
            <el-input
              v-model="shipForm.tracking_number"
              placeholder="请输入运单号"
              maxlength="50"
            />
          </el-form-item>
          
          <el-form-item label="物流公司">
            <el-select
              v-model="shipForm.logistics_tenant_id"
              placeholder="选择物流公司"
              clearable
            >
              <el-option
                v-for="logistics in logisticsList"
                :key="logistics.id"
                :label="logistics.name"
                :value="logistics.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="发货备注">
            <el-input
              v-model="shipForm.notes"
              type="textarea"
              :rows="3"
              placeholder="请输入发货备注（可选）"
              maxlength="200"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showShipDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitShipOrder"
            :loading="submitLoading"
          >
            确认发货
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
            v-if="selectedOrder && selectedOrder.status === 'PENDING' && currentRole === 'pharmacy'"
            type="danger" 
            @click="cancelOrderByPharmacy(selectedOrder)"
          >
            取消订单
          </el-button>
          <el-button 
            v-if="selectedOrder && selectedOrder.status === 'DELIVERED' && currentRole === 'pharmacy'"
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
// Props
const props = defineProps({
  selectedSupplyId: {
    type: [String, Number],
    default: null
  }
})

import { ref, reactive, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Plus, Refresh, ArrowDown
} from '@element-plus/icons-vue'
import { orderApi } from '@/api/orders'
import { supplyApi } from '@/api/supply'
import api from '@/api/orders'  // 用于其他API调用
import { logisticsApi } from '@/api/logistics'
import { formatDate } from '@/utils/date'
import { getCurrentUser } from '@/utils/authSession'

// 获取路由实例
const route = useRoute()

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const supplySearchLoading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showShipDialog = ref(false)
const selectedOrder = ref(null)
const createFormRef = ref(null)

// 订单列表和统计
const ordersList = ref([])
const orderStats = ref({})
const currentStatusFilter = ref('')  // 当前选中的状态过滤器

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

// 发货表单
const shipForm = reactive({
  tracking_number: '',
  logistics_tenant_id: null,
  notes: ''
})

// 供应信息选项
const supplyOptions = ref([])
const selectedSupplyInfo = computed(() => {
  return supplyOptions.value.find(s => s.id === createForm.supply_info_id)
})

// 物流公司列表
const logisticsList = ref([])

const currentUser = ref(getCurrentUser())
const currentRole = computed(() => currentUser.value?.role)
const canUseRealApi = computed(() => {
  const role = currentRole.value
  const user = currentUser.value
  console.log('canUseRealApi - 完整检查:')
  console.log('  currentUser:', user)
  console.log('  currentRole:', role)
  console.log('  user?.role:', user?.role)
  console.log('  localStorage token:', localStorage.getItem('token'))
  console.log('  localStorage user:', localStorage.getItem('user'))
  
  const canUse = role === 'pharmacy' || role === 'supplier' || role === 'admin' || role === 'logistics'
  console.log('  canUse result:', canUse)
  return canUse
})
const orderRoleFilter = computed(() => {
  // 后端已根据用户角色自动过滤，无需前端指定role_filter
  return undefined
})
const syncUser = () => {
  currentUser.value = getCurrentUser()
  console.log('MockOrder - syncUser called, new user:', getCurrentUser())
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
  console.log('fetchOrders - canUseRealApi:', canUseRealApi.value)
  console.log('fetchOrders - currentUser:', currentUser.value)
  console.log('fetchOrders - currentRole:', currentRole.value)
  
  if (!canUseRealApi.value) {
    console.log('fetchOrders - canUseRealApi is false, clearing orders')
    ordersList.value = []
    pagination.total = 0
    return
  }
  loading.value = true
  try {
    // 处理状态过滤：如果是CANCELLED，需要获取所有取消状态的订单
    let statusParam = currentStatusFilter.value || filters.status || undefined
    
    const params = {
      page: pagination.page,
      per_page: pagination.perPage,
      order_number: filters.orderNumber || undefined,
      status: statusParam === 'CANCELLED' ? undefined : statusParam, // 如果是CANCELLED，先不传status，在前端过滤
      drug_name: filters.drugName || undefined,
      role_filter: orderRoleFilter.value
    }
    if (!params.role_filter) {
      delete params.role_filter
    }
    
    console.log('fetchOrders - 请求参数:', params)
    
    const response = await orderApi.getOrders(params)
    
    console.log('fetchOrders - API响应:', response)
    console.log('fetchOrders - 响应数据:', response.data)
    
    if (response.data && response.data.data) {
      let items = response.data.data.items || []
      
      // 如果用户选择了"已取消"过滤器，在前端过滤出所有取消状态的订单
      if (currentStatusFilter.value === 'CANCELLED') {
        const cancelledStatuses = ['CANCELLED_BY_PHARMACY', 'CANCELLED_BY_SUPPLIER', 'EXPIRED_CANCELLED']
        items = items.filter(order => cancelledStatuses.includes(order.status))
        console.log('fetchOrders - 已取消状态过滤后的订单:', items)
      }
      
      ordersList.value = items
      pagination.total = response.data.data.pagination?.total || 0
      
      console.log('fetchOrders - 设置订单列表:', ordersList.value)
      console.log('fetchOrders - 总数:', pagination.total)
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

// 获取物流公司列表
const fetchLogisticsCompanies = async () => {
  try {
    const response = await logisticsApi.getCompanies()
    if (response.data && response.data.data) {
      logisticsList.value = response.data.data
      console.log('获取物流公司列表成功:', logisticsList.value)
    }
  } catch (error) {
    console.error('获取物流公司列表失败:', error)
    ElMessage.error('获取物流公司列表失败')
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

const filterByStatus = (status) => {
  console.log('filterByStatus:', status)
  currentStatusFilter.value = status
  filters.status = ''  // 清空筛选工具栏的状态选择
  pagination.page = 1
  fetchOrders()
}

const resetFilters = () => {
  filters.orderNumber = ''
  filters.status = ''
  filters.drugName = ''
  currentStatusFilter.value = ''
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

// 防抖计时器，避免频繁弹窗
let quantityCheckTimer = null
let lastDialogTime = 0
let isAutoAdjusting = false  // 标记是否正在自动调整，避免循环触发

// 监听数量变化，检查是否超过可供数量
const handleQuantityChange = (value) => {
  console.log('handleQuantityChange - 数量变化:', value, 'isAutoAdjusting:', isAutoAdjusting)
  
  // 如果是自动调整导致的变化，跳过检查
  if (isAutoAdjusting) {
    console.log('handleQuantityChange - 正在自动调整，跳过检查')
    return
  }
  
  checkQuantityExceedsLimit(value, 'change')
}

// 监听数量输入，检查是否超过可供数量
const handleQuantityInput = (value) => {
  console.log('handleQuantityInput - 数量输入:', value, 'isAutoAdjusting:', isAutoAdjusting)
  
  // 如果是自动调整导致的变化，跳过检查
  if (isAutoAdjusting) {
    console.log('handleQuantityInput - 正在自动调整，跳过检查')
    return
  }
  
  // 清除之前的计时器
  if (quantityCheckTimer) {
    clearTimeout(quantityCheckTimer)
  }
  
  // 设置防抖，避免用户快速输入时频繁触发
  quantityCheckTimer = setTimeout(() => {
    checkQuantityExceedsLimit(value, 'input')
  }, 500) // 500ms 防抖
}

// 统一的数量检查函数
const checkQuantityExceedsLimit = (value, triggerSource) => {
  console.log(`checkQuantityExceedsLimit - 来源:${triggerSource}, 数量:${value}`)
  console.log('checkQuantityExceedsLimit - 当前选择的供应信息:', selectedSupplyInfo.value)
  
  if (!selectedSupplyInfo.value) {
    console.log('checkQuantityExceedsLimit - 没有选择供应信息，跳过检查')
    return
  }
  
  const availableQty = selectedSupplyInfo.value.available_quantity
  const minOrderQty = selectedSupplyInfo.value.min_order_quantity
  
  console.log('checkQuantityExceedsLimit - 可供数量:', availableQty, '输入数量:', value)
  
  // 如果输入的数量超过可供数量，仅弹窗提示，不自动调整
  if (value > availableQty) {
    console.log('checkQuantityExceedsLimit - 数量超过可供量，显示弹窗')
    
    // 防止短时间内重复弹窗
    const now = Date.now()
    if (now - lastDialogTime > 2000) { // 2秒内不重复弹窗
      lastDialogTime = now
      showSupplyShortageDialog(availableQty, value)
    } else {
      console.log('checkQuantityExceedsLimit - 短时间内已显示过弹窗，跳过')
    }
  } else {
    console.log('checkQuantityExceedsLimit - 数量在可接受范围内')
  }
}

// 显示供应量不足弹窗的函数
const showSupplyShortageDialog = (availableQty, requestedQty) => {
  // 使用美观的弹窗提示
  ElMessageBox.alert(
    `该药品当前库存不足！

您输入的数量：${requestedQty} 个
最大可购买数量：${availableQty} 个

系统将自动调整采购数量为 ${availableQty} 个。`,
    '供应量不足提示',
    {
      confirmButtonText: '确定',
      type: 'warning',
      dangerouslyUseHTMLString: false,
      customClass: 'supply-shortage-alert',
      center: true
    }
  ).then(() => {
    console.log('showSupplyShortageDialog - 用户确认了弹窗，自动调整数量到最大可供量')
    autoAdjustQuantity(availableQty)
  }).catch(() => {
    console.log('showSupplyShortageDialog - 用户取消了弹窗，自动调整数量到最大可供量')
    autoAdjustQuantity(availableQty)
  })
}

// 自动调整数量的函数
const autoAdjustQuantity = (availableQty) => {
  // 设置标记，避免循环触发检查
  isAutoAdjusting = true
  
  // 设置数量为最大可供量
  createForm.quantity = availableQty
  
  // 延迟重置标记，确保变化事件已经处理完毕
  setTimeout(() => {
    isAutoAdjusting = false
    console.log('autoAdjustQuantity - 自动调整完成，重置标记')
  }, 100)
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
  
  // 清除防抖计时器和弹窗状态
  if (quantityCheckTimer) {
    clearTimeout(quantityCheckTimer)
    quantityCheckTimer = null
  }
  lastDialogTime = 0
  isAutoAdjusting = false  // 重置自动调整标记
  
  // 当用户关闭对话框时，也清除URL中的查询参数
  clearSupplyIdFromUrl()
}

const submitOrder = async () => {
  if (!canUseRealApi.value) {
    ElMessage.warning('请使用药店、供应商或管理员账号登录后再下单')
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
    const errorData = error.response?.data
    const message = errorData?.msg || '订单提交失败，请稍后重试'
    
    // 如果是库存不足错误，使用友好的弹窗提示
    if (message.includes('库存不足') || message.includes('供应量不足')) {
      console.log('submitOrder - 检测到供应量不足错误，显示弹窗')
      console.log('submitOrder - 错误消息:', message)
      console.log('submitOrder - 错误数据:', errorData)
      
      const availableQty = errorData?.available_quantity
      const requestedQty = errorData?.requested_quantity
      
      let alertMessage = message
      if (availableQty !== undefined && requestedQty !== undefined) {
        alertMessage = `抱歉，该药品当前供应量不足！

您需要采购：${requestedQty} 个
当前库存：${availableQty} 个
缺少数量：${requestedQty - availableQty} 个

请调整采购数量或联系供应商补货。`
      }
      
      console.log('submitOrder - 即将显示弹窗，消息:', alertMessage)
      
      ElMessageBox.alert(
        alertMessage,
        '供应量不足',
        {
          confirmButtonText: '我知道了',
          type: 'warning',
          dangerouslyUseHTMLString: false,
          customClass: 'supply-shortage-alert',
          center: true
        }
      ).then(() => {
        console.log('submitOrder - 用户确认了供应量不足弹窗')
      }).catch(() => {
        console.log('submitOrder - 用户取消了供应量不足弹窗')
      })
    } else {
      // 其他错误使用普通消息提示
      ElMessage.error(message)
    }
  } finally {
    submitLoading.value = false
  }
}

const viewOrderDetail = (order) => {
  selectedOrder.value = order
  showDetailDialog.value = true
}

// 供应商确认订单
const confirmOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要确认订单 ${order.order_number} 吗？`,
      '确认订单',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'success',
      }
    )

    const response = await orderApi.confirmOrder(order.id, {
      action: 'accept',
      notes: '供应商确认接受订单'
    })

    if (response.data) {
      ElMessage.success('订单确认成功')
      refreshOrders()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认订单失败:', error)
      ElMessage.error('确认订单失败，请稍后重试')
    }
  }
}

// 供应商拒绝订单
const rejectOrder = async (order) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      `拒绝订单 ${order.order_number}，请输入拒绝原因：`,
      '拒绝订单',
      {
        confirmButtonText: '确认拒绝',
        cancelButtonText: '取消',
        inputPattern: /.{1,}/,
        inputErrorMessage: '请输入拒绝原因',
        inputPlaceholder: '请输入拒绝原因'
      }
    )

    const response = await orderApi.confirmOrder(order.id, {
      action: 'reject',
      reason: reason,
      notes: `供应商拒绝订单：${reason}`
    })

    if (response.data) {
      ElMessage.success('订单拒绝成功')
      refreshOrders()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝订单失败:', error)
      ElMessage.error('拒绝订单失败，请稍后重试')
    }
  }
}

// 供应商发货
const shipOrder = async (order) => {
  selectedOrder.value = order
  // 重置发货表单
  shipForm.tracking_number = ''
  shipForm.logistics_tenant_id = null
  shipForm.notes = ''
  
  showShipDialog.value = true
  showDetailDialog.value = false
}

// 提交发货信息
const submitShipOrder = async () => {
  if (!shipForm.tracking_number.trim()) {
    ElMessage.error('请输入运单号')
    return
  }

  try {
    submitLoading.value = true
    
    const shipData = {}
    if (shipForm.tracking_number) {
      shipData.tracking_number = shipForm.tracking_number
    }
    if (shipForm.logistics_tenant_id) {
      shipData.logistics_tenant_id = shipForm.logistics_tenant_id
    }
    if (shipForm.notes) {
      shipData.notes = shipForm.notes
    }

    const response = await orderApi.shipOrder(selectedOrder.value.id, shipData)

    if (response.data) {
      ElMessage.success('发货成功')
      showShipDialog.value = false
      refreshOrders()
    }
  } catch (error) {
    console.error('发货失败:', error)
    ElMessage.error('发货失败，请稍后重试')
  } finally {
    submitLoading.value = false
  }
}

// 药店取消订单
const cancelOrderByPharmacy = async (order) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      `确定要取消订单 ${order.order_number} 吗？请输入取消原因：`,
      '取消订单',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '不取消',
        inputPattern: /.{1,}/,
        inputErrorMessage: '请输入取消原因',
        inputPlaceholder: '请输入取消原因'
      }
    )

    const response = await orderApi.cancelOrder(order.id, {
      reason: reason
    })

    if (response.data) {
      ElMessage.success('订单取消成功')
      refreshOrders()
      if (showDetailDialog.value) {
        showDetailDialog.value = false
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
      ElMessage.error('取消订单失败，请稍后重试')
    }
  }
}

// 管理员操作处理
const handleAdminAction = async (command, order) => {
  switch (command) {
    case 'confirm':
      await confirmOrder(order)
      break
    case 'reject':
      await rejectOrder(order)
      break
    case 'ship':
      await shipOrder(order)
      break
    case 'deliver':
      await markAsDelivered(order)
      break
    case 'receive':
      await confirmReceipt(order)
      break
    case 'cancel':
      await cancelOrderByPharmacy(order)
      break
  }
}

// 物流公司标记为运输中
const markAsInTransit = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要将订单 ${order.order_number} 标记为运输中吗？`,
      '标记运输中',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info',
      }
    )

    // 调用后端API更新订单状态
    const response = await orderApi.updateOrderStatus(order.id, 'IN_TRANSIT')

    if (response.data && response.data.success) {
      ElMessage.success(response.data.message || '订单已标记为运输中')
      
      // 立即更新本地订单状态，避免等待刷新
      const orderIndex = ordersList.value.findIndex(o => o.id === order.id)
      if (orderIndex !== -1) {
        ordersList.value[orderIndex].status = 'IN_TRANSIT'
        ordersList.value[orderIndex].updated_at = new Date().toISOString()
      }
      
      // 然后刷新整个列表确保数据同步
      refreshOrders()
    } else {
      throw new Error(response.data?.message || '更新失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('标记运输中失败:', error)
      const message = error.response?.data?.message || error.response?.data?.msg || error.message || '操作失败，请稍后重试'
      ElMessage.error(message)
    }
  }
}

// 标记订单为已送达（管理员和物流用户）
const markAsDelivered = async (order) => {
  try {
    const title = currentRole.value === 'logistics' ? '确认送达' : '标记为已送达'
    const message = currentRole.value === 'logistics' 
      ? `确定要将订单 ${order.order_number} 标记为已送达吗？`
      : `确定要将订单 ${order.order_number} 标记为已送达吗？\n注意：这是临时功能，实际应用中由物流系统自动更新。`
    
    await ElMessageBox.confirm(
      message,
      title,
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'success',
      }
    )

    if (currentRole.value === 'logistics') {
      // 物流用户调用真正的API
      const response = await orderApi.updateOrderStatus(order.id, 'DELIVERED')

      if (response.data && response.data.success) {
        ElMessage.success(response.data.message || '订单已标记为已送达')
        
        // 立即更新本地订单状态，避免等待刷新
        const orderIndex = ordersList.value.findIndex(o => o.id === order.id)
        if (orderIndex !== -1) {
          ordersList.value[orderIndex].status = 'DELIVERED'
          ordersList.value[orderIndex].updated_at = new Date().toISOString()
        }
        
        // 然后刷新整个列表确保数据同步
        refreshOrders()
      } else {
        throw new Error(response.data?.message || '更新失败')
      }
    } else {
      // 管理员的临时解决方案
      ElMessage.warning('这是一个模拟操作。在实际应用中，订单状态由物流系统自动更新。请手动刷新页面查看最新状态。')
      refreshOrders()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('标记为已送达失败:', error)
      const message = currentRole.value === 'logistics' 
        ? error.response?.data?.message || error.response?.data?.msg || '操作失败，请稍后重试'
        : '操作失败，请稍后重试'
      ElMessage.error(message)
    }
  }
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

    console.log('confirmReceipt - 开始确认收货，订单ID:', order.id)
    console.log('confirmReceipt - 订单详情:', order)

    const response = await orderApi.receiveOrder(order.id, {
      notes: '药店确认收货'
    })

    console.log('confirmReceipt - API响应:', response)

    if (response.data) {
      ElMessage.success('确认收货成功，订单已完成')
      refreshOrders()
      if (showDetailDialog.value) {
        showDetailDialog.value = false
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认收货失败:', error)
      console.error('错误详情:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config,
        url: error.config?.url
      })
      
      let errorMessage = '确认收货失败，请稍后重试'
      if (error.response?.data?.msg) {
        errorMessage = `确认收货失败：${error.response.data.msg}`
      } else if (error.response?.status === 404) {
        errorMessage = '订单不存在或已被删除'
      } else if (error.response?.status === 403) {
        errorMessage = '权限不足，无法确认收货'
      } else if (error.response?.status === 400) {
        errorMessage = '订单状态不允许确认收货'
      }
      
      ElMessage.error(errorMessage)
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

const getStatusText = (status) => {
  const role = currentRole.value
  
  // 物流用户看到的状态描述
  if (role === 'logistics') {
    const logisticsStatusMap = {
      'SHIPPED': '待揽收',
      'IN_TRANSIT': '运输中',
      'DELIVERED': '已送达'
    }
    return logisticsStatusMap[status] || status
  }
  
  // 药店和供应商用户看到的状态描述
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

// 监听传入的供应信息ID
const handlePreselectedSupply = async (supplyId) => {
  try {
    supplySearchLoading.value = true
    
    // 通过API获取指定的供应信息详情
    const response = await supplyApi.getSupplyInfo(supplyId)
    
    if (response.data?.data) {
      const supply = response.data.data
      
      // 将供应信息添加到选项列表中
      supplyOptions.value = [supply]
      
      // 预选这个供应信息
      createForm.supply_info_id = supply.id
      onSupplyInfoChange(supply.id)
      
      // 自动打开新建采购单对话框
      showCreateDialog.value = true
      
      // 清除URL中的supplyId查询参数，避免重复触发
      clearSupplyIdFromUrl()
    } else {
      ElMessage.warning('未找到指定的供应信息')
      showCreateDialog.value = true
      clearSupplyIdFromUrl()
    }
  } catch (error) {
    console.error('预选供应信息失败:', error)
    ElMessage.warning('加载选定的供应信息失败，请手动选择')
    showCreateDialog.value = true
    clearSupplyIdFromUrl()
  } finally {
    supplySearchLoading.value = false
  }
}

// 清除URL中的supplyId查询参数
const clearSupplyIdFromUrl = () => {
  // 需要从父组件或路由中清除supplyId参数
  // 这里我们需要通知父组件清除查询参数
  if (typeof window !== 'undefined' && window.history?.replaceState) {
    const url = new URL(window.location)
    url.searchParams.delete('supplyId')
    url.searchParams.delete('t') // 同时清除时间戳参数
    // 同时清除tab参数，避免下次进入时自动打开对话框
    // 只保留基础的B2B页面URL
    url.searchParams.delete('tab')
    window.history.replaceState({}, '', url)
  }
  
  // 不要重置processedSupplyData，而是标记为已完成状态
  // 这样可以防止用户手动导航时重新触发
  if (processedSupplyData.value.id && processedSupplyData.value.timestamp > 0) {
    // 保留当前数据，这样下次相同的请求会被正确识别为重复
    console.log('MockOrder - clearSupplyIdFromUrl: 保留processedSupplyData', processedSupplyData.value)
  }
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

// 已处理的供应信息ID和时间戳，避免重复处理
const processedSupplyData = ref({ id: null, timestamp: 0 })

// 监听路由查询参数中的supplyId变化
watch(() => route.query.supplyId, async (supplyId) => {
  console.log('MockOrder - Route supplyId changed:', supplyId, 'canUseRealApi:', canUseRealApi.value)
  console.log('MockOrder - Route query:', route.query)
  console.log('MockOrder - processedSupplyData:', processedSupplyData.value)
  
  // 如果没有supplyId参数，跳过处理
  if (!supplyId) {
    console.log('MockOrder - No supplyId, skipping')
    return
  }
  
  // 双重检查：确保URL中确实存在supplyId参数
  // 这是为了防止Vue组件状态与实际URL不同步的情况
  if (typeof window !== 'undefined') {
    const currentUrl = new URL(window.location)
    const actualSupplyId = currentUrl.searchParams.get('supplyId')
    if (!actualSupplyId) {
      console.log('MockOrder - URL中没有supplyId参数，跳过处理（可能是组件状态残留）')
      return
    }
    if (actualSupplyId !== String(supplyId)) {
      console.log('MockOrder - URL中的supplyId与路由参数不匹配，跳过处理')
      return
    }
  }
  
  // 检查是否有时间戳参数，如果有就使用它来判断是否为新操作
  const routeTimestamp = route.query.t ? parseInt(route.query.t) : 0
  console.log('MockOrder - routeTimestamp:', routeTimestamp)
  console.log('MockOrder - processed timestamp:', processedSupplyData.value.timestamp)
  
  // 如果有相同的时间戳，说明已经处理过了
  if (routeTimestamp > 0 && processedSupplyData.value.timestamp === routeTimestamp) {
    console.log('MockOrder - 相同时间戳，跳过处理')
    return
  }
  
  // 如果没有时间戳参数，但是是相同的ID且处理时间很近，也跳过
  if (routeTimestamp === 0 && processedSupplyData.value.id === supplyId) {
    const now = Date.now()
    const timeDiff = now - processedSupplyData.value.timestamp
    console.log('MockOrder - timeDiff:', timeDiff)
    if (timeDiff < 1000) {
      console.log('MockOrder - 最近处理过相同ID，跳过处理')
      return
    }
  }
  
  if (canUseRealApi.value) {
    try {
      console.log('MockOrder - 开始处理供应信息:', supplyId)
      // 记录处理的ID和时间戳（使用路由时间戳或当前时间戳）
      processedSupplyData.value = {
        id: supplyId,
        timestamp: routeTimestamp || Date.now()
      }
      await handlePreselectedSupply(supplyId)
      console.log('MockOrder - 供应信息处理完成')
    } catch (error) {
      console.error('处理预选供应信息时出错:', error)
    }
  } else {
    console.log('MockOrder - canUseRealApi is false, skipping')
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  window.addEventListener('storage', syncUser)
  refreshOrders()
  // 获取物流公司列表
  fetchLogisticsCompanies()
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', syncUser)
  // 清除防抖计时器
  if (quantityCheckTimer) {
    clearTimeout(quantityCheckTimer)
    quantityCheckTimer = null
  }
  // 重置自动调整标记
  isAutoAdjusting = false
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

.stats-card.compact {
  /* 紧凑型样式：适用于单行8列布局 */
  min-height: 80px;
}

.stats-card.compact .stats-content {
  padding: 8px 4px;
}

.stats-card.compact .stats-number {
  font-size: 20px;
  margin-bottom: 6px;
}

.stats-card.compact .stats-label {
  font-size: 13px;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stats-card.active {
  border: 2px solid #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.stats-card.pending {
  border-left: 4px solid #e6a23c;
}

.stats-card.pending.active {
  border: 2px solid #e6a23c;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.3);
}

.stats-card.confirmed {
  border-left: 4px solid #409eff;
}

.stats-card.confirmed.active {
  border: 2px solid #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.stats-card.shipped {
  border-left: 4px solid #909399;
}

.stats-card.shipped.active {
  border: 2px solid #909399;
  box-shadow: 0 4px 12px rgba(144, 147, 153, 0.3);
}

.stats-card.in-transit {
  border-left: 4px solid #409eff;
}

.stats-card.in-transit.active {
  border: 2px solid #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.stats-card.delivered {
  border-left: 4px solid #e6a23c;
}

.stats-card.delivered.active {
  border: 2px solid #e6a23c;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.3);
}

.stats-card.completed {
  border-left: 4px solid #67c23a;
}

.stats-card.completed.active {
  border: 2px solid #67c23a;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.stats-card.cancelled {
  border-left: 4px solid #f56c6c;
}

.stats-card.cancelled.active {
  border: 2px solid #f56c6c;
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
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

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.action-buttons .el-button {
  margin: 0;
}

/* 发货表单 */
.ship-order-form {
  max-height: 60vh;
  overflow-y: auto;
}

.order-info {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.order-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.order-info p {
  margin: 4px 0;
  color: #606266;
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
  
  /* 移动端统计卡片间距调整 */
  .stats-row-normal {
    margin: 0 -6px !important;
  }
  
  .stats-row-normal .el-col {
    padding: 0 6px;
    margin-bottom: 12px;
  }
  
  /* 移动端紧凑型布局：优化显示 */
  .stats-card.compact {
    min-height: 75px;
  }
  
  .stats-card.compact .stats-content {
    padding: 8px 4px;
  }
  
  .stats-card.compact .stats-number {
    font-size: 16px;
  }
  
  .stats-card.compact .stats-label {
    font-size: 11px;
    line-height: 1.2;
  }
}

@media (max-width: 992px) and (min-width: 769px) {
  /* 平板端：调整间距 */
  .stats-card.compact .stats-content {
    padding: 6px 2px;
  }
  
  .stats-card.compact .stats-number {
    font-size: 18px;
  }
  
  .stats-card.compact .stats-label {
    font-size: 12px;
  }
}

@media (min-width: 1200px) {
  /* 大屏幕：恢复正常尺寸 */
  .stats-card.compact .stats-content {
    padding: 10px 6px;
  }
  
  .stats-card.compact .stats-number {
    font-size: 22px;
  }
  
  .stats-card.compact .stats-label {
    font-size: 13px;
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

/* 自定义供应量不足弹窗样式 */
:deep(.supply-shortage-alert) {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

:deep(.supply-shortage-alert .el-message-box__header) {
  padding: 24px 24px 16px;
  background: linear-gradient(135deg, #fff5f0 0%, #ffe8e0 100%);
  border-radius: 12px 12px 0 0;
}

:deep(.supply-shortage-alert .el-message-box__title) {
  font-size: 18px;
  font-weight: 600;
  color: #e6a23c;
}

:deep(.supply-shortage-alert .el-message-box__content) {
  padding: 24px;
}

:deep(.supply-shortage-alert .el-message-box__message) {
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-line;
}

:deep(.supply-shortage-alert .el-message-box__btns) {
  padding: 16px 24px 24px;
}

:deep(.supply-shortage-alert .el-button--primary) {
  padding: 10px 32px;
  font-size: 15px;
  border-radius: 6px;
  background: linear-gradient(135deg, #e6a23c 0%, #f0a800 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.3);
  transition: all 0.3s ease;
}

:deep(.supply-shortage-alert .el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(230, 162, 60, 0.4);
}
</style>
