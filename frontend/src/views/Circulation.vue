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
            <div v-if="!isLogistics && !isRegulator" 
              class="nav-item" 
              :class="{ active: activeNav === 'inventory' }"
              @click="navigateTo('inventory')"
            >库存管理</div>
            <div v-if="isPharmacy" class="nav-item" :class="{ active: activeNav === 'nearby' }" @click="navigateTo('nearby')">就近推荐</div>
            <div v-if="!isLogistics"
              class="nav-item" 
              :class="{ active: activeNav === 'b2b' }"
              @click="navigateTo('b2b')"
            >B2B供求平台</div>
            <div 
              class="nav-item" 
              :class="{ active: activeNav === 'circulation' }"
              @click="navigateTo('circulation')"
            >流通监管</div>
            <div v-if="canViewAnalysis"
              class="nav-item" 
              :class="{ active: activeNav === 'analysis' }"
              @click="navigateTo('analysis')"
            >监管分析</div>
            <div v-if="isLogistics"
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
            <button
              v-if="currentUser"
              class="change-btn"
              @click="goToChangePassword"
            >修改密码</button>
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
              
              <!-- 药品追溯查询 -->
              <div class="trace-query-section">
                <h4 class="subsection-title">药品追溯查询</h4>
                <div class="trace-form">
                  <div class="form-group">
                    <label class="form-label">药品批号 <span class="required">*</span></label>
                    <div class="input-with-button">
                      <input 
                        type="text" 
                        class="form-input" 
                        v-model="traceForm.batch_number"
                        placeholder="请输入药品批号"
                        :disabled="tracing"
                        @keyup.enter="handleTrace"
                      >
                      <button 
                        class="query-btn" 
                        @click="handleTrace"
                        :disabled="tracing || !traceForm.batch_number.trim()"
                      >
                        {{ tracing ? '查询中...' : '查询' }}
                      </button>
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group">
                      <label class="form-label">开始日期（可选）</label>
                      <input 
                        type="date" 
                        class="form-input"
                        v-model="traceForm.start_date"
                        :disabled="tracing"
                      >
                    </div>
                    <div class="form-group">
                      <label class="form-label">结束日期（可选）</label>
                      <input 
                        type="date" 
                        class="form-input"
                        v-model="traceForm.end_date"
                        :disabled="tracing"
                      >
                    </div>
                  </div>
                </div>
                
                <!-- 追溯结果 -->
                <div v-if="traceResult" class="trace-result">
                  <div v-if="traceResult.drug" class="drug-info">
                    <h5>药品信息</h5>
                    <div class="info-grid">
                      <div><span class="label">通用名：</span>{{ traceResult.drug.generic_name }}</div>
                      <div><span class="label">批号：</span>{{ traceResult.batch_number }}</div>
                      <div v-if="traceResult.drug.manufacturer">
                        <span class="label">生产厂家：</span>{{ traceResult.drug.manufacturer }}
                      </div>
                    </div>
                  </div>
                  
                  <div class="trace-summary">
                    <div class="summary-item">
                      <span class="summary-label">流通记录数：</span>
                      <span class="summary-value">{{ traceResult.summary.total_records }}</span>
                    </div>
                    <div class="summary-item">
                      <span class="summary-label">关联订单数：</span>
                      <span class="summary-value">{{ traceResult.summary.total_orders }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="new-report-section">
                <h4 class="subsection-title">新增流通数据上报</h4>
                
                <div class="form-row">
                  <div class="form-group">
                    <label class="form-label">运单号 <span class="required">*</span></label>
                    <input 
                      type="text" 
                      class="form-input" 
                      v-model="reportForm.tracking_number"
                      placeholder="请输入运单号（必填）"
                      :disabled="!isAuthenticated || submitting"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label">运输状态 <span class="required">*</span></label>
                    <select 
                      class="form-select" 
                      v-model="reportForm.transport_status"
                      :disabled="!isAuthenticated || submitting"
                    >
                      <option value="">请选择运输状态</option>
                      <option value="SHIPPED">已发货</option>
                      <option value="IN_TRANSIT">运输中</option>
                      <option value="DELIVERED">已送达</option>
                    </select>
                  </div>
                </div>
                
                <div class="form-group">
                  <label class="form-label">时间戳 <span class="required">*</span></label>
                  <input 
                    type="datetime-local" 
                    class="form-input"
                    v-model="reportForm.timestamp"
                    :disabled="!isAuthenticated || submitting"
                  >
                  <div class="timestamp-hint">当前时间：{{ currentTimestamp }}</div>
                </div>
              </div>
              
              <!-- 权限提示 -->
              <div v-if="!isAuthenticated" class="permission-notice warning">
                <div class="notice-icon">⚠️</div>
                <div class="notice-text">请先登录后再提交流通数据上报</div>
              </div>
              <div v-else-if="!isAllowedRole" class="permission-notice warning">
                <div class="notice-icon">⚠️</div>
                <div class="notice-text">当前角色无权上报流通数据，仅药店、供应商、物流公司可以上报</div>
              </div>
              <div v-else class="permission-notice info">
                <div class="notice-icon">ℹ️</div>
                <div class="notice-text">状态流转规则：SHIPPED → IN_TRANSIT → DELIVERED（正向流转，DELIVERED 不可逆）</div>
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
                  <label class="form-label">详细地址（可选）</label>
                  <input 
                    type="text" 
                    class="form-input" 
                    placeholder="请输入当前位置文字描述" 
                    v-model="reportForm.current_location"
                    :disabled="!isAuthenticated || submitting"
                  >
                </div>
                
                <div class="coordinates">
                  <div class="coordinate-group">
                    <label class="form-label">经度（可选）</label>
                    <input 
                      type="number" 
                      step="any"
                      class="form-input coordinate" 
                      v-model.number="reportForm.longitude" 
                      placeholder="116.4074"
                      :disabled="!isAuthenticated || submitting"
                    >
                  </div>
                  <div class="coordinate-group">
                    <label class="form-label">纬度（可选）</label>
                    <input 
                      type="number" 
                      step="any"
                      class="form-input coordinate" 
                      v-model.number="reportForm.latitude" 
                      placeholder="39.9042"
                      :disabled="!isAuthenticated || submitting"
                    >
                  </div>
                </div>
                
                <div class="gps-action">
                  <button class="gps-btn" @click="useCurrentLocation">
                    📍 使用GPS定位当前值
                  </button>
                </div>
                
                <div class="form-group">
                  <label class="form-label">备注信息（可选）</label>
                  <textarea 
                    class="form-textarea" 
                    placeholder="请输入备注信息" 
                    v-model="reportForm.remarks"
                    :disabled="!isAuthenticated || submitting"
                  ></textarea>
                </div>
              </div>
            </div>
            
            <!-- 时间轴视图 -->
            <div v-if="traceResult && traceResult.timeline && traceResult.timeline.length > 0" class="section timeline-section">
              <h3 class="section-title">时间轴视图</h3>
              <div class="timeline-container">
                <div class="timeline">
                  <div 
                    v-for="(item, index) in traceResult.timeline" 
                    :key="item.id"
                    class="timeline-item"
                    :class="`status-${item.status.toLowerCase()}`"
                  >
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                      <div class="timeline-header">
                        <span class="timeline-status">{{ item.status_text }}</span>
                        <span class="timeline-time">{{ formatTime(item.timestamp) }}</span>
                      </div>
                      <div v-if="item.location" class="timeline-location">
                        📍 {{ item.location }}
                      </div>
                      <div v-if="item.remarks" class="timeline-remarks">
                        {{ item.remarks }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Sankey流向图 -->
            <div v-if="traceResult && traceResult.sankey" class="section sankey-section">
              <h3 class="section-title">流向图</h3>
              <div class="sankey-container">
                <div ref="sankeyChart" class="sankey-chart"></div>
              </div>
            </div>
            
            <!-- 操作提示 -->
            <div class="section operation-tips">
              <h3 class="section-title">操作提示</h3>
              
              <div class="tips-content">
                <ul class="tips-list">
                  <li>运单号必须与订单运单号一致</li>
                  <li>运输状态必须按顺序流转：已发货 → 运输中 → 已送达</li>
                  <li>已送达状态不可逆</li>
                  <li>运输中状态可以重复上报以更新位置信息</li>
                  <li>位置信息和备注为可选字段</li>
                  <li>监管用户可通过批号查询药品全生命周期追溯</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部操作按钮 -->
        <div class="action-buttons">
          <button 
            class="reset-btn" 
            @click="resetForm"
            :disabled="submitting"
          >
            重置
          </button>
          <button 
            class="submit-btn" 
            @click="submitProcess"
            :disabled="!isAuthenticated || !isAllowedRole || submitting"
            :loading="submitting"
          >
            {{ submitting ? '提交中...' : '提交流程' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getCurrentUser, getToken, isAuthenticated as checkAuth } from '@/utils/authSession'
import { roleToRoute } from '@/utils/roleRoute'
import { getRoleLabel } from '@/utils/roleLabel'
import { reportCirculation, traceDrug } from '@/api/circulation'

export default {
  name: 'Circulation',
  setup() {
    const router = useRouter()
    const activeNav = ref('circulation')
    const currentUser = ref(getCurrentUser())
    const isLogistics = computed(() => currentUser.value && currentUser.value.role === 'logistics')
    const isSupplier = computed(() => currentUser.value && currentUser.value.role === 'supplier')
    const isPharmacy = computed(() => currentUser.value && currentUser.value.role === 'pharmacy')
    const isRegulator = computed(() => currentUser.value && currentUser.value.role === 'regulator')
    const isAdmin = computed(() => currentUser.value && currentUser.value.role === 'admin')
    const canViewAnalysis = computed(() => isRegulator.value || isAdmin.value)
    const userDisplayName = computed(() => currentUser.value?.displayName || currentUser.value?.username || '')
    const userRoleLabel = computed(() => getRoleLabel(currentUser.value?.role))
    const submitting = ref(false)
    
    // 当前日期和时间
    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    })
    
    const currentTimestamp = ref('')
    
    // 认证状态
    const isAuthenticated = computed(() => checkAuth())
    
    // 允许的角色
    const ALLOWED_ROLES = ['pharmacy', 'supplier', 'logistics']
    const isAllowedRole = computed(() => {
      return currentUser.value && ALLOWED_ROLES.includes(currentUser.value.role)
    })
    
    // 位置信息（省市 / 区县）
    const location = ref({
      province: 'shanghai',
      district: 'chaoyang'
    })
    
    // 上报表单
    const reportForm = ref({
      tracking_number: '',
      transport_status: '',
      timestamp: '',
      current_location: '',
      latitude: null,
      longitude: null,
      remarks: ''
    })
    
    // 追溯查询表单
    const traceForm = ref({
      batch_number: '',
      start_date: '',
      end_date: ''
    })
    
    // 追溯结果
    const traceResult = ref(null)
    const tracing = ref(false)
    const sankeyChart = ref(null)
    let sankeyChartInstance = null
    
    // 更新当前时间戳（用于显示）
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
      
      // 同步更新表单中的时间戳（ISO格式，用于提交）
      const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      reportForm.value.timestamp = localDateTime.toISOString().slice(0, 16)
    }
    
    // 使用GPS定位
    const useCurrentLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            reportForm.value.longitude = parseFloat(position.coords.longitude.toFixed(6))
            reportForm.value.latitude = parseFloat(position.coords.latitude.toFixed(6))
            ElMessage.success('GPS定位成功')
          },
          (error) => {
            console.error('获取位置失败:', error)
            ElMessage.error('获取GPS位置失败，请确保已开启位置权限')
          }
        )
      } else {
        ElMessage.error('您的浏览器不支持GPS定位')
      }
    }
    
    // 重置表单
    const resetForm = () => {
      reportForm.value = {
        tracking_number: '',
        transport_status: '',
        timestamp: '',
        current_location: '',
        latitude: null,
        longitude: null,
        remarks: ''
      }
      updateTimestamp()
    }
    
    // 验证表单
    const validateForm = () => {
      if (!reportForm.value.tracking_number.trim()) {
        ElMessage.error('请输入运单号')
        return false
      }
      
      if (!reportForm.value.transport_status) {
        ElMessage.error('请选择运输状态')
        return false
      }
      
      if (!reportForm.value.timestamp) {
        ElMessage.error('请选择时间戳')
        return false
      }
      
      return true
    }
    
    // 提交流程
    const submitProcess = async () => {
      // 权限检查
      if (!isAuthenticated.value) {
        ElMessage.warning('请先登录后再提交')
        router.push({ name: 'login', query: { redirect: '/circulation' } })
        return
      }
      
      if (!isAllowedRole.value) {
        ElMessage.error('当前角色无权上报流通数据')
        return
      }
      
      // 表单验证
      if (!validateForm()) {
        return
      }
      
      submitting.value = true
      
      try {
        // 格式化时间戳为ISO格式
        const timestamp = new Date(reportForm.value.timestamp).toISOString()
        
        // 构建提交数据
        const payload = {
          tracking_number: reportForm.value.tracking_number.trim(),
          transport_status: reportForm.value.transport_status,
          timestamp: timestamp
        }
        
        // 可选字段
        if (reportForm.value.current_location) {
          payload.current_location = reportForm.value.current_location.trim()
        }
        if (reportForm.value.latitude !== null && reportForm.value.latitude !== '') {
          payload.latitude = parseFloat(reportForm.value.latitude)
        }
        if (reportForm.value.longitude !== null && reportForm.value.longitude !== '') {
          payload.longitude = parseFloat(reportForm.value.longitude)
        }
        if (reportForm.value.remarks) {
          payload.remarks = reportForm.value.remarks.trim()
        }
        
        // 调用API
        const result = await reportCirculation(payload)
        
        ElMessage.success('状态更新成功')
        
        // 重置表单
        resetForm()
        
        console.log('上报成功:', result)
        
      } catch (error) {
        console.error('上报失败:', error)
        ElMessage.error(error.message || '提交失败，请稍后重试')
      } finally {
        submitting.value = false
      }
    }
    
    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    // 处理追溯查询
    const handleTrace = async () => {
      if (!traceForm.value.batch_number.trim()) {
        ElMessage.warning('请输入药品批号')
        return
      }
      
      // 权限检查
      if (!isAuthenticated.value) {
        ElMessage.warning('请先登录后再查询')
        router.push({ name: 'login', query: { redirect: '/circulation' } })
        return
      }
      
      if (currentUser.value?.role !== 'regulator') {
        ElMessage.error('只有监管用户才能查询药品追溯')
        return
      }
      
      tracing.value = true
      
      try {
        const params = {
          batch_number: traceForm.value.batch_number.trim()
        }
        
        if (traceForm.value.start_date) {
          params.start_date = new Date(traceForm.value.start_date).toISOString()
        }
        if (traceForm.value.end_date) {
          // 结束日期设置为当天的23:59:59
          const endDate = new Date(traceForm.value.end_date)
          endDate.setHours(23, 59, 59, 999)
          params.end_date = endDate.toISOString()
        }
        
        const result = await traceDrug(params)
        traceResult.value = result
        
        ElMessage.success('查询成功')
        
        // 渲染Sankey图
        await nextTick()
        renderSankeyChart()
        
      } catch (error) {
        console.error('追溯查询失败:', error)
        traceResult.value = null
        ElMessage.error(error.message || '查询失败，请稍后重试')
      } finally {
        tracing.value = false
      }
    }
    
    // 渲染Sankey流向图
    const renderSankeyChart = () => {
      if (!traceResult.value || !traceResult.value.sankey) return
      if (!sankeyChart.value) return
      
      // 销毁旧图表
      if (sankeyChartInstance) {
        sankeyChartInstance.dispose()
      }
      
      const sankeyData = traceResult.value.sankey
      
      // 构建ECharts Sankey图数据
      const nodes = sankeyData.nodes.map((node, index) => ({
        name: node.name,
        itemStyle: {
          color: getNodeColor(node.category)
        }
      }))
      
      const links = sankeyData.links.map(link => ({
        source: nodes[link.source].name,
        target: nodes[link.target].name,
        value: link.value
      }))
      
      // 创建图表实例
      sankeyChartInstance = echarts.init(sankeyChart.value)
      
      const option = {
        title: {
          text: '药品流向图',
          left: 'center',
          textStyle: {
            fontSize: 16
          }
        },
        tooltip: {
          trigger: 'item',
          triggerOn: 'mousemove',
          formatter: (params) => {
            if (params.dataType === 'node') {
              return `${params.data.name}<br/>类别: ${params.data.category || '未知'}`
            } else if (params.dataType === 'edge') {
              return `${params.data.source} → ${params.data.target}<br/>流通次数: ${params.data.value}`
            }
            return ''
          }
        },
        series: [{
          type: 'sankey',
          data: nodes,
          links: links,
          emphasis: {
            focus: 'adjacency'
          },
          lineStyle: {
            color: 'gradient',
            curveness: 0.5
          },
          label: {
            fontSize: 12
          }
        }]
      }
      
      sankeyChartInstance.setOption(option)
      
      // 响应式调整
      const resizeHandler = () => {
        if (sankeyChartInstance) {
          sankeyChartInstance.resize()
        }
      }
      window.addEventListener('resize', resizeHandler)
      
      // 保存resize handler以便后续移除
      if (!window._sankeyResizeHandlers) {
        window._sankeyResizeHandlers = []
      }
      window._sankeyResizeHandlers.push(resizeHandler)
    }
    
    // 获取节点颜色
    const getNodeColor = (category) => {
      const colorMap = {
        'manufacturer': '#5470c6',
        'shipped': '#91cc75',
        'in_transit': '#fac858',
        'delivered': '#ee6666'
      }
      return colorMap[category] || '#73c0de'
    }
    
    // 监听追溯结果变化，自动渲染图表
    watch(() => traceResult.value, () => {
      if (traceResult.value && traceResult.value.sankey) {
        nextTick(() => {
          renderSankeyChart()
        })
      }
    })
    
    const goToLogin = () => { router.push('/login') }
    const goToChangePassword = () => {
      if (!currentUser.value) {
        router.push({ name: 'login', query: { redirect: '/change-password' } })
        return
      }
      router.push({ name: 'change-password' })
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
        case 'nearby':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/nearby-suppliers' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'nearby' } })
            break
          }
          router.push('/nearby-suppliers')
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
      // 销毁图表实例
      if (sankeyChartInstance) {
        sankeyChartInstance.dispose()
        sankeyChartInstance = null
      }
      const resizeHandler = () => {
        if (sankeyChartInstance) {
          sankeyChartInstance.resize()
        }
      }
      window.removeEventListener('resize', resizeHandler)
    })
    
    return {
      goToLogin,
      goToUserHome,
      goToEnterpriseAuth,
      goToEnterpriseReview,
      goToSystemStatus,
      goToAdminUsers,
      goToChangePassword,
      navigateTo,
      activeNav,
      currentDate,
      currentTimestamp,
      reportForm,
      traceForm,
      traceResult,
      tracing,
      sankeyChart,
      isAuthenticated,
      isAllowedRole,
      submitting,
      location,
      useCurrentLocation,
      resetForm,
      submitProcess,
      handleTrace,
      formatTime,
      currentUser,
      isLogistics,
      isSupplier,
      isPharmacy,
      isRegulator,
      isAdmin,
      canViewAnalysis,
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

.change-btn {
  border: 1px solid #1a73e8;
  background-color: transparent;
  color: #1a73e8;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
  transition: background-color 0.3s;
}

.change-btn:hover {
  background-color: rgba(26, 115, 232, 0.08);
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
.trace-query-section {
  margin-bottom: 30px;
}

.input-with-button {
  display: flex;
  gap: 10px;
}

.input-with-button .form-input {
  flex: 1;
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

.query-btn:hover:not(:disabled) {
  background-color: #0d62d9;
}

.query-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.trace-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.drug-info {
  margin-bottom: 15px;
}

.drug-info h5 {
  margin-bottom: 10px;
  color: #333;
  font-size: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.info-grid .label {
  font-weight: bold;
  color: #666;
  margin-right: 5px;
}

.trace-summary {
  display: flex;
  gap: 20px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  color: #666;
  font-size: 14px;
}

.summary-value {
  color: #1a73e8;
  font-weight: bold;
  font-size: 16px;
}

/* 权限提示 */
.permission-notice {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
}

.permission-notice.warning {
  background-color: #fff8e1;
  border: 1px solid #ffd54f;
}

.permission-notice.info {
  background-color: #e3f2fd;
  border: 1px solid #90caf9;
}

.notice-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.permission-notice.warning .notice-text {
  color: #e65100;
}

.permission-notice.info .notice-text {
  color: #1565c0;
}

.notice-text {
  font-size: 14px;
  line-height: 1.4;
}

.required {
  color: #f56c6c;
}

.timestamp-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
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

/* 时间轴样式 */
.timeline-container {
  padding: 20px;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e2e8f0;
}

.timeline-item {
  position: relative;
  margin-bottom: 30px;
  padding-left: 30px;
}

.timeline-dot {
  position: absolute;
  left: -22px;
  top: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid #cbd5e0;
  z-index: 1;
}

.timeline-item.status-shipped .timeline-dot {
  border-color: #91cc75;
  background: #91cc75;
}

.timeline-item.status-in_transit .timeline-dot {
  border-color: #fac858;
  background: #fac858;
}

.timeline-item.status-delivered .timeline-dot {
  border-color: #ee6666;
  background: #ee6666;
}

.timeline-content {
  background: #fff;
  padding: 15px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-status {
  font-weight: bold;
  color: #333;
  font-size: 15px;
}

.timeline-time {
  color: #999;
  font-size: 13px;
}

.timeline-location {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.timeline-remarks {
  color: #888;
  font-size: 13px;
  margin-top: 5px;
  font-style: italic;
}

/* Sankey图样式 */
.sankey-container {
  padding: 20px;
}

.sankey-chart {
  width: 100%;
  height: 500px;
  min-height: 400px;
}

/* 操作提示 */
.tips-content {
  padding: 10px 0;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  padding: 6px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  padding-left: 20px;
}

.tips-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #1a73e8;
  font-weight: bold;
}
</style>
