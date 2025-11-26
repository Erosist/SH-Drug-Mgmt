<template>
  <div class="status-page" v-if="isAdmin">
    <div class="page-header">
      <div>
        <p class="eyebrow">系统运行状态</p>
        <h2>实时掌握预警、订单与供应链健康度</h2>
        <p class="subtitle">数据来自最新统计，如需更细数据可进入对应模块查看。</p>
      </div>
      <div class="actions">
        <el-button @click="goToAdminUsers">用户管理</el-button>
        <el-button type="primary" plain :loading="loading" @click="loadStatus">刷新数据</el-button>
      </div>
    </div>

    <el-alert
      v-for="(msg, idx) in warningMessages"
      :key="idx"
      type="warning"
      :closable="false"
      show-icon
      class="warn-banner"
    >
      {{ msg }}
    </el-alert>

    <div class="status-meta">
      <span>最后更新：{{ lastUpdated }}</span>
      <span v-if="stats?.orders">订单总数：{{ stats.orders.total ?? '-' }}</span>
    </div>

    <div v-if="stats" class="sections">
      <section class="stat-section">
        <header>
          <h3>用户账户</h3>
          <small>总计 {{ stats.users?.total ?? '-' }} 个账号</small>
        </header>
        <div class="stat-grid">
          <div class="stat-card" v-for="card in userCards" :key="card.label">
            <p class="label">{{ card.label }}</p>
            <p class="value">{{ card.value }}</p>
            <p class="desc">{{ card.desc }}</p>
          </div>
        </div>
      </section>

      <section class="stat-section">
        <header>
          <h3>企业认证</h3>
          <small>审批进度一目了然</small>
        </header>
        <div class="stat-grid small">
          <div class="stat-card" v-for="card in certCards" :key="card.label">
            <p class="label">{{ card.label }}</p>
            <p class="value">{{ card.value }}</p>
          </div>
        </div>
      </section>

      <section class="stat-section">
        <header>
          <h3>订单概览</h3>
          <small>各业务状态订单数量</small>
        </header>
        <el-table :data="orderStatusEntries" border style="width: 100%" size="small" v-if="orderStatusEntries.length">
          <el-table-column label="状态" prop="label" width="200">
            <template #default="scope">
              <el-tag effect="plain">{{ scope.row[0] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="数量">
            <template #default="scope">{{ scope.row[1] }}</template>
          </el-table-column>
        </el-table>
        <el-empty description="暂无订单数据" v-else />
      </section>

      <section class="stat-section">
        <header>
          <h3>库存预警</h3>
          <small>库存条目：{{ stats.inventory?.total_items ?? '-' }}</small>
        </header>
        <div class="stat-grid small">
          <div class="stat-card">
            <p class="label">低库存</p>
            <p class="value danger">{{ stats.inventory?.low_stock ?? '-' }}</p>
            <p class="desc">低于阈值（10）的批次</p>
          </div>
          <div class="stat-card">
            <p class="label">近效期</p>
            <p class="value warning">{{ stats.inventory?.near_expiry ?? '-' }}</p>
            <p class="desc">30 天内到期</p>
          </div>
          <div class="stat-card">
            <p class="label">已过期</p>
            <p class="value danger">{{ stats.inventory?.expired ?? '-' }}</p>
            <p class="desc">需立即处置</p>
          </div>
        </div>
      </section>

      <section class="stat-section">
        <header>
          <h3>供应链活跃度</h3>
        </header>
        <div class="stat-grid small">
          <div class="stat-card">
            <p class="label">活跃供应信息</p>
            <p class="value">{{ stats.supply?.active_supplies ?? '-' }}</p>
          </div>
          <div class="stat-card">
            <p class="label">非活跃供应信息</p>
            <p class="value">{{ stats.supply?.inactive_supplies ?? '-' }}</p>
          </div>
        </div>
      </section>
    </div>
    <el-empty v-else description="暂无统计数据，请刷新" />
  </div>
  <div v-else class="no-access">
    <el-result icon="warning" title="仅系统管理员可访问">
      <template #extra><el-button type="primary" @click="goHome">返回首页</el-button></template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchSystemStatus } from '@/api/admin'
import { getCurrentUser } from '@/utils/authSession'

const router = useRouter()
const currentUser = ref(getCurrentUser())
const stats = ref(null)
const loading = ref(false)

const isAdmin = computed(() => currentUser.value?.role === 'admin')
const lastUpdated = computed(() =>
  stats.value?.generated_at ? new Date(stats.value.generated_at).toLocaleString() : '-'
)

const userCards = computed(() => {
  const data = stats.value?.users || {}
  return [
    { label: '用户总数', value: data.total ?? '-', desc: '平台已注册账号' },
    { label: '活跃账号', value: data.active ?? '-', desc: '状态正常，可登录' },
    { label: '禁用账号', value: data.disabled ?? '-', desc: '被管理员停用' },
    { label: '近7日新增', value: data.new_last_7_days ?? '-', desc: '近一周新增注册' },
  ]
})

const certCards = computed(() => {
  const data = stats.value?.certifications || {}
  return [
    { label: '待审核', value: data.pending ?? '-' },
    { label: '已通过', value: data.approved ?? '-' },
    { label: '已驳回', value: data.rejected ?? '-' },
  ]
})

const orderStatusEntries = computed(() => {
  const byStatus = stats.value?.orders?.by_status || {}
  return Object.entries(byStatus)
})

const warningMessages = computed(() => {
  const warns = []
  const inventory = stats.value?.inventory
  if (!inventory) return warns
  if ((inventory.low_stock ?? 0) > 0) {
    warns.push(`有 ${inventory.low_stock} 个批次低于库存阈值，请尽快补货。`)
  }
  if ((inventory.near_expiry ?? 0) > 0) {
    warns.push(`有 ${inventory.near_expiry} 个批次即将到期，注意调拨。`)
  }
  if ((inventory.expired ?? 0) > 0) {
    warns.push(`有 ${inventory.expired} 个批次已过期，需立即处理。`)
  }
  return warns
})

const loadStatus = async () => {
  if (!isAdmin.value) return
  loading.value = true
  try {
    stats.value = await fetchSystemStatus()
  } catch (err) {
    ElMessage.error(err?.message || '加载系统状态失败')
  } finally {
    loading.value = false
  }
}

const goToAdminUsers = () => router.push('/admin/users')
const goHome = () => router.push('/')

const refreshUser = () => {
  currentUser.value = getCurrentUser()
}

onMounted(() => {
  window.addEventListener('storage', refreshUser)
  if (isAdmin.value) loadStatus()
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', refreshUser)
})

watch(isAdmin, (val) => {
  if (val && !stats.value) {
    loadStatus()
  }
})
</script>

<style scoped>
.status-page {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fb;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #eef2f7;
}

.eyebrow {
  color: #1a73e8;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.subtitle {
  margin: 4px 0 0 0;
  color: #606266;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 10px;
}

.warn-banner {
  margin-bottom: 10px;
}

.status-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}

.sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-section {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #eef2f7;
  padding: 16px;
}

.stat-section header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 12px;
}

.stat-section header h3 {
  margin: 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.stat-grid.small {
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}

.stat-card {
  border: 1px solid #eef2f7;
  border-radius: 10px;
  padding: 12px;
  background: #fdfdfd;
}

.stat-card .label {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.stat-card .value {
  margin: 4px 0;
  font-size: 26px;
  font-weight: 600;
  color: #1f2d3d;
}

.stat-card .value.warning {
  color: #e6a23c;
}

.stat-card .value.danger {
  color: #f56c6c;
}

.stat-card .desc {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.no-access {
  padding: 40px;
}
</style>
