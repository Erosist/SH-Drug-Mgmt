# 上海药品信息管理与查询平台 - 项目Wiki

欢迎来到上海药品信息管理与查询平台的项目Wiki！这里是项目的中央知识库，包含了项目的完整文档和学习资源。

## 🚀 快速导航

### 📖 首次访问？
1. **[项目首页](Home.md)** - 了解项目概况和快速导航
2. **[快速开始](Development/GettingStarted.md)** - 环境搭建和本地运行
3. **[项目介绍](ProjectOverview/Introduction.md)** - 详细的项目背景和目标
4. **[用户角色](ProjectOverview/UserRoles.md)** - 了解不同用户角色和权限

### 🛠️ 开发团队
- **[技术架构](TechnicalArchitecture/SystemArchitecture.md)** - 系统架构和技术栈
- **[数据库设计](TechnicalArchitecture/Database.md)** - 数据库结构和关系
- **[开发指南](Development/)** - 代码规范、Git工作流等
- **[API文档](Documentation/API/)** - 完整的API接口文档

### 👥 用户和管理员
- **[用户指南](Documentation/UserGuide/)** - 各角色的操作手册
- **[部署指南](Deployment/DeploymentGuide.md)** - 环境部署和配置
- **[故障排除](Deployment/Troubleshooting.md)** - 常见问题解决

## 📚 文档结构

```
Wiki/
├── 📋 项目概述
│   ├── 🏠 [首页](Home.md)
│   ├── 📖 [项目介绍](ProjectOverview/Introduction.md)
│   ├── 👥 [用户角色](ProjectOverview/UserRoles.md)
│   └── 📊 [系统范围](ProjectOverview/SystemScope.md)
├── 🏗️ 技术架构
│   ├── 🏢 [系统架构](TechnicalArchitecture/SystemArchitecture.md)
│   ├── 🖥️ [前端技术](TechnicalArchitecture/Frontend.md)
│   ├── ⚙️ [后端技术](TechnicalArchitecture/Backend.md)
│   ├── 🗄️ [数据库设计](TechnicalArchitecture/Database.md)
│   └── 🔒 [安全设计](TechnicalArchitecture/Security.md)
├── 🛠️ 开发指南
│   ├── 🚀 [快速开始](Development/GettingStarted.md)
│   ├── 📝 [代码规范](Development/CodingStandards.md)
│   ├── 🧪 [测试指南](Development/Testing.md)
│   ├── 🌿 [Git工作流](Development/GitWorkflow.md)
│   └── 📡 [API规范](Development/APIStandards.md)
├── 📚 文档中心
│   ├── 🔌 [API文档](Documentation/API/)
│   │   ├── 🔐 [认证接口](Documentation/API/Authentication.md)
│   │   ├── 👤 [用户管理](Documentation/API/UserManagement.md)
│   │   ├── 📦 [库存管理](Documentation/API/Inventory.md)
│   │   ├── 📋 [订单管理](Documentation/API/Orders.md)
│   │   └── 🚚 [物流管理](Documentation/API/Logistics.md)
│   ├── 🗄️ [数据库文档](Documentation/Database/)
│   │   ├── 📊 [数据库结构](Documentation/Database/Schema.md)
│   │   ├── 📋 [表结构说明](Documentation/Database/Tables.md)
│   │   └── 🔄 [数据库迁移](Documentation/Database/Migrations.md)
│   └── 👥 [用户指南](Documentation/UserGuide/)
│       ├── 🏪 [药店用户指南](Documentation/UserGuide/PharmacyGuide.md)
│       ├── 🏭 [供应商指南](Documentation/UserGuide/SupplierGuide.md)
│       ├── 👮 [监管用户指南](Documentation/UserGuide/RegulatorGuide.md)
│       └── 🚚 [物流用户指南](Documentation/UserGuide/LogisticsGuide.md)
├── 🚀 部署运维
│   ├── ⚙️ [环境配置](Deployment/EnvironmentSetup.md)
│   ├── 🚀 [部署指南](Deployment/DeploymentGuide.md)
│   ├── 📊 [监控配置](Deployment/Monitoring.md)
│   └── 🔧 [故障排除](Deployment/Troubleshooting.md)
└── 📊 项目管理
    ├── 📅 [迭代计划](ProjectManagement/SprintPlan.md)
    ├── 📋 [任务跟踪](ProjectManagement/TaskTracking.md)
    ├── 🤝 [团队协作](ProjectManagement/TeamCollaboration.md)
    └── 📝 [变更日志](ProjectManagement/ChangeLog.md)
```

## 🎯 核心功能模块

| 模块 | 功能描述 | 主要用户 | 文档链接 |
|------|----------|----------|----------|
| 👤 **账户信息管理** | 用户注册、企业认证、权限管理 | 所有用户 | [详细介绍](ProjectOverview/UserRoles.md) |
| 🏪 **企业库存管理** | 药品库存登记、更新、智能预警 | 药店、供应商 | [API文档](Documentation/API/Inventory.md) |
| 🤝 **B2B供求平台** | 供应信息发布、模拟下单、订单管理 | 药店、供应商 | [订单文档](Documentation/API/Orders.md) |
| 📊 **流通监管** | 流通数据上报、药品全生命周期追溯 | 物流、监管部门 | [物流文档](Documentation/API/Logistics.md) |
| 📈 **监管分析** | 多维度监管看板、合规分析报告 | 监管部门 | [监管指南](Documentation/UserGuide/RegulatorGuide.md) |
| 🚚 **智能调度** | 药品定位、最优路径规划、实时监控 | 物流、监管部门 | [调度文档](TechnicalArchitecture/Backend.md#智能调度) |

## 🚀 快速开始

### 开发者
```bash
# 1. 克隆项目
git clone https://github.com/your-org/SH-Drug-Mgmt.git
cd SH-Drug-Mgmt

# 2. 查看快速开始指南
cat Wiki/Development/GettingStarted.md

# 3. 启动开发环境
npm run dev
```

### 用户
1. 阅读[用户角色介绍](ProjectOverview/UserRoles.md)了解适合的角色
2. 查看[用户指南](Documentation/UserGuide/)学习操作流程
3. 联系管理员获取账户权限

### 管理员
1. 阅读[部署指南](Deployment/DeploymentGuide.md)搭建系统
2. 查看用户管理和权限配置相关文档
3. 配置监控和备份策略

## 📊 项目状态

### 📈 开发进度
- **总体进度：** 30%
- **核心模块：** 账户管理、库存管理开发中
- **当前Sprint：** 基础功能实现

### 🔧 技术栈
- **前端：** Vue 3 + Vite + TypeScript
- **后端：** Flask + SQLite + JWT认证
- **数据库：** PostgreSQL（生产环境）
- **地图服务：** 高德地图API

### 📅 最近更新
- **2024-10-25：** 完成Wiki架构设计和核心文档
- **2024-10-24：** 更新项目README和状态机图
- **2024-10-20：** 完成基础架构搭建

## 🤝 贡献指南

### 参与方式
1. **代码贡献：** Fork项目，创建功能分支，提交Pull Request
2. **文档改进：** 发现文档问题或不足，提交Issue或直接改进
3. **测试反馈：** 使用系统并反馈bug或改进建议
4. **知识分享：** 分享使用经验和最佳实践

### 文档贡献流程
1. 发现文档问题或需要补充的内容
2. 在GitHub上提交Issue描述问题
3. Fork项目并创建文档改进分支
4. 编写或修改文档，确保格式正确
5. 提交Pull Request等待审核

### 文档编写规范
- 使用Markdown格式
- 遵循项目文档结构
- 包含代码示例和截图
- 及时更新文档版本

## 📞 获取帮助

### 技术支持
- **项目仓库：** https://github.com/your-org/SH-Drug-Mgmt
- **问题反馈：** https://github.com/your-org/SH-Drug-Mgmt/issues
- **技术讨论：** https://github.com/your-org/SH-Drug-Mgmt/discussions

### 联系方式
- **项目负责人：** [待补充]
- **技术负责人：** [待补充]
- **文档维护：** [待补充]

### 学习资源
- [Vue.js官方文档](https://vuejs.org/)
- [Flask官方文档](https://flask.palletsprojects.com/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)
- [Redis文档](https://redis.io/documentation)

## 📄 许可证

本项目采用 [MIT License](../LICENSE) 开源协议。

---

## 🎉 致谢

感谢所有为项目做出贡献的团队成员和社区参与者！

**文档维护：** 开发团队
**最后更新：** 2024-10-25
**版本：** v1.0.0

---

> 💡 **提示：** 这是一个持续更新的文档库，如果您在使用过程中发现任何问题或有改进建议，请随时提交Issue或Pull Request。