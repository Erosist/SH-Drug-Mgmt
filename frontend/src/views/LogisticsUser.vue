<template>
  <div class="logistics-page">
    <UserHeader :tags="['物流管理员']" />

    <div class="layout">
      <!-- 左侧菜单 -->
      <aside class="sider">
        <div class="sider-title">管理目录</div>
        <ul class="menu">
          <li class="menu-item active">运输任务概览</li>
          <li class="menu-item">在途监控</li>
          <li class="menu-item">冷链设备</li>
          <li class="menu-item">路线规划</li>
        </ul>
      </aside>

      <!-- 主内容 -->
      <main class="main">
        <section class="cards-row">
          <el-card class="panel">
            <div class="panel-head">
              <span>智能调度中心</span>
              <el-button size="small" type="primary">新建任务</el-button>
            </div>
            <div class="kpis">
              <div class="kpi">
                <div class="kpi-title">待分配任务</div>
                <div class="kpi-value">3</div>
              </div>
              <div class="kpi">
                <div class="kpi-title">运输中任务</div>
                <div class="kpi-value">12</div>
              </div>
              <div class="kpi">
                <div class="kpi-title">准时率</div>
                <div class="kpi-value">98%</div>
              </div>
            </div>
            <div class="table-mini">
              <div class="table-row table-head">
                <span>任务编号</span><span>状态</span><span>车辆</span><span>司机</span><span>操作</span>
              </div>
              <div class="table-row">
                <span>YD-2025-1001</span><span><em class="dot dot-info"></em>在途</span><span>沪A·12345</span><span>刘强</span><a href="#">轨迹</a>
              </div>
              <div class="table-row">
                <span>YD-2025-0996</span><span><em class="dot dot-success"></em>已送达</span><span>沪B·53210</span><span>王凯</span><a href="#">详情</a>
              </div>
              <div class="table-row">
                <span>YD-2025-0992</span><span><em class="dot dot-warn"></em>异常</span><span>沪C·98761</span><span>赵云</span><a href="#">处理</a>
              </div>
            </div>
          </el-card>

          <el-card class="panel">
            <div class="panel-head">
              <span>运力与统计</span>
              <div class="panel-actions">
                <el-button size="small" plain>导出</el-button>
                <el-button size="small" type="primary">同步</el-button>
              </div>
            </div>
            <div class="stats-tiles">
              <div class="tile"><div class="num">68</div><div class="label">车辆总数</div></div>
              <div class="tile"><div class="num">24</div><div class="label">在途车辆</div></div>
              <div class="tile"><div class="num">18</div><div class="label">冷链车</div></div>
              <div class="tile"><div class="num">9</div><div class="label">异常告警</div></div>
            </div>
          </el-card>
        </section>

        <section class="cards-row">
          <el-card class="panel full">
            <div class="panel-head">
              <span>货物与温控</span>
              <el-input class="search" placeholder="输入运单号/车牌号" size="small" clearable />
              <el-button size="small" type="primary">查询</el-button>
            </div>
            <div class="grid2">
              <div class="list">
                <div class="list-item">
                  <div>
                    <div class="item-title">运单号 #YW202510016</div>
                    <div class="item-desc">温度恢复正常，冷机已重启</div>
                  </div>
                  <div class="item-date">2025-10-26</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">运单号 #YW202510028</div>
                    <div class="item-desc">预计晚到 15 分钟，原因：道路拥堵</div>
                  </div>
                  <div class="item-date">2025-10-24</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">车辆巡检 #CAR202509782</div>
                    <div class="item-desc">冷链车 A 类保养完成</div>
                  </div>
                  <div class="item-date">2025-10-23</div>
                </div>
                <div class="list-item">
                  <div>
                    <div class="item-title">运单号 #YW202501056</div>
                    <div class="item-desc">到达签收，温控全程合规</div>
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
            <div class="row"><span class="k">所属公司</span><span class="v">{{ user.company }}</span></div>
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
  name: 'LogisticsUser',
  components: { UserHeader },
  data() {
    return {
      chart: null,
      user: {
        name: '李强',
        role: '运输部管理员',
        id: 'SH_LG_20220045',
        phone: '159****1234',
        company: '上海药通医药配送公司',
        registeredAt: '2022-08-15',
        avatar:
          'https://fastly.jsdelivr.net/gh/aleen42/PersonalWiki/images/emoji/others/man.png',
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
          name: '运力分布',
          type: 'pie',
          radius: ['45%', '70%'],
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          labelLine: { show: false },
          data: [
            { value: 26, name: '在途' },
            { value: 18, name: '空闲' },
            { value: 12, name: '冷链维护' },
            { value: 9, name: '异常处理' },
            { value: 3, name: '其他' },
          ],
        },
      ],
    })
    window.addEventListener('resize', this.resize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resize)
    if (this.chart) { this.chart.dispose(); this.chart = null }
  },
  methods: {
    resize() { this.chart && this.chart.resize() },
    editProfile() { this.$message && this.$message.info('编辑信息功能待实现') },
  },
}
</script>

<style scoped>
.logistics-page { min-height: 100vh; background: #f5f7fa; }

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
.panel-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 8px 0 12px; }
.kpi { background: #f7f9fc; border-radius: 8px; padding: 10px; text-align: center; }
.kpi-title { color: #909399; font-size: 13px; }
.kpi-value { font-size: 24px; font-weight: 700; color: #1f2d3d; }

.table-mini { margin-top: 4px; border: 1px solid #f0f0f0; border-radius: 8px; overflow: hidden; }
.table-row { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr .8fr; gap: 8px; padding: 10px 12px; border-top: 1px solid #f5f5f5; align-items: center; }
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

.sidebar { position: sticky; top: 72px; display: flex; flex-direction: column; gap: 16px; }
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
