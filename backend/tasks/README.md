# ⏱️ 定时任务（Tasks）

本目录用于存放后台定时任务脚本（原 `backend/` 根目录的 `task_*.py` 已迁移至此）。

## 包含脚本
- `task_inventory_warning.py` — 库存预警定时任务
- `task_expire_orders.py` — 订单过期清理任务

## 使用方式
在项目根或 `backend/` 目录下执行：

```cmd
cd backend
python tasks/task_inventory_warning.py
```

## 约定
- 所有定时任务脚本以 `task_` 前缀命名
- 任务脚本应可独立运行，避免对交互式输入的依赖
- 如需在生产中通过系统服务（如 systemd）运行，请在仓库的部署文档中更新路径引用
