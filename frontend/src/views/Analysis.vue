<template>
  <div class="analysis-container">
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

    <!-- 监管分析主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 左侧窄侧边栏：筛选 -->
        <aside class="sidebar">
          <div class="section filter-section">
            <h3 class="section-title">应用筛选</h3>
            
            <div class="filter-groups">
              <div class="filter-group">
                <label class="filter-label">药品类型</label>
                <div class="checkbox-group">
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.drugTypes" value="prescription">
                    <span class="checkmark"></span>
                    处方药
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.drugTypes" value="nonPrescription">
                    <span class="checkmark"></span>
                    单处方药
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.drugTypes" value="traditional">
                    <span class="checkmark"></span>
                    中药制剂
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.drugTypes" value="biological">
                    <span class="checkmark"></span>
                    生物制品
                  </label>
                </div>
              </div>
              
              <div class="filter-group">
                <label class="filter-label">企业类型</label>
                <div class="checkbox-group">
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.companyTypes" value="producer">
                    <span class="checkmark"></span>
                    生产企业
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.companyTypes" value="user">
                    <span class="checkmark"></span>
                    使用单位
                  </label>
                </div>
              </div>
              
              <div class="filter-group">
                <label class="filter-label">合规状态</label>
                <div class="checkbox-group">
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.complianceStatus" value="compliant">
                    <span class="checkmark"></span>
                    合规
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.complianceStatus" value="limited">
                    <span class="checkmark"></span>
                    限量中
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" v-model="filters.complianceStatus" value="violation">
                    <span class="checkmark"></span>
                    违规
                  </label>
                </div>
              </div>
              
              <div class="filter-group">
                <label class="filter-label">经营企业</label>
                <div class="percentage-bars">
                  <div class="percentage-item">
                    <span class="percentage-label">生产企业</span>
                    <div class="percentage-bar">
                      <div class="percentage-fill" style="width: 36%"></div>
                    </div>
                    <span class="percentage-value">36%</span>
                  </div>
                  <div class="percentage-item">
                    <span class="percentage-label">流通企业</span>
                    <div class="percentage-bar">
                      <div class="percentage-fill" style="width: 9%"></div>
                    </div>
                    <span class="percentage-value">9%</span>
                  </div>
                  <div class="percentage-item">
                    <span class="percentage-label">使用单位</span>
                    <div class="percentage-bar">
                      <div class="percentage-fill" style="width: 5%"></div>
                    </div>
                    <span class="percentage-value">5%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="filter-actions">
              <button class="reset-btn">重置</button>
            </div>
          </div>
        </aside>
        
        <div class="main-area">
          <!-- 数据概览卡片 -->
          <div class="data-overview">
          <div class="data-card">
            <div class="data-header">
              <div class="data-title">合规率</div>
              <div class="data-source">数据来源：易观数据库</div>
            </div>
            <div class="data-value">94.7%</div>
            <div class="data-trend">
              <span class="trend-up">↑ 24%</span>
              <span class="trend-text">线上服务</span>
            </div>
          </div>
          
          <div class="data-card">
            <div class="data-header">
              <div class="data-title">预警数量</div>
              <div class="data-source">数据来源：易观数据库</div>
            </div>
            <div class="data-value">86.3%</div>
            <div class="data-trend">
              <span class="trend-up">↑ 31.8%</span>
              <span class="trend-text">线上服务</span>
            </div>
          </div>
          
          <div class="data-card">
            <div class="data-header">
              <div class="data-title">投放效率</div>
              <div class="data-source">数据来源：易观数据库</div>
            </div>
            <div class="data-value">248</div>
            <div class="data-trend">
              <span class="trend-down">↓ 4%</span>
              <span class="trend-text">与上期服务</span>
            </div>
          </div>
          
          <div class="data-card">
            <div class="data-header">
              <div class="data-title">企业概况</div>
              <div class="data-source">数据来源：易观数据库</div>
            </div>
            <div class="data-value">78.4%</div>
            <div class="data-trend">
              <span class="trend-up">↑ 19.1%</span>
              <span class="trend-text">线上服务</span>
            </div>
            <div class="data-tag">全额归档</div>
          </div>
        </div>

        <div class="analysis-content">
          <div class="left-content">
            <!-- 监管趋势分析 -->
            <div class="section trend-analysis">
              <h3 class="section-title">监管趋势分析</h3>
              
              <div class="trend-chart">
                <div class="chart-placeholder">
                  <div class="chart-lines">
                    <div class="chart-line" style="height: 80%"></div>
                    <div class="chart-line" style="height: 60%"></div>
                    <div class="chart-line" style="height: 40%"></div>
                    <div class="chart-line" style="height: 20%"></div>
                    <div class="chart-line" style="height: 10%"></div>
                  </div>
                  <div class="chart-bars">
                    <div class="chart-bar" style="height: 70%"></div>
                    <div class="chart-bar" style="height: 85%"></div>
                    <div class="chart-bar" style="height: 60%"></div>
                    <div class="chart-bar" style="height: 90%"></div>
                  </div>
                </div>
                <div class="chart-labels">
                  <span>2016 Q1</span>
                  <span>2015 Q2</span>
                  <span>2016 Q3</span>
                  <span>2016 Q4</span>
                </div>
              </div>
              
              <div class="coverage-info">
                <span>非覆盖率</span>
                <span>- 0% - 0% - 0% - 0%</span>
              </div>
            </div>
          </div>
          
          <!-- 右侧图表和表格 -->
          <div class="right-content">
            <!-- 区域热力对比 -->
            <div class="section regional-comparison">
              <h3 class="section-title">区域热力对比</h3>
              
              <div class="comparison-chart">
                <div class="chart-bars-horizontal">
                  <div class="bar-item">
                    <span class="city-name">北京</span>
                    <div class="bar-container">
                      <div class="bar-fill" style="width: 90%"></div>
                    </div>
                    <span class="bar-value">140</span>
                  </div>
                  <div class="bar-item">
                    <span class="city-name">上海</span>
                    <div class="bar-container">
                      <div class="bar-fill" style="width: 80%"></div>
                    </div>
                    <span class="bar-value">120</span>
                  </div>
                  <div class="bar-item">
                    <span class="city-name">广州</span>
                    <div class="bar-container">
                      <div class="bar-fill" style="width: 70%"></div>
                    </div>
                    <span class="bar-value">100</span>
                  </div>
                  <div class="bar-item">
                    <span class="city-name">深圳</span>
                    <div class="bar-container">
                      <div class="bar-fill" style="width: 60%"></div>
                    </div>
                    <span class="bar-value">80</span>
                  </div>
                  <div class="bar-item">
                    <span class="city-name">杭州</span>
                    <div class="bar-container">
                      <div class="bar-fill" style="width: 50%"></div>
                    </div>
                    <span class="bar-value">60</span>
                  </div>
                  <div class="bar-item">
                    <span class="city-name">南京</span>
                    <div class="bar-container">
                      <div class="bar-fill" style="width: 40%"></div>
                    </div>
                    <span class="bar-value">40</span>
                  </div>
                  <div class="bar-item">
                    <span class="city-name">成都</span>
                    <div class="bar-container">
                      <div class="bar-fill" style="width: 20%"></div>
                    </div>
                    <span class="bar-value">20</span>
                  </div>
                </div>
              </div>
              
              <div class="chart-footer">
                <span>区域能力分布</span>
              </div>
            </div>
            
            <!-- 数据表格 -->
            <div class="section data-table">
              <div class="table-header">
                <h3 class="section-title">企业监管数据</h3>
                <div class="data-source">数据来源：易观数据库</div>
              </div>
              
              <div class="table-container">
                <table class="analysis-table">
                  <thead>
                    <tr>
                      <th>企业名称</th>
                      <th>药品类型</th>
                      <th>药品类别</th>
                      <th>销售范围</th>
                      <th>合规状态</th>
                      <th>标签数量</th>
                      <th>二级机构</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in tableData" :key="index">
                      <td>{{ item.companyName }}</td>
                      <td>{{ item.drugType }}</td>
                      <td>{{ item.drugCategory }}</td>
                      <td>{{ item.salesScope }}</td>
                      <td>
                        <span :class="['status', item.complianceStatus]">
                          {{ item.complianceStatus }}
                        </span>
                      </td>
                      <td>{{ item.labelCount }}</td>
                      <td>{{ item.secondaryOrg }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="table-footer">
                <div class="pagination-info">
                  显示 1-{{ tableData.length }} 条，共 258 条
                </div>
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
  name: 'Analysis',
  setup() {
    const router = useRouter()
  const activeNav = ref('analysis')
  const currentUser = ref(getCurrentUser())
    
    // 当前日期
    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })
    
    // 筛选条件
    const filters = ref({
      drugTypes: ['prescription', 'nonPrescription', 'traditional', 'biological'],
      companyTypes: ['producer', 'user'],
      complianceStatus: ['compliant', 'limited', 'violation']
    })
    
    // 表格数据
    const tableData = ref([
      {
        companyName: '北京市朝阳区第一药业公司',
        drugType: '处方药',
        drugCategory: '抗生素',
        salesScope: '全国',
        complianceStatus: '通过',
        labelCount: '15',
        secondaryOrg: '北京市药品监督管理局'
      },
      {
        companyName: '上海市浦东新区第二药业公司',
        drugType: '非处方药',
        drugCategory: '维生素',
        salesScope: '华东地区',
        complianceStatus: '违规',
        labelCount: '8',
        secondaryOrg: '上海市药品监督管理局'
      },
      {
        companyName: '广州市天河区第三药业公司',
        drugType: '中药制剂',
        drugCategory: '感冒药',
        salesScope: '华南地区',
        complianceStatus: '未通过',
        labelCount: '20',
        secondaryOrg: '广东省药品监督管理局'
      },
      {
        companyName: '杭州市西湖区第四药业公司',
        drugType: '生物制品',
        drugCategory: '疫苗',
        salesScope: '华东地区',
        complianceStatus: '通过',
        labelCount: '12',
        secondaryOrg: '浙江省药品监督管理局'
      },
      {
        companyName: '成都市高新区第五药业公司',
        drugType: '处方药',
        drugCategory: '抗癌药',
        salesScope: '西南地区',
        complianceStatus: '违规',
        labelCount: '5',
        secondaryOrg: '四川省药品监督管理局'
      }
    ])
    
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
    
    onMounted(() => { window.addEventListener('storage', refreshUser) })
    onBeforeUnmount(() => { window.removeEventListener('storage', refreshUser) })

    return {
      navigateTo,
      activeNav,
      currentDate,
      filters,
      tableData,
      goToLogin,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      goToUserHome,
      currentUser
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

.analysis-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 - 与Home.vue一致 */
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

.user-info {
  color: #666;
  font-size: 14px;
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
  /* 左侧为窄侧栏用于筛选，右侧为宽主区用于图表与表格 */
  grid-template-columns: 260px 1fr;
  gap: 20px;
  height: 100%;
}

/* 登录按钮样式（与 Home.vue 对齐） */
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

/* 数据概览卡片 */
.data-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.data-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.data-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.data-source {
  font-size: 12px;
  color: #999;
}

.data-value {
  font-size: 32px;
  font-weight: bold;
  color: #1a73e8;
  margin-bottom: 10px;
}

.data-trend {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-up {
  color: #52c41a;
  font-weight: bold;
}

.trend-down {
  color: #f5222d;
  font-weight: bold;
}

.trend-text {
  color: #666;
  font-size: 14px;
}

.data-tag {
  background-color: #f0f7ff;
  color: #1a73e8;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  align-self: flex-start;
  margin-top: 10px;
}

/* 分析内容布局 */
.analysis-content {
  display: grid;
  /* 主区内部：左侧大图 右侧窄栏（对比图 + 表格） */
  grid-template-columns: 1fr 920px;
  gap: 20px;
}

.sidebar {
  /* 让侧栏在滚动时保持可见 */
  align-self: start;
}

.sidebar .filter-section {
  position: sticky;
  top: 20px;
}

.main-area {
  display: flex;
  flex-direction: column;
}

/* 区块样式 */
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

/* 筛选条件样式 */
.filter-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.checkbox-item input {
  margin: 0;
}

/* 百分比条样式 */
.percentage-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.percentage-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.percentage-label {
  font-size: 14px;
  color: #666;
  width: 80px;
}

.percentage-bar {
  flex-grow: 1;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.percentage-fill {
  height: 100%;
  background-color: #1a73e8;
  border-radius: 4px;
}

.percentage-value {
  font-size: 14px;
  color: #333;
  width: 30px;
  text-align: right;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.reset-btn {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #495057;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.reset-btn:hover {
  background-color: #e9ecef;
}

/* 趋势分析图表 */
.trend-chart {
  margin-bottom: 15px;
}

.chart-placeholder {
  height: 200px;
  background-color: #f8f9fa;
  border-radius: 4px;
  position: relative;
  display: flex;
  align-items: flex-end;
  padding: 10px;
}

.chart-lines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding: 0 20px;
}

.chart-line {
  width: 2px;
  background-color: #e8e8e8;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  width: 100%;
  height: 100%;
  padding: 0 20px;
}

.chart-bar {
  width: 30px;
  background-color: #1a73e8;
  border-radius: 2px 2px 0 0;
  margin: 0 10px;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
  font-size: 12px;
  color: #666;
}

.coverage-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

/* 区域对比图表 */
.comparison-chart {
  margin-bottom: 15px;
}

.chart-bars-horizontal {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.city-name {
  font-size: 14px;
  color: #333;
  width: 50px;
}

.bar-container {
  flex-grow: 1;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background-color: #1a73e8;
  border-radius: 10px;
}

.bar-value {
  font-size: 14px;
  color: #333;
  width: 30px;
  text-align: right;
}

.chart-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

/* 数据表格样式 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-container {
  overflow-x: auto;
}

.analysis-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.analysis-table th,
.analysis-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.analysis-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.analysis-table tbody tr:hover {
  background-color: #f5f7fa;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status.通过 {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status.违规 {
  background-color: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.status.未通过 {
  background-color: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .data-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .analysis-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 992px) {
  .content-wrapper {
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
  
  .data-overview {
    grid-template-columns: 1fr;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
