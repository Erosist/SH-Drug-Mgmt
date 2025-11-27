<template>
  <div class="unauth-page">
    <div class="header">
      <div class="header-content">
        <div class="platform-info">
          <h1 class="platform-title">上海药品监管信息平台</h1>
          <div class="current-date">{{ currentDate }}</div>
        </div>

        <div class="nav-section">
          <div class="nav-menu">
            <div class="nav-item" :class="{ active: activeNav === 'home' }" @click="navigateTo('home')">首页</div>
            <div class="nav-item" :class="{ active: activeNav === 'inventory' }" @click="navigateTo('inventory')">库存管理</div>
            <div class="nav-item" :class="{ active: activeNav === 'b2b' }" @click="navigateTo('b2b')">B2B供求平台</div>
            <div class="nav-item" :class="{ active: activeNav === 'circulation' }" @click="navigateTo('circulation')">流通监管</div>
            <div class="nav-item" :class="{ active: activeNav === 'analysis' }" @click="navigateTo('analysis')">监管分析</div>
            <div class="nav-item" :class="{ active: activeNav === 'service' }" @click="navigateTo('service')">智能调度</div>
          </div>

          <div class="user-actions">
            <div v-if="currentUser" class="user-info">
              <span class="user-name">{{ userDisplayName }}</span>
              <span class="user-role">{{ userRoleLabel }}</span>
            </div>
            <button v-if="!currentUser || currentUser.role === 'unauth'" class="auth-btn" @click="goToEnterpriseAuth">企业认证</button>
            <button v-if="currentUser && currentUser.role === 'admin'" class="review-btn" @click="goToEnterpriseReview">认证审核</button>
            <button v-if="currentUser && currentUser.role === 'admin'" class="admin-btn" @click="goToSystemStatus">系统状态</button>
            <button v-if="currentUser && currentUser.role === 'admin'" class="admin-btn" @click="goToAdminUsers">用户管理</button>
            <button v-if="!currentUser" class="login-btn" @click="goToLogin">登录</button>
            <button v-else class="logout-btn" @click="handleLogout">退出登录</button>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div class="notice-card">
        <div class="warn-icon">!</div>
        <h2 class="title">当前账号尚未完成企业认证</h2>
        <p class="subtitle">完成认证后即可使用库存、订单、监管等全部功能，请先提交企业资质。</p>
        <el-button type="primary" size="large" class="primary-btn" @click="goToEnterpriseAuth">立即前往认证</el-button>
        <p class="support">如需帮助，请联系平台管理员或拨打 400-000-0000。</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { getCurrentUser, clearAuth } from '@/utils/authSession'
import { getRoleLabel } from '@/utils/roleLabel'

export default {
  name: 'UnauthenticatedUser',
  setup() {
    const router = useRouter()
    const activeNav = ref('home')
    const currentUser = ref(getCurrentUser())

    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })

    const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
    const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))

    const goToLogin = () => router.push({ name: 'login' })

    const handleLogout = () => {
      clearAuth()
      currentUser.value = null
      router.push({ name: 'login' })
    }

    const goToEnterpriseAuth = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/enterprise-auth' } })
        return
      }
      router.push({ name: 'enterprise-auth' })
    }

    const goToEnterpriseReview = () => {
      if (!currentUser.value) return router.push({ name: 'login' })
      if (currentUser.value.role !== 'admin') return
      router.push({ name: 'enterprise-review' })
    }

    const goToSystemStatus = () => {
      if (!currentUser.value) return router.push({ name: 'login' })
      if (currentUser.value.role !== 'admin') return
      router.push({ name: 'admin-status' })
    }

    const goToAdminUsers = () => {
      if (!currentUser.value) return router.push({ name: 'login' })
      if (currentUser.value.role !== 'admin') return
      router.push({ name: 'admin-users' })
    }

    const navigateTo = (page) => {
      activeNav.value = page
      switch (page) {
        case 'home':
          router.push('/'); break
        case 'inventory':
          router.push('/inventory'); break
        case 'b2b':
          router.push('/b2b'); break
        case 'circulation':
          router.push('/circulation'); break
        case 'analysis':
          router.push('/analysis'); break
        case 'service':
          router.push('/service'); break
        default:
          router.push('/')
      }
    }

    const refreshUser = () => {
      currentUser.value = getCurrentUser()
    }

    onMounted(() => {
      window.addEventListener('storage', refreshUser)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
    })

    return {
      currentDate,
      activeNav,
      currentUser,
      userDisplayName,
      userRoleLabel,
      navigateTo,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      goToLogin,
      handleLogout
    }
  }
}
</script>

<style scoped>
.unauth-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
}

.header-content {
  width: 100%;
  margin: 0 auto;
  padding: 0 20px;
}

.platform-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.platform-title {
  font-size: 24px;
  font-weight: bold;
  color: #1a73e8;
  margin: 0;
}

.current-date {
  color: #666;
  font-size: 16px;
}

.nav-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-item {
  font-size: 16px;
  color: #333;
  cursor: pointer;
  padding: 5px 0;
  transition: color 0.3s;
}

.nav-item.active {
  color: #1a73e8;
  border-bottom: 2px solid #1a73e8;
}

.nav-item:hover {
  color: #1a73e8;
}

.user-actions {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 999px;
  background-color: #f0f5ff;
  color: #1a73e8;
  font-size: 14px;
  font-weight: 600;
  margin-right: 10px;
  gap: 8px;
}

.user-name {
  white-space: nowrap;
}

.user-role {
  padding: 2px 10px;
  border-radius: 999px;
  background-color: #fff;
  border: 1px solid rgba(26, 115, 232, 0.2);
  font-size: 12px;
  color: #1a73e8;
}

.auth-btn,
.login-btn,
.logout-btn,
.admin-btn,
.review-btn {
  border-radius: 4px;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
}

.auth-btn {
  background-color: #fff;
  color: #1a73e8;
  border: 1px solid #1a73e8;
}

.auth-btn:hover {
  background-color: rgba(26, 115, 232, 0.08);
}

.review-btn {
  background-color: #fff7e6;
  color: #b76c00;
  border: 1px solid #f3e5b8;
}

.review-btn:hover {
  background-color: #ffeccc;
}

.admin-btn {
  background-color: #f0f5ff;
  color: #1a73e8;
  border: 1px solid #d6e4ff;
}

.admin-btn:hover {
  background-color: #e5edff;
}

.login-btn,
.logout-btn {
  background-color: #1a73e8;
  color: #fff;
}

.login-btn:hover,
.logout-btn:hover {
  background-color: #0d62d9;
}

.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px 120px;
}

.notice-card {
  width: 100%;
  max-width: 760px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
  padding: 64px 48px;
  text-align: center;
}

.warn-icon {
  width: 88px;
  height: 88px;
  margin: 0 auto 24px;
  border-radius: 50%;
  background: rgba(251, 140, 0, 0.12);
  color: #fb8c00;
  font-size: 48px;
  font-weight: 700;
  line-height: 88px;
}

.title {
  font-size: 28px;
  color: #1f2937;
  margin-bottom: 12px;
}

.subtitle {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 32px;
}

.primary-btn {
  width: 260px;
  height: 48px;
  font-size: 16px;
  margin-bottom: 16px;
}

.support {
  color: #9ca3af;
  font-size: 14px;
}

@media (max-width: 768px) {
  .nav-menu {
    gap: 16px;
    flex-wrap: wrap;
  }

  .notice-card {
    padding: 48px 24px;
  }

  .primary-btn {
    width: 100%;
  }
}
</style>
