<template>
  <div class="supplier-list">
    <div class="header">
      <h3>供应信息查看</h3>
      <div class="header-actions">
        <el-button @click="refreshList" :loading="loading" icon="Refresh" circle />
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-toolbar">
        <el-input
          v-model="filters.drugName"
          placeholder="搜索药品名称"
          style="width: 200px"
          clearable
          @input="handleFilter"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-input
          v-model="filters.supplierName"
          placeholder="搜索供应商名称"
          style="width: 180px"
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

    <!-- 供应信息列表 -->
    <el-card class="list-card" shadow="never">
      <div v-loading="loading" class="supply-list-container">
        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && supplyList.length === 0" 
          description="暂无供应信息"
          :image-size="80"
        />
        
        <!-- 供应信息卡片列表 -->
        <div v-else class="supply-cards">
          <div 
            v-for="item in supplyList" 
            :key="item.id" 
            class="supply-card"
            @click="viewDetail(item)"
          >
            <div class="card-header">
              <div class="drug-info">
                <h4 class="drug-name">{{ item.drug.generic_name }}</h4>
                <p class="drug-brand" v-if="item.drug.brand_name">
                  {{ item.drug.brand_name }}
                </p>
                <div class="drug-meta">
                  <span class="specification">{{ item.drug.specification }}</span>
                  <span class="separator">|</span>
                  <span class="manufacturer">{{ item.drug.manufacturer }}</span>
                </div>
              </div>
              <div class="price-info">
                <div class="unit-price">¥{{ item.unit_price }}</div>
                <div class="price-label">单价</div>
              </div>
            </div>
            
            <div class="card-content">
              <div class="supply-details">
                <div class="detail-item">
                  <span class="label">可供数量：</span>
                  <span class="value highlight">{{ item.available_quantity }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">起订量：</span>
                  <span class="value">{{ item.min_order_quantity }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">有效期至：</span>
                  <span class="value" :class="getValidityClass(item.valid_until)">
                    {{ formatDate(item.valid_until) }}
                  </span>
                </div>
              </div>
              
              <div class="supplier-info">
                <div class="supplier-name">
                  <el-icon><Shop /></el-icon>
                  {{ item.tenant.name }}
                </div>
                <div class="contact-info" v-if="item.tenant.contact_phone">
                  <el-icon><Phone /></el-icon>
                  {{ item.tenant.contact_phone }}
                </div>
              </div>
            </div>

            <div class="card-footer">
              <div class="published-time">
                发布于 {{ formatDateTime(item.created_at) }}
              </div>
              <div class="card-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  @click.stop="contactSupplier(item)"
                >
                  <el-icon><Message /></el-icon>
                  联系供应商
                </el-button>
                <el-button 
                  type="success" 
                  size="small"
                  @click.stop="createOrder(item)"
                >
                  <el-icon><ShoppingCart /></el-icon>
                  立即采购
                </el-button>
              </div>
            </div>

            <!-- 备注信息 -->
            <div v-if="item.description" class="card-note">
              <el-icon><InfoFilled /></el-icon>
              {{ item.description }}
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="supplyList.length > 0" class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.perPage"
            :page-sizes="[12, 24, 48]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 供应信息详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="供应信息详情"
      width="600px"
      @closed="selectedItem = null"
    >
      <div v-if="selectedItem" class="detail-content">
        <div class="detail-section">
          <h4>药品信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="通用名称">
              {{ selectedItem.drug.generic_name }}
            </el-descriptions-item>
            <el-descriptions-item label="商品名称">
              {{ selectedItem.drug.brand_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="规格">
              {{ selectedItem.drug.specification || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="剂型">
              {{ selectedItem.drug.dosage_form || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="生产厂家">
              {{ selectedItem.drug.manufacturer || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="批准文号">
              {{ selectedItem.drug.approval_number || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h4>供应信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="可供数量">
              <span class="highlight">{{ selectedItem.available_quantity }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="单价">
              <span class="price-highlight">¥{{ selectedItem.unit_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="最小起订量">
              {{ selectedItem.min_order_quantity }}
            </el-descriptions-item>
            <el-descriptions-item label="有效期至">
              <span :class="getValidityClass(selectedItem.valid_until)">
                {{ formatDate(selectedItem.valid_until) }}
              </span>
            </el-descriptions-item>
          </el-descriptions>
          <div v-if="selectedItem.description" class="description">
            <h5>备注说明</h5>
            <p>{{ selectedItem.description }}</p>
          </div>
        </div>

        <div class="detail-section">
          <h4>供应商信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="企业名称">
              {{ selectedItem.tenant.name }}
            </el-descriptions-item>
            <el-descriptions-item label="联系电话" v-if="selectedItem.tenant.contact_phone">
              {{ selectedItem.tenant.contact_phone }}
            </el-descriptions-item>
            <el-descriptions-item label="联系邮箱" v-if="selectedItem.tenant.contact_email">
              {{ selectedItem.tenant.contact_email }}
            </el-descriptions-item>
            <el-descriptions-item label="企业地址" v-if="selectedItem.tenant.address">
              {{ selectedItem.tenant.address }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button type="primary" @click="contactSupplier(selectedItem)">
            <el-icon><Message /></el-icon>
            联系供应商
          </el-button>
          <el-button type="success" @click="createOrder(selectedItem)">
            <el-icon><ShoppingCart /></el-icon>
            立即采购
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  Search, Shop, Phone, Message, ShoppingCart, InfoFilled, Refresh 
} from '@element-plus/icons-vue'
import { supplyApi } from '@/api/supply'
import { formatDate } from '@/utils/date'

// 响应式数据
const loading = ref(false)
const showDetailDialog = ref(false)
const selectedItem = ref(null)

// 供应信息列表
const supplyList = ref([])

// 筛选条件
const filters = reactive({
  drugName: '',
  supplierName: ''
})

// 分页
const pagination = reactive({
  page: 1,
  perPage: 12,
  total: 0
})

// 方法
const fetchSupplyList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage,
      drug_name: filters.drugName || undefined,
      supplier_name: filters.supplierName || undefined
    }
    
    const response = await supplyApi.getSupplyList(params)
    
    if (response.data && response.data.data) {
      supplyList.value = response.data.data.items || []
      pagination.total = response.data.data.pagination?.total || 0
      
      if (supplyList.value.length === 0 && filters.drugName) {
        ElMessage.info('未找到匹配的供应信息')
      }
    }
  } catch (error) {
    console.error('获取供应信息列表失败:', error)
    ElMessage.error('获取供应信息列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const refreshList = () => {
  fetchSupplyList()
}

const handleFilter = () => {
  pagination.page = 1
  fetchSupplyList()
}

const resetFilters = () => {
  filters.drugName = ''
  filters.supplierName = ''
  handleFilter()
}

const handleSizeChange = (size) => {
  pagination.perPage = size
  pagination.page = 1
  fetchSupplyList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchSupplyList()
}

const viewDetail = (item) => {
  selectedItem.value = item
  showDetailDialog.value = true
}

const contactSupplier = (item) => {
  if (item.tenant.contact_phone) {
    ElNotification({
      title: '联系方式',
      message: `供应商：${item.tenant.name}\n联系电话：${item.tenant.contact_phone}`,
      type: 'info',
      duration: 8000
    })
  } else {
    ElMessage.warning('该供应商未提供联系方式')
  }
}

const createOrder = (item) => {
  ElMessage.info('采购功能正在开发中，敬请期待')
  // 这里可以跳转到订单创建页面或打开采购对话框
}

const getValidityClass = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'expired'
  if (diffDays <= 30) return 'warning'
  return 'normal'
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

// 生命周期
onMounted(() => {
  fetchSupplyList()
})
</script>

<style scoped>
.supplier-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.filter-card {
  margin-bottom: 20px;
}

.filter-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.list-card {
  min-height: 500px;
}

.supply-list-container {
  min-height: 400px;
}

.supply-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.supply-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.supply-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.drug-info {
  flex: 1;
}

.drug-name {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.drug-brand {
  margin: 0 0 6px 0;
  color: #909399;
  font-size: 13px;
}

.drug-meta {
  color: #909399;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.separator {
  color: #dcdfe6;
}

.price-info {
  text-align: right;
}

.unit-price {
  font-size: 20px;
  font-weight: 700;
  color: #e6a23c;
  line-height: 1;
}

.price-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.card-content {
  margin-bottom: 12px;
}

.supply-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 13px;
}

.detail-item .label {
  color: #909399;
  margin-right: 4px;
}

.detail-item .value {
  color: #303133;
  font-weight: 500;
}

.detail-item .value.highlight {
  color: #67c23a;
  font-weight: 600;
}

.supplier-info {
  padding-top: 8px;
  border-top: 1px solid #f0f2f5;
}

.supplier-name {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.contact-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
}

.published-time {
  font-size: 12px;
  color: #c0c4cc;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-note {
  margin-top: 12px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  border-left: 3px solid #409eff;
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

.expired {
  color: #f56c6c;
  font-weight: 500;
}

/* 详情对话框样式 */
.detail-content {
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

.detail-section h5 {
  margin: 12px 0 6px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 600;
}

.description p {
  margin: 0;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  color: #606266;
  line-height: 1.5;
}

.highlight {
  color: #67c23a;
  font-weight: 600;
}

.price-highlight {
  color: #e6a23c;
  font-weight: 700;
  font-size: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .supply-cards {
    grid-template-columns: 1fr;
  }
  
  .filter-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-toolbar > * {
    width: 100%;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .card-actions {
    justify-content: space-between;
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
</style>
