<template>
  <div class="inventory-warning">
    <div class="header">
      <h3>库存预警管理</h3>
      <div class="header-actions">
        <el-button @click="refreshWarnings" :loading="loading" icon="Refresh" circle />
        <el-button 
          v-if="userRole === 'admin'"
          type="primary"
          @click="triggerManualScan"
          :loading="scanLoading"
          icon="Search"
        >
          手动扫描
        </el-button>
      </div>
    </div>

    <div class="warning-description">
      <p>实时监测低库存、临期批次并给出调拨建议。</p>
      <p class="note">预警规则：单批次数量少于10件或有效期在30天内会被标记，请及时联动补货或调拨。</p>
      <p class="note">严重预警：库存为0或批次将在7天内到期（含已过期）会以红色标识提示，需优先处理。</p>
    </div>

    <!-- 预警统计面板 -->
    <div class="stats-panel">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stats-card critical">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="32"><WarningFilled /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ summaryData.critical_count || 0 }}</div>
                <div class="stats-label">严重预警</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stats-card low-stock">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="32"><Box /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ summaryData.low_stock_count || 0 }}</div>
                <div class="stats-label">低库存</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stats-card near-expiry">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="32"><Clock /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ summaryData.near_expiry_count || 0 }}</div>
                <div class="stats-label">近效期</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stats-card total">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="32"><DataBoard /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ summaryData.total_warnings || 0 }}</div>
                <div class="stats-label">总预警数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选工具栏 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-toolbar">
        <el-select
          v-model="filters.warningType"
          placeholder="预警类型"
          style="width: 150px"
          clearable
          @change="handleFilter"
        >
          <el-option label="全部预警" value="all" />
          <el-option label="低库存" value="low_stock" />
          <el-option label="近效期" value="near_expiry" />
        </el-select>
        <el-button type="primary" @click="handleFilter" :loading="loading">
          <el-icon><Search /></el-icon>
          筛选
        </el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 预警列表 -->
    <el-card class="list-card" shadow="never">
      <div v-loading="loading" class="warnings-list-container">
        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && warningsList.length === 0" 
          description="暂无预警信息"
          :image-size="80"
        >
          <template #description>
            <div>
              <p>暂无预警信息</p>
              <p class="empty-tip">当前库存状态良好 😊</p>
            </div>
          </template>
        </el-empty>
        
        <!-- 预警表格 -->
        <el-table
          v-else
          :data="warningsList"
          stripe
        >
          <el-table-column prop="drug.generic_name" label="药品名称" width="200">
            <template #default="{ row }">
              <div class="drug-info">
                <div class="drug-name">{{ getDrugName(row) }}</div>
                <div class="drug-brand" v-if="getDrugBrand(row)">
                  {{ getDrugBrand(row) }}
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="batch_number" label="生产批号" width="120" />
          
          <el-table-column prop="quantity" label="库存数量" width="100" align="right">
            <template #default="{ row }">
              <span 
                :class="{ 
                  'critical-quantity': row.quantity === 0,
                  'low-quantity': row.quantity > 0 && row.quantity < 10 
                }"
              >
                {{ row.quantity }}
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="expiry_date" label="有效期" width="120">
            <template #default="{ row }">
              <span :class="getExpiryClass(row.expiry_date)">
                {{ formatDate(row.expiry_date) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column label="预警类型" width="200">
            <template #default="{ row }">
              <div class="warning-tags">
                <el-tag
                  v-for="warningType in row.warning_types || []"
                  :key="warningType.type"
                  :type="getWarningTagType(warningType.severity)"
                  size="small"
                  class="warning-tag"
                >
                  {{ getWarningTypeText(warningType.type) }}
                </el-tag>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="预警级别" width="100" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="getSeverityType(getMaxSeverity(row.warning_types))"
                size="small"
              >
                {{ getSeverityText(getMaxSeverity(row.warning_types)) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small"
                @click="handleWarning(row)"
              >
                处理预警
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div v-if="warningsList.length > 0" class="pagination">
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  Search, WarningFilled, Warning, Box, Clock, DataBoard, Refresh
} from '@element-plus/icons-vue'
import { inventoryWarningApi } from '@/api/inventory'
import { formatDate } from '@/utils/date'
import { getCurrentUser } from '@/utils/authSession'

// 响应式数据
const loading = ref(false)
const scanLoading = ref(false)
const warningsList = ref([])
const summaryData = ref({})

// 用户信息
const currentUser = getCurrentUser()
const userRole = computed(() => currentUser?.role || '')

// 筛选条件
const filters = reactive({
  warningType: 'all'
})

// 分页
const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

// 方法
const fetchWarnings = async () => {
  loading.value = true
  try {
    const params = {
      warning_type: filters.warningType,
      page: pagination.page,
      per_page: pagination.perPage
    }
    
    const response = await inventoryWarningApi.getWarnings(params)
    
    if (response.data && response.data.success) {
      const data = response.data.data
      warningsList.value = data.warnings || []
      pagination.total = data.pagination?.total || 0
      
      // 更新统计信息
      if (data.statistics) {
        summaryData.value = data.statistics
      }
    }
  } catch (error) {
    console.error('获取预警列表失败:', error)
    ElMessage.error('获取预警列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const fetchWarningSummary = async () => {
  try {
    const response = await inventoryWarningApi.getWarningSummary()
    
    if (response.data && response.data.success) {
      const data = response.data.data
      summaryData.value = data.summary || {}
    }
  } catch (error) {
    console.error('获取预警摘要失败:', error)
  }
}

const refreshWarnings = () => {
  fetchWarnings()
  fetchWarningSummary()
}

const handleFilter = () => {
  pagination.page = 1
  fetchWarnings()
}

const resetFilters = () => {
  filters.warningType = 'all'
  handleFilter()
}

const handleSizeChange = (size) => {
  pagination.perPage = size
  pagination.page = 1
  fetchWarnings()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchWarnings()
}

const triggerManualScan = async () => {
  scanLoading.value = true
  try {
    const response = await inventoryWarningApi.scanWarnings()
    
    if (response.data && response.data.success) {
      ElMessage.success('预警扫描完成')
      refreshWarnings()
    }
  } catch (error) {
    console.error('手动扫描失败:', error)
    ElMessage.error('扫描失败，请稍后重试')
  } finally {
    scanLoading.value = false
  }
}

const handleWarning = (item) => {
  ElNotification({
    title: '预警处理',
    message: `请及时处理 ${getDrugName(item)} 的库存问题`,
    type: 'warning',
    duration: 5000
  })
}

const getDrugName = (row = {}) => {
  return row.drug?.generic_name || row.drug_name || row.drug?.brand_name || row.drug_brand || '未知药品'
}

const getDrugBrand = (row = {}) => {
  return row.drug?.brand_name || row.drug_brand || ''
}

const getExpiryClass = (dateStr) => {
  if (!dateStr) return 'normal'
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'expired'
  if (diffDays <= 7) return 'critical'
  if (diffDays <= 30) return 'warning'
  return 'normal'
}

const getWarningTagType = (severity) => {
  return severity === 'critical' ? 'danger' : 'warning'
}

const getWarningTypeText = (type) => {
  const map = {
    'low_stock': '低库存',
    'near_expiry': '近效期'
  }
  return map[type] || type
}

const getSeverityType = (severity) => {
  return severity === 'critical' ? 'danger' : 'warning'
}

const getSeverityText = (severity) => {
  const map = {
    'critical': '严重',
    'warning': '警告'
  }
  return map[severity] || '一般'
}

const getMaxSeverity = (warningTypes) => {
  if (!warningTypes || warningTypes.length === 0) return 'warning'
  return warningTypes.some(w => w.severity === 'critical') ? 'critical' : 'warning'
}

// 生命周期
onMounted(() => {
  fetchWarnings()
  fetchWarningSummary()
})
</script>

<style scoped>
.inventory-warning {
  padding: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.warning-description {
  margin: 0 0 16px;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.warning-description .note {
  color: #909399;
  margin-top: 4px;
}

/* 统计面板 */
.stats-panel {
  margin-bottom: 12px;
}

.stats-card {
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stats-card.critical {
  background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
  color: white;
}

.stats-card.low-stock {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
}

.stats-card.near-expiry {
  background: linear-gradient(135deg, #feca57, #ff9ff3);
  color: white;
}

.stats-card.total {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
}

.stats-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stats-icon {
  margin-right: 16px;
  opacity: 0.8;
}

.stats-info {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  opacity: 0.9;
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
  margin-bottom: 20px;
}

.warnings-list-container {
  min-height: 300px;
}

.drug-info {
  line-height: 1.4;
}

.drug-name {
  font-weight: 600;
  color: #303133;
}

.drug-brand {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.critical-quantity {
  color: #ff6b6b;
  font-weight: bold;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

.low-quantity {
  color: #e6a23c;
  font-weight: bold;
}

.warning-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.warning-tag {
  margin: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 有效期样式 */
.normal {
  color: #67c23a;
}

.warning {
  color: #e6a23c;
  font-weight: 500;
}

.critical {
  color: #ff6b6b;
  font-weight: 500;
}

.expired {
  color: #ff6b6b;
  font-weight: bold;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

/* 空状态 */
.empty-tip {
  color: #67c23a;
  font-size: 14px;
  margin-top: 8px;
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
}

:deep(.el-card__body) {
  padding: 16px;
}

:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f2f5;
}

:deep(.el-table) {
  font-size: 14px;
}
</style>
