<template>
  <div class="change-password-page">
    <div class="page-header">
      <h1>修改登录密码</h1>
      <p>出于安全考虑，修改密码前需要验证当前密码，新密码需满足至少8位且包含大小写字母和数字。</p>
    </div>
    <el-card class="change-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input v-model="form.oldPassword" type="password" placeholder="请输入当前密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="form.newPassword" type="password" placeholder="至少8位且含大小写字母和数字" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
        <div class="actions">
          <el-button type="primary" :loading="loading" @click="handleSubmit">更新密码</el-button>
          <el-button text type="info" @click="goForgot">忘记密码？</el-button>
        </div>
      </el-form>
      <p class="hint">密码修改成功后会自动退出当前会话，需要使用新密码重新登录。</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { changePassword } from '@/api/auth'
import { clearAuth } from '@/utils/authSession'

const router = useRouter()
const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const loading = ref(false)
const formRef = ref(null)

const passwordStrengthRule = (rule, value, callback) => {
  const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/
  if (!pattern.test(value || '')) {
    callback(new Error('至少8位，包含大小写字母和数字'))
  } else {
    callback()
  }
}

const confirmRule = (rule, value, callback) => {
  if (value !== form.newPassword) {
    callback(new Error('两次输入不一致'))
  } else {
    callback()
  }
}

const rules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: passwordStrengthRule, trigger: ['blur', 'change'] }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: confirmRule, trigger: ['blur', 'change'] }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    loading.value = true
    await changePassword({ oldPassword: form.oldPassword, newPassword: form.newPassword })
    ElMessage.success('密码修改成功，请重新登录')
    clearAuth()
    router.push({ name: 'login' })
  } catch (error) {
    ElMessage.error(error.message || '修改密码失败')
  } finally {
    loading.value = false
  }
}

const goForgot = () => {
  router.push({ name: 'forgot-password' })
}
</script>

<style scoped>
.change-password-page {
  max-width: 520px;
  margin: 40px auto;
  padding: 0 16px 40px;
}
.page-header {
  text-align: center;
  margin-bottom: 24px;
}
.change-card {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}
.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.actions .el-button.is-text {
  padding: 0 10px;
}
.hint {
  margin-top: 16px;
  color: #909399;
}
</style>
