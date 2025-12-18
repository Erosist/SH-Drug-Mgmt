# 🛠️ 脚本工具目录

## 📋 目录说明

本目录包含用于手动测试和调试的API测试脚本。这些脚本主要用于开发过程中的手动验证，不同于 `tests/` 目录中的自动化单元测试。

## 📁 文件列表

### API 测试脚本
- **`api_test.ps1`** - PowerShell 版本的库存预警API测试脚本
- **`api_test_inventory_warning.py`** - Python 版本的库存预警功能手动测试
- **`api_test_supply.py`** - 供应信息API手动测试脚本
- **`api_test_amoxicillin.py`** - 阿莫西林胶囊下单测试
- **`api_test_current_order.py`** - 当前用户订单测试
- **`api_test_dev_users.py`** - 开发用户账户登录测试
- **`api_test_frontend_scenarios.py`** - 前端场景API测试
- **`api_test_no_tenant_user.py`** - 无租户关联用户测试
- **`api_test_order_flow.py`** - 订单流程测试
- **`api_test_token_info.py`** - JWT token和用户信息测试

### 校验/调试脚本（从根目录收拢迁移）
- **`verify_amap_implementation.py`** - 高德地图实现校验
- **`verify_gps_storage.py`** - GPS 存储校验
- **`verify_nearby_api.py`** - 附近搜索 API 校验
- **`quick_check.py`** - 快速连通性/基本功能检查
- **`see_data.py`** - 快速查看数据脚本
- **`simple_check.py`** - 轻量检查脚本
- **`simulate_order_creation.py`** - 模拟订单创建
- **`demo_dispatch.py`** - 配送演示脚本
- **`check_data.py`** - 数据一致性/完整性检查
- **`check_db_config.py`** - 数据库配置检查
- **`check_latest_gps.py`** - 最近 GPS 数据检查

## 🚀 使用方法

### PowerShell 脚本
```powershell
# 确保后端服务正在运行
cd backend
python run.py

# 在新的PowerShell窗口中运行测试
cd scripts
.\api_test.ps1
```

### Python 脚本
```bash
# 确保后端服务正在运行
cd backend
python run.py

# 在新的终端中运行API测试
python scripts/api_test_supply.py
python scripts/api_test_inventory_warning.py

# 运行校验/调试脚本示例
python scripts/verify_nearby_api.py
python scripts/quick_check.py
```

## ⚠️ 注意事项

1. **依赖项**: 这些脚本需要后端服务处于运行状态
2. **测试数据**: 可能需要先运行 `create_warning_test_data.py` 创建测试数据
3. **端口配置**: 默认测试 `http://127.0.0.1:5000`，如有需要请修改脚本中的BASE_URL

## 🔗 相关文件

- `../create_warning_test_data.py` - 创建测试数据
- `../tests/` - 自动化单元测试目录
- `../run.py` - 后端服务启动文件
 - `../tasks/` - 定时任务脚本目录（如 task_inventory_warning.py）