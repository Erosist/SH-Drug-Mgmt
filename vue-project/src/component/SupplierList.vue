<template>
  <div class="supplier-list-placeholder">
    <h4>供应信息列表</h4>
    <p>这里展示后端返回的供应信息列表（占位组件）。</p>
    <ul>
      <li v-for="(s, i) in demo" :key="i">{{ s.name }} - {{ s.spec }} - 库存：{{ s.stock }}</li>
    </ul>
    <p class="note">提示：当前为占位实现，后续可替换为真实接口渲染。</p>
  </div>
</template>

<script>
export default {
  name: 'SupplierList',
  setup() {
    const demo = [
      { name: '感冒灵颗粒', spec: '10袋/盒', stock: 120 },
      { name: '维生素C', spec: '100片/瓶', stock: 80 },
      { name: '头孢拉定', spec: '0.25g*24粒', stock: 60 },
    ]
    return { demo }
  }
}
</script>

<style scoped>
.supplier-list-placeholder { padding: 10px; background: #f8fafc; border: 1px dashed #cfe0ff; border-radius: 6px; }
.note { color: #888; font-size: 12px; margin-top: 6px; }
</style>
