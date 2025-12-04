<template>
  <div class="compliance-report-page">
    <el-page-header content="合规分析报告" @back="$router.back()" />

    <el-card class="filters-card">
      <div class="filters-row">
        <el-form :inline="true" :model="filters">
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DDTHH:mm:ss"
            />
          </el-form-item>
          <el-form-item label="区域">
            <el-input
              v-model="filters.region"
              placeholder="请输入区域关键词，如：黄浦区"
              clearable
              style="width: 260px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="loadReport">
              生成报告
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <div v-if="loading" class="hint">
        正在生成报告，请稍候（数据量较大时可能需要几秒钟）…
      </div>
    </el-card>

    <el-card v-if="report" class="summary-card">
      <template #header>
        <div class="summary-header">
          <span>报告概览</span>
          <div class="actions">
            <el-button size="small" @click="download('excel')" :loading="exportingExcel">
              导出 Excel
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="download('pdf')"
              :loading="exportingPdf"
            >
              导出 PDF
            </el-button>
          </div>
        </div>
      </template>
      <div class="summary-content">
        <div class="summary-item">
          <div class="label">库存异常比例</div>
          <div class="value">
            {{ (report.inventory.summary.abnormal_ratio * 100).toFixed(2) }}%
          </div>
        </div>
        <div class="summary-item">
          <div class="label">流通延迟比例</div>
          <div class="value">
            {{ (report.circulation.summary.delayed_ratio * 100).toFixed(2) }}%
          </div>
        </div>
        <div class="summary-item">
          <div class="label">纳入统计企业数</div>
          <div class="value">{{ report.enterprise.items.length }}</div>
        </div>
      </div>
    </el-card>

    <div v-if="report" class="grids">
      <el-card class="grid-card">
        <template #header>库存合规分析</template>
        <el-table :data="report.inventory.by_tenant" size="small" height="320">
          <el-table-column prop="tenant_name" label="企业" min-width="160" />
          <el-table-column prop="total_batches" label="批次" width="80" />
          <el-table-column prop="abnormal_batches" label="异常批次" width="90" />
          <el-table-column
            label="异常比例"
            width="100"
          >
            <template #default="{ row }">
              {{ (row.abnormal_ratio * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="risk_level" label="风险等级" width="90" />
        </el-table>
      </el-card>

      <el-card class="grid-card">
        <template #header>流通时效对比</template>
        <el-table :data="report.circulation.timeliness_trend" size="small" height="320">
          <el-table-column prop="date" label="日期" width="110" />
          <el-table-column prop="total_shipments" label="发运批次" width="90" />
          <el-table-column prop="on_time" label="按时批次" width="90" />
          <el-table-column label="按时比例">
            <template #default="{ row }">
              {{ (row.on_time_ratio * 100).toFixed(2) }}%
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <el-card v-if="report" class="enterprise-card">
      <template #header>企业合规分析</template>
      <el-table :data="report.enterprise.items" size="small" height="360">
        <el-table-column prop="tenant_name" label="企业" min-width="160" />
        <el-table-column prop="type" label="类型" width="90" />
        <el-table-column prop="inventory_violations" label="库存违规" width="90" />
        <el-table-column prop="circulation_violations" label="流通违规" width="90" />
        <el-table-column prop="total_violations" label="总违规" width="90" />
        <el-table-column label="合规率" width="100">
          <template #default="{ row }">
            {{ (row.compliance_rate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="90" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchCompliancePreview, exportComplianceReport } from '@/api/compliance'

const loading = ref(false)
const exportingPdf = ref(false)
const exportingExcel = ref(false)
const report = ref(null)

const filters = ref({
  region: '',
})
const dateRange = ref([])

function initDefaultRange() {
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - 30)
  const toIso = (d) => `${d.toISOString().slice(0, 19)}`
  dateRange.value = [toIso(start), toIso(end)]
}

async function loadReport() {
  loading.value = true
  try {
    const [start, end] = dateRange.value || []
    const res = await fetchCompliancePreview({
      start,
      end,
      region: filters.value.region,
    })
    report.value = res.data
  } catch (err) {
    ElMessage.error(err.message || '生成报告失败')
  } finally {
    loading.value = false
  }
}

async function download(format) {
  const exportingFlag = format === 'pdf' ? exportingPdf : exportingExcel
  exportingFlag.value = true
  try {
    const [start, end] = dateRange.value || []
    const blob = await exportComplianceReport({
      start,
      end,
      region: filters.value.region,
      format,
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    const suffix = format === 'pdf' ? 'pdf' : 'xlsx'
    a.href = url
    a.download = `compliance-report.${suffix}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    ElMessage.error(err.message || '下载报告失败')
  } finally {
    exportingFlag.value = false
  }
}

onMounted(() => {
  initDefaultRange()
  loadReport()
})
</script>

<style scoped>
.compliance-report-page {
  padding: 16px;
}

.filters-card,
.summary-card,
.enterprise-card {
  margin-bottom: 16px;
}

.filters-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-content {
  display: flex;
  gap: 24px;
}

.summary-item .label {
  font-size: 12px;
  color: #909399;
}

.summary-item .value {
  margin-top: 4px;
  font-size: 20px;
  font-weight: 600;
}

.grids {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.grid-card {
  min-height: 360px;
}

@media (max-width: 1024px) {
  .grids {
    grid-template-columns: 1fr;
  }
}
</style>


