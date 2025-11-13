<template>
  <div class="register-wrapper">
    <!-- 顶部标题区域 -->
    <div class="header-section">
      <div class="header-content">
        <h1>上海药品监管信息平台</h1>
      </div>
    </div>

    <!-- 注册主体区域 -->
    <div class="register-main">
      <div class="register-card">
        <h2 class="register-title">注册账户</h2>
        
        <!-- 注册表单 -->
        <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" class="register-form">
          <!-- 用户名 -->
          <el-form-item prop="username" class="form-item">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>

          <!-- 邮箱 -->
          <el-form-item prop="email" class="form-item">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱"
              size="large"
              prefix-icon="Message"
            />
          </el-form-item>

          <!-- 角色选择 -->
          <el-form-item prop="role" class="form-item">
            <el-select v-model="registerForm.role" placeholder="请选择角色" size="large" style="width: 100%">
              <el-option label="药店用户" value="pharmacy" />
              <el-option label="供应商用户" value="supplier" />
              <el-option label="物流用户" value="logistics" />
              <el-option label="监管人员" value="regulator" />
              <el-option label="未认证用户" value="unauth" />
            </el-select>
          </el-form-item>
          
          <!-- 密码 -->
          <el-form-item prop="password" class="form-item">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <!-- 确认密码 -->
          <el-form-item prop="confirmPassword" class="form-item">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <!-- 去除验证码：不再需要 -->

          <!-- 协议同意 -->
          <div class="agreement-section">
            <el-checkbox v-model="agreementChecked">
              我已阅读并同意
              <el-link type="primary" @click="showAgreement = true">《用户注册协议》</el-link>
              和
              <el-link type="primary" @click="showPrivacy = true">《隐私政策》</el-link>
            </el-checkbox>
          </div>

          <!-- 注册按钮 -->
          <el-button 
            type="primary" 
            size="large" 
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            立即注册
          </el-button>
        </el-form>

        <!-- 已有账户 -->
        <div class="register-footer">
          <div class="login-link">
            <span>已有账户？</span>
            <el-link type="primary" @click="goToLogin">立即登录</el-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部页脚区域 -->
    <div class="footer-section">
      <div class="footer-content">
        <p>© 2025 上海市药品监管管理局 版权所有 | 沪ICP备00000000X</p>
      </div>
    </div>

    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="showAgreement"
      title="用户注册协议"
      width="70%"
      center
    >
      <div class="agreement-content">
        <p>这里是用户注册协议的具体内容...</p>
        <!-- 这里可以添加详细的协议内容 -->
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="showAgreement = false">我已阅读</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 隐私政策对话框 -->
    <el-dialog
      v-model="showPrivacy"
      title="隐私政策"
      width="70%"
      center
    >
      <div class="privacy-content">
        <p>这里是隐私政策的具体内容...</p>
        <!-- 这里可以添加详细的隐私政策内容 -->
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="showPrivacy = false">我已阅读</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  role: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 16, message: '用户名长度为2-16个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur','change'] }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 选项
const agreementChecked = ref(false)
const loading = ref(false)
const registerFormRef = ref()
const showAgreement = ref(false)
const showPrivacy = ref(false)
// 去除发送验证码逻辑

// 注册处理
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  if (!agreementChecked.value) {
    ElMessage.warning('请阅读并同意用户协议和隐私政策')
    return
  }
  
  try {
    const valid = await registerFormRef.value.validate()
    if (valid) {
      loading.value = true
      // 调用真实注册 API
      try {
        const { register } = await import('@/api/auth.js')
        await register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          role: registerForm.role
        })
        ElMessage.success('注册成功')
        router.push('/login')
      } catch (e) {
        ElMessage.error(e.message || '注册失败')
      }
    }
  } catch (error) {
    ElMessage.error('注册失败，请检查输入信息')
  } finally {
    loading.value = false
  }
}

// 跳转到登录页面
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部标题区域 - 深蓝色背景 */
.header-section {
  background-color: #ffffff;
  color: rgb(0, 0, 0);
  padding: 20px 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  padding: 0 20px;
}

.header-content h1 {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
}

/* 注册主体区域 - 渐变背景 */
.register-main {
  flex: 1;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.register-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.register-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 20px;
  font-weight: 600;
}

/* 注册表单样式 */
.register-form {
  margin-top: 20px;
}

.form-item {
  margin-bottom: 20px;
}

/* 验证码容器 */
.captcha-container {
  display: flex;
  gap: 10px;
}

.captcha-btn {
  flex-shrink: 0;
  width: 140px;
}

/* 协议同意区域 */
.agreement-section {
  margin: 20px 0;
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  background-color: #409eff;
  border-color: #409eff;
  margin-top: 10px;
}

.register-btn:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.register-footer {
  margin-top: 25px;
  text-align: center;
}

.login-link span {
  color: #666;
  margin-right: 8px;
}

/* 底部页脚区域 - 深蓝色背景 */
.footer-section {
  background-color: #ffffff;
  color: rgb(0, 0, 0);
  padding: 15px 0;
  text-align: center;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content p {
  margin: 0;
  font-size: 14px;
}

/* 协议内容样式 */
.agreement-content,
.privacy-content {
  max-height: 400px;
  overflow-y: auto;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-card {
    padding: 30px 20px;
  }
  
  .captcha-container {
    flex-direction: column;
  }
  
  .captcha-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .header-content h1 {
    font-size: 22px;
  }
}
</style>
