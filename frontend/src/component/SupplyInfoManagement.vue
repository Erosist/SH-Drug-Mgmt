<template>
  <div class="supply-info-management">
    <div class="header">
      <h2>供应信息管理</h2>
      <el-button 
        type="primary" 
        @click="showCreateDialog = true"
        icon="Plus"
      >
        发布供应信息
      </el-button>
    </div>

    <!-- 筛选工具栏 -->
    <el-card class="filter-card">
      <div class="filter-toolbar">
        <el-input
          v-model="filters.drugName"
          placeholder="搜索药品名称"
          style="width: 200px"
          clearable
          @input="handleFilter"
        />
        <el-select
          v-model="filters.status"
          placeholder="状态筛选"
          style="width: 120px"
          clearable
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="活跃" value="ACTIVE" />
          <el-option label="下架" value="INACTIVE" />
          <el-option label="已过期" value="EXPIRED" />
        </el-select>
        <el-button @click="handleFilter">搜索</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 供应信息列表 -->
    <el-card class="list-card">
      <el-table 
        v-loading="loading"
        :data="supplyList"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="drug.generic_name" label="药品名称" width="180">
          <template #default="{ row }">
            <div>
              <div class="drug-name">{{ row.drug.generic_name }}</div>
              <div class="drug-brand" v-if="row.drug.brand_name">
                {{ row.drug.brand_name }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="drug.specification" label="规格" width="100" />
        <el-table-column prop="available_quantity" label="可供数量" width="100">
          <template #default="{ row }">
            <span class="quantity">{{ row.available_quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价(元)" width="100">
          <template #default="{ row }">
            <span class="price">¥{{ row.unit_price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="min_order_quantity" label="起订量" width="80" />
        <el-table-column prop="valid_until" label="有效期至" width="120">
          <template #default="{ row }">
            <span :class="getValidityClass(row.valid_until)">
              {{ formatDate(row.valid_until) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="editSupplyInfo(row)"
              link
            >
              编辑
            </el-button>
            <el-button 
              v-if="row.status === 'ACTIVE'"
              type="warning" 
              size="small" 
              @click="toggleStatus(row, 'INACTIVE')"
              link
            >
              下架
            </el-button>
            <el-button 
              v-else-if="row.status === 'INACTIVE'"
              type="success" 
              size="small" 
              @click="toggleStatus(row, 'ACTIVE')"
              link
            >
              上架
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteSupplyInfo(row)"
              link
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.perPage"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 发布/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingItem ? '编辑供应信息' : '发布供应信息'"
      width="600px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="药品" prop="drug_id">
          <el-select
            v-model="form.drug_id"
            placeholder="请选择药品"
            style="width: 100%"
            filterable
            remote
            :remote-method="searchDrugs"
            :loading="drugsLoading"
            @change="onDrugChange"
          >
            <el-option
              v-for="drug in drugOptions"
              :key="drug.id"
              :label="`${drug.generic_name} (${drug.specification})`"
              :value="drug.id"
            >
              <div>
                <div>{{ drug.generic_name }}</div>
                <div style="font-size: 12px; color: #999;">
                  {{ drug.brand_name }} | {{ drug.specification }}
                </div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="可供数量" prop="available_quantity">
          <el-input-number
            v-model="form.available_quantity"
            :min="1"
            :max="999999"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="单价(元)" prop="unit_price">
          <el-input-number
            v-model="form.unit_price"
            :min="0.01"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="最小起订量" prop="min_order_quantity">
          <el-input-number
            v-model="form.min_order_quantity"
            :min="1"
            :max="form.available_quantity || 999999"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="有效期至" prop="valid_until">
          <el-date-picker
            v-model="form.valid_until"
            type="date"
            placeholder="选择有效期"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        
        <el-form-item label="备注说明">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入备注说明(可选)"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="submitting"
            @click="handleSubmit"
          >
            {{ editingItem ? '更新' : '发布' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate } from '@/utils/date'
import { supplyApi, drugApi } from '@/api/supply'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const drugsLoading = ref(false)
const showCreateDialog = ref(false)
const editingItem = ref(null)
const formRef = ref(null)

// 供应信息列表
const supplyList = ref([])
const drugOptions = ref([])

// 筛选条件
const filters = reactive({
  drugName: '',
  status: '',
  onlyMine: true // 只显示我的供应信息
})

// 分页
const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

// 表单数据
const form = reactive({
  drug_id: '',
  available_quantity: 1,
  unit_price: 0.01,
  min_order_quantity: 1,
  valid_until: '',
  description: ''
})

// 表单验证规则
const rules = reactive({
  drug_id: [
    { required: true, message: '请选择药品', trigger: 'change' }
  ],
  available_quantity: [
    { required: true, message: '请输入可供数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '可供数量必须大于0', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '单价必须大于0', trigger: 'blur' }
  ],
  min_order_quantity: [
    { required: true, message: '请输入最小起订量', trigger: 'blur' },
    { type: 'number', min: 1, message: '最小起订量必须大于0', trigger: 'blur' }
  ],
  valid_until: [
    { required: true, message: '请选择有效期', trigger: 'change' }
  ]
})

// 计算属性
const isValidForm = computed(() => {
  return form.drug_id && 
         form.available_quantity > 0 && 
         form.unit_price > 0 && 
         form.min_order_quantity > 0 && 
         form.valid_until
})

// 方法
const fetchSupplyList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage,
      only_mine: filters.onlyMine,
      drug_name: filters.drugName || undefined,
      status: filters.status || undefined
    }
    
    const response = await supplyApi.getSupplyList(params)
    
    if (response.data && response.data.data) {
      supplyList.value = response.data.data.items || []
      pagination.total = response.data.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取供应信息列表失败:', error)
    ElMessage.error('获取供应信息列表失败')
  } finally {
    loading.value = false
  }
}

const searchDrugs = async (query) => {
  if (!query) {
    drugOptions.value = []
    return
  }
  
  drugsLoading.value = true
  try {
    const response = await drugApi.getDrugList({ search: query, per_page: 50 })
    if (response.data && response.data.data) {
      drugOptions.value = response.data.data.items || []
    }
  } catch (error) {
    console.error('搜索药品失败:', error)
  } finally {
    drugsLoading.value = false
  }
}

const onDrugChange = () => {
  // 当选择药品时，可以做一些处理
}

const handleFilter = () => {
  pagination.page = 1
  fetchSupplyList()
}

const resetFilters = () => {
  filters.drugName = ''
  filters.status = ''
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

const resetForm = () => {
  Object.assign(form, {
    drug_id: '',
    available_quantity: 1,
    unit_price: 0.01,
    min_order_quantity: 1,
    valid_until: '',
    description: ''
  })
  editingItem.value = null
  drugOptions.value = []
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const editSupplyInfo = (item) => {
  editingItem.value = item
  Object.assign(form, {
    drug_id: item.drug_id,
    available_quantity: item.available_quantity,
    unit_price: item.unit_price,
    min_order_quantity: item.min_order_quantity,
    valid_until: item.valid_until,
    description: item.description || ''
  })
  
  // 设置当前药品选项
  if (item.drug) {
    drugOptions.value = [item.drug]
  }
  
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const submitData = {
        drug_id: form.drug_id,
        available_quantity: form.available_quantity,
        unit_price: form.unit_price,
        min_order_quantity: form.min_order_quantity,
        valid_until: formatDateForSubmit(form.valid_until),
        description: form.description
      }
      
      if (editingItem.value) {
        await supplyApi.updateSupplyInfo(editingItem.value.id, submitData)
        ElMessage.success('供应信息更新成功')
      } else {
        await supplyApi.createSupplyInfo(submitData)
        ElMessage.success('供应信息发布成功')
      }
      
      showCreateDialog.value = false
      fetchSupplyList()
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error(error.response?.data?.msg || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const toggleStatus = async (item, newStatus) => {
  try {
    const action = newStatus === 'ACTIVE' ? '上架' : '下架'
    await ElMessageBox.confirm(`确定要${action}此供应信息吗？`, '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await supplyApi.updateSupplyInfo(item.id, { status: newStatus })
    ElMessage.success(`${action}成功`)
    fetchSupplyList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('状态切换失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

const deleteSupplyInfo = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除此供应信息吗？删除后不可恢复！', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await supplyApi.deleteSupplyInfo(item.id)
    ElMessage.success('删除成功')
    fetchSupplyList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getStatusType = (status) => {
  const map = {
    'ACTIVE': 'success',
    'INACTIVE': 'warning',
    'EXPIRED': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'ACTIVE': '活跃',
    'INACTIVE': '下架',
    'EXPIRED': '过期'
  }
  return map[status] || '未知'
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

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 // 禁用今天之前的日期
}

const formatDateForSubmit = (date) => {
  if (!date) return ''
  return new Date(date).toISOString().split('T')[0]
}

// 生命周期
onMounted(() => {
  fetchSupplyList()
})
</script>

<style scoped>
.supply-info-management {
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
  margin-bottom: 20px;
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

.quantity {
  font-weight: 600;
  color: #67C23A;
}

.price {
  font-weight: 600;
  color: #E6A23C;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 有效期样式 */
.normal {
  color: #67C23A;
}

.warning {
  color: #E6A23C;
}

.expired {
  color: #F56C6C;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #f8f9fa;
  color: #303133;
  font-weight: 600;
}

:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 600;
}
</style>
