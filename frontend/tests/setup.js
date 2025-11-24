import { config } from '@vue/test-utils'

// 全局测试配置
config.global.stubs = {
  // 存根化路由组件
  'router-link': true,
  'router-view': true
}

// 模拟 Element Plus 组件（如果需要）
config.global.stubs['el-button'] = true
config.global.stubs['el-input'] = true
config.global.stubs['el-table'] = true
config.global.stubs['el-dialog'] = true

// 设置全局属性
config.global.mocks = {
  $t: (key) => key // 模拟国际化函数
}
