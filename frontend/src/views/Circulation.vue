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
              v-if="isLogistics || isRegulator"
              class="nav-item" 
              :class="{ active: activeNav === 'circulation' }"
              @click="navigateTo('circulation')"
            >{{ isRegulator ? '药品追溯查询' : '流通数据上报' }}</div>
            <div v-if="canViewAnalysis"
              class="nav-item" 
              :class="{ active: activeNav === 'analysis' }"
              @click="navigateTo('analysis')"
            >监管分析</div>
            <div 
              v-if="isRegulator"
              class="nav-item" 
              :class="{ active: activeNav === 'compliance' }"
              @click="navigateTo('compliance')"
            >合规分析报告</div>
            <div v-if="isLogistics"
              class="nav-item" 
              :class="{ active: activeNav === 'service' }"
              @click="navigateTo('service')"
            >智能调度</div>
            <div v-if="isLogistics"
              class="nav-item"
              :class="{ active: activeNav === 'orders' }"
              @click="navigateTo('logistics-orders')"
            >订单查看</div>
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

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 监管用户：药品追溯查询 -->
        <div v-if="isRegulator" class="regulator-content">
          <div class="section trace-query">
            <h3 class="section-title">药品追溯查询</h3>
            <div class="trace-form">
              <div class="form-group">
                <label class="form-label">运单号 <span class="required">*</span></label>
                <div class="input-with-button">
                  <input 
                    type="text" 
                    class="form-input" 
                    v-model="traceForm.tracking_number"
                    placeholder="请输入运单号"
                    :disabled="tracing"
                    @keyup.enter="handleTrace"
                  >
                  <button 
                    class="query-btn" 
                    @click="handleTrace"
                    :disabled="tracing || !traceForm.tracking_number.trim()"
                  >
                    {{ tracing ? '查询中...' : '查询' }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 追溯结果 -->
            <div v-if="traceResult" class="trace-result">
              <div v-if="traceResult.drug" class="drug-info">
                <h5>药品信息</h5>
                <div class="info-grid">
                  <div><span class="label">通用名：</span>{{ traceResult.drug.generic_name }}</div>
                  <div><span class="label">运单号：</span>{{ traceResult.tracking_number }}</div>
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
                    
                    <!-- 位置信息显示 -->
                    <div v-if="item.latitude && item.longitude" class="timeline-gps">
                      📍 GPS坐标: {{ item.latitude.toFixed(6) }}, {{ item.longitude.toFixed(6) }}
                    </div>
                    <div v-if="item.location" class="timeline-location">
                      📍 位置描述: {{ item.location }}
                    </div>
                    <div v-if="!item.latitude && !item.longitude && !item.location" class="timeline-no-location">
                      📍 位置信息: 未记录
                    </div>
                    
                    <div v-if="item.remarks" class="timeline-remarks">
                      💬 备注: {{ item.remarks }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 流通记录详细表格 -->
          <div v-if="traceResult && traceResult.timeline && traceResult.timeline.length > 0" class="section records-table-section">
            <h3 class="section-title">流通记录详情</h3>
            <div class="records-table-container">
              <table class="records-table">
                <thead>
                  <tr>
                    <th>时间</th>
                    <th>状态</th>
                    <th>GPS坐标</th>
                    <th>位置描述</th>
                    <th>备注</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="(item, index) in traceResult.timeline" 
                    :key="item.id"
                    :class="`status-row-${item.status.toLowerCase()}`"
                  >
                    <td class="time-cell">{{ formatTime(item.timestamp) }}</td>
                    <td class="status-cell">
                      <span :class="`status-badge status-${item.status.toLowerCase()}`">
                        {{ item.status_text }}
                      </span>
                    </td>
                    <td class="gps-cell">
                      <span v-if="item.latitude && item.longitude" class="gps-coords">
                        {{ item.latitude.toFixed(6) }}, {{ item.longitude.toFixed(6) }}
                      </span>
                      <span v-else class="no-gps">-</span>
                    </td>
                    <td class="location-cell">
                      <span v-if="item.location">{{ item.location }}</span>
                      <span v-else class="no-location">-</span>
                    </td>
                    <td class="remarks-cell">
                      <span v-if="item.remarks">{{ item.remarks }}</span>
                      <span v-else class="no-remarks">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- Sankey流向图 -->
          <div v-if="traceResult && traceResult.sankey" class="section sankey-section">
            <h3 class="section-title">流向图</h3>
            <div class="sankey-container">
              <div ref="sankeyChart" class="sankey-chart"></div>
            </div>
          </div>
        </div>

        <!-- 物流用户：流通数据上报 -->
        <div v-else-if="isLogistics" class="logistics-content">
          <!-- 左侧内容 -->
          <div class="left-content">
            <div class="section data-reporting">
              <h3 class="section-title">流通数据上报</h3>
              
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
                    <option value="SHIPPED">待揽收</option>
                    <option value="IN_TRANSIT">运输中</option>
                    <option value="DELIVERED">已送达</option>
                  </select>
                </div>
              </div>
              
              <div class="form-group">
                <label class="form-label">时间戳</label>
                <input 
                  type="datetime-local" 
                  class="form-input"
                  v-model="reportForm.timestamp"
                  :disabled="!isAuthenticated || submitting"
                >
                <div class="timestamp-hint">系统自动设置，当前时间：{{ currentTimestamp }}</div>
              </div>
              
              <!-- 权限提示 -->
              <div v-if="!isAuthenticated" class="permission-notice warning">
                <div class="notice-icon">⚠️</div>
                <div class="notice-text">请先登录后再提交流通数据上报</div>
              </div>
              <div v-else-if="!isAllowedRole" class="permission-notice warning">
                <div class="notice-icon">⚠️</div>
                <div class="notice-text">当前角色无权上报流通数据，仅物流公司可以上报</div>
              </div>
              <div v-else class="permission-notice info">
                <div class="notice-icon">ℹ️</div>
                <div class="notice-text">状态流转规则：待揽收 → 运输中 → 已送达（正向流转，已送达 不可逆）</div>
              </div>
            </div>
          </div>
          
          <!-- 右侧内容 -->
          <div class="right-content">
            <!-- 位置信息 -->
            <div class="section location-info">
              <h3 class="section-title">位置信息</h3>
              
              <div class="location-form">
                <div class="gps-action">
                  <button class="gps-btn" @click="useCurrentLocation" :disabled="!isAuthenticated || submitting">
                    📍 获取GPS定位（必填）
                  </button>
                  
                  <!-- GPS状态显示 -->
                  <div v-if="reportForm.longitude && reportForm.latitude" class="gps-status success">
                    <div class="status-icon">✅</div>
                    <div class="status-text">
                      <div class="status-title">GPS定位已获取</div>
                      <div class="gps-hint">经度 {{ reportForm.longitude }}, 纬度 {{ reportForm.latitude }}</div>
                    </div>
                  </div>
                  
                  <div v-else class="gps-status warning">
                    <div class="status-icon">⚠️</div>
                    <div class="status-text">
                      <div class="status-title">请先获取GPS定位</div>
                      <div class="gps-hint">必须获取GPS位置信息才能提交</div>
                    </div>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">备注信息（可选）</label>
                  <textarea 
                    class="form-textarea" 
                    placeholder="可填写补充说明（若需）" 
                    v-model="reportForm.remarks"
                    :disabled="!isAuthenticated || submitting"
                  ></textarea>
                </div>
              </div>
            </div>
            
            <!-- 操作提示 -->
            <div class="section operation-tips">
              <h3 class="section-title">操作提示</h3>
              <div class="tips-content">
                <ul class="tips-list">
                  <li>运单号必须与订单运单号一致</li>
                  <li>必须先使用GPS定位当前位置才能提交</li>
                  <li>运输状态必须按顺序流转：待揽收 → 运输中 → 已送达</li>
                  <li>已送达状态不可逆</li>
                  <li>运输中状态可以重复上报以更新位置信息</li>
                  <li>备注为可选字段</li>
                </ul>
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
              :disabled="!isAuthenticated || !isAllowedRole || submitting || !reportForm.latitude || !reportForm.longitude"
              :loading="submitting"
            >
              {{ submitting ? '提交中...' : '提交' }}
            </button>
          </div>
        </div>

        <!-- 其他用户：无权限提示 -->
        <div v-else class="unauthorized-content">
          <div class="section unauthorized-notice">
            <h3 class="section-title">访问受限</h3>
            <div class="notice-content">
              <div class="notice-icon">🔒</div>
              <div class="notice-text">
                <p>此功能仅对以下角色开放：</p>
                <ul>
                  <li><strong>监管用户：</strong>可进行药品追溯查询</li>
                  <li><strong>物流用户：</strong>可进行流通数据上报</li>
                </ul>
                <p>请使用具有相应权限的账户登录。</p>
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
    
    // 允许的角色 - 只有物流用户可以上报数据
    const ALLOWED_ROLES = ['logistics']
    const isAllowedRole = computed(() => {
      return currentUser.value && ALLOWED_ROLES.includes(currentUser.value.role)
    })
    
    // 上报表单
    const reportForm = ref({
      tracking_number: '',
      transport_status: '',
      timestamp: '',
      latitude: null,
      longitude: null,
      remarks: ''
    })
    
    // 追溯查询表单
    const traceForm = ref({
      tracking_number: ''
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
      
      // 必须使用GPS定位
      if (!reportForm.value.latitude || !reportForm.value.longitude) {
        ElMessage.error('请先使用GPS定位当前位置')
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
          timestamp: timestamp,
          latitude: parseFloat(reportForm.value.latitude),
          longitude: parseFloat(reportForm.value.longitude)
        }
        
        // 可选字段
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
    
    // 处理追溯查询 - 修改为使用运单号查询
    const handleTrace = async () => {
      if (!traceForm.value.tracking_number.trim()) {
        ElMessage.warning('请输入运单号')
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
          tracking_number: traceForm.value.tracking_number.trim()
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
      // 保持 activeNav 的可控性：对于特定页面我们希望使用统一的高亮键
      if (page === 'logistics-orders') {
        activeNav.value = 'orders'
      } else {
        activeNav.value = page
      }

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
        case 'logistics-orders':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/logistics-orders' } })
            break
          }
          if (currentUser.value.role === 'unauth') {
            router.push({ name: 'unauth', query: { active: 'orders' } })
            break
          }
          router.push('/logistics-orders')
          break
        case 'compliance':
          if (!currentUser.value) {
            router.push({ name: 'login', query: { redirect: '/compliance-report' } })
            break
          }
          if (currentUser.value.role !== 'regulator') {
            router.push('/')
            break
          }
          router.push({ name: 'compliance-report' })
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
  /* line-height: 1.6; //宽度不一致的关键 */
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

.nav-menu.disabled-nav {
  flex: 1;
  align-items: center;
  gap: 0;
  color: #999;
  font-size: 14px;
}

.nav-disabled-text {
  color: #999;
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

.user-info {
  display: flex;
  align-items: center;
  padding: 6px 12px;
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

.auth-btn {
  background-color: #fff;
  color: #1a73e8;
  border: 1px solid #1a73e8;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
  transition: background-color 0.3s;
}

.auth-btn:hover {
  background-color: rgba(26, 115, 232, 0.08);
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

/* 主内容区域样式 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px;
}

.content-wrapper {
  width: 100%;
  height: 100%;
}

/* 监管用户内容布局 */
.regulator-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 物流用户内容布局 */
.logistics-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  /* 第一行为弹性高度，底部操作为自适应高度 */
  grid-template-rows: 1fr auto;
  height: 100%;
}

.logistics-content .left-content {
  grid-column: 1;
  grid-row: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 允许子元素溢出/滚动 */
}

.logistics-content .right-content {
  grid-column: 2;
  grid-row: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.logistics-content .action-buttons {
  grid-column: 1 / -1;
  grid-row: 2;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 20px;
}

/* 无权限用户内容 */
.unauthorized-content .unauthorized-notice {
  text-align: center;
  padding: 60px 20px;
}

.unauthorized-content .notice-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  max-width: 500px;
  margin: 0 auto;
}

.unauthorized-content .notice-icon {
  font-size: 48px;
  opacity: 0.6;
}

.unauthorized-content .notice-text {
  color: #666;
  line-height: 1.6;
}

.unauthorized-content .notice-text ul {
  text-align: left;
  margin: 16px 0;
  padding-left: 20px;
}

.unauthorized-content .notice-text li {
  margin: 8px 0;
}

/* 通用区块样式 */
.section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 6px rgba(10, 20, 30, 0.04);
  padding: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #222;
}

/* 表单样式 */
.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #333;
}

.required {
  color: #d93025;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #1a73e8;
  box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.input-with-button {
  display: flex;
  gap: 8px;
}

.input-with-button .form-input {
  flex: 1;
}

.query-btn {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.query-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.query-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* GPS定位按钮 */
.gps-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 12px;
  transition: background-color 0.3s;
}

.gps-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.gps-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #9e9e9e;
}

.gps-hint {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
}

.gps-status {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  border-radius: 6px;
  margin-top: 12px;
  margin-bottom: 16px;
}

.gps-status.success {
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
}

.gps-status.warning {
  background-color: #fefce8;
  border: 1px solid #fde047;
}

.gps-status .status-icon {
  font-size: 18px;
  margin-top: 2px;
}

.gps-status .status-text {
  flex: 1;
}

.gps-status .status-title {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.gps-status.success .status-title {
  color: #0369a1;
}

.gps-status.warning .status-title {
  color: #a16207;
}

.timestamp-hint {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

/* 使左侧的 data-reporting 与右侧的 location-info 能够对齐底部 */
.data-reporting {
  display: flex;
  flex-direction: column;
  /* 在网格的1fr行中拉伸填满高度 */
  flex: 1 1 auto;
  min-height: 0;
}

.location-info {
  display: flex;
  flex-direction: column;
  /* 右侧位置信息拉伸，与左侧 data-reporting 保持相同高度 */
  flex: 1 1 auto;
  min-height: 0;
}

/* 权限提示 */
.permission-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
}

.permission-notice.warning {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
}

.permission-notice.info {
  background-color: #e3f2fd;
  border: 1px solid #bbdefb;
}

.notice-icon {
  font-size: 18px;
}

.notice-text {
  font-size: 14px;
  line-height: 1.4;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 20px;
}

.reset-btn, .submit-btn {
  padding: 10px 24px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn {
  background-color: transparent;
  border: 1px solid #ccc;
  color: #666;
}

.reset-btn:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.submit-btn {
  background-color: #1a73e8;
  border: 1px solid #1a73e8;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0d62d9;
}

.reset-btn:disabled, .submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 追溯结果样式 */
.trace-result {
  margin-top: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.drug-info h5 {
  margin-bottom: 12px;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}

.info-grid div {
  font-size: 14px;
}

.info-grid .label {
  font-weight: 600;
  color: #666;
}

.trace-summary {
  display: flex;
  gap: 24px;
  margin-top: 12px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: #666;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #1a73e8;
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
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #e0e0e0;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-dot {
  position: absolute;
  left: -22px;
  top: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #1a73e8;
  border: 2px solid #fff;
  box-shadow: 0 0 0 3px #1a73e8;
}

.timeline-content {
  background-color: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-status {
  font-weight: 600;
  color: #333;
}

.timeline-time {
  color: #666;
  font-size: 13px;
}

.timeline-location {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.timeline-gps {
  color: #1976d2;
  font-size: 13px;
  margin-top: 5px;
  font-family: 'Courier New', monospace;
}

.timeline-no-location {
  color: #999;
  font-size: 13px;
  margin-top: 5px;
  font-style: italic;
}

.timeline-remarks {
  color: #888;
  font-size: 13px;
  margin-top: 5px;
  font-style: italic;
}

/* 流通记录表格样式 */
.records-table-section {
  margin-top: 24px;
}

.records-table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  font-size: 14px;
}

.records-table th {
  background-color: #f5f7fa;
  color: #333;
  font-weight: 600;
  padding: 12px;
  text-align: left;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

.records-table td {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: top;
}

.records-table tbody tr:hover {
  background-color: #f9f9f9;
}

.records-table tbody tr:last-child td {
  border-bottom: none;
}

/* 状态行样式 */
.status-row-shipped {
  border-left: 4px solid #91cc75;
}

.status-row-in_transit {
  border-left: 4px solid #fac858;
}

.status-row-delivered {
  border-left: 4px solid #ee6666;
}

/* 单元格样式 */
.time-cell {
  min-width: 160px;
  font-family: 'Courier New', monospace;
}

.status-cell {
  min-width: 100px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.status-shipped {
  background-color: #f0f9ff;
  color: #0369a1;
  border: 1px solid #bae6fd;
}

.status-badge.status-in_transit {
  background-color: #fefce8;
  color: #a16207;
  border: 1px solid #fde047;
}

.status-badge.status-delivered {
  background-color: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.gps-cell {
  min-width: 180px;
  font-family: 'Courier New', monospace;
}

.gps-coords {
  color: #1976d2;
  font-size: 13px;
}

.location-cell {
  min-width: 150px;
  max-width: 200px;
  word-wrap: break-word;
}

.remarks-cell {
  max-width: 200px;
  word-wrap: break-word;
}

.no-gps, .no-location, .no-remarks {
  color: #ccc;
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

/* 响应式调整 */
@media (max-width: 1024px) {
  .logistics-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }
  
  .logistics-content .left-content {
    grid-column: 1;
    grid-row: 1;
  }
  
  .logistics-content .right-content {
    grid-column: 1;
    grid-row: 2;
  }
  
  .logistics-content .action-buttons {
    grid-column: 1;
    grid-row: 3;
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
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
