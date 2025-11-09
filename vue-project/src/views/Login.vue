<template>
  <div class="login-wrapper">
    <!-- 顶部标题区域 -->
    <div class="header-section">
      <div class="header-content">
        <h1>上海药品监管信息平台</h1>
      </div>
    </div>

    <!-- 登录卡片区域 -->
    <div class="login-main">
      <div class="login-card">
        <h2 class="login-title">登录账户</h2>

        <!-- 登录表单 -->
        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名或手机号"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <!-- 选项 -->
          <div class="login-options">
            <el-checkbox v-model="rememberMe">记住登录状态</el-checkbox>
            <el-checkbox v-model="twoFactorAuth">启用两步验证</el-checkbox>
          </div>

          <!-- 登录按钮 -->
          <el-button 
            type="primary" 
            size="large" 
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录系统
          </el-button>
        </el-form>

        <!-- 注册和游客模式 -->
        <div class="login-footer">
          <div class="register-link">
            <span>没有账户？</span>
            <el-link type="primary" @click="goToRegister">立即注册</el-link>
          </div>
          <el-link type="info" class="guest-mode" @click="goToGuestMode">游客模式浏览</el-link>
        </div>
      </div>
    </div>

    <!-- 底部页脚区域 -->
    <div class="footer-section">
      <div class="footer-content">
        <p>© 2025 上海市药品监管管理局 版权所有 | 沪ICP备00000000X</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { login as mockLogin, roleToRoute } from '../mocks/auth'

const router = useRouter()

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名或手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 选项
const rememberMe = ref(false)
const twoFactorAuth = ref(false)
const loading = ref(false)
const loginFormRef = ref()

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (valid) {
      loading.value = true
      // 使用前端mock进行登录校验
      const user = mockLogin(loginForm.username, loginForm.password)
      if (!user) {
        ElMessage.error('用户名或密码错误（试试 regulator_staff / logistics_mgr / supplier_user / pharmacy_admin / unauth_user，密码均为 123456）')
      } else {
        ElMessage.success(`登录成功，欢迎 ${user.displayName}`)
        const redirect = roleToRoute(user.role)
        // 若从受限页跳来，优先回跳
        const fromRedirect = router.currentRoute.value.query.redirect
        router.push(typeof fromRedirect === 'string' ? fromRedirect : redirect)
      }
    }
  } catch (error) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

// 跳转到注册页面
const goToRegister = () => {
  router.push('/register')
}

// 跳转到游客模式
const goToGuestMode = () => {
  router.push('/')
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部标题区域 - 深蓝色背景 */
.header-section {
  background-color: #ffffff; /* 颜色位置1：顶部标题区域背景色 */
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

/* 登录主体区域 - 渐变背景 */
.login-main {
  flex: 1;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); /* 颜色位置2：中间区域渐变背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-title {
  text-align: center;
  color: #2c3e50; /* 颜色位置3：登录标题文字颜色 */
  margin-bottom: 30px;
  font-size: 20px;
  font-weight: 600;
}

.login-form {
  margin-top: 20px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 25px;
}

.login-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  background-color: #409eff; /* 颜色位置16：登录按钮背景色 */
  border-color: #409eff; /* 颜色位置17：登录按钮边框色 */
}

.login-btn:hover {
  background-color: #66b1ff; /* 颜色位置18：登录按钮悬停背景色 */
  border-color: #66b1ff; /* 颜色位置19：登录按钮悬停边框色 */
}

.login-footer {
  margin-top: 25px;
  text-align: center;
}

.register-link {
  margin-bottom: 15px;
}

.register-link span {
  color: #666; /* 颜色位置20：注册链接前文字颜色 */
  margin-right: 8px;
}

.guest-mode {
  font-size: 14px;
}

/* 底部页脚区域 - 深蓝色背景 */
.footer-section {
  background-color: #ffffff; /* 颜色位置21：底部页脚区域背景色 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    padding: 30px 20px;
  }
  
  .login-options {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .header-content h1 {
    font-size: 22px;
  }
}
</style>
