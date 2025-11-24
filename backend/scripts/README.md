# 🛠️ 脚本工具目录

## 📋 目录说明

本目录包含用于手动测试和调试的API测试脚本。这些脚本主要用于开发过程中的手动验证，不同于 `tests/` 目录中的自动化单元测试。

## 📁 文件列表

### API 测试脚本
- **`api_test.ps1`** - PowerShell 版本的库存预警API测试脚本
- **`api_test_inventory_warning.py`** - Python 版本的库存预警功能手动测试
- **`api_test_supply.py`** - 供应信息API手动测试脚本

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
```

## ⚠️ 注意事项

1. **依赖项**: 这些脚本需要后端服务处于运行状态
2. **测试数据**: 可能需要先运行 `create_warning_test_data.py` 创建测试数据
3. **端口配置**: 默认测试 `http://127.0.0.1:5000`，如有需要请修改脚本中的BASE_URL

## 🔗 相关文件

- `../create_warning_test_data.py` - 创建测试数据
- `../tests/` - 自动化单元测试目录
- `../run.py` - 后端服务启动文件