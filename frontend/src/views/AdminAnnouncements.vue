<template>
  <div class="admin-announcements" v-if="isAdmin">
    <div class="page-header">
      <div>
        <p class="eyebrow">公告与资讯管理</p>
        <h2>管理健康资讯与紧急通知</h2>
        <p class="subtitle">支持发布、编辑、删除公告，控制前端展示内容。</p>
      </div>
      <div class="actions">
        <el-button type="primary" @click="openCreateDialog">新建公告</el-button>
        <el-button @click="goToHome">返回首页</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <div class="filters">
        <el-select v-model="filters.type" placeholder="类型" clearable @change="loadData" style="width: 150px">
          <el-option label="健康资讯" value="health_news" />
          <el-option label="紧急通知" value="urgent_notice" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable @change="loadData" style="width: 120px">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
        <el-button type="primary" @click="loadData" :loading="loading">查询</el-button>
      </div>

      <el-table :data="list" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'urgent_notice' ? 'danger' : 'info'" effect="plain">
              {{ row.type === 'urgent_notice' ? '紧急通知' : '健康资讯' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTagType(row.level)" size="small">{{ levelLabel(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布日期" width="120" />
        <el-table-column prop="source" label="来源" width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" :type="row.status === 'active' ? 'warning' : 'success'" text @click="handleToggle(row)">
              {{ row.status === 'active' ? '停用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" text @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          layout="prev, pager, next"
          :total="total"
          :page-size="perPage"
          :current-page="page"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑公告' : '新建公告'" width="600px" :close-on-click-modal="false">
      <el-form :model="form" label-width="100px" ref="formRef" :rules="formRules">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="选择类型" style="width: 100%">
            <el-option label="健康资讯" value="health_news" />
            <el-option label="紧急通知" value="urgent_notice" />
          </el-select>
        </el-form-item>
        <el-form-item label="级别" prop="level">
          <el-select v-model="form.level" placeholder="选择级别" style="width: 100%">
            <el-option label="普通" value="normal" />
            <el-option label="重要" value="important" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布日期" prop="publish_date">
          <el-date-picker v-model="form.publish_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="form.source" placeholder="如：卫健委、药监局等" maxlength="100" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="5" placeholder="请输入内容" maxlength="2000" show-word-limit />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="form.status" active-value="active" inactive-value="inactive" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>

  <div v-else class="no-access">
    <el-result icon="warning" title="仅系统管理员可访问">
      <template #extra><el-button type="primary" @click="goToHome">返回首页</el-button></template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCurrentUser } from '@/utils/authSession'
import {
  fetchAnnouncements,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement,
  toggleAnnouncement
} from '@/api/announcements'

const router = useRouter()
const currentUser = ref(getCurrentUser())
const isAdmin = computed(() => currentUser.value?.role === 'admin')

// 列表数据
const list = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)

// 筛选条件
const filters = reactive({
  type: '',
  status: ''
})

// 弹窗相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const defaultForm = {
  title: '',
  content: '',
  type: 'health_news',
  level: 'normal',
  publish_date: '',
  source: '',
  status: 'active'
}

const form = reactive({ ...defaultForm })

const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  publish_date: [{ required: true, message: '请选择发布日期', trigger: 'change' }]
}

// 级别标签
const levelLabel = (level) => {
  const map = { normal: '普通', important: '重要', urgent: '紧急' }
  return map[level] || level || '-'
}

const levelTagType = (level) => {
  const map = { normal: 'info', important: 'warning', urgent: 'danger' }
  return map[level] || 'info'
}

// 加载数据
const loadData = async () => {
  if (!isAdmin.value) return
  loading.value = true
  try {
    const res = await fetchAnnouncements({
      type: filters.type,
      status: filters.status,
      page: page.value,
      perPage: perPage.value
    })
    list.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    ElMessage.error(err.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (p) => {
  page.value = p
  loadData()
}

// 新建弹窗
const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, defaultForm)
  // 默认今天
  form.publish_date = new Date().toISOString().slice(0, 10)
  dialogVisible.value = true
}

// 编辑弹窗
const openEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    content: row.content,
    type: row.type,
    level: row.level || 'normal',
    publish_date: row.publish_date,
    source: row.source || '',
    status: row.status
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateAnnouncement(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createAnnouncement(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 切换状态
const handleToggle = async (row) => {
  try {
    await toggleAnnouncement(row.id)
    ElMessage.success('状态已更新')
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await deleteAnnouncement(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '删除失败')
    }
  }
}

const goToHome = () => router.push('/')

onMounted(() => {
  if (isAdmin.value) loadData()
})
</script>

<style scoped>
.admin-announcements {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-header .eyebrow {
  font-size: 12px;
  color: #909399;
  margin: 0 0 4px 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.page-header .subtitle {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.page-header .actions {
  display: flex;
  gap: 10px;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.pager {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.no-access {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
</style>
