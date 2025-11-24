# 🛠️ 调试工具目录

## 📋 目录说明

本目录包含用于项目调试、问题诊断和开发过程中的辅助工具。这些工具主要用于开发阶段的问题排查和数据分析。

## 📁 文件列表

### 🐛 调试脚本
- **`debug_detailed.py`** - 详细调试脚本
- **`debug_permissions.py`** - 权限调试脚本  
- **`debug_order.py`** - 订单相关问题调试
- **`debug-api.html`** - API调试的HTML界面

### 🔍 分析工具
- **`analyze_db.py`** - 数据库分析工具
- **`check_supply_data.py`** - 供应数据检查脚本
- **`verify_token.py`** - JWT token验证工具

### 🔧 修复脚本
- **`fix_validation.py`** - 数据验证修复脚本

## 🚀 使用方法

### 运行调试脚本
```bash
# 进入backend目录
cd backend

# 运行调试脚本
python ../debug-tools/debug_order.py
python ../debug-tools/analyze_db.py
python ../debug-tools/verify_token.py
```

### 数据检查
```bash
# 检查供应数据
python ../debug-tools/check_supply_data.py

# 分析数据库
python ../debug-tools/analyze_db.py
```

### API调试
- 在浏览器中打开 `debug-api.html` 进行API测试

## ⚠️ 注意事项

1. **开发环境专用**: 这些工具仅用于开发和测试环境
2. **数据安全**: 不要在生产环境中运行这些脚本
3. **依赖项**: 确保backend服务已启动（如需要）
4. **权限**: 某些脚本可能需要数据库写权限

## 🔗 相关目录

- `../backend/tools/` - 开发工具和数据生成脚本
- `../backend/scripts/` - API手动测试脚本
- `../backend/tests/` - 自动化单元测试
