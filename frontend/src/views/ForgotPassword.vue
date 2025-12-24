<template>
  <div class="forgot-page">
    <div class="page-header">
      <h1>找回登录密码</h1>
      <p>通过账号和绑定的邮箱或手机号验证后，即可重置密码。</p>
    </div>

    <el-card class="card">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="账号" prop="identifier">
          <el-input v-model="form.identifier" placeholder="请输入用户名/邮箱/手机号" />
        </el-form-item>
        <el-form-item label="验证方式" prop="channel">
          <el-radio-group v-model="form.channel">
            <el-radio-button label="email">邮箱</el-radio-button>
            <el-radio-button label="phone">手机号</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="form.channel === 'email' ? '邮箱' : '手机号'" prop="contact">
          <el-input v-model="form.contact" :placeholder="form.channel === 'email' ? '请输入注册时的邮箱' : '请输入注册时的手机号'" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="form.newPassword" type="password" placeholder="至少8位且含大小写字母和数字" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
        <div class="actions">
          <el-button type="primary" :loading="loading" @click="handleSubmit">确认重置</el-button>
          <el-button text type="info" @click="goLogin">返回登录</el-button>
        </div>
      </el-form>
      <p class="tips">系统将验证您的账号和联系方式是否匹配，验证通过后即可重置密码。</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { resetPassword } from '@/api/auth'

const router = useRouter()
const form = reactive({
  identifier: '',
  channel: 'email',
  contact: '',
  newPassword: '',
  confirmPassword: ''
})
const formRef = ref(null)
const loading = ref(false)

const emailPattern = /^[\w-.]+@[\w-]+(\.[\w-]+)+$/
const phonePattern = /^\d{6,20}$/

const contactValidator = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入信息'))
    return
  }
  if (form.channel === 'email' && !emailPattern.test(value)) {
    callback(new Error('邮箱格式不正确'))
    return
  }
  if (form.channel === 'phone' && !phonePattern.test(value)) {
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
  if (value !== form.newPassword) {
    callback(new Error('两次输入不一致'))
  } else {
    callback()
  }
}

const rules = {
  identifier: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  channel: [{ required: true, message: '请选择方式', trigger: 'change' }],
  contact: [{ required: true, validator: contactValidator, trigger: ['blur', 'change'] }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: passwordValidator, trigger: ['blur', 'change'] }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: confirmValidator, trigger: ['blur', 'change'] }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    loading.value = true
    await resetPassword({
      identifier: form.identifier,
      channel: form.channel,
      contact: form.contact,
      newPassword: form.newPassword
    })
    ElMessage.success('密码重置成功，请使用新密码登录')
    router.push({ name: 'login' })
  } catch (error) {
    ElMessage.error(error.message || '密码重置失败')
  } finally {
    loading.value = false
  }
}

const goLogin = () => {
  router.push({ name: 'login' })
}
</script>

<style scoped>
.forgot-page {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 16px 40px;
}
.page-header {
  text-align: center;
  margin-bottom: 24px;
}
.card {
  margin-bottom: 24px;
}
.actions {
  display: flex;
  gap: 12px;
}
.tips {
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
}
</style>
