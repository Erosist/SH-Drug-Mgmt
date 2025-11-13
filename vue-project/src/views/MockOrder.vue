<template>
  <div class="mock-order-placeholder">
    <h4>模拟下单</h4>
    <p>这里可以选择供应条目并创建模拟订单（占位组件）。</p>
    <div class="form-row">
      <input placeholder="药品名称" />
      <input type="number" min="1" placeholder="数量" />
      <button>创建订单</button>
    </div>
    <p class="note">提示：当前为占位实现，后续可替换为真实下单流程与后端接口。</p>
  </div>
</template>

<script>
export default { name: 'MockOrder' }
</script>

<style scoped>
.mock-order-placeholder { padding: 10px; background: #fff7e6; border: 1px dashed #ffd591; border-radius: 6px; }
.form-row { display: flex; gap: 8px; margin-top: 8px; }
.form-row input { border: 1px solid #ddd; border-radius: 4px; padding: 6px 8px; }
.form-row button { background: #1a73e8; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.note { color: #888; font-size: 12px; margin-top: 6px; }
</style>
