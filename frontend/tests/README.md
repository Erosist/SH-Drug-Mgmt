# 前端测试文档

## 测试框架
- **Vitest**: 现代化的测试框架，基于Vite
- **Vue Test Utils**: Vue组件测试工具
- **Happy DOM**: 轻量级DOM环境

## 测试文件结构
```
frontend/tests/
├── auth.test.js          # 认证功能测试
├── inventory.test.js     # 库存管理测试
├── orders.test.js        # 订单管理测试
├── setup.js             # 测试环境配置
└── test-utils.js        # 测试工具函数
```

## 运行测试

### 运行所有测试
```bash
cd frontend
npm test
```

### 运行特定测试文件
```bash
npm test auth.test.js
npm test inventory.test.js
npm test orders.test.js
```

### 监听模式运行测试
```bash
npm test -- --watch
```

### 生成测试覆盖率报告
```bash
npm run test:coverage
```

## 测试覆盖的功能

### 认证测试 (auth.test.js)
- ✅ 用户登录成功/失败
- ✅ 用户注册功能
- ✅ Token验证
- ✅ localStorage存储

### 库存管理测试 (inventory.test.js)
- ✅ 获取库存列表
- ✅ 添加库存项目
- ✅ 更新库存项目
- ✅ 删除库存项目
- ✅ 库存搜索功能
- ✅ 库存预警 (低库存、即将过期)
- ✅ 库存筛选

### 订单管理测试 (orders.test.js)
- ✅ 创建订单
- ✅ 订单状态更新
- ✅ 订单查询和分页
- ✅ 订单搜索
- ✅ 订单统计分析
- ✅ 订单历史记录

## Mock策略
- 使用 `vi.mock('axios')` Mock所有HTTP请求
- 每个测试前重置Mock状态
- 模拟真实的API响应数据

## 测试最佳实践
1. **命名规范**: 描述性的测试用例名称
2. **隔离性**: 每个测试相互独立
3. **Mock外部依赖**: API调用、localStorage等
4. **断言明确**: 验证预期的行为和结果
5. **测试覆盖**: 覆盖正常情况和异常情况

## 添加新测试
1. 在 `tests/` 目录下创建新的测试文件
2. 按照现有模式编写测试
3. 使用适当的Mock策略
4. 运行测试确保通过
