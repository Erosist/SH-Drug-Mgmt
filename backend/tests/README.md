# 后端测试文档

## 测试框架
- **pytest**: Python标准测试框架
- **Flask-Testing**: Flask应用测试扩展
- **SQLite内存数据库**: 快速的测试数据库

## 测试文件结构
```
backend/tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # pytest配置和fixtures
├── base.py                        # 测试基类
├── test_app_config.py            # 应用配置测试
├── test_auth.py                   # 认证功能测试
├── test_inventory_management.py   # 库存管理测试
├── test_order_management.py       # 订单管理测试
├── test_enterprise.py             # 企业管理测试
├── test_supply.py                 # 供应管理测试
└── test_integration.py            # 集成测试
```

## 运行测试

### 运行所有测试
```bash
cd backend
python -m pytest -v
```

### 运行特定测试文件
```bash
python -m pytest -v tests/test_auth.py
python -m pytest -v tests/test_inventory_management.py
python -m pytest -v tests/test_order_management.py
```

### 运行特定测试函数
```bash
python -m pytest -v tests/test_auth.py::TestAuthAPI::test_login_success
```

### 生成测试覆盖率报告
```bash
python -m pytest --cov=. --cov-report=html
```

### 运行测试并显示详细输出
```bash
python -m pytest -v -s
```

## 测试环境配置
- **FLASK_ENV**: 自动设置为 'testing'
- **数据库**: 使用SQLite内存数据库 `sqlite:///:memory:`
- **JWT密钥**: 使用测试专用密钥
- **调试模式**: 启用以便调试

## 测试覆盖的功能

### 应用配置测试 (test_app_config.py)
- ✅ 开发/生产/测试环境配置
- ✅ 环境变量加载
- ✅ 数据库路径配置
- ✅ 应用创建和蓝图注册
- ✅ CORS配置

### 认证功能测试 (test_auth.py)
- ✅ 用户注册/登录
- ✅ JWT Token生成和验证
- ✅ 权限检查
- ✅ 密码加密验证

### 库存管理测试 (test_inventory_management.py)
- ✅ CRUD操作 (增删改查)
- ✅ 库存搜索功能
- ✅ 低库存预警
- ✅ 过期预警
- ✅ 租户权限隔离

### 订单管理测试 (test_order_management.py)
- ✅ 订单创建和验证
- ✅ 订单状态管理
- ✅ 订单查询和搜索
- ✅ 订单统计分析
- ✅ 完整订单生命周期

## Fixtures说明
- **app**: 测试应用实例
- **client**: 测试客户端
- **auth_headers**: 认证头信息
- **test_data**: 测试数据创建

## 数据库测试策略
1. **每个测试类使用独立的数据库实例**
2. **测试前创建表结构**
3. **测试后清理数据库**
4. **使用事务回滚保证数据隔离**

## Mock策略
- **外部API调用**: 使用Mock模拟
- **邮件服务**: Mock邮件发送
- **文件操作**: Mock文件系统操作

## 测试最佳实践
1. **AAA模式**: Arrange-Act-Assert
2. **独立性**: 每个测试相互独立
3. **可重复性**: 多次运行结果一致
4. **快速执行**: 使用内存数据库
5. **全面覆盖**: 正常情况和异常情况

## 添加新测试
1. 在 `tests/` 目录下创建测试文件
2. 继承现有的测试基类或使用fixtures
3. 按照AAA模式编写测试
4. 确保测试数据清理
5. 运行测试验证功能
