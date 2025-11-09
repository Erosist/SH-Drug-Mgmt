<template>
  <div class="b2b-container">
    <!-- 顶部导航栏 -->
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
            <button class="login-btn" @click="goToLogin">登录</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="page-header">
        <h2 class="page-title">B2B供求管理</h2>
        <div class="page-date">{{ currentDate }}</div>
      </div>

      <!-- 标签切换 -->
      <div class="tabs">
        <div class="tab-item" :class="{ active: activeTab === 'supply' }" @click="activeTab='supply'">供给信息发布</div>
        <div class="tab-item" :class="{ active: activeTab === 'demand' }" @click="activeTab='demand'">需求信息发布</div>
      </div>

      <div class="form-sections">
        <!-- 供给表单 -->
        <div v-if="activeTab==='supply'" class="card">
          <h3 class="card-title">发布药品供给信息</h3>
          <!-- 药品基本信息 -->
          <div class="sub-card">
            <h4 class="sub-title">药品基本信息</h4>
            <div class="form-grid">
              <div class="form-item">
                <label>药品ID / 追溯码</label>
                <input v-model="supplyForm.drugId" placeholder="输入药品ID或追溯码" />
              </div>
              <div class="form-item">
                <label>生产厂家</label>
                <input v-model="supplyForm.manufacturer" placeholder="输入生产厂家" />
              </div>
              <div class="form-item">
                <label>药品名称</label>
                <input v-model="supplyForm.drugName" placeholder="输入药品名称" />
              </div>
              <div class="form-item">
                <label>药品规格</label>
                <input v-model="supplyForm.spec" placeholder="输入药品规格" />
              </div>
            </div>
          </div>

          <!-- 供给详细信息 -->
          <div class="sub-card">
            <h4 class="sub-title">供给详细信息</h4>
            <div class="form-grid">
              <div class="form-item">
                <label>供给数量</label>
                <input v-model.number="supplyForm.quantity" type="number" min="0" placeholder="输入数量" />
              </div>
              <div class="form-item">
                <label>生产日期</label>
                <input v-model="supplyForm.prodDate" type="date" />
              </div>
              <div class="form-item">
                <label>单价(元)</label>
                <input v-model.number="supplyForm.unitPrice" type="number" min="0" step="0.01" placeholder="输入单价" />
              </div>
              <div class="form-item">
                <label>有效期至</label>
                <input v-model="supplyForm.expireDate" type="date" />
              </div>
              <div class="form-item">
                <label>总价(自动计算)</label>
                <input :value="totalPrice" disabled />
              </div>
              <div class="form-item">
                <label>供货状态</label>
                <select v-model="supplyForm.status">
                  <option value="supplying">供应中</option>
                  <option value="paused">暂停</option>
                  <option value="ended">结束</option>
                </select>
              </div>
            </div>
            <div class="form-actions">
              <button class="secondary-btn" @click="resetSupplyForm">重置表单</button>
              <button class="primary-btn" @click="submitSupply">提交发布</button>
            </div>
          </div>
        </div>

        <!-- 需求表单 -->
        <div v-else class="card">
          <h3 class="card-title">发布药品需求信息</h3>
          <div class="sub-card">
            <h4 class="sub-title">需求基本信息</h4>
            <div class="form-grid">
              <div class="form-item">
                <label>需求药品名称</label>
                <input v-model="demandForm.drugName" placeholder="输入药品名称" />
              </div>
              <div class="form-item">
                <label>需求数量</label>
                <input v-model.number="demandForm.quantity" type="number" min="0" placeholder="输入数量" />
              </div>
              <div class="form-item">
                <label>期望价格(元)</label>
                <input v-model.number="demandForm.expectPrice" type="number" min="0" step="0.01" placeholder="输入期望价格" />
              </div>
              <div class="form-item">
                <label>最晚交付日期</label>
                <input v-model="demandForm.deadline" type="date" />
              </div>
            </div>
            <div class="form-actions">
              <button class="secondary-btn" @click="resetDemandForm">重置表单</button>
              <button class="primary-btn" @click="submitDemand">提交需求</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 已发布记录列表 -->
      <div class="records-section">
        <h3 class="section-title">最新发布记录</h3>
        <table class="records-table">
          <thead>
            <tr>
              <th>类型</th>
              <th>药品名称</th>
              <th>数量</th>
              <th>价格/总价</th>
              <th>状态</th>
              <th>日期</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r,i) in records" :key="i">
              <td>{{ r.kind }}</td>
              <td>{{ r.drugName }}</td>
              <td>{{ r.quantity }}</td>
              <td>{{ r.priceInfo }}</td>
              <td>{{ r.status }}</td>
              <td>{{ r.date }}</td>
            </tr>
            <tr v-if="records.length===0">
              <td colspan="6" class="empty">暂无记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'B2BPlatform',
  setup() {
    const router = useRouter()
    const activeNav = ref('b2b')
    const activeTab = ref('supply')

    const currentDate = computed(() => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日`
    })

    const supplyForm = ref({
      drugId: '',
      manufacturer: '',
      drugName: '',
      spec: '',
      quantity: 0,
      prodDate: '',
      unitPrice: 0,
      expireDate: '',
      status: 'supplying'
    })

    const demandForm = ref({
      drugName: '',
      quantity: 0,
      expectPrice: 0,
      deadline: ''
    })

    const records = ref([])

    const totalPrice = computed(() => {
      const q = supplyForm.value.quantity || 0
      const p = supplyForm.value.unitPrice || 0
      return (q * p).toFixed(2)
    })

    const resetSupplyForm = () => {
      supplyForm.value = { drugId:'', manufacturer:'', drugName:'', spec:'', quantity:0, prodDate:'', unitPrice:0, expireDate:'', status:'supplying' }
    }
    const resetDemandForm = () => {
      demandForm.value = { drugName:'', quantity:0, expectPrice:0, deadline:'' }
    }

    const validateSupply = () => {
      return supplyForm.value.drugName && supplyForm.value.quantity > 0 && supplyForm.value.unitPrice > 0
    }
    const validateDemand = () => {
      return demandForm.value.drugName && demandForm.value.quantity > 0
    }

    const submitSupply = () => {
      if (!validateSupply()) {
        alert('请填写完整供给关键信息')
        return
      }
      records.value.unshift({
        kind: '供给',
        drugName: supplyForm.value.drugName,
        quantity: supplyForm.value.quantity,
        priceInfo: `${supplyForm.value.unitPrice} / ${totalPrice.value}`,
        status: supplyForm.value.status,
        date: currentDate.value
      })
      resetSupplyForm()
    }

    const submitDemand = () => {
      if (!validateDemand()) {
        alert('请填写完整需求关键信息')
        return
      }
      records.value.unshift({
        kind: '需求',
        drugName: demandForm.value.drugName,
        quantity: demandForm.value.quantity,
        priceInfo: demandForm.value.expectPrice ? demandForm.value.expectPrice + ' (期望)' : '-',
        status: '待匹配',
        date: currentDate.value
      })
      resetDemandForm()
    }

    const navigateTo = (page) => {
      activeNav.value = page
      switch(page) {
        case 'home': router.push('/') ; break
        case 'inventory': router.push('/inventory') ; break
        case 'b2b': router.push('/b2b') ; break
        case 'circulation': router.push('/circulation') ; break
        case 'analysis': router.push('/analysis') ; break
        case 'service': router.push('/service') ; break
        default: router.push('/')
      }
    }

    const goToLogin = () => router.push('/login')

    return { activeNav, activeTab, navigateTo, goToLogin, currentDate, supplyForm, demandForm, totalPrice, resetSupplyForm, resetDemandForm, submitSupply, submitDemand, records }
  }
}
</script>

<style scoped>
* { margin:0; padding:0; box-sizing:border-box; }
.b2b-container { min-height:100vh; background:#f5f7fa; font-family:'Microsoft YaHei', Arial, sans-serif; display:flex; flex-direction:column; }
.header { background:#fff; box-shadow:0 2px 10px rgba(0,0,0,.1); padding:15px 0; }
.header-content { padding:0 20px; }
.platform-info { display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; }
.platform-title { font-size:24px; font-weight:bold; color:#1a73e8; }
.current-date { color:#666; font-size:16px; }
.nav-section { display:flex; justify-content:space-between; align-items:center; border-top:1px solid #eee; padding-top:15px; }
.nav-menu { display:flex; gap:30px; }
.nav-item { font-size:16px; color:#333; cursor:pointer; padding:5px 0; transition:color .3s; }
.nav-item:hover { color:#1a73e8; }
.nav-item.active { color:#1a73e8; border-bottom:2px solid #1a73e8; }
.login-btn { background:#1a73e8; color:#fff; border:none; padding:8px 20px; border-radius:4px; cursor:pointer; font-size:14px; }
.login-btn:hover { background:#0d62d9; }

.main-content { flex:1; padding:20px; }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; }
.page-title { font-size:20px; font-weight:bold; color:#333; }
.page-date { font-size:14px; color:#666; }

.tabs { display:flex; gap:40px; border-bottom:1px solid #e5e5e5; margin-bottom:20px; }
.tab-item { padding:10px 0; cursor:pointer; font-size:14px; color:#555; position:relative; }
.tab-item.active { color:#1a73e8; font-weight:600; }
.tab-item.active::after { content:''; position:absolute; left:0; bottom:0; height:2px; width:100%; background:#1a73e8; }

.form-sections { margin-bottom:30px; }
.card { background:#fff; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,.05); padding:20px; }
.card-title { font-size:16px; font-weight:bold; color:#333; margin-bottom:15px; }
.sub-card { border:1px solid #eef0f4; border-radius:6px; padding:15px 15px 10px; margin-bottom:20px; background:#fbfcfd; }
.sub-title { font-size:14px; font-weight:600; color:#1a1a1a; margin-bottom:12px; }
.form-grid { display:grid; grid-template-columns:repeat(2, 1fr); gap:16px 24px; }
.form-item { display:flex; flex-direction:column; }
.form-item label { font-size:12px; color:#555; margin-bottom:6px; }
.form-item input, .form-item select { height:36px; border:1px solid #d9d9d9; border-radius:4px; padding:0 10px; font-size:14px; outline:none; background:#fff; }
.form-item input:focus, .form-item select:focus { border-color:#1a73e8; box-shadow:0 0 0 2px rgba(26,115,232,.15); }
.form-actions { display:flex; justify-content:flex-end; gap:12px; margin-top:5px; }
.primary-btn { background:#1a73e8; color:#fff; border:none; padding:8px 18px; border-radius:4px; cursor:pointer; font-size:14px; }
.primary-btn:hover { background:#0d62d9; }
.secondary-btn { background:#fff; color:#333; border:1px solid #d9d9d9; padding:8px 18px; border-radius:4px; cursor:pointer; font-size:14px; }
.secondary-btn:hover { background:#f5f5f5; }

.records-section { background:#fff; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,.05); padding:20px; }
.section-title { font-size:16px; font-weight:bold; color:#333; margin-bottom:15px; padding-bottom:10px; border-bottom:1px solid #eee; }
.records-table { width:100%; border-collapse:collapse; font-size:14px; }
.records-table th, .records-table td { padding:10px 8px; border-bottom:1px solid #eee; text-align:left; }
.records-table th { background:#f8f9fa; font-weight:600; }
.records-table tbody tr:hover { background:#f5f7fa; }
.empty { text-align:center; color:#999; }

@media (max-width: 992px) {
  .form-grid { grid-template-columns:1fr; }
}
</style>