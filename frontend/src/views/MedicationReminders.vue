<template>
  <div class="reminders-page">
    <div class="page-header">
      <h1>用药提醒管理</h1>
      <button class="btn-primary" @click="openCreateDialog">+ 新建提醒</button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <select v-model="filterActive" @change="loadReminders">
        <option value="">全部状态</option>
        <option value="true">已启用</option>
        <option value="false">已禁用</option>
      </select>
    </div>

    <!-- 提醒列表 -->
    <div class="reminders-list" v-loading="loading">
      <div v-if="reminders.length === 0 && !loading" class="empty-state">
        暂无用药提醒，点击右上角创建
      </div>
      
      <div v-for="item in reminders" :key="item.id" class="reminder-card" :class="{ inactive: !item.is_active }">
        <div class="reminder-main">
          <div class="drug-info">
            <span class="drug-name">{{ item.drug_name }}</span>
            <span class="dosage">{{ item.dosage }}</span>
          </div>
          <div class="schedule-info">
            <span class="frequency">{{ formatFrequency(item.frequency) }}</span>
            <span class="times">{{ (item.remind_times || []).join('、') }}</span>
          </div>
          <div class="date-range">
            {{ item.start_date }} 至 {{ item.end_date || '长期' }}
          </div>
        </div>
        <div class="reminder-actions">
          <el-switch 
            :model-value="item.is_active" 
            @change="toggleStatus(item)"
            active-text="启用"
            inactive-text="禁用"
          />
          <button class="btn-edit" @click="openEditDialog(item)">编辑</button>
          <button class="btn-delete" @click="confirmDelete(item)">删除</button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > perPage">
      <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
      <span>第 {{ page }} / {{ Math.ceil(total / perPage) }} 页</span>
      <button :disabled="page >= Math.ceil(total / perPage)" @click="changePage(page + 1)">下一页</button>
    </div>

    <!-- 创建/编辑对话框 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog-box">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑提醒' : '新建提醒' }}</h3>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>药品名称 *</label>
            <input v-model="form.drug_name" placeholder="请输入药品名称" />
          </div>
          <div class="form-group">
            <label>剂量 *</label>
            <input v-model="form.dosage" placeholder="如：每次2粒" />
          </div>
          <div class="form-group">
            <label>频率 *</label>
            <select v-model="form.frequency">
              <option value="daily">每天</option>
              <option value="weekly">每周</option>
              <option value="monthly">每月</option>
              <option value="custom">自定义</option>
            </select>
          </div>
          <div class="form-group">
            <label>提醒时间 *</label>
            <div class="time-inputs">
              <div v-for="(time, index) in form.remind_times" :key="index" class="time-row">
                <input type="time" v-model="form.remind_times[index]" />
                <button v-if="form.remind_times.length > 1" class="btn-remove" @click="removeTime(index)">-</button>
              </div>
              <button class="btn-add-time" @click="addTime">+ 添加时间</button>
            </div>
          </div>
          <div class="form-group">
            <label>开始日期 *</label>
            <input type="date" v-model="form.start_date" />
          </div>
          <div class="form-group">
            <label>结束日期（可选）</label>
            <input type="date" v-model="form.end_date" />
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="form.notes" placeholder="如：饭后服用"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDialog">取消</button>
          <button class="btn-submit" @click="submitForm" :disabled="submitting">
            {{ submitting ? '提交中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { homeApi } from '@/api/home'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'MedicationReminders',
  setup() {
    const loading = ref(false)
    const reminders = ref([])
    const page = ref(1)
    const perPage = ref(10)
    const total = ref(0)
    const filterActive = ref('')
    
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const editingId = ref(null)
    const submitting = ref(false)
    
    const defaultForm = {
      drug_name: '',
      dosage: '',
      frequency: 'daily',
      remind_times: ['08:00'],
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      notes: ''
    }
    const form = ref({ ...defaultForm })

    const loadReminders = async () => {
      loading.value = true
      try {
        const params = { page: page.value, per_page: perPage.value }
        if (filterActive.value) {
          params.is_active = filterActive.value
        }
        const res = await homeApi.getReminders(params)
        if (res.data?.success) {
          reminders.value = res.data.items || []
          total.value = res.data.total || 0
        }
      } catch (e) {
        console.error('加载提醒列表失败', e)
        ElMessage.error('加载失败')
      } finally {
        loading.value = false
      }
    }

    const formatFrequency = (freq) => {
      const map = { daily: '每天', weekly: '每周', monthly: '每月', custom: '自定义' }
      return map[freq] || freq
    }

    const openCreateDialog = () => {
      isEdit.value = false
      editingId.value = null
      form.value = { ...defaultForm, remind_times: ['08:00'] }
      dialogVisible.value = true
    }

    const openEditDialog = (item) => {
      isEdit.value = true
      editingId.value = item.id
      form.value = {
        drug_name: item.drug_name,
        dosage: item.dosage,
        frequency: item.frequency,
        remind_times: [...(item.remind_times || ['08:00'])],
        start_date: item.start_date,
        end_date: item.end_date || '',
        notes: item.notes || ''
      }
      dialogVisible.value = true
    }

    const closeDialog = () => {
      dialogVisible.value = false
    }

    const addTime = () => {
      form.value.remind_times.push('12:00')
    }

    const removeTime = (index) => {
      form.value.remind_times.splice(index, 1)
    }

    const submitForm = async () => {
      const { drug_name, dosage, frequency, remind_times, start_date } = form.value
      if (!drug_name || !dosage || !frequency || !remind_times.length || !start_date) {
        ElMessage.warning('请填写所有必填项')
        return
      }

      submitting.value = true
      try {
        const payload = {
          drug_name: form.value.drug_name,
          dosage: form.value.dosage,
          frequency: form.value.frequency,
          remind_times: form.value.remind_times.filter(t => t),
          start_date: form.value.start_date,
          end_date: form.value.end_date || null,
          notes: form.value.notes || null
        }

        if (isEdit.value) {
          await homeApi.updateReminder(editingId.value, payload)
          ElMessage.success('更新成功')
        } else {
          await homeApi.createReminder(payload)
          ElMessage.success('创建成功')
        }
        closeDialog()
        loadReminders()
      } catch (e) {
        console.error('提交失败', e)
        ElMessage.error(e.response?.data?.msg || '操作失败')
      } finally {
        submitting.value = false
      }
    }

    const toggleStatus = async (item) => {
      try {
        await homeApi.toggleReminder(item.id)
        item.is_active = !item.is_active
        ElMessage.success(item.is_active ? '已启用' : '已禁用')
      } catch (e) {
        ElMessage.error('操作失败')
      }
    }

    const confirmDelete = (item) => {
      ElMessageBox.confirm(`确定删除「${item.drug_name}」的提醒吗？`, '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await homeApi.deleteReminder(item.id)
          ElMessage.success('删除成功')
          loadReminders()
        } catch (e) {
          ElMessage.error('删除失败')
        }
      }).catch(() => {})
    }

    const changePage = (p) => {
      page.value = p
      loadReminders()
    }

    onMounted(() => {
      loadReminders()
    })

    return {
      loading,
      reminders,
      page,
      perPage,
      total,
      filterActive,
      dialogVisible,
      isEdit,
      form,
      submitting,
      loadReminders,
      formatFrequency,
      openCreateDialog,
      openEditDialog,
      closeDialog,
      addTime,
      removeTime,
      submitForm,
      toggleStatus,
      confirmDelete,
      changePage
    }
  }
}
</script>

<style scoped>
.reminders-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  color: #333;
}

.btn-primary {
  background: #1a73e8;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover {
  background: #0d62d9;
}

.filter-bar {
  margin-bottom: 16px;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.reminders-list {
  min-height: 200px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 60px 0;
}

.reminder-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reminder-card.inactive {
  opacity: 0.6;
  background: #f9f9f9;
}

.reminder-main {
  flex: 1;
}

.drug-info {
  margin-bottom: 8px;
}

.drug-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-right: 12px;
}

.dosage {
  color: #666;
  font-size: 14px;
}

.schedule-info {
  margin-bottom: 4px;
}

.frequency {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.times {
  color: #666;
  font-size: 13px;
}

.date-range {
  color: #999;
  font-size: 12px;
}

.reminder-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-edit, .btn-delete {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}

.btn-edit {
  background: #f0f0f0;
  border: 1px solid #ddd;
  color: #333;
}

.btn-delete {
  background: #fff;
  border: 1px solid #f56c6c;
  color: #f56c6c;
}

.btn-delete:hover {
  background: #f56c6c;
  color: #fff;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-box {
  background: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.dialog-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.time-inputs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-row {
  display: flex;
  gap: 8px;
}

.time-row input {
  flex: 1;
}

.btn-remove {
  background: #f56c6c;
  color: #fff;
  border: none;
  width: 32px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-add-time {
  background: #f0f0f0;
  border: 1px dashed #ccc;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.btn-cancel {
  padding: 10px 20px;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-submit {
  padding: 10px 20px;
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
