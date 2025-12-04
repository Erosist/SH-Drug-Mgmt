<template>
  <div class="inventory-manage-panel">
    <div class="panel-header">
      <div>
        <h2>库存维护</h2>
        <p class="panel-subtitle">在同一面板登记新批次并调整库存。</p>
      </div>
      <div class="list-search">
        <input
          type="text"
          placeholder="按批次或药品关键字搜索"
          v-model="listKeyword"
          @keyup.enter="searchList"
        />
        <button class="primary" :disabled="listLoading" @click="searchList">搜索</button>
        <button class="ghost" :disabled="listLoading || !listKeyword" @click="resetList">重置</button>
      </div>
    </div>

    <div class="forms-grid">
      <section class="form-card">
        <div class="card-title">
          <h3>新增批次</h3>
          <p>将现有库存与药品档案关联后入库。</p>
        </div>
        <form @submit.prevent="submitCreate" class="form-body">
          <div class="field-block">
            <label>药品</label>
            <input
              type="text"
              list="drug-options-list"
              placeholder="输入药品名称或批准文号匹配"
              v-model="selectedDrugDisplay"
              @input="handleDrugInput"
              @change="handleDrugSelection"
            />
            <datalist id="drug-options-list">
              <option v-for="drug in drugOptions" :key="drug.id" :value="buildDrugLabel(drug)"></option>
            </datalist>
            <p v-if="drugError" class="field-error">{{ drugError }}</p>
          </div>

          <div class="field-block">
            <label>批次号</label>
            <input type="text" v-model="createForm.batchNumber" placeholder="例如 B20241201" />
          </div>

          <div class="cluster">
            <div class="field-block">
              <label>生产日期</label>
              <input type="date" v-model="createForm.productionDate" />
            </div>
            <div class="field-block">
              <label>有效期</label>
              <input type="date" v-model="createForm.expiryDate" />
            </div>
          </div>

          <div class="cluster">
            <div class="field-block">
              <label>数量</label>
              <input type="number" v-model="createForm.quantity" min="1" step="1" />
            </div>
            <div class="field-block">
              <label>单价</label>
              <input type="number" v-model="createForm.unitPrice" min="0" step="0.01" />
            </div>
          </div>

          <div class="field-block">
            <label>备注</label>
            <textarea rows="2" v-model="createForm.notes" placeholder="可选备注"></textarea>
          </div>

          <div class="form-messages">
            <p v-if="createError" class="field-error">{{ createError }}</p>
            <p v-if="createMessage" class="field-success">{{ createMessage }}</p>
          </div>

          <button class="primary" type="submit" :disabled="createSubmitting || !canSubmitCreate">
            {{ createSubmitting ? '保存中...' : '创建批次' }}
          </button>
        </form>
      </section>

      <section class="form-card">
        <div class="card-title">
          <h3>库存调整</h3>
          <p>选择已有批次并记录出入库变动。</p>
        </div>
        <form @submit.prevent="submitAdjust" class="form-body">
          <div class="field-block">
            <label>批次</label>
            <select v-model="adjustForm.itemId">
              <option value="">请选择要调整的批次</option>
              <option v-for="item in items" :key="item.id" :value="item.id">
                {{ item.batch_number }} - {{ item.drug?.generic_name || item.drug_name }} ({{ item.quantity }})
              </option>
            </select>
          </div>

          <div v-if="selectedItem" class="selection-glance">
            <p><strong>药品：</strong> {{ selectedItem.drug?.generic_name || selectedItem.drug_name }}</p>
            <p><strong>当前数量：</strong> {{ selectedItem.quantity }}</p>
            <p><strong>有效期：</strong> {{ formatDate(selectedItem.expiry_date) }}</p>
          </div>

          <div class="cluster">
            <div class="field-block">
              <label>调整方式</label>
              <select v-model="adjustForm.direction">
                <option value="increase">增加</option>
                <option value="decrease">减少</option>
              </select>
            </div>
            <div class="field-block">
              <label>调整数量</label>
              <input type="number" v-model="adjustForm.quantityDelta" min="1" step="1" placeholder="请输入正整数" />
            </div>
          </div>

          <div class="field-block">
            <label>单价（可选）</label>
            <input type="number" v-model="adjustForm.unitPrice" min="0" step="0.01" />
          </div>

          <div class="field-block">
            <label>修改有效期</label>
            <input type="date" v-model="adjustForm.expiryDate" />
          </div>

          <div class="field-block">
            <label>备注</label>
            <textarea rows="2" v-model="adjustForm.notes" placeholder="可选备注"></textarea>
          </div>

          <div class="form-messages">
            <p v-if="adjustError" class="field-error">{{ adjustError }}</p>
            <p v-if="adjustMessage" class="field-success">{{ adjustMessage }}</p>
          </div>

          <button class="primary" type="submit" :disabled="adjustSubmitting || !canSubmitAdjust">
            {{ adjustSubmitting ? '处理中...' : '提交调整' }}
          </button>
        </form>
      </section>
    </div>

    <section class="recent-list">
      <div class="list-bar">
        <div>
          <h3>最新批次</h3>
          <p class="panel-subtitle">按更新时间倒序显示。</p>
        </div>
        <button class="ghost" :disabled="listLoading" @click="reloadItems">刷新</button>
      </div>

      <div v-if="listLoading" class="list-placeholder">库存加载中...</div>
      <div v-else-if="listError" class="list-placeholder error">{{ listError }}</div>
      <div v-else-if="!items.length" class="list-placeholder">当前筛选没有匹配的批次。</div>
      <div v-else class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>批次号</th>
              <th>药品</th>
              <th>数量</th>
              <th>单价</th>
              <th>有效期</th>
              <th>更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.batch_number }}</td>
              <td>
                <div class="cell-main">{{ item.drug?.generic_name || item.drug_name || '暂无' }}</div>
                <div class="cell-sub">{{ item.drug?.brand_name || item.drug_brand }}</div>
              </td>
              <td>{{ item.quantity }}</td>
              <td>{{ formatPrice(item.unit_price) }}</td>
              <td>{{ formatDate(item.expiry_date) }}</td>
              <td>{{ formatDateTime(item.updated_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="items.length && pagination.total > pagination.perPage" class="pager">
        <button class="ghost" :disabled="pagination.page === 1" @click="goToPage(pagination.page - 1)">上一页</button>
        <span>第 {{ pagination.page }} / {{ totalPages }} 页</span>
        <button class="ghost" :disabled="pagination.page >= totalPages" @click="goToPage(pagination.page + 1)">下一页</button>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { inventoryItemApi } from '@/api/inventory'
import { fetchDrugs } from '@/api/catalog'

export default {
  name: 'InventoryManagePanel',
  setup() {
    const listKeyword = ref('')
    const listLoading = ref(false)
    const listError = ref('')
    const items = ref([])
    const pagination = ref({ page: 1, perPage: 5, total: 0 })

    const drugOptions = ref([])
    const drugLoading = ref(false)
    const drugError = ref('')
    const selectedDrugDisplay = ref('')

    const createForm = ref({
      drugId: '',
      batchNumber: '',
      productionDate: '',
      expiryDate: '',
      quantity: '',
      unitPrice: '',
      notes: ''
    })
    const createSubmitting = ref(false)
    const createMessage = ref('')
    const createError = ref('')

    const adjustForm = ref({
      itemId: '',
      quantityDelta: '',
      direction: 'increase',
      unitPrice: '',
      expiryDate: '',
      notes: ''
    })
    const adjustSubmitting = ref(false)
    const adjustMessage = ref('')
    const adjustError = ref('')

    const unwrap = (response) => response?.data ?? response ?? {}
    const extractError = (error) => error?.response?.data?.description || error?.response?.data?.message || error?.message || '请求失败'
    const buildDrugLabel = (drug) => {
      if (!drug) return ''
      const primary = drug.generic_name || drug.brand_name || '未命名'
      const secondary = drug.brand_name && drug.brand_name !== primary ? ` / ${drug.brand_name}` : ''
      const approval = drug.approval_number ? ` (${drug.approval_number})` : ''
      return `${primary}${secondary}${approval}`.trim()
    }

    const totalPages = computed(() => {
      const size = pagination.value.perPage || 1
      return Math.max(1, Math.ceil((pagination.value.total || 0) / size))
    })

    const selectedItem = computed(() => {
      const id = Number(adjustForm.value.itemId)
      if (!id) return null
      return items.value.find((entry) => Number(entry.id) === id) || null
    })

    const canSubmitCreate = computed(() => {
      const form = createForm.value
      return Boolean(
        form.drugId &&
        form.batchNumber.trim() &&
        form.productionDate &&
        form.expiryDate &&
        form.quantity !== '' &&
        Number(form.quantity) > 0 &&
        form.unitPrice !== '' &&
        Number(form.unitPrice) >= 0
      )
    })

    const canSubmitAdjust = computed(() => {
      const form = adjustForm.value
      const amount = Number(form.quantityDelta)
      return Boolean(form.itemId && form.direction && amount > 0)
    })

    const buildListParams = () => ({
      keyword: listKeyword.value.trim() || undefined,
      page: pagination.value.page,
      per_page: pagination.value.perPage
    })

    const loadItems = async () => {
      listLoading.value = true
      listError.value = ''
      try {
        const payload = unwrap(await inventoryItemApi.list(buildListParams()))
        items.value = payload.items || []
        pagination.value = {
          page: payload.page ?? pagination.value.page,
          perPage: payload.per_page ?? pagination.value.perPage,
          total: payload.total ?? items.value.length
        }
      } catch (error) {
        listError.value = extractError(error)
        items.value = []
      } finally {
        listLoading.value = false
      }
    }

    const reloadItems = () => {
      loadItems()
    }

    const searchList = () => {
      pagination.value = { ...pagination.value, page: 1 }
      loadItems()
    }

    const resetList = () => {
      if (!listKeyword.value) {
        loadItems()
        return
      }
      listKeyword.value = ''
      pagination.value = { ...pagination.value, page: 1 }
      loadItems()
    }

    const goToPage = (page) => {
      if (page < 1 || page > totalPages.value || page === pagination.value.page) {
        return
      }
      pagination.value = { ...pagination.value, page }
      loadItems()
    }

    const searchDrugs = async (keyword) => {
      drugError.value = ''
      drugOptions.value = []
      if (!keyword) {
        return
      }
      drugLoading.value = true
      try {
        const response = await fetchDrugs({ keyword, perPage: 20 })
        drugOptions.value = response.items || []
        syncSelectedDrugDisplay()
        if (!drugOptions.value.length) {
          drugError.value = '没有与该关键字匹配的药品。'
        }
      } catch (error) {
        drugError.value = error.message || '药品列表加载失败。'
      } finally {
        drugLoading.value = false
      }
    }

    const resetCreateForm = () => {
      createForm.value = {
        drugId: '',
        batchNumber: '',
        productionDate: '',
        expiryDate: '',
        quantity: '',
        unitPrice: '',
        notes: ''
      }
      selectedDrugDisplay.value = ''
    }

    const handleDrugSelection = () => {
      const keyword = selectedDrugDisplay.value.trim()
      if (!keyword) {
        createForm.value.drugId = ''
        return
      }
      const exact = drugOptions.value.find((drug) => buildDrugLabel(drug) === keyword)
      const fuzzy = exact || drugOptions.value.find((drug) => {
        const fields = [drug.generic_name, drug.brand_name, drug.approval_number].filter(Boolean)
        return fields.some((field) => field.includes(keyword))
      })
      if (fuzzy) {
        createForm.value.drugId = String(fuzzy.id)
        drugError.value = ''
      } else {
        createForm.value.drugId = ''
        drugError.value = '未在列表中找到匹配药品，请重新输入或搜索。'
      }
    }

    const handleDrugInput = async () => {
      const keyword = selectedDrugDisplay.value.trim()
      if (!keyword) {
        createForm.value.drugId = ''
        drugOptions.value = []
        drugError.value = ''
        return
      }
      const cachedMatch = drugOptions.value.find((drug) => buildDrugLabel(drug) === keyword)
      if (cachedMatch) {
        createForm.value.drugId = String(cachedMatch.id)
        drugError.value = ''
        return
      }
      await searchDrugs(keyword)
      handleDrugSelection()
    }

    const syncSelectedDrugDisplay = () => {
      if (!createForm.value.drugId) {
        return
      }
      const match = drugOptions.value.find((drug) => String(drug.id) === String(createForm.value.drugId))
      selectedDrugDisplay.value = match ? buildDrugLabel(match) : ''
    }

    const submitCreate = async () => {
      createError.value = ''
      createMessage.value = ''
      if (!canSubmitCreate.value) {
        createError.value = '请填写所有必填项。'
        return
      }
      createSubmitting.value = true
      try {
        await inventoryItemApi.create({
          drug_id: Number(createForm.value.drugId),
          batch_number: createForm.value.batchNumber.trim(),
          production_date: createForm.value.productionDate,
          expiry_date: createForm.value.expiryDate,
          quantity: Number(createForm.value.quantity),
          unit_price: Number(createForm.value.unitPrice),
          notes: createForm.value.notes.trim() || undefined
        })
        createMessage.value = '库存批次创建成功。'
        resetCreateForm()
        await loadItems()
      } catch (error) {
        createError.value = extractError(error)
      } finally {
        createSubmitting.value = false
      }
    }

    const submitAdjust = async () => {
      adjustError.value = ''
      adjustMessage.value = ''
      if (!canSubmitAdjust.value) {
        adjustError.value = '请选择批次并填写大于0的调整数量。'
        return
      }
      adjustSubmitting.value = true
      try {
        const magnitude = Math.abs(Number(adjustForm.value.quantityDelta))
        const signedDelta = adjustForm.value.direction === 'decrease' ? -magnitude : magnitude
        const payload = {
          quantity_delta: signedDelta,
          notes: adjustForm.value.notes.trim() || undefined
        }
        if (adjustForm.value.unitPrice !== '') {
          payload.unit_price = Number(adjustForm.value.unitPrice)
        }
        if (adjustForm.value.expiryDate) {
          payload.expiry_date = adjustForm.value.expiryDate
        }
        await inventoryItemApi.update(adjustForm.value.itemId, payload)
        adjustMessage.value = '库存已更新。'
        adjustForm.value = {
          itemId: '',
          quantityDelta: '',
          direction: 'increase',
          unitPrice: '',
          expiryDate: '',
          notes: ''
        }
        await loadItems()
      } catch (error) {
        adjustError.value = extractError(error)
      } finally {
        adjustSubmitting.value = false
      }
    }

    const formatDate = (value) => {
      if (!value) return '暂无'
      return String(value).slice(0, 10)
    }

    const formatPrice = (value) => {
      if (value === null || value === undefined || value === '') {
        return '暂无'
      }
      return `¥${Number(value).toFixed(2)}`
    }

    const formatDateTime = (value) => {
      if (!value) return '暂无'
      return String(value).replace('T', ' ').replace('Z', '')
    }

    onMounted(() => {
      loadItems()
    })

    return {
      listKeyword,
      listLoading,
      listError,
      items,
      pagination,
      totalPages,
      reloadItems,
      searchList,
      resetList,
      goToPage,
      createForm,
      createSubmitting,
      createMessage,
      createError,
      canSubmitCreate,
      submitCreate,
      adjustForm,
      adjustSubmitting,
      adjustMessage,
      adjustError,
      canSubmitAdjust,
      submitAdjust,
      selectedItem,
      formatDate,
      formatPrice,
      formatDateTime,
      drugOptions,
      drugLoading,
      drugError,
      handleDrugInput,
      selectedDrugDisplay,
      handleDrugSelection,
      buildDrugLabel
    }
  }
}
</script>

<style scoped>
.inventory-manage-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.panel-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-end;
}

.panel-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1a237e;
}

.panel-subtitle {
  color: #6b7280;
  font-size: 14px;
  margin-top: 4px;
}

.list-search {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.list-search input {
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  min-width: 220px;
}

.forms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.form-card {
  border: 1px solid rgba(26, 115, 232, 0.12);
  border-radius: 10px;
  padding: 16px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

.card-title h3 {
  margin: 0;
  font-size: 18px;
  color: #111827;
}

.card-title p {
  margin: 4px 0 16px;
  color: #6b7280;
  font-size: 14px;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-block label {
  font-size: 13px;
  color: #4b5563;
  font-weight: 600;
}

.field-block input,
.field-block select,
.field-block textarea {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 14px;
}

.field-block textarea {
  resize: vertical;
}

.inline-field {
  display: flex;
  gap: 8px;
}

.cluster {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.primary {
  background-color: #1a73e8;
  color: #fff;
  border: none;
  padding: 9px 18px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.primary:not(:disabled):hover {
  background-color: #1558b0;
}

.ghost {
  background-color: transparent;
  border: 1px solid #1a73e8;
  color: #1a73e8;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.ghost:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ghost:not(:disabled):hover {
  background-color: rgba(26, 115, 232, 0.08);
}

.field-error {
  color: #d93025;
  font-size: 13px;
}

.field-success {
  color: #1e8e3e;
  font-size: 13px;
}

.form-messages {
  min-height: 18px;
}

.selection-glance {
  background-color: #f5f9ff;
  border: 1px solid rgba(26, 115, 232, 0.2);
  border-radius: 6px;
  padding: 10px;
  font-size: 13px;
  color: #1f2937;
}

.selection-glance p {
  margin: 2px 0;
}

.recent-list {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 10px;
  padding: 16px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.table-wrapper {
  overflow-x: auto;
}

.recent-list table {
  width: 100%;
  border-collapse: collapse;
}

.recent-list th,
.recent-list td {
  text-align: left;
  padding: 10px 6px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
}

.cell-main {
  font-weight: 600;
}

.cell-sub {
  font-size: 12px;
  color: #6b7280;
}

.list-placeholder {
  text-align: center;
  color: #6b7280;
  padding: 20px 0;
}

.list-placeholder.error {
  color: #d93025;
}

.pager {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  align-items: center;
}

@media (max-width: 768px) {
  .inline-field {
    flex-direction: column;
  }
  .list-search {
    flex-direction: column;
    align-items: flex-start;
  }
  .list-search input {
    width: 100%;
  }
}
</style>
