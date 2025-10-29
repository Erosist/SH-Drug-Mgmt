<template>
  <div class="login-page">
    <h1>用户登录</h1>
    <form @submit.prevent="handleLogin">
      <div>
        <label>用户名</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>密码</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">登录</button>
    </form>
    <p>没有账号？<router-link to="/register">注册</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const router = useRouter()

function handleLogin() {
  if (username.value && password.value) {
    alert(`登录成功: ${username.value}`)
    router.push('/dashboard')
  } else {
    alert('请输入用户名和密码')
  }
}
</script>

<style scoped>
/* 简单样式，可根据需求修改 */
.login-page { max-width: 400px; margin: 100px auto; padding: 2rem; border: 1px solid #ccc; border-radius: 8px; }
input { width: 100%; padding: 0.5rem; margin-bottom: 1rem; }
button { width: 100%; padding: 0.6rem; background-color: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:hover { background-color: #66b1ff; }
</style>
