<template>
  <div class="unauth-page">
    <UserHeader :tags="['未认证用户']" />

    <!-- 主体区域 -->
    <div class="content">
      <div class="main-card">
        <div class="msg">
          <div class="line1">你还没进行企业认证， 无</div>
          <div class="line2">法使用个人信息功能</div>
        </div>
        <el-button type="primary" size="large" class="primary-btn" @click="goToAuth">
          立即认证
        </el-button>
      </div>

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
            <div class="row">
              <span class="k">用户ID</span>
              <span class="v">{{ user.id }}</span>
            </div>
            <div class="row">
              <span class="k">联系电话</span>
              <span class="v">{{ user.phone }}</span>
            </div>
            <div class="row">
              <span class="k">所属药店</span>
              <span class="v">{{ user.store }}</span>
            </div>
            <div class="row">
              <span class="k">注册时间</span>
              <span class="v">{{ user.registeredAt }}</span>
            </div>
            <div class="row">
              <span class="k">状态</span>
              <span class="v status"><i class="dot" />在线</span>
            </div>
          </div>
          <div class="actions">
            <a class="edit" href="#" @click.prevent="editProfile">编辑信息</a>
          </div>
        </div>
      </aside>
    </div>
  </div>
  
</template>

<script>
import UserHeader from '../component/UserHeader.vue'

export default {
  name: 'UnauthenticatedUser',
  components: { UserHeader },
  data() {
    return {
      today: this.formatToday(),
      user: {
        name: '张伟',
        role: '药店管理员',
        id: 'SH_YD_20230001',
        phone: '138****5678',
        store: '上海广和药店(浦东分店)',
        registeredAt: '2023-05-12',
        avatar:
          'https://fastly.jsdelivr.net/gh/aleen42/PersonalWiki/images/emoji/others/man.png',
      },
    }
  },
  methods: {
    formatToday() {
      const d = new Date()
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}年${m}月${day}日`
    },
    goToAuth() {
      this.$router.push({ name: 'enterprise-auth' })
    },
    editProfile() {
      // 这里可以打开资料编辑对话框或跳转到资料编辑页面
      this.$message && this.$message.info('编辑信息功能待实现')
    },
  },
}
</script>

<style scoped>
.unauth-page { min-height: 100vh; background: #f5f7fa; }

.content {
  max-width: 1200px;
  margin: 24px auto;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

.main-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  padding: 48px 24px 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 420px;
}
.msg { text-align: center; color: #1f2d3d; }
.msg .line1 { font-size: 44px; font-weight: 700; letter-spacing: 1px; }
.msg .line2 { font-size: 44px; font-weight: 700; margin-top: 10px; }
.primary-btn { margin-top: 28px; width: 320px; height: 44px; font-size: 16px; }

.sidebar {
  position: sticky;
  top: 24px;
  align-self: start;
}
.profile-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  padding: 16px 16px 12px;
}
.profile-head { display: flex; align-items: center; gap: 12px; padding: 8px 0 16px; border-bottom: 1px solid #f0f0f0; }
.avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.info .name { font-size: 18px; font-weight: 600; }
.info .role { font-size: 12px; color: #409eff; margin-top: 2px; }

.kv { padding-top: 10px; }
.row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #eee; }
.row:last-child { border-bottom: none; }
.k { color: #909399; font-size: 13px; }
.v { color: #303133; font-size: 14px; }
.status .dot { display: inline-block; width: 8px; height: 8px; background: #67c23a; border-radius: 50%; margin-right: 6px; }

.actions { margin-top: 10px; text-align: right; }
.edit { color: #409eff; text-decoration: none; font-size: 13px; }
.edit:hover { text-decoration: underline; }

@media (max-width: 992px) {
  .content { grid-template-columns: 1fr; }
}
</style>
