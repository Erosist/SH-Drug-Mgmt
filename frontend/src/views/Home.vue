<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="header-content">
        <div class="platform-info">
          <h1 class="platform-title">上海药品监管信息平台</h1>
          <div class="current-date">{{ currentDate }}</div>
        </div>
        
        <div class="nav-section">
          <div class="nav-menu">
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'home' }"
              @click="navigateTo('home')"
            >首页</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'inventory' }"
              @click="navigateTo('inventory')"
            >库存管理</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'b2b' }"
              @click="navigateTo('b2b')"
            >B2B供求平台</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'circulation' }"
              @click="navigateTo('circulation')"
            >流通监管</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'analysis' }"
              @click="navigateTo('analysis')"
            >监管分析</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'service' }"
              @click="navigateTo('service')"
            >智能调度</div>
          </div>
          
          <div class="user-actions">
            <button v-if="!currentUser || currentUser.role==='unauth'" class="auth-btn" @click="goToEnterpriseAuth">企业认证</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="review-btn" @click="goToEnterpriseReview">认证审核</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToSystemStatus">系统状态</button>
            <button v-if="currentUser && currentUser.role==='admin'" class="admin-btn" @click="goToAdminUsers">用户管理</button>
            <button v-if="!currentUser" class="login-btn" @click="goToLogin">登录</button>
            <button v-else class="login-btn" @click="goToUserHome">我的主页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 左侧主要内容 -->
        <div class="left-content">
          <!-- 核心功能服务 - 一行三列 -->
          <div class="section core-functions">
            <h2 class="section-title">核心功能服务</h2>
            <div class="function-cards three-columns">
              <!-- 药品信息查询 -->
              <div class="function-card">
                <h3>药品信息查询</h3>
                <p>快速查询超过10000种药品信息，包含药品成分、使用说明及注意事项</p>
                <button class="action-btn">立即查询</button>
              </div>
              
              <!-- 附近药房定位 -->
              <div class="function-card">
                <h3>附近药房定位</h3>
                <p>基于地理位置查找附近药房，实时获取查询时间与库存信息</p>
                <div class="map-container">
                  <div class="map-placeholder">地图定位区域</div>
                </div>
                <div class="pharmacy-info">上海第一医药商城</div>
              </div>
              
              <!-- 健康资讯中心 -->
              <div class="function-card health-news-card">
                <h3>健康资讯中心</h3>
                <p>获取最新健康资讯、疾病预防知识和健康生活方式建议</p>
                <div class="health-news-list">
                  <div class="news-item">
                    <span class="news-title">疫情防控指南更新</span>
                    <span class="news-date">01-01</span>
                  </div>
                  <div class="news-item">
                    <span class="news-title">冬季流感预防措施</span>
                    <span class="news-date">12-28</span>
                  </div>
                  <div class="news-item">
                    <span class="news-title">健康饮食推荐</span>
                    <span class="news-date">12-25</span>
                  </div>
                </div>
                <button class="action-btn">更多资讯</button>
              </div>
            </div>
          </div>
          
          <!-- 重要提醒与公告 -->
          <div class="section notices">
            <h2 class="section-title">重要提醒与公告</h2>
            <div class="notice-content">
              <div class="urgent-notice">
                <div class="notice-title">紧急通知：某批次清关药品召回通知</div>
                <div class="notice-desc">即产品到期后，国家药品监督管理局2025年6月报2004年1月发布。</div>
              </div>
              
              <div class="report-input">
                <input type="text" placeholder="本市2024年度报告请输入" class="report-field">
                <button class="submit-btn">提交</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧特色服务 -->
        <div class="right-content">
          <div class="section feature-services">
            <h2 class="section-title">特色服务</h2>
            <div class="feature-list">
              <div class="feature-item">
                <div class="feature-icon">⏰</div>
                <div class="feature-content">
                  <h3>个性化用药提醒</h3>
                  <p>定制您的用药计划，维护健康生活，确保您享受健康</p>
                  <button class="feature-btn">创建提醒</button>
                </div>
              </div>
              
              <div class="feature-item">
                <div class="feature-icon">💰</div>
                <div class="feature-content">
                  <h3>药品价格对比</h3>
                  <p>一批批次药品在附近药房的价格差异，选择最低限购买方案</p>
                  <button class="feature-btn">比价查询</button>
                </div>
              </div>
              
              <div class="feature-item">
                <div class="feature-icon">💬</div>
                <div class="feature-content">
                  <h3>药物在线咨询</h3>
                  <p>专业的药7x24小时在线，随时解答关于用药安全的疑问</p>
                  <button class="feature-btn">咨询指南</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { getCurrentUser } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const activeNav = ref('home')
    const currentUser = ref(getCurrentUser())

    // 动态日期
    const currentDate = computed(() => {
      const now = new Date()
      const y = now.getFullYear()
      const m = now.getMonth() + 1
      const d = now.getDate()
      return `${y}年${m}月${d}日`
    })
    
    const goToLogin = () => {
      router.push('/login')
    }

    const goToEnterpriseAuth = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/enterprise-auth' } })
        return
      }
      if (['regulator','admin'].includes(currentUser.value.role)) return
      router.push('/enterprise-auth')
    }

    const goToEnterpriseReview = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push('/enterprise-review')
    }

    const goToSystemStatus = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push('/admin/status')
    }

    const goToAdminUsers = () => {
      if (!currentUser.value) return router.push('/login')
      if (currentUser.value.role !== 'admin') return
      router.push('/admin/users')
    }

    const refreshUser = () => {
      currentUser.value = getCurrentUser()
    }

    const goToUserHome = () => {
      const u = currentUser.value
      if (!u) return router.push('/login')
      router.push(roleToRoute(u.role))
    }
    
    const navigateTo = (page) => {
      activeNav.value = page
      
      // 根据页面名称跳转到对应路由
      switch(page) {
        case 'home':
          router.push('/')
          break
        case 'inventory':
          router.push('/inventory')
          break
        case 'b2b':
          router.push('/b2b')
          break
        case 'circulation':
          router.push('/circulation')
          break
        case 'analysis':
          router.push('/analysis')
          break
        case 'service':
          router.push('/service')
          break
        default:
          router.push('/')
      }
    }
    onMounted(() => {
      window.addEventListener('storage', refreshUser)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('storage', refreshUser)
    })

    return {
      goToLogin,
      goToUserHome,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      navigateTo,
      activeNav,
      currentUser,
      currentDate
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 */
.header {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  width: 100%;
}

.header-content {
  width: 100%;
  max-width: 100%;
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

.nav-item:hover {
  color: #1a73e8;
}

.nav-item.active {
  color: #1a73e8;
  border-bottom: 2px solid #1a73e8;
}

.user-actions {
  display: flex;
  align-items: center;
}

.auth-btn {
  background-color: #fff;
  color: #1a73e8;
  border: 1px solid #1a73e8;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.auth-btn:hover {
  background-color: rgba(26, 115, 232, 0.08);
}

.review-btn {
  background-color: #fff7e6;
  color: #b76c00;
  border: 1px solid #f3e5b8;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.review-btn:hover {
  background-color: #ffeccc;
}

.admin-btn {
  background-color: #f0f5ff;
  color: #1a73e8;
  border: 1px solid #d6e4ff;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.admin-btn:hover {
  background-color: #e5edff;
}

.login-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #0d62d9;
}

/* 主内容区域样式 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  height: 100%;
}

.section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

/* 核心功能服务样式 - 三列布局 */
.function-cards.three-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.function-card {
  display: flex;
  flex-direction: column;
  height: 320px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.function-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.function-card h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.function-card p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 15px;
  flex-grow: 1;
}

.action-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  align-self: flex-start;
  transition: background-color 0.3s;
  margin-top: auto;
}

.action-btn:hover {
  background-color: #0d62d9;
}

.map-container {
  height: 120px;
  background-color: #f0f2f5;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px 0;
}

.map-placeholder {
  color: #999;
}

.pharmacy-info {
  font-weight: bold;
  text-align: center;
  color: #333;
  margin-top: 10px;
}

/* 健康资讯中心样式 */
.health-news-card {
  background-color: #f8fafc;
}

.health-news-list {
  margin: 15px 0;
}

.news-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.news-item:last-child {
  border-bottom: none;
}

.news-title {
  color: #333;
  font-size: 14px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.news-date {
  color: #999;
  font-size: 12px;
  margin-left: 10px;
}

/* 重要提醒与公告样式 */
.urgent-notice {
  margin-bottom: 20px;
}

.notice-title {
  font-weight: bold;
  color: #e74c3c;
  margin-bottom: 8px;
}

.notice-desc {
  color: #666;
  line-height: 1.5;
}

.report-input {
  display: flex;
  margin-top: 15px;
}

.report-field {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  outline: none;
}

.report-field:focus {
  border-color: #1a73e8;
}

.submit-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #0d62d9;
}

/* 特色服务样式 */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  gap: 15px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.feature-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.feature-icon {
  width: 40px;
  height: 40px;
  background-color: #f0f9ff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  color: #1a73e8;
  flex-shrink: 0;
}

.feature-content {
  flex-grow: 1;
}

.feature-content h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: #333;
}

.feature-content p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 10px;
  font-size: 14px;
}

.feature-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.feature-btn:hover {
  background-color: #0d62d9;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .function-cards.three-columns {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 992px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .function-cards.three-columns {
    grid-template-columns: 1fr;
  }
  
  .nav-menu {
    gap: 15px;
  }
}

@media (max-width: 768px) {
  .platform-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .nav-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .nav-menu {
    flex-wrap: wrap;
  }
  
  .main-content {
    padding: 10px;
  }
}
</style>
