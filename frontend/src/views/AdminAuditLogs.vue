<template>
  <div class="audit-page" v-if="isAdmin">
    <div class="page-header">
      <div>
        <p class="eyebrow">审计记录</p>
        <h2>追踪所有管理员关键操作</h2>
        <p class="subtitle">支持按管理员、目标用户、操作类型及时间范围过滤，便于合规留痕。</p>
      </div>
      <div class="actions">
        <el-button @click="goToSystemStatus">系统状态</el-button>
        <el-button type="primary" @click="goToAdminUsers">用户管理</el-button>
        <el-button @click="goToAnnouncements">公告管理</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <div class="filters">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="管理员ID">
            <el-input v-model="filters.adminId" placeholder="例如 1001" clearable />
          </el-form-item>
          <el-form-item label="目标用户ID">
            <el-input v-model="filters.targetUserId" placeholder="用户ID" clearable />
          </el-form-item>
          <el-form-item label="操作类型">
            <el-select v-model="filters.action" placeholder="全部" clearable filterable>
              <el-option v-for="opt in actionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filters.dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始"
              end-placeholder="结束"
              value-format="YYYY-MM-DDTHH:mm:ssZ"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset" :disabled="loading">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="logs" v-loading="loading" style="width: 100%">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="admin_id" label="管理员" width="140">
          <template #default="scope">
            <div class="cell-user">
              <span>ID {{ scope.row.admin_id }}</span>
              <small v-if="scope.row.admin?.username">{{ scope.row.admin.username }}</small>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" width="160">
          <template #default="scope">
            <el-tag effect="plain" size="small">{{ getActionLabel(scope.row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_user_id" label="目标用户" width="150">
          <template #default="scope">
            <span v-if="scope.row.target_user_id">ID {{ scope.row.target_user_id }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="资源" min-width="160">
          <template #default="scope">
            <div>
              <span>{{ scope.row.resource_type || '-' }}</span>
              <small v-if="scope.row.resource_id">#{{ scope.row.resource_id }}</small>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="request_path" label="请求" min-width="200">
          <template #default="scope">
            <div class="request-info">
              <span>{{ scope.row.request_method }}</span>
              <span>{{ scope.row.request_path }}</span>
            </div>
            <small class="request-ip" v-if="scope.row.request_ip">IP {{ scope.row.request_ip }}</small>
          </template>
        </el-table-column>
        <el-table-column label="详情" width="120">
          <template #default="scope">
            <el-button type="primary" text size="small" @click="openDrawer(scope.row)">查看</el-button>
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
          hide-on-single-page
        />
      </div>
    </el-card>

    <el-drawer
      v-model="drawerVisible"
      title="操作详情"
      size="40%"
      :close-on-click-modal="true"
    >
      <template v-if="activeLog">
        <el-descriptions column="2" border size="small">
          <el-descriptions-item label="时间">{{ formatDate(activeLog.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="操作">{{ getActionLabel(activeLog.action) }}</el-descriptions-item>
          <el-descriptions-item label="管理员">
            ID {{ activeLog.admin_id }}
            <template v-if="activeLog.admin?.username">（{{ activeLog.admin.username }}）</template>
          </el-descriptions-item>
          <el-descriptions-item label="目标用户">
            <span v-if="activeLog.target_user_id">ID {{ activeLog.target_user_id }}</span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="资源">
            {{ activeLog.resource_type || '-' }}
            <template v-if="activeLog.resource_id"> #{{ activeLog.resource_id }}</template>
          </el-descriptions-item>
          <el-descriptions-item label="请求">
            {{ activeLog.request_method }} {{ activeLog.request_path }}
          </el-descriptions-item>
          <el-descriptions-item label="IP">{{ activeLog.request_ip || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="details-block">
          <div class="block-title">附加详情</div>
          <el-empty description="无附加字段" v-if="!hasDetails" />
          <el-scrollbar height="220px" v-else>
            <pre class="json-view">{{ formattedDetails }}</pre>
          </el-scrollbar>
        </div>
      </template>
      <el-empty v-else description="无数据" />
    </el-drawer>
  </div>
  <div v-else class="no-access">
    <el-result icon="warning" title="仅系统管理员可访问">
      <template #extra><el-button type="primary" @click="goHome">返回首页</el-button></template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchAdminAuditLogs } from '@/api/admin'
import { getCurrentUser } from '@/utils/authSession'

const router = useRouter()
const currentUser = ref(getCurrentUser())
const logs = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const drawerVisible = ref(false)
const activeLog = ref(null)

const filters = reactive({
  adminId: '',
  targetUserId: '',
  action: '',
  dateRange: [],
})

const actionOptions = [
  { label: '查看用户列表', value: 'list_users' },
  { label: '导出用户列表', value: 'export_users' },
  { label: '禁用用户', value: 'disable_user' },
  { label: '启用用户', value: 'enable_user' },
  { label: '删除用户', value: 'delete_user' },
  { label: '更新用户角色', value: 'update_user_role' },
  { label: '通过企业认证审核', value: 'approve_enterprise_cert' },
  { label: '驳回企业认证审核', value: 'reject_enterprise_cert' },
  { label: '查看审计日志', value: 'list_audit_logs' },
  { label: '查看系统状态', value: 'system_status' },
]

const actionLabelMap = actionOptions.reduce((acc, item) => {
  acc[item.value] = item.label
  return acc
}, {})

const getActionLabel = (val) => actionLabelMap[val] || val || '-'

const isAdmin = computed(() => currentUser.value?.role === 'admin')
const hasDetails = computed(() => activeLog.value && Object.keys(activeLog.value.details || {}).length > 0)
const formattedDetails = computed(() => {
  if (!hasDetails.value) return ''
  return JSON.stringify(activeLog.value.details, null, 2)
})

const formatDate = (value) => {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return value
  }
}

const buildParams = () => {
  const [start, end] = filters.dateRange || []
  return {
    adminId: filters.adminId || undefined,
    targetUserId: filters.targetUserId || undefined,
    action: filters.action || undefined,
    start: start || undefined,
    end: end || undefined,
    page: page.value,
    perPage: perPage.value,
  }
}

const loadLogs = async () => {
  if (!isAdmin.value) return
  loading.value = true
  try {
    const res = await fetchAdminAuditLogs(buildParams())
    logs.value = res.items || []
    total.value = res.total || 0
    page.value = res.page || 1
    perPage.value = res.per_page || perPage.value
  } catch (err) {
    ElMessage.error(err?.message || '加载审计日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadLogs()
}

const handleReset = () => {
  filters.adminId = ''
  filters.targetUserId = ''
  filters.action = ''
  filters.dateRange = []
  page.value = 1
  loadLogs()
}

const handlePageChange = (p) => {
  page.value = p
  loadLogs()
}

const openDrawer = (row) => {
  activeLog.value = row
  drawerVisible.value = true
}

const goHome = () => router.push('/')
const goToSystemStatus = () => router.push('/admin/status')
const goToAdminUsers = () => router.push('/admin/users')
const goToAnnouncements = () => router.push('/admin/announcements')

const refreshUser = () => {
  currentUser.value = getCurrentUser()
}

onMounted(() => {
  window.addEventListener('storage', refreshUser)
  if (isAdmin.value) loadLogs()
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', refreshUser)
})
</script>

<style scoped>
.audit-page {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fb;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #eef2f7;
}

.eyebrow {
  color: #1a73e8;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.subtitle {
  margin: 4px 0 0 0;
  color: #606266;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 10px;
}

.filters {
  margin-bottom: 12px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  align-items: flex-end;
}

.cell-user {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  line-height: 1.2;
}

.request-info {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #303133;
}

.request-ip {
  font-size: 11px;
  color: #909399;
}

.pager {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

.details-block {
  margin-top: 16px;
}

.block-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.json-view {
  background: #1e1e1e;
  color: #dcdcdc;
  border-radius: 6px;
  padding: 12px;
  font-size: 12px;
}

.no-access {
  padding: 40px;
}
</style>
