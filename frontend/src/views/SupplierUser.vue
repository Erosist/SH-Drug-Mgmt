<template>
  <div class="supplier-page">
    <UserHeader :tags="['供应商']" />

    <div class="layout">
      <!-- 左侧菜单 -->
      <aside class="sider">
        <div class="sider-title">供应商控制台</div>
        <ul class="menu">
          <li class="menu-item" :class="{active: activeMenu==='orders'}" @click="activeMenu='orders'">订单管理</li>
          <li class="menu-item" :class="{active: activeMenu==='supply'}" @click="activeMenu='supply'">供应信息管理</li>
          <li class="menu-item" :class="{active: activeMenu==='inventory'}" @click="activeMenu='inventory'">药品库存管理</li>
          <li class="menu-item" :class="{active: activeMenu==='logistics'}" @click="activeMenu='logistics'">物流管理</li>
          <li class="menu-item" :class="{active: activeMenu==='analysis'}" @click="activeMenu='analysis'">业绩分析</li>
        </ul>
      </aside>

      <!-- 主内容 -->
      <main class="main">
        <!-- 供应信息管理 -->
        <div v-if="activeMenu==='supply'">
          <SupplyInfoManagement />
        </div>

        <!-- 库存管理 -->
        <div v-else-if="activeMenu==='inventory'">
          <el-card class="panel">
            <div class="tabs">
              <div class="tab" :class="{active: activeTab==='list'}" @click="activeTab='list'">库存列表</div>
              <div class="tab" :class="{active: activeTab==='create'}" @click="activeTab='create'">新增库存</div>
            </div>

            <div v-if="activeTab==='list'" class="list-pane">
              <div class="toolbar">
                <el-input v-model="q" size="small" placeholder="搜索药品..." clearable class="search" />
                <el-select v-model="status" size="small" class="filter" placeholder="全部状态">
                  <el-option label="全部" value="" />
                  <el-option label="合格" value="ok" />
                  <el-option label="待检" value="pending" />
                </el-select>
                <el-select v-model="category" size="small" class="filter" placeholder="全部药品">
                  <el-option label="全部药品" value="" />
                  <el-option label="阿莫西林胶囊" value="amox" />
                  <el-option label="布洛芬片" value="ibu" />
                  <el-option label="连花清瘟胶囊" value="lhqw" />
                </el-select>
              </div>

              <el-table :data="filteredData" size="small" class="table" border>
                <el-table-column prop="name" label="商品名称" min-width="180" />
                <el-table-column prop="batch" label="批号" width="120" />
                <el-table-column prop="mfg" label="生产日期" width="120" />
                <el-table-column prop="exp" label="有效期" width="120" />
                <el-table-column prop="stock" label="库存数量" width="100" />
                <el-table-column label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag type="success" v-if="row.status==='ok'">合格</el-tag>
                    <el-tag type="warning" v-else>待检</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="140">
                  <template #default>
                    <el-link type="primary" :underline="false">编辑</el-link>
                    <el-divider direction="vertical" />
                    <el-link type="danger" :underline="false">删除</el-link>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div v-else class="create-pane">
              <el-form :model="form" label-width="86px" size="small" class="form">
                <el-form-item label="商品名称">
                  <el-input v-model="form.name" />
                </el-form-item>
                <el-form-item label="批号">
                  <el-input v-model="form.batch" />
                </el-form-item>
                <el-form-item label="生产日期">
                  <el-date-picker v-model="form.mfg" type="date" placeholder="选择日期" />
                </el-form-item>
                <el-form-item label="有效期">
                  <el-date-picker v-model="form.exp" type="date" placeholder="选择日期" />
                </el-form-item>
                <el-form-item label="库存数量">
                  <el-input-number v-model="form.stock" :min="0" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary">保存</el-button>
                  <el-button @click="activeTab='list'">取消</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </div>

        <!-- 其他功能模块 -->
        <div v-else>
          <el-card class="panel">
            <el-empty description="该功能模块正在开发中..." />
          </el-card>
        </div>
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
            <div class="row"><span class="k">所属单位</span><span class="v">{{ user.company }}</span></div>
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
import UserHeader from '../component/UserHeader.vue'
import SupplyInfoManagement from '../component/SupplyInfoManagement.vue'

export default {
  name: 'SupplierUser',
  components: { 
    UserHeader,
    SupplyInfoManagement
  },
  data() {
    return {
      activeMenu: 'supply',
      activeTab: 'list',
      q: '',
      status: '',
      category: '',
      form: { name: '', batch: '', mfg: '', exp: '', stock: 0 },
      rows: [
        { name: '阿莫西林胶囊', batch: '国药准字H20000001', mfg: '2023-05-01', exp: '2025-04-30', stock: '1,200盒', status: 'ok' },
        { name: '布洛芬片', batch: '国药准字H20000002', mfg: '2023-06-15', exp: '2025-06-14', stock: '850盒', status: 'ok' },
        { name: '连花清瘟胶囊', batch: '国药准字Z20000063', mfg: '2023-04-10', exp: '2025-04-09', stock: '320盒', status: 'pending' },
      ],
      user: {
        name: '王芳',
        role: '医药采购师',
        id: 'SH_YY_20230112',
        phone: '136****8765',
        company: '上海第一人民医院',
        registeredAt: '2023-02-20',
        avatar:
          'https://fastly.jsdelivr.net/gh/aleen42/PersonalWiki/images/emoji/others/woman.png',
      },
    }
  },
  computed: {
    filteredData() {
      return this.rows.filter(r =>
        (!this.q || r.name.includes(this.q)) &&
        (!this.status || r.status === this.status) &&
        (!this.category || (this.category==='amox' && r.name.includes('阿莫') || this.category==='ibu' && r.name.includes('布洛芬') || this.category==='lhqw' && r.name.includes('连花清瘟')))
      )
    },
  },
  methods: {
    editProfile() { this.$message && this.$message.info('编辑信息功能待实现') },
  },
}
</script>

<style scoped>
.supplier-page { min-height: 100vh; background: #f5f7fa; }

.layout { max-width: 1300px; margin: 16px auto 24px; display: grid; grid-template-columns: 200px 1fr 320px; gap: 16px; }
.sider { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.06); padding: 12px; }
.sider-title { padding: 10px 8px; color: #606266; font-weight: 600; }
.menu { list-style: none; margin: 0; padding: 8px; }
.menu-item { padding: 10px 12px; border-radius: 6px; cursor: pointer; color: #303133; }
.menu-item:hover { background: #f0f6ff; }
.menu-item.active { background: #ecf5ff; color: #409eff; font-weight: 600; }

.main { display: flex; flex-direction: column; gap: 16px; }
.panel { border-radius: 8px; }
.panel :deep(.el-card__body) { padding: 14px; }
.tabs { display: flex; gap: 12px; border-bottom: 1px solid #f0f0f0; margin-bottom: 12px; }
.tab { padding: 8px 12px; cursor: pointer; color: #606266; border-bottom: 2px solid transparent; }
.tab.active { color: #409eff; border-color: #409eff; font-weight: 600; }
.toolbar { display: flex; gap: 8px; margin-bottom: 10px; }
.search { width: 260px; }
.filter { width: 140px; }
.table { background: #fff; }

.create-pane .form { max-width: 520px; }

.sidebar {
  position: sticky;
  top: 16px;
  align-self: start;
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
}
</style>
