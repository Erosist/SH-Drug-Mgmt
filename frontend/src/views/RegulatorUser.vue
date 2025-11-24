<template>
  <div class="regulator-page">
    <UserHeader :tags="[user.role]" />

    <div class="layout">
      <!-- 左侧菜单 -->
      <aside class="sider">
        <div class="sider-title">管理目录</div>
        <ul class="menu">
          <li class="menu-item active">监管概览</li>
          <li class="menu-item">异常预警</li>
          <li class="menu-item">企业监管</li>
          <li class="menu-item">药品流通</li>
        </ul>
      </aside>

      <!-- 主内容 -->
      <main class="main">
        <section class="cards-row">
          <el-card class="panel">
            <div class="panel-head">
              <span>智能监管中心</span>
              <el-button size="small" type="primary">新建任务</el-button>
            </div>
            <div class="kpis">
              <div class="kpi">
                <div class="kpi-title">待处理事件</div>
                <div class="kpi-value">1</div>
              </div>
              <div class="kpi">
                <div class="kpi-title">进行中核查</div>
                <div class="kpi-value">2</div>
              </div>
              <div class="kpi">
                <div class="kpi-title">资源使用率</div>
                <div class="kpi-value">7%</div>
              </div>
            </div>
            <div class="table-mini">
              <div class="table-row table-head">
                <span>任务</span><span>状态</span><span>责任人</span><span>时长</span><span>操作</span>
              </div>
              <div class="table-row">
                <span>冷链温度核查</span><span><em class="dot dot-warn"></em>待处理</span><span>—</span><span>—</span><a href="#">详情</a>
              </div>
              <div class="table-row">
                <span>企业资质审查</span><span><em class="dot dot-info"></em>进行中</span><span>王磊</span><span>2小时</span><a href="#">详情</a>
              </div>
              <div class="table-row">
                <span>台账抽查</span><span><em class="dot dot-success"></em>已完成</span><span>张敏</span><span>30分钟</span><a href="#">详情</a>
              </div>
            </div>
          </el-card>

          <el-card class="panel">
            <div class="panel-head">
              <span>基础数据管理</span>
              <div class="panel-actions">
                <el-button size="small" plain>导出报表</el-button>
                <el-button size="small" type="primary">同步数据</el-button>
              </div>
            </div>
            <div class="stats-tiles">
              <div class="tile"><div class="num">5,26</div><div class="label">药品总量</div></div>
              <div class="tile"><div class="num">24</div><div class="label">管理企业</div></div>
              <div class="tile"><div class="num">18</div><div class="label">监管用户</div></div>
              <div class="tile"><div class="num">3.51</div><div class="label">日均处理</div></div>
            </div>
          </el-card>
        </section>

        <section class="cards-row">
          <el-card class="panel full">
            <div class="panel-head">
              <span>药品流通监控</span>
              <el-input class="search" placeholder="输入药品名称/批次号" size="small" clearable />
              <el-button size="small" type="primary">查询</el-button>
            </div>
            <div class="grid2">
              <div class="list">
                <div class="list-item">
                  <div>
                    <div class="item-title">异常告警 #AL202510016</div>
                    <div class="item-desc">配送温度异常，需核查冷链日志</div>
                  </div>
                  <div class="item-date">2025-10-26</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">抽检任务 #QC202500280</div>
                    <div class="item-desc">重点批次：ZX-2025-10，抽检覆盖三仓</div>
                  </div>
                  <div class="item-date">2025-10-24</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">异常上报 #AR202509782</div>
                    <div class="item-desc">仓内摄像头遮挡，AI可见性降低</div>
                  </div>
                  <div class="item-date">2025-10-23</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">日常巡检 #RC202501056</div>
                    <div class="item-desc">重点检查：冷库门禁与温湿度传感器</div>
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

      <!-- 右侧资料卡 -->
      <aside class="sidebar">
        <div class="profile-card">
          <div class="profile-head">
            <img :src="user.avatar" alt="avatar" class="avatar" />
            <div class="info">
              <div class="name">{{ user.name }}</div>
              <div class="role">{{ user.role }}</div>
            </div>
          </div>
          <div class="kv">
            <div class="row"><span class="k">用户ID</span><span class="v">{{ user.id }}</span></div>
            <div class="row"><span class="k">联系电话</span><span class="v">{{ user.phone }}</span></div>
            <div class="row"><span class="k">所属单位</span><span class="v">{{ user.org }}</span></div>
            <div class="row"><span class="k">注册时间</span><span class="v">{{ user.registeredAt }}</span></div>
            <div class="row"><span class="k">状态</span><span class="v status"><i class="dot-online" />在线</span></div>
          </div>
          <div class="actions"><a href="#" @click.prevent="editProfile" class="edit">编辑信息</a></div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import UserHeader from '../component/UserHeader.vue'

export default {
  name: 'RegulatorUser',
  components: { UserHeader },
  data() {
    return {
      chart: null,
      user: {
        name: '王芳',
        role: '市级药监所',
        id: 'SH_YW_20230112',
        phone: '136****8756',
        org: '上海市人民路',
        registeredAt: '2020-02-20',
        avatar:
          'https://fastly.jsdelivr.net/gh/aleen42/PersonalWiki/images/emoji/others/woman.png',
      },
    }
  },
  mounted() {
    const el = this.$refs.donutRef
    if (!el) return
    this.chart = echarts.init(el)
    this.chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [
        {
          name: '告警类型',
          type: 'pie',
          radius: ['45%', '70%'],
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          labelLine: { show: false },
          data: [
            { value: 335, name: '温度异常' },
            { value: 310, name: '资质预警' },
            { value: 234, name: '台账异常' },
            { value: 135, name: '流通异常' },
            { value: 154, name: '其他' },
          ],
        },
      ],
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
    resize() { this.chart && this.chart.resize() },
    editProfile() {
      this.$message && this.$message.info('编辑信息功能待实现')
    },
  },
}
</script>

<style scoped>
.regulator-page { min-height: 100vh; background: #f5f7fa; }

.layout { max-width: 1300px; margin: 16px auto 24px; display: grid; grid-template-columns: 200px 1fr 320px; gap: 16px; }
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
.panel-head { display: flex; align-items: center; gap: 8px; }
.panel-head { justify-content: space-between; margin-bottom: 8px; }
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

.sidebar {
  align-self: start;
  position: sticky;
  top: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.profile-card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.06); padding: 16px; }
.profile-head { display: flex; align-items: center; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0; }
.avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.info .name { font-size: 18px; font-weight: 600; }
.info .role { font-size: 12px; color: #409eff; margin-top: 2px; }
.kv { padding-top: 10px; }
.row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #eee; }
.row:last-child { border-bottom: none; }
.k { color: #909399; font-size: 13px; }
.v { color: #303133; font-size: 14px; }
.status .dot-online { display: inline-block; width: 8px; height: 8px; background: #67c23a; border-radius: 50%; margin-right: 6px; }
.actions { margin-top: 10px; text-align: right; }
.edit { color: #409eff; text-decoration: none; font-size: 13px; }
.edit:hover { text-decoration: underline; }

@media (max-width: 1280px) {
  .layout { grid-template-columns: 200px 1fr; }
  .sidebar { grid-column: 1 / span 2; }
  .cards-row { grid-template-columns: 1fr; }
  .cards-row .full { grid-column: 1; }
}
</style>
