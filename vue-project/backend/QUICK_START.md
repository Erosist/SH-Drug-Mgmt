# 🚀 项目启动指南

## 快速开始

### 1. 安装依赖
```bash
cd vue-project/backend
pip install -r requirements.txt
pip install -r requirements-test.txt  # 测试依赖（可选）
```

### 2. 启动后端服务
```bash
python run.py
```
服务将在 http://localhost:5000 启动

### 3. 启动定时任务（可选）
在新的终端窗口：
```bash
cd vue-project/backend
python task_inventory_warning.py
```

### 4. 运行测试（开发时）
```bash
# 快速运行
python run_tests.py

# 或使用pytest
$env:PYTHONPATH = ".;$env:PYTHONPATH"
pytest
```

## 📁 重要文件说明

- `run.py` - 主启动脚本，包含数据库初始化
- `task_inventory_warning.py` - 库存预警定时任务
- `run_tests.py` - 测试运行脚本
- `tests/` - 所有测试代码
- `requirements.txt` - 生产依赖
- `requirements-test.txt` - 测试依赖

## 🔧 开发工作流

1. **日常开发**: 运行 `python run.py`
2. **测试**: 运行 `python run_tests.py`
3. **CI/CD**: GitLab会自动运行 `pytest`
4. **定时任务**: 生产环境运行 `python task_inventory_warning.py`

## ✅ 项目已清理

已删除的冗余文件：
- ✅ `test_admin_reset_password.py` - 已迁移到 `tests/`
- ✅ `test_supply_api.py` - 已迁移到 `tests/`  
- ✅ `test_inventory_warning.py` - 已迁移到 `tests/`
- ✅ `start_inventory_warning.py` - 功能重复，已删除

项目结构现在更加清晰和标准化！🎉
