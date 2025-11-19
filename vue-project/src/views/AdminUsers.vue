<template>
  <div class="admin-users" v-if="isAdmin">
    <div class="page-header">
      <div>
        <p class="eyebrow">用户管理</p>
        <h2>查看和管理所有用户账号</h2>
        <p class="subtitle">支持按角色、状态、企业搜索，禁用后账号立即无法登录。</p>
      </div>
      <div class="filters">
        <el-input v-model="keyword" placeholder="用户名/姓名/企业" clearable @change="loadData" style="width:220px" />
        <el-select v-model="role" placeholder="角色" clearable @change="loadData" style="width:150px">
          <el-option label="药店" value="pharmacy" />
          <el-option label="供应商" value="supplier" />
          <el-option label="物流" value="logistics" />
          <el-option label="监管" value="regulator" />
          <el-option label="未认证" value="unauth" />
        </el-select>
        <el-select v-model="status" placeholder="状态" clearable @change="loadData" style="width:150px">
          <el-option label="正常" value="enabled" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-button type="primary" @click="loadData" :loading="loading">查询</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-table :data="users" style="width: 100%" :loading="loading">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="real_name" label="真实姓名" min-width="120" />
        <el-table-column prop="company_name" label="所属企业" min-width="180" />
        <el-table-column prop="certification" label="认证状态" width="140">
          <template #default="scope">
            <el-tag v-if="scope.row.certification" :type="certTag(scope.row.certification.status)">
              {{ certText(scope.row.certification.status) }}
            </el-tag>
            <span v-else>未提交</span>
          </template>
        </el-table-column>
        <el-table-column prop="certification" label="认证角色" width="120">
          <template #default="scope">
            <span v-if="scope.row.certification">{{ roleLabel(scope.row.certification.role) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag type="info" effect="plain">{{ roleLabel(scope.row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">{{ scope.row.is_active ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" width="180">
          <template #default="scope">{{ formatDate(scope.row.last_login_at) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" type="warning" v-if="scope.row.is_active" @click="toggle(scope.row, 'disable')">禁用</el-button>
            <el-button size="small" type="success" v-else @click="toggle(scope.row, 'enable')">启用</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          layout="prev, pager, next"
          :total="total"
          :page-size="perPage"
          :current-page="page"
          @current-change="(p)=>{page=p;loadData()}"
        />
      </div>
    </el-card>
  </div>
  <div v-else class="no-access">
    <el-result icon="warning" title="仅监管/管理员可访问">
      <template #extra><el-button type="primary" @click="goHome">返回首页</el-button></template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchUsers, updateUserStatus } from '@/api/admin'
import { getCurrentUser } from '@/utils/authSession'

const router = useRouter()
const currentUser = getCurrentUser()
const isAdmin = computed(() => currentUser?.role === 'admin')

const keyword = ref('')
const role = ref('')
const status = ref('')
const users = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)

const roleLabel = (value) => {
  const map = { pharmacy: '药店', supplier: '供应商', logistics: '物流', regulator: '监管', unauth: '未认证' }
  return map[value] || value || '-'
}

const certText = (status) => {
  if (status === 'approved') return '已通过'
  if (status === 'pending') return '审核中'
  if (status === 'rejected') return '已驳回'
  return '未提交'
}

const certTag = (status) => {
  if (status === 'approved') return 'success'
  if (status === 'pending') return 'info'
  if (status === 'rejected') return 'danger'
  return ''
}

const formatDate = (value) => {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return value
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await fetchUsers({
      keyword: keyword.value,
      role: role.value,
      status: status.value,
      page: page.value,
      perPage: perPage.value,
    })
    users.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    ElMessage.error(err?.message || '加载用户失败')
  } finally {
    loading.value = false
  }
}

const toggle = async (row, action) => {
  try {
    await updateUserStatus(row.id, action)
    ElMessage.success(action === 'enable' ? '已启用' : '已禁用')
    loadData()
  } catch (err) {
    ElMessage.error(err?.message || '操作失败')
  }
}

const goHome = () => router.push('/')

onMounted(() => {
  if (isAdmin.value) loadData()
})
</script>

<style scoped>
.admin-users { padding:20px; background:#f5f7fb; min-height:100vh; }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; background:#fff; padding:14px; border-radius:10px; border:1px solid #eef2f7; }
.eyebrow { color:#1a73e8; font-weight:600; margin:0 0 4px 0; }
.subtitle { margin:4px 0 0 0; color:#606266; font-size:13px; }
.filters { display:flex; gap:10px; align-items:center; }
.pager { margin-top:12px; display:flex; justify-content:flex-end; }
.no-access { padding:40px; }
</style>
