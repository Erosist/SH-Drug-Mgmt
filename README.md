# 上海药品信息管理与查询平台 (SH-Drug-Mgmt)

一个连接药店、供应商、监管部门、物流公司的B2B药品信息管理平台，实现药品信息集中管理、流通追溯、库存监控与监管可视化。

## 📋 项目概述

**项目名称：** 上海药品信息管理与查询平台（Shanghai Drug Management Platform）
**架构类型：** B/S架构Web平台
**技术栈：** Vue3 + Vite + Flask + SQLite
**核心目标：** 实现药品全生命周期管理，支持B2B模拟交易与智能监管

## ✨ 主要功能

### 🔧 核心模块
- **🏪 企业库存管理** - 药品库存登记、更新、智能预警
- **🤝 B2B供求平台** - 供应信息发布、模拟下单、订单管理
- **📊 流通监管** - 流通数据上报、药品全生命周期追溯
- **📈 监管分析** - 多维度监管看板、合规分析报告
- **🚚 智能调度** - 药品定位、最优路径规划、实时运输监控

### 👥 用户角色
- **药店用户** - 库存管理、采购下单
- **供应商用户** - 供应信息管理、订单处理
- **监管用户** - 数据监控、合规分析
- **物流用户** - 运输状态上报、位置更新
- **系统管理员** - 用户权限管理

## 🛠 技术架构

### 前端
- **框架：** Vue 3 + Vite
- **兼容性：** Chrome 90+/Firefox 88+/Edge 90+
- **地图服务：** 高德地图API集成

### 后端
- **框架：** Flask (Python)
- **数据库：** SQLite (开发) / PostgreSQL (生产)
- **认证：** JWT
- **权限：** RBAC
- **实时通信：** WebSocket

### 数据库设计
- **12张核心表** - 支持用户、药品、库存、订单、物流等完整业务流程
- **租户数据隔离** - 严格的多租户数据安全隔离
- **事务一致性** - 库存与流通记录的事务保障

## 📁 项目结构

```
SH-Drug-Mgmt/
├── CLAUDE.md                    # 项目开发参考手册
├── README.md                    # 项目说明文档
├── Docs/                        # 项目文档
│   ├── LearningMaterials/       # 团队学习资料
│   └── RequirementAnalysis/     # 需求分析文档
├── frontend/                    # Vue3前端项目
│   ├── src/
│   │   ├── components/          # Vue组件
│   │   ├── views/              # 页面视图
│   │   ├── router/             # 路由配置
│   │   └── api/                # API接口
│   ├── package.json
│   └── vite.config.js
├── backend/                     # Flask后端项目
│   ├── app.py                  # 应用入口
│   ├── models/                 # 数据模型
│   ├── routes/                 # 路由处理
│   ├── services/               # 业务逻辑
│   └── requirements.txt
├── database/                    # 数据库相关
│   ├── schema.sql              # 数据库结构
│   └── migrations/             # 数据库迁移
└── tests/                      # 测试文件
    ├── unit/                   # 单元测试
    └── integration/            # 集成测试
```

## 🚀 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+
- Git

### 安装与运行

1. **克隆项目**
   ```bash
   git clone https://gitlab.com/tj-cs-swe/CS10102302-2025/group4/shanghaidrugmanagementplatform_1.git
   cd SH-Drug-Mgmt
   ```

2. **前端环境**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **后端环境**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

4. **数据库初始化**
   ```bash
   python manage.py init-db
   ```


## 🔧 开发规范

### API设计
- RESTful API风格
- JSON数据格式
- JWT认证机制
- 统一错误处理

### 代码规范
- 前端：Vue3 Composition API + TypeScript
- 后端：Python PEP8规范
- 数据库：外键约束 + 索引优化

### 安全要求
- 密码加密存储
- 租户数据严格隔离
- API访问权限控制
- 操作日志记录

## 📊 性能指标

- **页面加载时间** ≤ 3秒
- **API响应时间** ≤ 2秒
- **并发用户数** ≥ 10用户
- **数据容量** 支持5000+流通记录
- **系统可用性** ≥ 95%

## 🚨 项目约束

### 功能边界
- ❌ 不支持真实在线支付
- ❌ 不与国家药监局系统直连
- ❌ 不支持B2C功能（仅B2B）

### 业务约束
- 所有交易均为模拟性质
- 不可用于真实商业交易
- 监管数据仅供分析使用

## 🤝 团队协作

### Git工作流
- **分支策略：** GitFlow
- **代码审查：** 所有PR必须经过审查
- **提交规范：** 遵循Conventional Commits

### Issue管理
- **任务分配：** 基于GitLab Issues
- **进度跟踪：** Milestone管理
- **文档同步：** Wiki文档更新

## 📈 开发计划

### 第一阶段 (高优先级)
- [x] 项目文档完善
- [ ] 用户认证与权限系统
- [ ] 基础库存管理功能
- [ ] B2B供求平台基础功能

### 第二阶段 (中优先级)
- [ ] 流通监管系统
- [ ] 数据分析看板
- [ ] 实时位置监控

### 第三阶段 (低优先级)
- [ ] 智能路径优化
- [ ] 高级数据分析
- [ ] 系统性能优化

