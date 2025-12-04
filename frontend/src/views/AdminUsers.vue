<template>
  <div class="admin-users" v-if="isAdmin">
    <div class="admin-top-actions">
      <div class="user-actions">
        <div v-if="currentUser" class="user-info">
          <span class="user-name">{{ userDisplayName }}</span>
          <span class="user-role">{{ userRoleLabel }}</span>
        </div>
        <button
          v-if="currentUser"
          class="admin-btn"
          @click="goToChangePassword"
        >修改密码</button>
        <button v-if="!currentUser || currentUser.role==='unauth'" class="auth-btn" @click="goToEnterpriseAuth">企业认证</button>
        <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToEnterpriseReview">认证审核</button>
        <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToSystemStatus">系统状态</button>
        <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToAdminUsers">用户管理</button>
        <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToAuditLogs">审计日志</button>
        <button v-if="!currentUser" class="login-btn" @click="goToLogin">登录</button>
        <button v-else class="login-btn" @click="handleLogout">退出登录</button>
      </div>
    </div>
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
        <el-button type="success" plain :loading="exportLoading" @click="handleExport">导出用户</el-button>
        <el-button type="info" plain @click="goToSystemStatus">系统状态</el-button>
        <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
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
        <el-table-column label="操作" width="320">
          <template #default="scope">
            <div class="table-actions">
              <el-button size="small" type="primary" text @click.stop="openDetail(scope.row)">详情</el-button>
              <el-button
                size="small"
                type="warning"
                v-if="scope.row.is_active"
                :loading="statusLoadingId === scope.row.id"
                @click.stop="toggle(scope.row, 'disable')"
              >禁用</el-button>
              <el-button
                size="small"
                type="success"
                v-else
                :loading="statusLoadingId === scope.row.id"
                @click.stop="toggle(scope.row, 'enable')"
              >启用</el-button>
              <el-button size="small" type="primary" @click.stop="openResetDialog(scope.row)">重置密码</el-button>
              <el-button
                size="small"
                type="danger"
                plain
                :loading="deleteLoadingId === scope.row.id"
                @click.stop="confirmDeleteUser(scope.row)"
              >删除</el-button>
            </div>
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
    <el-drawer
      v-model="detailVisible"
      :with-header="true"
      :close-on-click-modal="false"
      size="46%"
      title="用户详情"
    >
      <div v-if="detailLoading" class="drawer-loading">
        <el-skeleton :rows="6" animated />
      </div>
      <div v-else-if="activeUser" class="detail-content">
        <div class="detail-section">
          <div class="section-title">账户概览</div>
          <el-descriptions :column="2" size="small" border>
            <el-descriptions-item label="用户名">{{ activeUser.username }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag type="info" effect="plain">{{ roleLabel(activeUser.role) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="真实姓名">{{ activeUser.real_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="所属企业">{{ activeUser.company_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="activeUser.is_active ? 'success' : 'danger'">
                {{ activeUser.is_active ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="实名状态">
              <el-tag :type="activeUser.is_authenticated ? 'success' : 'info'">
                {{ activeUser.is_authenticated ? '已实名' : '未实名' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ activeUser.email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ activeUser.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="所属租户" :span="2">
              <span v-if="activeUser.tenant">{{ activeUser.tenant.name }}（{{ activeUser.tenant.type }}）</span>
              <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">{{ formatDate(activeUser.last_login_at) }}</el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ formatDate(activeUser.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <div class="section-title">角色与权限</div>
          <el-alert
            v-if="viewingSelf"
            show-icon
            type="warning"
            :closable="false"
            title="无法在此处修改自己的角色，请联系其他管理员协助。"
          />
          <div class="role-form">
            <el-select
              v-model="roleForm.role"
              placeholder="选择角色"
              style="width: 200px"
              :disabled="viewingSelf || roleSaving"
            >
              <el-option v-for="opt in roleOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
            <el-checkbox v-model="roleForm.isAuthenticated" :disabled="viewingSelf || roleSaving">
              标记为已实名
            </el-checkbox>
            <el-button type="primary" :disabled="viewingSelf" :loading="roleSaving" @click="submitRoleChange">
              保存角色
            </el-button>
          </div>
        </div>

        <div class="detail-section">
          <div class="section-title">企业认证</div>
          <el-empty v-if="!activeUser.certification" description="尚未发起企业认证" />
          <template v-else>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="申请角色">
                <el-tag effect="plain">{{ roleLabel(activeUser.certification.role) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="certTag(activeUser.certification.status)">
                  {{ certText(activeUser.certification.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="公司">{{ activeUser.certification.company_name }}</el-descriptions-item>
              <el-descriptions-item label="统一社会信用代码">
                {{ activeUser.certification.unified_social_credit_code }}
              </el-descriptions-item>
              <el-descriptions-item label="联系人">{{ activeUser.certification.contact_person }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{ activeUser.certification.contact_phone }}</el-descriptions-item>
              <el-descriptions-item label="提交时间">{{ formatDate(activeUser.certification.submitted_at) }}</el-descriptions-item>
              <el-descriptions-item label="审核时间">{{ formatDate(activeUser.certification.reviewed_at) }}</el-descriptions-item>
              <el-descriptions-item label="驳回原因" :span="2">
                {{ activeUser.certification.reject_reason || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </template>
        </div>
      </div>
      <div v-else class="drawer-empty">
        <el-empty description="请选择用户" />
      </div>
    </el-drawer>
  </div>
  <div v-else class="no-access">
    <el-result icon="warning" title="仅监管/管理员可访问">
      <template #extra><el-button type="primary" @click="goHome">返回首页</el-button></template>
    </el-result>
  </div>
  <el-dialog v-model="resetDialogVisible" title="重置用户密码" width="420px" :close-on-click-modal="false">
    <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef" label-width="90px">
      <el-form-item label="用户" prop="username">
        <el-input v-model="resetForm.username" disabled />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="resetForm.newPassword" show-password placeholder="至少8位，含大小写与数字" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetLoading" @click="submitReset">确认重置</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  fetchUsers,
  updateUserStatus,
  getUserDetail,
  deleteUser as deleteUserApi,
  updateUserRole as updateUserRoleApi,
  exportUsersFile,
} from '@/api/admin'
import { adminResetUserPassword } from '@/api/auth'
import { getCurrentUser, clearAuth } from '@/utils/authSession'

const router = useRouter()
const currentUser = getCurrentUser()

const roleLabel = (value) => {
  const map = {
    pharmacy: '药店',
    supplier: '供应商',
    logistics: '物流',
    regulator: '监管',
    admin: '管理员',
    unauth: '未认证',
  }
  return map[value] || value || '-'
}

const userDisplayName = computed(() => currentUser?.displayName || currentUser?.username || '')
const userRoleLabel = computed(() => roleLabel(currentUser?.role))
const isAdmin = computed(() => currentUser?.role === 'admin')

const keyword = ref('')
const role = ref('')
const status = ref('')
const users = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const resetDialogVisible = ref(false)
const resetLoading = ref(false)
const resetFormRef = ref(null)
const resetForm = reactive({ userId: null, username: '', newPassword: '' })
const detailVisible = ref(false)
const detailLoading = ref(false)
const activeUser = ref(null)
const statusLoadingId = ref(null)
const deleteLoadingId = ref(null)
const roleSaving = ref(false)
const exportLoading = ref(false)
const roleForm = reactive({ role: '', isAuthenticated: true })

const roleOptions = [
  { label: '药店', value: 'pharmacy' },
  { label: '供应商', value: 'supplier' },
  { label: '物流', value: 'logistics' },
  { label: '监管', value: 'regulator' },
  { label: '管理员', value: 'admin' },
  { label: '未认证', value: 'unauth' },
]

const viewingSelf = computed(
  () => !!(activeUser.value && currentUser && activeUser.value.id === currentUser.id)
)

const passwordValidator = (_, value, callback) => {
  if (!value) return callback(new Error('请输入新密码'))
  const errors = []
  if (value.length < 8) errors.push('至少8位')
  if (!/[a-z]/.test(value)) errors.push('需含小写字母')
  if (!/[A-Z]/.test(value)) errors.push('需含大写字母')
  if (!/\d/.test(value)) errors.push('需含数字')
  if (errors.length) return callback(new Error(errors.join('、')))
  return callback()
}

const resetRules = {
  newPassword: [{ validator: passwordValidator, trigger: 'blur' }],
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

const applyActiveUser = (user) => {
  activeUser.value = user
  roleForm.role = user?.role || ''
  roleForm.isAuthenticated = !!user?.is_authenticated
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

const openDetail = async (row) => {
  detailVisible.value = true
  detailLoading.value = true
  try {
    const res = await getUserDetail(row.id)
    applyActiveUser(res.user)
  } catch (err) {
    detailVisible.value = false
    ElMessage.error(err?.message || '加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

const toggle = async (row, action) => {
  statusLoadingId.value = row.id
  try {
    const res = await updateUserStatus(row.id, action)
    ElMessage.success(action === 'enable' ? '已启用' : '已禁用')
    if (res?.user && activeUser.value?.id === row.id) {
      applyActiveUser(res.user)
    }
    loadData()
  } catch (err) {
    ElMessage.error(err?.message || '操作失败')
  } finally {
    statusLoadingId.value = null
  }
}

const submitRoleChange = async () => {
  if (!activeUser.value) return
  if (!roleForm.role) {
    ElMessage.error('请选择角色')
    return
  }
  roleSaving.value = true
  try {
    const res = await updateUserRoleApi(activeUser.value.id, {
      role: roleForm.role,
      markAuthenticated: roleForm.isAuthenticated,
    })
    applyActiveUser(res.user)
    ElMessage.success('角色已更新')
    loadData()
  } catch (err) {
    ElMessage.error(err?.message || '角色更新失败')
  } finally {
    roleSaving.value = false
  }
}

const confirmDeleteUser = (row) => {
  if (currentUser && row.id === currentUser.id) {
    ElMessage.error('无法删除当前登录的管理员账号')
    return
  }
  ElMessageBox.confirm(`确认删除用户【${row.username}】？该操作会立即生效，请谨慎。`, '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => handleDeleteUser(row))
    .catch(() => {})
}

const handleDeleteUser = async (row) => {
  deleteLoadingId.value = row.id
  try {
    await deleteUserApi(row.id)
    ElMessage.success('用户已删除')
    if (activeUser.value?.id === row.id) {
      detailVisible.value = false
      activeUser.value = null
    }
    loadData()
  } catch (err) {
    ElMessage.error(err?.message || '删除失败')
  } finally {
    deleteLoadingId.value = null
  }
}

const handleLogout = () => {
  clearAuth()
  ElMessage.success('已退出登录')
  router.push({ name: 'login' })
}

const goToLogin = () => router.push('/login')

const goToChangePassword = () => {
  if (!currentUser) {
    router.push({ name: 'login', query: { redirect: '/change-password' } })
    return
  }
  router.push({ name: 'change-password' })
}

const goToEnterpriseAuth = () => {
  if (!currentUser) {
    router.push({ name: 'login', query: { redirect: '/enterprise-auth' } })
    return
  }
  if (['regulator', 'admin'].includes(currentUser.role)) return
  router.push('/enterprise-auth')
}

const goToEnterpriseReview = () => {
  if (!currentUser) return router.push('/login')
  if (currentUser.role !== 'admin') return
  router.push('/enterprise-review')
}

const goToAdminUsers = () => router.push({ name: 'admin-users' })
const goToAuditLogs = () => router.push({ name: 'admin-audit-logs' })

const handleExport = async () => {
  exportLoading.value = true
  try {
    const res = await exportUsersFile('csv')
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const dateStr = new Date().toISOString().slice(0, 10)
    link.href = url
    link.download = `用户列表_${dateStr}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('用户列表已导出')
  } catch (err) {
    ElMessage.error(err?.message || '导出失败')
  } finally {
    exportLoading.value = false
  }
}

const openResetDialog = (row) => {
  resetForm.userId = row.id
  resetForm.username = row.username
  resetForm.newPassword = ''
  resetDialogVisible.value = true
}

const submitReset = () => {
  if (!resetFormRef.value) return
  resetFormRef.value.validate(async (valid) => {
    if (!valid) return
    resetLoading.value = true
    try {
      await adminResetUserPassword({ userId: resetForm.userId, newPassword: resetForm.newPassword })
      ElMessage.success('密码已重置')
      resetDialogVisible.value = false
      loadData()
    } catch (err) {
      ElMessage.error(err?.message || '重置失败')
    } finally {
      resetLoading.value = false
    }
  })
}

const goToSystemStatus = () => router.push('/admin/status')
const goHome = () => router.push('/')

onMounted(() => {
  if (isAdmin.value) loadData()
})
</script>

<style scoped>
.admin-users { padding:20px; background:#f5f7fb; min-height:100vh; }
.admin-top-actions { display:flex; justify-content:flex-end; margin-bottom:12px; }
.user-actions { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.user-info { display:flex; align-items:center; padding:6px 12px; border-radius:999px; background-color:#f0f5ff; color:#1a73e8; font-size:14px; font-weight:600; gap:8px; }
.user-name { white-space:nowrap; }
.user-role { padding:2px 10px; border-radius:999px; background-color:#fff; border:1px solid rgba(26,115,232,0.2); font-size:12px; color:#1a73e8; }
.auth-btn { border:1px solid #1a73e8; background-color:transparent; color:#1a73e8; padding:8px 14px; border-radius:4px; cursor:pointer; transition:background-color 0.3s; }
.auth-btn:hover { background-color:rgba(26,115,232,0.08); }
.admin-btn { background-color:#f0f5ff; color:#1a73e8; border:1px solid #d6e4ff; padding:8px 14px; border-radius:4px; cursor:pointer; }
.admin-btn:hover { background-color:#e5edff; }
.login-btn { background-color:#1a73e8; color:#fff; border:none; padding:8px 20px; border-radius:4px; cursor:pointer; font-size:14px; transition:background-color 0.3s; }
.login-btn:hover { background-color:#0d62d9; }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; background:#fff; padding:14px; border-radius:10px; border:1px solid #eef2f7; }
.eyebrow { color:#1a73e8; font-weight:600; margin:0 0 4px 0; }
.subtitle { margin:4px 0 0 0; color:#606266; font-size:13px; }
.filters { display:flex; gap:10px; align-items:center; }
.pager { margin-top:12px; display:flex; justify-content:flex-end; }
.no-access { padding:40px; }
.dialog-footer { display:flex; justify-content:flex-end; gap:10px; }
.table-actions { display:flex; flex-wrap:wrap; gap:6px; }
.drawer-loading { padding:20px; }
.detail-content { display:flex; flex-direction:column; gap:18px; }
.detail-section { margin-bottom:4px; }
.detail-section .section-title { font-weight:600; margin-bottom:8px; }
.role-form { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-top:8px; }
</style>
