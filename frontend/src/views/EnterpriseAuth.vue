<template>
  <div class="enterprise-auth-page">
    <div class="page-header">
      <div>
        <p class="eyebrow">企业认证</p>
        <h2>根据企业类型提交资质信息，审核通过后解锁角色权限</h2>
        <p class="subtitle">基础信息为必填项，药店/供应商/物流可选择是否上传资质文件。</p>
      </div>
      <div class="status-chip" :class="status">
        <span>{{ statusText }}</span>
        <small v-if="application?.reject_reason">原因：{{ application.reject_reason }}</small>
      </div>
    </div>

    <div class="content-grid">
      <div class="left-col">
        <el-card shadow="never" class="card">
          <div class="card-header">
            <div>
              <div class="card-title">1. 选择认证角色</div>
              <p class="card-desc">不同角色的资质要求不同，监管/管理员账号无需在此认证。</p>
            </div>
            <el-tag size="small" type="info">营业执照选填</el-tag>
          </div>
          <el-alert
            v-if="roleForbidden"
            type="warning"
            show-icon
            title="当前登录角色由系统管理员直接配置，无需在此提交认证"
            description="如需变更角色，请联系系统管理员。"
          />
          <template v-else>
            <el-radio-group v-model="selectedRole" class="role-group">
              <el-radio-button v-for="item in availableRoles" :key="item.key" :label="item.key">
                {{ item.label }}
              </el-radio-button>
            </el-radio-group>
            <div class="requirement-panel">
              <div class="req-title">资质要求</div>
              <ul class="req-list">
                <li v-for="doc in currentRequirement.docs" :key="doc">
                  <el-icon><DocumentChecked /></el-icon>
                  <span>{{ doc }}</span>
                </li>
              </ul>
              <p class="note">{{ currentRequirement.note }}</p>
              <div class="base-fields">
                <div class="base-title">基础信息（必填）</div>
                <div class="chips">
                  <el-tag v-for="field in baseRequiredFields" :key="field" type="warning" effect="plain" size="small">
                    {{ baseFieldLabels[field] || field }}
                  </el-tag>
                </div>
              </div>
              <div class="remind">
                <el-icon><BellFilled /></el-icon>
                <span>提交后状态变为“审核中”，服务目标 3 个工作日内完成，24 小时后自动提醒管理员团队。</span>
              </div>
            </div>
          </template>
        </el-card>

        <el-card shadow="never" class="card status-card">
          <div class="card-header">
            <div class="card-title">2. 审核进度</div>
            <el-tag :type="statusTagType" size="small">{{ statusText }}</el-tag>
          </div>
          <el-steps :active="stepActive" simple finish-status="success">
            <el-step title="已提交" />
            <el-step title="审核中" />
            <el-step title="审核完成" />
          </el-steps>
          <ul class="status-meta">
            <li><strong>当前状态：</strong>{{ statusText }}</li>
            <li><strong>最近提交：</strong>{{ application?.submitted_at ? formatDate(application.submitted_at) : '未提交' }}</li>
            <li><strong>预计完成：</strong>{{ reviewEtaText }}</li>
            <li><strong>剩余可重提次数：</strong>{{ attemptsLeft }}</li>
            <li v-if="application?.reject_reason"><strong>驳回原因：</strong>{{ application.reject_reason }}</li>
            <li v-if="application?.qualification_files?.length"><strong>已存储附件：</strong>{{ application.qualification_files.length }} 个</li>
          </ul>
        </el-card>
      </div>

      <div class="right-col">
        <el-card v-if="!roleForbidden" shadow="never" class="card form-card">
          <div class="card-header">
            <div class="card-title">3. 填写企业信息</div>
            <el-tag type="warning" effect="plain" size="small">基础信息必填</el-tag>
          </div>
          <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="auth-form">
            <el-form-item label="企业名称" prop="company_name">
              <el-input v-model="form.company_name" placeholder="填写企业名称" />
            </el-form-item>
            <el-form-item label="统一社会信用代码" prop="unified_social_credit_code">
              <el-input v-model="form.unified_social_credit_code" placeholder="18 位统一社会信用代码" />
            </el-form-item>
            <el-form-item label="企业联系人" prop="contact_person">
              <el-input v-model="form.contact_person" placeholder="填写企业联系人" />
            </el-form-item>
            <div class="two-col">
              <el-form-item label="联系电话" prop="contact_phone">
                <el-input v-model="form.contact_phone" placeholder="手机或座机号码" />
              </el-form-item>
              <el-form-item label="联系邮箱" prop="contact_email">
                <el-input v-model="form.contact_email" placeholder="用于接收审核通知" />
              </el-form-item>
            </div>
            <el-form-item label="注册地址" prop="registered_address">
              <el-input v-model="form.registered_address" placeholder="填写营业执照上的注册地址" />
            </el-form-item>
            <el-form-item label="经营范围" prop="business_scope">
              <el-input v-model="form.business_scope" type="textarea" :rows="3" placeholder="填写药品经营/生产范围" />
            </el-form-item>

            <el-form-item label="资质文件（可选上传，JPG/PNG/PDF，≤5MB）">
              <el-upload
                drag
                multiple
                :limit="5"
                :show-file-list="true"
                :auto-upload="false"
                :file-list="fileList"
                :before-upload="beforeUpload"
                :on-change="onFileChange"
                :on-remove="onFileRemove"
              >
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 JPG、PNG、PDF，单个文件不超过 5MB，可不上传资质文件；若已提交过附件再无更新，可直接提交基础信息。
                  </div>
                </template>
              </el-upload>
              <div v-if="application?.qualification_files?.length" class="existing-files">
                <div class="label">已存储附件（上次提交）</div>
                <ul>
                  <li v-for="(file, idx) in application.qualification_files" :key="idx">
                    <el-icon><Document /></el-icon>
                    <span>{{ file.name }}</span>
                    <small>{{ formatSize(file.size) }}</small>
                  </li>
                </ul>
              </div>
            </el-form-item>

            <div class="form-actions">
              <el-button @click="resetForm" :disabled="submitting">重置</el-button>
              <el-button type="primary" :loading="submitting" @click="submit">
                {{ status === 'pending' ? '更新资料' : '提交认证' }}
              </el-button>
            </div>
          </el-form>
        </el-card>
        <el-card v-else shadow="never" class="card form-card">
          <el-result
            icon="info"
            title="当前角色无需认证"
            sub-title="监管/管理员账号由系统管理员直接配置，如需调整请联系管理员。"
          />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, DocumentChecked, Document, BellFilled } from '@element-plus/icons-vue'
import { fetchRequirements, fetchMyApplication, submitApplication } from '@/api/enterprise'
import { getCurrentUser } from '@/utils/authSession'

const formRef = ref(null)
const submitting = ref(false)
const application = ref(null)
const attemptsLeft = ref(3)
const requirements = ref({ roles: {} })
const uploadPolicy = ref({ max_size_mb: 5, allowed_ext: ['jpg', 'jpeg', 'png', 'pdf'] })
const reviewEta = ref(null)

const baseRoleOptions = [
  { key: 'pharmacy', label: '药店用户' },
  { key: 'supplier', label: '供应商用户' },
  { key: 'logistics', label: '物流用户' },
]

const currentUser = getCurrentUser()
const roleForbidden = computed(() => ['regulator', 'admin'].includes(currentUser?.role))
const availableRoles = computed(() => {
  if (roleForbidden.value) return []
  if (!currentUser?.role) return baseRoleOptions
  const matched = baseRoleOptions.find((r) => r.key === currentUser.role)
  return matched ? [matched] : baseRoleOptions
})
const defaultRole = availableRoles.value[0]?.key || baseRoleOptions[0].key
const selectedRole = ref(defaultRole)

const form = reactive({
  company_name: '',
  unified_social_credit_code: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  registered_address: '',
  business_scope: '',
})

const rules = {
  company_name: [{ required: true, message: '请填写企业名称', trigger: 'blur' }],
  unified_social_credit_code: [{ required: true, message: '请填写统一社会信用代码', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请填写企业联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请填写联系电话', trigger: 'blur' }],
  contact_email: [
    { required: true, message: '请填写联系邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] },
  ],
  registered_address: [{ required: true, message: '请填写注册地址', trigger: 'blur' }],
  business_scope: [{ required: true, message: '请填写经营范围', trigger: 'blur' }],
}

const baseFieldLabels = {
  company_name: '企业名称',
  unified_social_credit_code: '统一社会信用代码',
  contact_person: '企业联系人',
  contact_phone: '联系电话',
  contact_email: '联系邮箱',
  registered_address: '注册地址',
  business_scope: '经营范围',
}

const fileList = ref([])
const baseRequiredFields = computed(() => requirements.value.base_required_fields || Object.keys(baseFieldLabels))

const currentRequirement = computed(() => {
  const matched = requirements.value.roles?.[selectedRole.value]
  return matched || { docs: [], note: '请选择角色查看要求' }
})

const status = computed(() => application.value?.status || 'unsubmitted')
const statusText = computed(() => {
  if (status.value === 'approved') return '审核通过'
  if (status.value === 'pending') return '审核中'
  if (status.value === 'rejected') return '审核未通过'
  return '未提交'
})
const statusTagType = computed(() => {
  if (status.value === 'approved') return 'success'
  if (status.value === 'pending') return 'info'
  if (status.value === 'rejected') return 'danger'
  return ''
})
const stepActive = computed(() => {
  if (status.value === 'approved' || status.value === 'rejected') return 3
  if (status.value === 'pending') return 2
  return 1
})

const reviewEtaText = computed(() => {
  if (application.value?.status === 'pending' && reviewEta.value) return reviewEta.value
  if (!application.value) return '提交后生成'
  return application.value.reviewed_at ? formatDate(application.value.reviewed_at) : '预计 3 个工作日内完成'
})

function formatDate(value) {
  try {
    return new Date(value).toLocaleString()
  } catch {
    return value
  }
}

function formatSize(size) {
  if (!size && size !== 0) return ''
  const mb = size / 1024 / 1024
  if (mb >= 1) return `${mb.toFixed(2)} MB`
  return `${(size / 1024).toFixed(1)} KB`
}

async function loadRequirements() {
  const res = await fetchRequirements()
  requirements.value = res
  uploadPolicy.value = res.upload_policy || uploadPolicy.value
}

async function loadApplication() {
  const res = await fetchMyApplication()
  application.value = res.application
  attemptsLeft.value = res.attempts_left ?? attemptsLeft.value
  if (res.application) {
    selectedRole.value = res.application.role || selectedRole.value
    Object.keys(form).forEach((key) => {
      form[key] = res.application[key] || ''
    })
  }
}

const beforeUpload = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  const allowed = uploadPolicy.value.allowed_ext || []
  if (allowed.length && !allowed.includes(ext)) {
    ElMessage.error(`仅支持 ${allowed.join('/')} 格式`)
    return false
  }
  const maxBytes = (uploadPolicy.value.max_size_mb || 5) * 1024 * 1024
  if (file.size > maxBytes) {
    ElMessage.error('单个文件不能超过 5MB')
    return false
  }
  return true
}

const onFileChange = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const onFileRemove = (file, uploadFiles) => {
  fileList.value = uploadFiles
}

function resetForm() {
  Object.keys(form).forEach((key) => (form[key] = ''))
  fileList.value = []
}

async function submit() {
  if (roleForbidden.value) {
    ElMessage.warning('当前角色由管理员直接配置，无需在此提交认证')
    return
  }
  if (application.value?.status === 'rejected' && attemptsLeft.value <= 0) {
    ElMessage.error('重提次数已达上限，请联系管理员')
    return
  }
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = { ...form }
    const resp = await submitApplication({
      role: selectedRole.value,
      form: payload,
      files: fileList.value,
    })
    application.value = resp.application
    attemptsLeft.value = resp.attempts_left ?? attemptsLeft.value
    reviewEta.value = resp.review_eta
    fileList.value = []
    ElMessage.success(resp.msg || '已提交认证，等待审核')
  } catch (err) {
    ElMessage.error(err?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    await loadRequirements()
    await loadApplication()
  } catch (err) {
    ElMessage.error(err?.message || '加载认证信息失败')
  }
})
</script>

<style scoped>
.enterprise-auth-page {
  padding: 20px;
  background: #f5f7fb;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #eef2f7;
  margin-bottom: 18px;
}

.eyebrow {
  color: #1a73e8;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1f2f3d;
}

.subtitle {
  margin: 6px 0 0 0;
  color: #606266;
  font-size: 14px;
}

.status-chip {
  padding: 10px 14px;
  border-radius: 10px;
  background: #f4f4f5;
  min-width: 140px;
  text-align: right;
}

.status-chip.pending {
  background: #eaf3ff;
  color: #1a73e8;
}

.status-chip.approved {
  background: #e6ffed;
  color: #1e8a4b;
}

.status-chip.rejected {
  background: #fff5f5;
  color: #c53030;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 16px;
}

.card {
  border: 1px solid #eef2f7;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-title {
  font-weight: 600;
  color: #1f2f3d;
}

.card-desc {
  margin: 4px 0 0 0;
  color: #606266;
  font-size: 13px;
}

.role-group {
  width: 100%;
  margin-bottom: 12px;
}

.requirement-panel {
  background: #f8fbff;
  border: 1px dashed #d6e6ff;
  padding: 12px;
  border-radius: 10px;
}

.req-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.req-list {
  list-style: none;
  padding: 0;
  margin: 0 0 8px 0;
}

.req-list li {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  color: #303133;
}

.note {
  color: #606266;
  font-size: 13px;
  margin: 4px 0 10px 0;
}

.base-fields {
  margin-top: 6px;
}

.base-title {
  font-size: 13px;
  color: #303133;
  margin-bottom: 6px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.remind {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 10px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #eef2f7;
  color: #303133;
}

.status-card .status-meta {
  list-style: none;
  margin: 12px 0 0 0;
  padding: 0;
  color: #303133;
  line-height: 1.6;
}

.right-col .card-header {
  margin-bottom: 16px;
}

.auth-form .two-col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.upload-icon {
  font-size: 28px;
  color: #409eff;
  margin-bottom: 6px;
}

.existing-files {
  margin-top: 10px;
  background: #f8f8f8;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ededed;
}

.existing-files .label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.existing-files ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.existing-files li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  color: #303133;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 12px;
}

@media (max-width: 1080px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .auth-form .two-col {
    grid-template-columns: 1fr;
  }
}
</style>
