<template>
  <div class="forgot-page">
    <div class="page-header">
      <h1>找回登录密码</h1>
      <p>选择绑定的邮箱或手机号获取验证码，验证码有效期为10分钟。</p>
    </div>

    <el-row :gutter="24">
      <el-col :xs="24" :md="12">
        <el-card class="card">
          <template #header>
            <div class="card-header">
              <span>第一步：获取验证码</span>
            </div>
          </template>
          <el-form ref="requestRef" :model="requestForm" :rules="requestRules" label-position="top">
            <el-form-item label="账号" prop="identifier">
              <el-input v-model="requestForm.identifier" placeholder="请输入用户名/邮箱/手机号" />
            </el-form-item>
            <el-form-item label="验证方式" prop="channel">
              <el-radio-group v-model="requestForm.channel">
                <el-radio-button label="email">邮箱</el-radio-button>
                <el-radio-button label="phone">手机号</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item :label="requestForm.channel === 'email' ? '邮箱' : '手机号'" prop="contact">
              <el-input v-model="requestForm.contact" :placeholder="requestForm.channel === 'email' ? '请输入注册时的邮箱' : '请输入注册时的手机号'" />
            </el-form-item>
            <el-button type="primary" :loading="sending" :disabled="countdown > 0" @click="handleSendCode">
              {{ countdown > 0 ? `重新发送 (${countdown}s)` : '发送验证码' }}
            </el-button>
            <p class="tips">验证码有效期10分钟，同一方式在倒计时结束前无法重新发送。</p>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="card">
          <template #header>
            <div class="card-header">
              <span>第二步：验证并重置密码</span>
            </div>
          </template>
          <el-alert v-if="!lastRequest" type="info" show-icon title="请先完成第一步获取验证码" class="mb-16" />
          <el-form ref="resetRef" :model="resetForm" :rules="resetRules" label-position="top" :disabled="!lastRequest">
            <el-form-item label="验证码" prop="code">
              <el-input v-model="resetForm.code" placeholder="请输入验证码" />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input v-model="resetForm.newPassword" type="password" placeholder="至少8位且含大小写字母和数字" show-password />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input v-model="resetForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
            </el-form-item>
            <el-button type="primary" :loading="resetting" :disabled="!lastRequest" @click="handleReset">确认重置</el-button>
            <el-button text type="info" @click="goLogin">返回登录</el-button>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { requestResetCode, resetPassword } from '@/api/auth'

const router = useRouter()
const requestForm = reactive({
  identifier: '',
  channel: 'email',
  contact: ''
})
const resetForm = reactive({
  code: '',
  newPassword: '',
  confirmPassword: ''
})
const requestRef = ref(null)
const resetRef = ref(null)
const sending = ref(false)
const resetting = ref(false)
const countdown = ref(0)
const lastRequest = ref(null)
let countdownTimer = null

const emailPattern = /^[\w-.]+@[\w-]+(\.[\w-]+)+$/
const phonePattern = /^\d{6,20}$/

const contactValidator = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入信息'))
    return
  }
  if (requestForm.channel === 'email' && !emailPattern.test(value)) {
    callback(new Error('邮箱格式不正确'))
    return
  }
  if (requestForm.channel === 'phone' && !phonePattern.test(value)) {
    callback(new Error('手机号仅支持6-20位数字'))
    return
  }
  callback()
}

const passwordValidator = (rule, value, callback) => {
  const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/
  if (!pattern.test(value || '')) {
    callback(new Error('至少8位，包含大小写字母和数字'))
  } else {
    callback()
  }
}

const confirmValidator = (rule, value, callback) => {
  if (value !== resetForm.newPassword) {
    callback(new Error('两次输入不一致'))
  } else {
    callback()
  }
}

const requestRules = {
  identifier: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  channel: [{ required: true, message: '请选择方式', trigger: 'change' }],
  contact: [{ required: true, validator: contactValidator, trigger: ['blur', 'change'] }]
}

const resetRules = {
  code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: passwordValidator, trigger: ['blur', 'change'] }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: confirmValidator, trigger: ['blur', 'change'] }
  ]
}

const startCountdown = (seconds = 60) => {
  countdown.value = seconds
  countdownTimer && clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
      countdown.value = 0
    }
  }, 1000)
}

const handleSendCode = async () => {
  if (!requestRef.value) return
  try {
    const valid = await requestRef.value.validate()
    if (!valid) return
    sending.value = true
    const payload = {
      identifier: requestForm.identifier,
      channel: requestForm.channel,
      contact: requestForm.contact
    }
    const resp = await requestResetCode(payload)
    lastRequest.value = payload
    startCountdown(60)
    ElMessage.success('验证码已发送，请在10分钟内完成验证')
    if (resp?.debug_code) {
      ElMessage.info(`开发环境验证码：${resp.debug_code}`)
    }
  } catch (error) {
    ElMessage.error(error.message || '验证码发送失败')
  } finally {
    sending.value = false
  }
}

const handleReset = async () => {
  if (!lastRequest.value || !resetRef.value) return
  try {
    const valid = await resetRef.value.validate()
    if (!valid) return
    resetting.value = true
    await resetPassword({
      ...lastRequest.value,
      code: resetForm.code,
      newPassword: resetForm.newPassword
    })
    ElMessage.success('密码重置成功，请使用新密码登录')
    router.push({ name: 'login' })
  } catch (error) {
    ElMessage.error(error.message || '密码重置失败')
  } finally {
    resetting.value = false
  }
}

const goLogin = () => {
  router.push({ name: 'login' })
}

onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})
</script>

<style scoped>
.forgot-page {
  max-width: 1100px;
  margin: 30px auto;
  padding: 0 16px 40px;
}
.page-header {
  text-align: center;
  margin-bottom: 24px;
}
.card {
  margin-bottom: 24px;
}
.card-header {
  font-weight: 600;
}
.tips {
  margin-top: 12px;
  color: #909399;
}
.mb-16 {
  margin-bottom: 16px;
}
</style>
