<template>
  <header class="topbar">
    <div class="left">
      <span class="logo">上海药品监管信息平台</span>
      <nav class="nav">
        <router-link class="nav-item" :class="{ active: isActive('home') }" :to="{ name: 'home' }">首页</router-link>
        <router-link class="nav-item" :class="{ active: isActive('inventory') }" :to="{ name: 'inventory' }">库存管理</router-link>
        <router-link class="nav-item" :class="{ active: isActive('b2b') }" :to="{ name: 'b2b' }">B2B供货平台</router-link>
        <router-link class="nav-item" :class="{ active: isActive('circulation') }" :to="{ name: 'circulation' }">流通监管</router-link>
        <router-link class="nav-item" :class="{ active: isActive('analysis') }" :to="{ name: 'analysis' }">监管分析</router-link>
        <router-link class="nav-item" :class="{ active: isActive('service') }" :to="{ name: 'service' }">智能调度</router-link>
      </nav>
    </div>
    <div class="right">
      <span v-for="(t, i) in tags" :key="i" class="tag">{{ t }}</span>
      <el-dropdown v-if="currentUser" trigger="click">
        <span class="user-entry">
          {{ currentUser.displayName || currentUser.username }}<i class="el-icon--right el-icon-arrow-down" />
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>账号：{{ currentUser.username }}</el-dropdown-item>
            <el-dropdown-item divided @click.native="doLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <router-link v-else class="login-link" :to="{ name: 'login' }">登录</router-link>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getCurrentUser, logout as doMockLogout } from '../mocks/auth'

const props = defineProps({
  tags: { type: Array, default: () => [] },
})

const router = useRouter()
const route = useRoute()
const currentUser = computed(() => getCurrentUser())

const isActive = (name) => route.name === name

const doLogout = () => {
  doMockLogout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.topbar {
  height: 56px;
  background: linear-gradient(90deg, #1976d2, #1e88e5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 0 20px;
}
.topbar .left { display: flex; align-items: center; gap: 16px; }
.logo { font-weight: 700; }
.nav { display: flex; gap: 14px; margin-left: 6px; }
.nav-item { color: #e3f2fd; text-decoration: none; font-size: 14px; }
.nav-item.active, .nav-item:hover { color: #fff; text-decoration: underline; }
.right { display: flex; align-items: center; gap: 8px; }
.tag { padding: 4px 10px; background: rgba(255,255,255,.2); border-radius: 14px; font-size: 12px; }
.user-entry { cursor: pointer; padding: 4px 10px; background: rgba(255,255,255,.2); border-radius: 14px; font-size: 12px; color: #fff; }
.login-link { color: #e3f2fd; text-decoration: none; font-size: 14px; }
.login-link:hover { color: #fff; text-decoration: underline; }
</style>