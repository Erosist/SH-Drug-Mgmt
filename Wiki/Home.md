# 上海药品信息管理与查询平台 - 项目Wiki

> 🏥 **项目愿景：** 构建连接药店、供应商、监管部门、物流公司的数字化药品管理生态系统，实现药品全生命周期透明化管理和智能化监管。

## 📋 项目快速导航

### 🚀 快速开始
- **[项目介绍](ProjectOverview/Introduction.md)** - 了解项目背景和目标
- **[快速开始](Development/GettingStarted.md)** - 环境搭建和运行指南
- **[用户角色](ProjectOverview/UserRoles.md)** - 了解不同用户角色和权限

### 🏗️ 技术文档
- **[系统架构](TechnicalArchitecture/SystemArchitecture.md)** - 整体技术架构设计
- **[数据库设计](Documentation/Database/Schema.md)** - 数据库表结构和关系
- **[API文档](Documentation/API/)** - 完整的API接口文档
- **[前端开发](TechnicalArchitecture/Frontend.md)** - Vue3前端技术栈

### 👥 用户指南
- **[药店用户指南](Documentation/UserGuide/PharmacyGuide.md)** - 药店用户操作手册
- **[供应商指南](Documentation/UserGuide/SupplierGuide.md)** - 供应商操作手册
- **[监管用户指南](Documentation/UserGuide/RegulatorGuide.md)** - 监管部门操作手册
- **[物流用户指南](Documentation/UserGuide/LogisticsGuide.md)** - 物流公司操作手册

### 🛠️ 开发文档
- **[代码规范](Development/CodingStandards.md)** - 前后端代码规范
- **[测试指南](Development/Testing.md)** - 单元测试和集成测试
- **[Git工作流](Development/GitWorkflow.md)** - 团队协作流程
- **[部署指南](Deployment/DeploymentGuide.md)** - 生产环境部署

## 🎯 核心功能模块

| 模块 | 功能描述 | 主要用户 | 文档链接 |
|------|----------|----------|----------|
| 👤 **账户信息管理** | 用户注册、企业认证、权限管理 | 所有用户 | [详细介绍](ProjectOverview/UserRoles.md) |
| 🏪 **企业库存管理** | 药品库存登记、更新、智能预警 | 药店、供应商 | [API文档](Documentation/API/Inventory.md) |
| 🤝 **B2B供求平台** | 供应信息发布、模拟下单、订单管理 | 药店、供应商 | [订单文档](Documentation/API/Orders.md) |
| 📊 **流通监管** | 流通数据上报、药品全生命周期追溯 | 物流、监管部门 | [物流文档](Documentation/API/Logistics.md) |
| 📈 **监管分析** | 多维度监管看板、合规分析报告 | 监管部门 | [监管指南](Documentation/UserGuide/RegulatorGuide.md) |
| 🚚 **智能调度** | 药品定位、最优路径规划、实时监控 | 物流、监管部门 | [调度文档](TechnicalArchitecture/Backend.md#智能调度) |

## 📊 项目状态

### 🚧 开发进度
- **总体进度：** 30%
- **核心模块：** 账户管理、库存管理开发中
- **当前阶段：** 基础架构搭建和核心功能开发

### 🏗️ 技术栈
- **前端：** Vue 3 + Vite + TypeScript
- **后端：** Flask + SQLite + JWT认证
- **地图服务：** 高德地图API
- **实时通信：** WebSocket

### 📈 性能指标
- **页面加载：** ≤ 3秒
- **API响应：** ≤ 2秒
- **并发支持：** 10+用户
- **数据容量：** 5000+流通记录

## 🔧 快速操作

### 开发者常用链接
- [本地开发环境搭建](Development/GettingStarted.md#本地开发)
- [API接口测试](Documentation/API/Authentication.md#接口测试)
- [数据库迁移](Documentation/Database/Migrations.md)
- [代码提交规范](Development/GitWorkflow.md#提交规范)

### 管理员常用链接
- [用户权限管理](ProjectOverview/UserRoles.md#权限管理)
- [企业认证审核](ProjectOverview/UserRoles.md#企业认证)
- [系统监控配置](Deployment/Monitoring.md)
- [故障排除指南](Deployment/Troubleshooting.md)

## 📅 最近更新

### 2024-10-25
- ✅ 完成项目Wiki架构设计
- ✅ 创建基础文档模板
- 🔄 正在完善API文档结构

### 2024-10-24
- ✅ 更新项目README文档
- ✅ 完成状态机图设计
- 🔄 订单管理系统开发中

## 🤝 团队协作

### 📋 当前Sprint任务
- [ ] 用户认证系统完善
- [ ] 库存管理API开发
- [ ] 前端登录注册页面
- [ ] 数据库索引优化

### 📞 联系方式
- **项目负责人：** [待补充]
- **技术负责人：** [待补充]
- **产品负责人：** [待补充]

### 📚 相关文档
- [项目需求文档](../Docs/RequirementAnalysis/)
- [团队学习资料](../Docs/LearningMaterials/)
- [CLAUDE开发手册](../CLAUDE.md)

---

> 💡 **提示：** 这个Wiki是项目的中央知识库，所有团队成员都应该熟悉如何使用和贡献内容。如有疑问或建议，请在项目Issues中提出。

**最后更新：** 2024-10-25
**维护人员：** 开发团队