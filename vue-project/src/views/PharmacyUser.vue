<template>
  <div class="pharmacy-page">
    <UserHeader :tags="headerTags" />

    <div class="layout">
      <!-- 左侧菜单 -->
      <aside class="sider">
        <div class="sider-title">管理目录</div>
        <ul class="menu">
          <li class="menu-item active">首页</li>
          <li class="menu-item">库存管理</li>
          <li class="menu-item">商品流通管理</li>
        </ul>
      </aside>

      <!-- 主内容 -->
      <main class="main">
        <section class="cards-row">
          <el-card class="panel">
            <div class="panel-head">
              <span>智能管理中心</span>
              <el-button size="small">新增任务</el-button>
            </div>
            <div class="kpis">
              <div class="kpi">
                <div class="kpi-title">待分配任务</div>
                <div class="kpi-value">1</div>
              </div>
              <div class="kpi">
                <div class="kpi-title">进行中任务</div>
                <div class="kpi-value">2</div>
              </div>
              <div class="kpi">
                <div class="kpi-title">资源使用率</div>
                <div class="kpi-value">7%</div>
              </div>
            </div>
            <div class="table-mini">
              <div class="table-row table-head">
                <span>调度任务</span><span>任务状态</span><span>负责人</span><span>预计用时</span><span>操作</span>
              </div>
              <div class="table-row">
                <span>到货上架</span><span><em class="dot dot-warn"></em>待分配</span><span>—</span><span>—</span><a href="#">详情</a>
              </div>
              <div class="table-row">
                <span>药品库存盘点</span><span><em class="dot dot-info"></em>进行中</span><span>王磊</span><span>2小时</span><a href="#">详情</a>
              </div>
              <div class="table-row">
                <span>用户信息核验</span><span><em class="dot dot-success"></em>已完成</span><span>张敏</span><span>30分钟</span><a href="#">详情</a>
              </div>
            </div>
          </el-card>

          <el-card class="panel">
            <div class="panel-head">
              <span>链路链管理</span>
              <div class="panel-actions">
                <el-button size="small" plain>导出数据</el-button>
                <el-button size="small" type="primary">同步链路</el-button>
              </div>
            </div>
            <div class="stats-tiles">
              <div class="tile"><div class="num">5,26</div><div class="label">药品总量</div></div>
              <div class="tile"><div class="num">24</div><div class="label">管理仓库</div></div>
              <div class="tile"><div class="num">18</div><div class="label">关联药厂</div></div>
              <div class="tile"><div class="num">3.51</div><div class="label">日均周转</div></div>
            </div>
          </el-card>
        </section>

        <section class="cards-row">
          <el-card class="panel full">
            <div class="panel-head">
              <span>商品监测管理</span>
              <el-input class="search" placeholder="输入药品名称/批次号" size="small" clearable />
              <el-button size="small" type="primary">查询</el-button>
            </div>
            <div class="grid2">
              <div class="list">
                <div class="list-item">
                  <div>
                    <div class="item-title">药品批号 #YP202501016</div>
                    <div class="item-desc">异常事件：配送路径异常 - 来自第三仓库</div>
                  </div>
                  <div class="item-date">2025-10-26</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">药品批号 #YP202500280</div>
                    <div class="item-desc">企业地址：上海静安药品分厂</div>
                  </div>
                  <div class="item-date">2025-10-24</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">药品批号 #YP202509782</div>
                    <div class="item-desc">异常事件：冷链监控温度报警（原因：余热）</div>
                  </div>
                  <div class="item-date">2025-10-23</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">药品批号 #YP202501056</div>
                    <div class="item-desc">库存预警：低库存提醒 阈值: 80</div>
                  </div>
                  <div class="item-date">2025-10-22</div>
                </div>
              </div>
              <div class="chart">
                <div ref="donutRef" class="chart-box"></div>
              </div>
            </div>
          </el-card>
        </section>
      </main>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import UserHeader from '../component/UserHeader.vue'

export default {
  name: 'PharmacyUser',
  components: { UserHeader },
  data() {
    return {
      chart: null,
      headerTags: ['药店用户'],
    }
  },
  mounted() {
    this.$nextTick(() => {
      const el = this.$refs.donutRef
      if (!el) return
      this.chart = echarts.init(el)
      this.chart.setOption({
        tooltip: { trigger: 'item' },
        legend: { top: 'bottom' },
        series: [
          {
            name: '库存品类',
            type: 'pie',
            radius: ['45%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
            labelLine: { show: false },
            data: [
              { value: 1048, name: '处方药' },
              { value: 735, name: '非处方药' },
              { value: 580, name: '器械耗材' },
              { value: 484, name: '中成药' },
              { value: 300, name: '保健品' },
            ],
          },
        ],
      })
    })
    window.addEventListener('resize', this.resize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resize)
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
  },
  methods: {
    resize() {
      this.chart && this.chart.resize()
    },
  },
}
</script>

<style scoped>
.pharmacy-page { min-height: 100vh; background: #f5f7fa; }

.layout { max-width: 1200px; margin: 16px auto 24px; display: grid; grid-template-columns: 200px 1fr; gap: 16px; }
.sider { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.06); padding: 12px; }
.sider-title { padding: 10px 8px; color: #606266; font-weight: 600; }
.menu { list-style: none; margin: 0; padding: 8px; }
.menu-item { padding: 10px 12px; border-radius: 6px; cursor: pointer; color: #303133; }
.menu-item:hover { background: #f0f6ff; }
.menu-item.active { background: #ecf5ff; color: #409eff; font-weight: 600; }

.main { display: flex; flex-direction: column; gap: 16px; }
.cards-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.cards-row .full { grid-column: 1 / span 2; }
.panel { border-radius: 8px; }
.panel :deep(.el-card__body) { padding: 14px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 8px 0 12px; }
.kpi { background: #f7f9fc; border-radius: 8px; padding: 10px; text-align: center; }
.kpi-title { color: #909399; font-size: 13px; }
.kpi-value { font-size: 24px; font-weight: 700; color: #1f2d3d; }

.table-mini { margin-top: 4px; border: 1px solid #f0f0f0; border-radius: 8px; overflow: hidden; }
.table-row { display: grid; grid-template-columns: 2fr 1.2fr 1fr 1fr .8fr; gap: 8px; padding: 10px 12px; border-top: 1px solid #f5f5f5; align-items: center; }
.table-head { background: #fafafa; font-weight: 600; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot-warn { background: #e6a23c; }
.dot-info { background: #409eff; }
.dot-success { background: #67c23a; }

.stats-tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 8px; }
.tile { background: #f7f9fc; border-radius: 8px; padding: 10px; text-align: center; }
.tile .num { font-size: 20px; font-weight: 700; }
.tile .label { color: #909399; font-size: 12px; margin-top: 4px; }

.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.list { display: flex; flex-direction: column; gap: 10px; }
.list-item { display: flex; align-items: center; justify-content: space-between; background: #fdfdff; border: 1px solid #f1f2f6; border-radius: 8px; padding: 12px; }
.item-title { font-weight: 600; }
.item-desc { font-size: 12px; color: #909399; margin-top: 4px; }
.item-date { color: #606266; font-size: 12px; }

.chart-box { height: 260px; width: 100%; }

@media (max-width: 1100px) {
  .cards-row { grid-template-columns: 1fr; }
  .cards-row .full { grid-column: 1; }
  .grid2 { grid-template-columns: 1fr; }
}
</style>
