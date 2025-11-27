<template>
  <div class="circulation-container">
    <!-- 顶部导航栏 - 与Home.vue完全一致 -->
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
            <div v-if="currentUser" class="user-info">
              <span class="user-name">{{ userDisplayName }}</span>
              <span class="user-role">{{ userRoleLabel }}</span>
            </div>
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

    <!-- 流通监管主内容区域 - 与Home.vue边界保持一致 -->
    <div class="main-content">
      <div class="content-wrapper">

        <div class="circulation-content">
          <!-- 左侧内容 -->
          <div class="left-content">
            <!-- 流通数据上报 -->
            <div class="section data-reporting">
              <h3 class="section-title">流通数据上报</h3>
              
              <div class="trace-query">
                <button class="query-btn">药品追溯查询</button>
              </div>
              
              <div class="new-report-section">
                <h4 class="subsection-title">新增流通数据上报</h4>
                
                <div class="form-row">
                  <div class="form-group">
                    <label class="form-label">运单号</label>
                    <input type="text" class="form-input" placeholder="请输入运单号">
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label">运输状态</label>
                    <select class="form-select" v-model="transportStatus">
                      <option value="transporting">运输中</option>
                      <option value="pending">待发货</option>
                      <option value="delivered">已送达</option>
                      <option value="cancelled">已取消</option>
                    </select>
                  </div>
                </div>
                
                <div class="form-group">
                  <label class="form-label">商品信息</label>
                  <input type="text" class="form-input" placeholder="可手动输入商品名称和会员数量">
                </div>
                
                <div class="form-group">
                  <label class="form-label">时间戳</label>
                  <div class="timestamp">{{ currentTimestamp }}</div>
                </div>
              </div>
              
              <!-- 权限提示 -->
              <div class="permission-notice">
                <div class="notice-icon">⚠️</div>
                <div class="notice-text">当前客户可提交数据，但无法编辑或修改记录</div>
              </div>
            </div>
          </div>
          
          <!-- 右侧内容 -->
          <div class="right-content">
            <!-- 位置信息 -->
            <div class="section location-info">
              <h3 class="section-title">位置信息</h3>
              
              <div class="location-form">
                <div class="form-row">
                  <div class="form-group">
                    <label class="form-label">省市</label>
                    <select class="form-select" v-model="location.province">
                      <option value="beijing">北京市</option>
                      <option value="shanghai">上海市</option>
                      <option value="guangdong">广东省</option>
                    </select>
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label">区县</label>
                    <select class="form-select" v-model="location.district">
                      <option value="chaoyang">朝阳区</option>
                      <option value="haidian">海淀区</option>
                      <option value="dongcheng">东城区</option>
                    </select>
                  </div>
                </div>
                
                <div class="form-group">
                  <label class="form-label">详细地址</label>
                  <input type="text" class="form-input" placeholder="华图地址" v-model="location.address">
                </div>
                
                <div class="coordinates">
                  <div class="coordinate-group">
                    <label class="form-label">经度</label>
                    <input type="text" class="form-input coordinate" v-model="location.longitude" placeholder="116.4074">
                  </div>
                  <div class="coordinate-group">
                    <label class="form-label">纬度</label>
                    <input type="text" class="form-input coordinate" v-model="location.latitude" placeholder="39.9042">
                  </div>
                </div>
                
                <div class="gps-action">
                  <button class="gps-btn" @click="useCurrentLocation">
                    📍 使用GPS定位当前值
                  </button>
                </div>
                
                <div class="form-group">
                  <label class="form-label">备注信息</label>
                  <textarea class="form-textarea" placeholder="请输入店铺备注信息" v-model="location.remarks"></textarea>
                </div>
              </div>
            </div>
            
            <!-- 上传及推送 -->
            <div class="section upload-push">
              <h3 class="section-title">上传及推送</h3>
              
              <div class="upload-info">
                <div class="file-format">文件格式：jsp/product</div>
                <div class="file-size">最大文件大小：10MB</div>
              </div>
              
              <div class="upload-actions">
                <button class="upload-btn">选择文件</button>
                <button class="push-btn">推送至监管平台</button>
              </div>
            </div>
            
            <!-- 审核反馈 -->
            <div class="section audit-feedback">
              <h3 class="section-title">审核反馈</h3>
              
              <div class="feedback-content">
                <textarea class="feedback-textarea" placeholder="操作员反馈" v-model="auditFeedback"></textarea>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部操作按钮 -->
        <div class="action-buttons">
          <button class="reset-btn">重置</button>
          <button class="submit-btn" @click="submitProcess">提交流程</button>
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
import { getRoleLabel } from '@/utils/roleLabel'

export default {
  name: 'Circulation',
  setup() {
    const router = useRouter()
  const activeNav = ref('circulation')
  const currentUser = ref(getCurrentUser())
  const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
  const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))
    
    // 当前日期和时间
    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })
    
    const pageDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })
    
    const currentTimestamp = ref('')
    
    // 运输状态
    const transportStatus = ref('transporting')
    
    // 位置信息
    const location = ref({
      province: 'beijing',
      district: 'chaoyang',
      address: '',
      longitude: '116.4074',
      latitude: '39.9042',
      remarks: ''
    })
    
    // 审核反馈
    const auditFeedback = ref('')
    
    // 更新当前时间戳
    const updateTimestamp = () => {
      const now = new Date()
      currentTimestamp.value = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    // 使用GPS定位
    const useCurrentLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            location.value.longitude = position.coords.longitude.toFixed(6)
            location.value.latitude = position.coords.latitude.toFixed(6)
          },
          (error) => {
            console.error('获取位置失败:', error)
            alert('获取GPS位置失败，请确保已开启位置权限')
          }
        )
      } else {
        alert('您的浏览器不支持GPS定位')
      }
    }
    
    // 提交流程
    const submitProcess = () => {
      // 这里可以添加表单验证
      console.log('提交流通数据:', {
        transportStatus: transportStatus.value,
        location: location.value,
        auditFeedback: auditFeedback.value
      })
      
      // 模拟提交成功
      alert('流通数据提交成功！')
    }
    
    const goToLogin = () => { router.push('/login') }

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

    const refreshUser = () => { currentUser.value = getCurrentUser() }

    const goToUserHome = () => {
      const u = currentUser.value
      if (!u) return router.push('/login')
      router.push(roleToRoute(u.role))
    }
    
    const navigateTo = (page) => {
      activeNav.value = page
      
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
    
    // 初始化时间戳
    onMounted(() => {
      updateTimestamp()
      window.addEventListener('storage', refreshUser)
      // 每秒更新一次时间戳
      setInterval(updateTimestamp, 1000)
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
      currentDate,
      pageDate,
      currentTimestamp,
      transportStatus,
      location,
      auditFeedback,
      useCurrentLocation,
      submitProcess,
      currentUser,
      userDisplayName,
      userRoleLabel
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

.circulation-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 - 与Home.vue完全一致 */
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
  flex-wrap: wrap;
  gap: 15px;
}

.nav-menu {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
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
  flex-wrap: wrap;
  gap: 10px;
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


.auth-btn {
  background-color: #fff;
  color: #1a73e8;
  border: 1px solid #1a73e8;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
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

/* 主内容区域样式 - 与Home.vue边界保持一致 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  height: 100%;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.page-date {
  color: #666;
  font-size: 16px;
}

/* 流通内容布局 - 与Home.vue网格布局一致 */
.circulation-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

/* 区块样式 - 与Home.vue完全一致 */
.section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 0;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.subsection-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

/* 表单样式 */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
  font-size: 14px;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: #1a73e8;
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
}

/* 时间戳样式 */
.timestamp {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
}

/* 药品追溯查询按钮 */
.trace-query {
  margin-bottom: 20px;
}

.query-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.query-btn:hover {
  background-color: #0d62d9;
}

/* 权限提示 */
.permission-notice {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 15px;
  background-color: #fff8e1;
  border: 1px solid #ffd54f;
  border-radius: 4px;
  margin-top: 20px;
}

.notice-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.notice-text {
  color: #e65100;
  font-size: 14px;
  line-height: 1.4;
}

/* 坐标输入 */
.coordinates {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.coordinate-group {
  display: flex;
  flex-direction: column;
}

.coordinate {
  text-align: center;
}

/* GPS按钮 */
.gps-action {
  margin-bottom: 15px;
}

.gps-btn {
  width: 100%;
  padding: 10px;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 4px;
  color: #0369a1;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.gps-btn:hover {
  background-color: #e0f2fe;
  border-color: #7dd3fc;
}

/* 上传及推送 */
.upload-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.upload-actions {
  display: flex;
  gap: 10px;
}

.upload-btn, .push-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.upload-btn {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #495057;
}

.upload-btn:hover {
  background-color: #e9ecef;
}

.push-btn {
  background-color: #1a73e8;
  color: white;
}

.push-btn:hover {
  background-color: #0d62d9;
}

/* 审核反馈 */
.feedback-textarea {
  min-height: 120px;
}

/* 底部操作按钮 - 与Home.vue按钮样式一致 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 0;
}

.reset-btn, .submit-btn {
  padding: 10px 25px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.reset-btn {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #495057;
}

.reset-btn:hover {
  background-color: #e9ecef;
}

.submit-btn {
  background-color: #1a73e8;
  color: white;
}

.submit-btn:hover {
  background-color: #0d62d9;
}

/* 响应式设计 - 与Home.vue保持一致 */
@media (max-width: 1200px) {
  .circulation-content {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 992px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .circulation-content {
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
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .coordinates {
    grid-template-columns: 1fr;
  }
  
  .upload-actions {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
