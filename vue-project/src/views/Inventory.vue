<template>
  <div class="inventory-container">
    <!-- 顶部导航栏 - 与Home.vue保持一致 -->
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
            <button class="login-btn" @click="goToLogin">登录</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 库存管理主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 左侧主要内容 -->
        <div class="left-content">
          <!-- 药品定位与就近推荐 -->
          <div class="section drug-location">
            <h2 class="section-title">药品定位与就近推荐</h2>
            
            <!-- 搜索筛选区域 -->
            <div class="search-filters">
              <div class="filter-row">
                <div class="filter-group">
                  <label>药品名称/ID</label>
                  <div class="search-input-group">
                    <input type="text" placeholder="输入药品名称或ID" class="search-field">
                    <button class="search-btn">搜索</button>
                  </div>
                </div>
                
                <div class="filter-group">
                  <label>供应商类型</label>
                  <select class="filter-select">
                    <option>全部</option>
                    <option>医院药房</option>
                    <option>连锁药店</option>
                    <option>个体药店</option>
                  </select>
                </div>
              </div>
              
              <div class="filter-row">
                <div class="filter-group">
                  <label>金额</label>
                  <input type="text" placeholder="输入金额范围" class="filter-field">
                </div>
                
                <div class="filter-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="within5km">
                    <span class="checkmark"></span>
                    5公里内
                  </label>
                </div>
              </div>
            </div>
            
            <!-- 推荐供应商列表 -->
            <div class="recommended-suppliers">
              <h3 class="subsection-title">推荐供应商</h3>
              
              <div class="supplier-list">
                <div 
                  class="supplier-card" 
                  :class="{ active: selectedSupplier === 'renji' }"
                  @click="selectSupplier('renji')"
                >
                  <div class="supplier-name">仁济医院药房</div>
                  <div class="supplier-info">
                    <span class="medical-insurance">医保</span>
                    <span class="distance">1.2公里</span>
                  </div>
                </div>
                
                <div 
                  class="supplier-card" 
                  :class="{ active: selectedSupplier === 'baixin' }"
                  @click="selectSupplier('baixin')"
                >
                  <div class="supplier-name">百信连锁药店</div>
                  <div class="supplier-info">
                    <span class="medical-insurance">医保</span>
                    <span class="distance">3.5公里</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧供应商详情 -->
        <div class="right-content">
          <!-- 供应商详情 -->
          <div class="section supplier-detail">
            <h2 class="section-title">供应商详情</h2>
            
            <div v-if="selectedSupplier === 'renji'" class="supplier-info-panel">
              <div class="supplier-header">
                <h3 class="supplier-title">仁济医院药房</h3>
              </div>
              
              <div class="supplier-metrics">
                <div class="metric-item">
                  <span class="metric-label">有效率</span>
                  <span class="metric-value">4.9</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">配送时间</span>
                  <span class="metric-value">1.2公里</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">库存用量</span>
                  <span class="metric-value">充足</span>
                </div>
              </div>
            </div>
            
            <div v-if="selectedSupplier === 'baixin'" class="supplier-info-panel">
              <div class="supplier-header">
                <h3 class="supplier-title">百信连锁药店</h3>
              </div>
              
              <div class="supplier-metrics">
                <div class="metric-item">
                  <span class="metric-label">有效率</span>
                  <span class="metric-value">4.7</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">配送时间</span>
                  <span class="metric-value">3.5公里</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">库存用量</span>
                  <span class="metric-value">一般</span>
                </div>
              </div>
            </div>
            
            <div v-if="!selectedSupplier" class="no-supplier-selected">
              请选择左侧的供应商查看详情
            </div>
          </div>
          
          <!-- 供应商位置分布 -->
          <div class="section supplier-distribution">
            <h2 class="section-title">供应商位置分布</h2>
            
            <div class="distribution-metrics">
              <div class="distribution-item">
                <span class="distribution-label">有效率</span>
                <span class="distribution-value">0.8</span>
              </div>
              <div class="distribution-item">
                <span class="distribution-label">库存数量</span>
                <span class="distribution-value">1.6</span>
              </div>
              <div class="distribution-item">
                <span class="distribution-label">运输时间</span>
                <span class="distribution-value">1.7</span>
              </div>
            </div>
            
            <!-- 订单信息 -->
            <div class="order-info">
              <div class="order-code">平码至36开间</div>
              <div class="order-time">23分钟</div>
              <div class="order-status">当前订单</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'

export default {
  name: 'Inventory',
  setup() {
    const router = useRouter()
    const activeNav = ref('inventory')
    const selectedSupplier = ref('renji') // 默认选中仁济医院
    const within5km = ref(true)
    
    // 获取当前日期
    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })
    
    const goToLogin = () => {
      router.push('/login')
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
    
    const selectSupplier = (supplier) => {
      selectedSupplier.value = supplier
    }
    
    return {
      goToLogin,
      navigateTo,
      activeNav,
      selectedSupplier,
      selectSupplier,
      within5km,
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

.inventory-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 - 与Home.vue保持一致 */
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

/* 搜索筛选区域样式 */
.search-filters {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.filter-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.search-input-group {
  display: flex;
}

.search-field {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  outline: none;
}

.search-field:focus {
  border-color: #1a73e8;
}

.search-btn {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.filter-select, .filter-field {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

.filter-select:focus, .filter-field:focus {
  border-color: #1a73e8;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-top: 8px;
}

.checkbox-label input {
  margin-right: 8px;
}

/* 推荐供应商样式 */
.subsection-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.supplier-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.supplier-card {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.supplier-card:hover {
  border-color: #1a73e8;
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.1);
}

.supplier-card.active {
  border-color: #1a73e8;
  background-color: #f0f7ff;
}

.supplier-name {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.supplier-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.medical-insurance {
  color: #27ae60;
  font-weight: bold;
}

.distance {
  color: #666;
}

/* 供应商详情样式 */
.supplier-info-panel {
  padding: 10px 0;
}

.supplier-header {
  margin-bottom: 20px;
}

.supplier-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.supplier-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-label {
  color: #666;
  font-size: 14px;
}

.metric-value {
  font-weight: bold;
  color: #333;
}

.no-supplier-selected {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-style: italic;
}

/* 供应商位置分布样式 */
.distribution-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.distribution-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.distribution-label {
  color: #666;
  font-size: 14px;
}

.distribution-value {
  font-weight: bold;
  color: #333;
}

.order-info {
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  text-align: center;
}

.order-code {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.order-time {
  color: #1a73e8;
  font-weight: bold;
  margin-bottom: 5px;
}

.order-status {
  color: #666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .filter-row {
    flex-direction: column;
    gap: 10px;
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