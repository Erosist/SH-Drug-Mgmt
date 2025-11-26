<template>
  <div class="review-page" v-if="isAdmin">
    <div class="page-header">
      <div>
        <p class="eyebrow">企业认证审核</p>
        <h2>根据用户申请角色逐项核验资质</h2>
        <p class="subtitle">服务目标 3 个工作日完成审核，提交 24 小时后自动提醒管理员。</p>
      </div>
      <div class="filters">
        <el-select v-model="statusFilter" placeholder="状态" size="small" @change="loadList">
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
          <el-option label="全部" value="" />
        </el-select>
        <el-select v-model="roleFilter" placeholder="角色" size="small" @change="loadList">
          <el-option label="全部" value="" />
          <el-option label="药店" value="pharmacy" />
          <el-option label="供应商" value="supplier" />
          <el-option label="物流" value="logistics" />
        </el-select>
        <el-button type="primary" size="small" @click="loadList" :loading="loading">刷新</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>待审核列表</span>
          <span class="hint">仅显示当前筛选条件下的申请，点击行查看详情并审核。</span>
        </div>
      </template>
      <el-table :data="applications" style="width: 100%" @row-click="openDetail" :loading="loading">
        <el-table-column prop="company_name" label="企业名称" min-width="200" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag type="info" effect="plain">{{ roleLabel(scope.row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="statusTag(scope.row.status)">{{ statusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="scope">{{ formatDate(scope.row.submitted_at) }}</template>
        </el-table-column>
        <el-table-column prop="attempt_count" label="提交次数" width="120" />
        <el-table-column prop="reject_reason" label="最近驳回原因" min-width="200">
          <template #default="scope">
            <span>{{ scope.row.reject_reason || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="drawerVisible" size="48%" :title="detailTitle">
      <div v-if="detail">
        <div class="section">
          <div class="section-title">企业信息</div>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="企业名称">{{ detail.company_name }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag type="info" effect="plain">{{ roleLabel(detail.role) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="统一社会信用代码">{{ detail.unified_social_credit_code }}</el-descriptions-item>
            <el-descriptions-item label="联系人">{{ detail.contact_person }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ detail.contact_phone }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ detail.contact_email }}</el-descriptions-item>
            <el-descriptions-item label="注册地址" :span="2">{{ detail.registered_address }}</el-descriptions-item>
            <el-descriptions-item label="经营范围" :span="2">{{ detail.business_scope }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="section">
          <div class="section-title">审核标准</div>
          <p class="role-tip">当前审核角色：{{ roleLabel(detail.role) }}</p>
          <div class="standard-group">
            <div class="standard-title">共通标准</div>
            <el-checkbox-group v-model="checkedStandards.common">
              <el-checkbox v-for="item in standards.common" :key="item" :label="item">{{ item }}</el-checkbox>
            </el-checkbox-group>
          </div>
          <div class="standard-group">
            <div class="standard-title">角色专属标准</div>
            <el-checkbox-group v-model="checkedStandards.role">
              <el-checkbox v-for="item in roleStandards" :key="item" :label="item">{{ item }}</el-checkbox>
            </el-checkbox-group>
          </div>
          <div class="standard-actions">
            <el-button size="small" @click="checkAll">全部符合</el-button>
            <el-button size="small" @click="clearChecks">清空勾选</el-button>
          </div>
        </div>

        <div class="section">
          <div class="section-title">资质文件（可选）</div>
          <el-empty description="未上传文件" v-if="!detail.qualification_files || !detail.qualification_files.length" />
          <el-timeline v-else>
            <el-timeline-item v-for="(file, idx) in detail.qualification_files" :key="idx" :timestamp="formatSize(file.size)">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ file.name }}</span>
              <span class="file-path">已安全存储</span>
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="section">
          <div class="section-title">审核决策</div>
          <el-alert type="info" show-icon title="驳回时必须选择标准化原因，可补充备注说明" :closable="false" />
          <div class="decision-row">
            <el-select v-model="rejectReason" placeholder="选择驳回原因" style="flex:1">
              <el-option v-for="item in rejectReasons" :key="item.code" :label="item.label" :value="item.code" />
            </el-select>
            <el-input v-model="remark" type="textarea" :rows="2" placeholder="可选备注说明" />
          </div>
          <div class="action-row">
            <el-button type="success" :loading="reviewing" @click="submitDecision('approved')">通过审核</el-button>
            <el-button type="danger" plain :loading="reviewing" @click="submitDecision('rejected')">驳回申请</el-button>
          </div>
        </div>

        <div class="section" v-if="detail.review_logs?.length">
          <div class="section-title">审核记录</div>
          <el-timeline>
            <el-timeline-item v-for="log in detail.review_logs" :key="log.id" :timestamp="formatDate(log.created_at)">
              <span class="log-item">{{ log.decision === 'approved' ? '通过' : '驳回' }} - {{ log.reason_text || log.reason_code || '' }}</span>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-drawer>
  </div>

  <div v-else class="no-access">
    <el-result icon="warning" title="仅系统管理员可访问">
      <template #extra>
        <el-button type="primary" @click="goHome">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/utils/authSession'
import { fetchApplications, fetchApplicationDetail, reviewCertificationByCert } from '@/api/enterprise'

const router = useRouter()
const currentUser = getCurrentUser()
const isAdmin = computed(() => currentUser?.role === 'admin')

const applications = ref([])
const loading = ref(false)
const statusFilter = ref('pending')
const roleFilter = ref('')
const drawerVisible = ref(false)
const detail = ref(null)
const standards = ref({ common: [], roles: {} })
const rejectReasons = ref([])
const checkedStandards = ref({ common: [], role: [] })
const rejectReason = ref('')
const remark = ref('')
const reviewing = ref(false)

const roleLabel = (role) => {
  const map = { pharmacy: '药店', supplier: '供应商', logistics: '物流' }
  return map[role] || role || '-'
}

const statusText = (status) => {
  if (status === 'approved') return '已通过'
  if (status === 'pending') return '待审核'
  if (status === 'rejected') return '已驳回'
  return status || '-'
}

const statusTag = (status) => {
  if (status === 'approved') return 'success'
  if (status === 'pending') return 'info'
  if (status === 'rejected') return 'danger'
  return ''
}

const roleStandards = computed(() => {
  const role = detail.value?.role
  return standards.value.roles?.[role] || []
})

const detailTitle = computed(() => (detail.value ? `审核：${detail.value.company_name}` : '企业详情'))

const formatDate = (value) => {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return value
  }
}

const formatSize = (size) => {
  if (!size && size !== 0) return ''
  const mb = size / 1024 / 1024
  return mb >= 1 ? `${mb.toFixed(2)} MB` : `${(size / 1024).toFixed(1)} KB`
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await fetchApplications({ status: statusFilter.value, role: roleFilter.value })
    applications.value = res.items || []
    standards.value = res.standards || standards.value
    rejectReasons.value = res.reject_reasons || []
  } catch (err) {
    ElMessage.error(err?.message || '加载列表失败')
  } finally {
    loading.value = false
  }
}

const openDetail = async (row) => {
  drawerVisible.value = true
  detail.value = null
  rejectReason.value = ''
  remark.value = ''
  checkedStandards.value = { common: [], role: [] }
  try {
    const res = await fetchApplicationDetail(row.id)
    detail.value = res.application
    if (res.application?.standards) {
      standards.value = {
        common: res.application.standards.common || standards.value.common,
        roles: { ...(standards.value.roles || {}), [res.application.role]: res.application.standards.roles || [] },
      }
    }
    rejectReasons.value = res.application?.reject_reasons || rejectReasons.value
  } catch (err) {
    ElMessage.error(err?.message || '加载详情失败')
  }
}

const checkAll = () => {
  checkedStandards.value = {
    common: [...(standards.value.common || [])],
    role: [...roleStandards.value],
  }
}

const clearChecks = () => {
  checkedStandards.value = { common: [], role: [] }
}

const submitDecision = async (decision) => {
  if (!detail.value) return
  if (decision === 'rejected' && !rejectReason.value) {
    ElMessage.warning('请选择标准化驳回原因')
    return
  }
  const confirmed = await ElMessageBox.confirm(
    `确认将该申请标记为「${decision === 'approved' ? '通过' : '驳回'}」吗？`,
    '确认操作',
    { type: decision === 'approved' ? 'success' : 'warning' }
  ).catch(() => null)
  if (!confirmed) return
  if (decision === 'rejected' && !rejectReason.value) return

  reviewing.value = true
  try {
    await reviewCertificationByCert({
      certId: detail.value.id,
      decision,
      reasonCode: decision === 'rejected' ? rejectReason.value : undefined,
      remark: remark.value,
    })
    ElMessage.success('审核结果已记录')
    drawerVisible.value = false
    await loadList()
  } catch (err) {
    ElMessage.error(err?.message || '提交失败')
  } finally {
    reviewing.value = false
  }
}

const goHome = () => router.push('/')

onMounted(() => {
  if (!isAdmin.value) return
  loadList()
})
</script>

<style scoped>
.review-page {
  padding: 20px;
  background: #f5f7fb;
  min-height: 100vh;
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

.filters {
  display: flex;
  gap: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint {
  color: #909399;
  font-size: 13px;
}

.section {
  margin-bottom: 18px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.role-tip {
  margin: 0 0 6px 0;
  color: #606266;
}

.standard-group {
  border: 1px solid #eef2f7;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
  background: #f9fbff;
}

.standard-title {
  font-size: 13px;
  margin-bottom: 6px;
  color: #303133;
}

.standard-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

.decision-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 10px 0;
}

.action-row {
  display: flex;
  gap: 10px;
}

.file-name {
  margin-left: 8px;
}

.file-path {
  margin-left: 8px;
  color: #909399;
}

.log-item {
  color: #303133;
}

.no-access {
  padding: 40px;
}
</style>
