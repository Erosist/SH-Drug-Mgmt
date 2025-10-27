<template>
    <div class="home">
      <h1>首页</h1>
      <p>欢迎来到我们的应用</p>
      <!-- 在这里添加首页内容 -->
      <button><router-link to="/login">跳转到登录页面</router-link></button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'Home',
    data() {
      return {
        // 数据定义
      }
    },
    mounted() {
      // 组件挂载后的逻辑
    },
    methods: {
      // 方法定义
    }
  }
  </script>
  
  <style scoped>
  .home {
    padding: 20px;
    text-align: center;
  }
  
  h1 {
    color: #2c3e50;
    margin-bottom: 20px;
  }
  </style>