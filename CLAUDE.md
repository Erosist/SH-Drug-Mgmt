# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 项目概述

**项目名称：** 上海药品信息管理与查询平台（SH-Drug-Mgmt）

**架构类型：** B/S架构Web平台

**核心目标：** 连接药店、供应商、监管部门、物流公司，实现药品信息集中管理、流通追溯、库存监控、B2B模拟交易与监管可视化

# 技术栈

## 前端

- **框架：** Vue 3 + Vite
- **要求：** 兼容 Chrome 90+/Firefox 88+/Edge 90+
- **语言：** 简体中文

## 后端

- **框架：** Flask
- **数据库：** SQLite
- **认证：** JWT
- **权限控制：** RBAC

## 外部服务

- **地图服务：** 高德地图API
- **实时通信：** WebSocket（位置推送）

# 系统架构

## 核心模块
1. **账户信息管理子系统** - 用户注册、企业认证、权限管理
2. **企业库存管理子系统** - 药品库存登记、更新、预警
3. **B2B供求平台子系统** - 供应信息发布、查看、模拟下单
4. **流通监管子系统** - 流通数据上报、全生命周期追溯
5. **监管分析子系统** - 监管看板、合规分析报告
6. **智能调度子系统** - 药品定位、路径规划、实时监控

## 数据库设计
**15张核心表：**
```
数据库表结构
├── 用户权限类 (5张)
│   ├── users                # 用户基本信息
│   ├── roles                # 角色定义
│   ├── permissions          # 权限定义
│   ├── user_roles           # 用户角色关联
│   └── role_permissions     # 角色权限关联
├── 企业认证类 (2张)
│   ├── tenants              # 企业信息
│   └── enterprise_certifications  # 企业认证
├── 业务核心类 (6张)
│   ├── drugs                # 药品信息
│   ├── inventory_items      # 库存项
│   ├── supply_info          # 供应信息
│   ├── orders               # 订单（头）
│   ├── order_items          # 订单明细
│   ├── circulation_records  # 流通记录
│   └── logistics_records    # 物流记录
├── 系统管理类 (2张)
│   ├── operation_logs       # 操作日志
│   └── password_reset_tokens # 密码重置令牌
```

# 用户角色与权限

## 用户类型
1. **未认证用户（UNAUTHENTICATED）** - 新注册用户默认角色，仅可查看公开信息、提交企业认证申请、修改个人资料
2. **药店用户（PHARMACY）** - 库存管理、下单采购、查看供应商信息
3. **供应商用户（SUPPLIER）** - 库存管理、发布供应信息、处理订单
4. **监管用户（REGULATOR）** - 数据监控、合规分析、查看所有数据
5. **物流用户（LOGISTICS）** - 运输状态上报、路径规划、位置更新
6. **系统管理员（ADMIN）** - 用户管理、权限配置、企业认证审核、系统维护

## 关键约束
- **租户数据隔离：** 所有数据访问必须基于租户ID校验
- **密码策略：** 最少8位，必须包含字母和数字
- **权限控制：** 基于RBAC的细粒度权限管理

# 核心功能需求

## :busts_in_silhouette: 账号信息管理子系统

### 1.1 用户注册

#### 功能描述

新用户通过填写基本信息完成账号注册，获得系统的基础访问权限。

#### 功能需求

**FR-1.1.1 注册信息填写**

- 必填字段：用户名、密码、手机号或邮箱
- 选填字段：真实姓名、联系地址
- 用户名唯一性实时校验
- 密码强度要求：至少8位，包含字母和数字
- 前端密码强度提示，后端严格校验

**FR-1.1.2 注册流程控制**

- 注册成功后用户默认角色为"未认证用户"
- 可查看公开信息和修改个人资料
- 需要完成企业认证才能获得业务角色权限
- 注册成功后可选择立即登录或跳转企业认证页面

#### 验收标准

* 用户填写完整信息后可以成功注册
* 系统检查用户名唯一性
* 密码符合强度要求
* 注册成功后自动登录或跳转到登录页面
* 新用户默认角色为"未认证用户"

### 1.2 企业信息认证

#### 功能描述

企业用户根据业务类型提交相应的资质信息进行认证，以获得对应角色的系统权限。

#### 功能需求

**FR-1.2.1 角色认证差异化要求**

- **药店用户(PHARMACY)**：《药品经营许可证》、《营业执照》
- **供应商用户(SUPPLIER)**：《药品生产/经营许可证》(批发)、《营业执照》
- **物流用户(LOGISTICS)**：《道路运输经营许可证》、《营业执照》
- **监管用户(REGULATOR)**：由系统管理员直接创建，无需认证

**FR-1.2.2 认证文件上传**

- 支持JPG、PNG、PDF格式
- 单个文件大小不超过5MB
- 建议分辨率300dpi以上，确保文字清晰
- 文件安全存储，符合隐私保护要求

**FR-1.2.3 认证审核流程**

- 提交认证后用户状态变为"审核中"，功能受限
- 管理员在3个工作日内完成审核
- 审核通过后用户获得对应角色权限
- 认证失败显示具体原因并可重新提交（最多3次）

#### 验收标准

* 用户注册时根据选择的角色类型显示对应的认证要求
* 药店/供应商/物流用户必须上传对应的资质证书
* 提交认证后用户状态变为"审核中"
* 管理员在3个工作日内完成审核
* 认证通过后用户获得对应角色权限，功能解锁
* 认证失败显示具体原因并可重新提交

### 1.3 密码管理

#### 功能描述

用户可以修改登录密码和找回忘记的密码，确保账号安全。

#### 功能需求

**FR-1.3.1 密码修改**

- 用户登录后可以修改密码
- 必须验证旧密码
- 新密码符合安全策略要求（至少8位，包含字母和数字）
- 密码修改后需要重新登录

**FR-1.3.2 密码找回**

- 用户可根据注册时绑定的手机或邮箱选择找回方式
- 系统发送验证码到用户手机或邮箱
- 验证码有效期为10分钟
- 验证成功后可设置新密码

#### 验收标准

* 用户登录后可以修改密码，需要验证旧密码
* 新密码符合安全策略要求
* 忘记密码时可以通过手机或邮箱收到验证码
* 验证码的有效期为10分钟
* 密码修改后需要重新登录

### 1.4 用户信息管理

#### 功能描述

系统管理员可以查看和管理所有用户账号，维护系统的用户数据安全和完整性。

#### 功能需求

**FR-1.4.1 用户列表展示**

- 列表显示：用户名、真实姓名、所属企业、用户角色、账号状态（正常/禁用）、最后登录时间、注册时间
- 点击详情查看完整信息，包括联系方式
- 支持分页显示，每页20条记录

**FR-1.4.2 搜索和筛选功能**

- 支持按用户名、真实姓名、企业名称的关键词搜索
- 筛选条件：用户角色、账号状态、企业类型、注册时间范围

**FR-1.4.3 用户状态管理**

- 管理员可以禁用/启用用户账号
- 禁用账号后用户立即无法登录系统
- 禁用账号后所有现有的JWT Token立即失效

**FR-1.4.4 操作记录管理**

- 所有管理操作记录审计日志
- 包含操作人、时间、操作内容

#### 验收标准

* 管理员可以查看完整的用户列表
* 支持按角色、状态、企业等条件筛选
* 可以禁用/启用用户账号
* 禁用后用户无法登录系统
* 所有管理操作记录审计日志

### 1.5 角色权限管理

#### 功能描述

系统管理员可以为用户分配和调整角色权限，确保用户只能访问其职责范围内的功能。

#### 功能需求

**FR-1.5.1 预定义角色系统**

- `UNAUTHENTICATED`：未认证用户 - 查看系统介绍、提交企业认证申请、修改个人资料
- `PHARMACY`：药店用户 - 库存管理、采购、查看供应商
- `SUPPLIER`：供应商用户 - 库存管理、发布供应信息、处理订单
- `REGULATOR`：监管用户 - 查看所有数据、监管看板、追溯查询
- `LOGISTICS`：物流用户 - 上报运输状态、路径规划
- `ADMIN`：系统管理员 - 用户管理、系统维护

**FR-1.5.2 权限变更管理**

- 管理员可以为用户分配角色
- 权限变更对已登录用户需要重新登录后生效
- 角色之间没有继承关系，采用扁平化设计
- 用户登录后只能看到权限范围内的功能菜单

#### 验收标准

* 管理员可以为用户分配角色
* 角色权限变更需要重新登录生效
* 用户登录后只能看到权限范围内的功能菜单
* 无权限访问的功能返回明确错误提示
* 权限变更记录审计日志

### 1.6 企业认证审核

#### 功能描述

系统管理员根据用户申请的角色类型，按照对应标准审核其企业资质。

#### 功能需求

**FR-1.6.1 差异化审核标准**

- **所有角色共通标准**：《营业执照》真实有效，企业信息与证件信息完全一致
- **药店用户专属标准**：具备有效的《药品经营许可证》（零售）
- **供应商用户专属标准**：具备有效的《药品生产许可证》或《药品经营许可证》（批发）
- **物流用户专属标准**：具备有效的《道路运输经营许可证》

**FR-1.6.2 审核界面和流程**

- 审核界面显著标明当前审核角色和对应的审核标准清单
- 管理员可以逐项核对标准，查看用户上传的资质文件
- 提供标准化的驳回原因下拉菜单
- 审核时限目标为3个工作日，超过24小时自动提醒

**FR-1.6.3 审核结果处理**

- 审核通过后，用户角色立即从'未认证'更新为对应的企业角色
- 审核不通过时，管理员必须选择标准化驳回原因并可补充说明
- 用户通过站内信收到审核结果，包含具体的改进指导
- 记录每一次审核操作的管理员、时间、结果和原因

#### 验收标准

* 管理员在待审核列表中能清晰看到每个申请对应的用户角色
* 进入审核界面后，系统根据角色动态显示对应的审核标准清单
* 管理员可以逐项核对标准，并查看用户上传的所有资质文件
* 审核通过后，用户角色立即从'未认证'更新为对应的企业角色
* 审核不通过时，管理员必须从标准化的原因列表中选择，并可补充说明
* 用户通过站内信收到审核结果，驳回信息中包含具体、明确的改进指导
* 系统自动记录每一次审核操作的管理员、时间、结果和原因

## :convenience_store: 企业库存管理子系统

### 2.1 库存登记与更新

#### 功能描述

药店用户和供应商用户可以登记和更新药品库存数据，实现准确的库存水平管理。

#### 功能需求

**FR-2.1.1 库存信息管理**

- 核心字段：药品ID（从系统主数据选择）、生产批号（手动输入）、生产日期、有效期限、库存数量
- 所有字段为必填项
- 库存数量绝对不能为负数
- 出库操作时，超过当前库存则拒绝操作并返回明确错误信息

**FR-2.1.2 权限和数据隔离**

- 前后端双重权限验证
- 每个库存项关联tenant_id（租户id）
- 任何创建、更新、读取操作都必须验证当前用户的tenant_id匹配
- 用户只能操作本企业的库存数据

**FR-2.1.3 操作审计**

- 当前版本无需审核流程，操作者直接负责
- 所有操作记录在operation_logs表中，便于后续审计
- 操作响应时间要求小于3秒

#### 验收标准

* 用户登录后可以访问库存管理界面
* 成功添加新库存项后显示确认信息
* 库存数量更新实时生效
* 非本企业用户无法修改库存数据
* 操作响应时间小于3秒

### 2.2 库存预警

#### 功能描述

系统自动预警低库存和近效期药品，帮助药店用户及时补货和处理临期药品。

#### 功能需求

**FR-2.2.1 预警阈值设置**

- 第一版使用系统默认值
- 库存数量低于10件触发预警
- 药品有效期在30天内触发预警
- 后续迭代支持用户自定义阈值

**FR-2.2.2 预警通知方式**

- 第一期在系统内提供视觉提示
- 库存列表页面，预警项用黄色或红色高亮显示
- 用户登录后的首页提供"预警中心"列表
- 邮件和短信通知放在V2.0

**FR-2.2.3 预警扫描机制**

- 采用每日定时任务方式，凌晨执行扫描
- 不采用实时扫描，避免数据库压力
- 预警准确率要求达到100%

#### 验收标准

* 系统每日自动执行库存扫描
* 正确识别低于阈值的库存项
* 准确识别30天内到期的药品
* 预警信息在界面中清晰显示
* 预警准确率达到100%

## :handshake: B2B供求平台子系统

### 3.1 发布供应信息

#### 功能描述

供应商用户可以发布可供应的药品信息，供药店用户查看并联系采购。

#### 功能需求

**FR-3.1.1 供应信息字段管理**

- 必填字段：药品ID（从列表选择）、可供数量、有效期限
- 可选字段：备注信息
- 发布后供应信息状态为`ACTIVE`

**FR-3.1.2 供应信息有效期设置**

- 提供具体日期选择和预设选项（1个月、3个月、长期有效）
- 默认设置为1年后自动过期
- 过期后状态自动变为`EXPIRED`

**FR-3.1.3 供应信息状态管理**

- **`ACTIVE` (活跃/上架)**：已发布，对药店用户可见，可被查询和下单
- **`INACTIVE` (非活跃/下架)**：供应商主动下架，不对药店用户可见
- **`EXPIRED` (已过期)**：超出有效期限，系统自动置为此状态

**FR-3.1.4 编辑权限控制**

- 没有关联任何订单时：可以任意修改所有字段或直接下架
- 有关联`PENDING`状态订单时：
  - 可以修改'备注'字段
  - 不能修改'药品'、'数量'等核心信息
  - 不能直接下架，必须先处理完所有待确认订单

#### 验收标准

* 登录供应商用户可以访问发布界面
* 成功发布后供应信息状态为`ACTIVE`
* 发布的信息与供应商正确关联（通过tenant_id）
* 有效期设置正确：用户自定义日期或预设选项均能正确保存
* 当供应信息没有关联`PENDING`订单时，供应商可以修改所有字段
* 当供应信息有关联`PENDING`订单时，系统阻止修改核心字段和下架操作
* 新发布的供应信息在5分钟内在药店用户的列表中可见

### 3.2 查看供应信息

#### 功能描述

药店用户可以浏览所有有效的供应信息，找到合适的供应商采购药品。

#### 功能需求

**FR-3.2.1 供应信息展示**

- 只显示状态为`ACTIVE`且有效期限大于当前时间的供应信息
- 列表包含完整的药品信息（通用名、商品名）和供应商企业名称
- 默认按发布时间倒序排列，最新的在最前面

**FR-3.2.2 搜索和筛选功能**

- 支持按药品通用名或商品名进行关键词搜索
- 第一期可选择性支持按供应商企业名称的筛选
- V1.0不展示价格，不支持按价格排序

**FR-3.2.3 联系方式显示**

- 显示供应商的企业名称和公开的联系电话
- 不显示具体联系人姓名、邮箱等敏感信息
- 药店用户需要进一步沟通可通过系统内的'联系供应商'功能

**FR-3.2.4 分页和更新机制**

- 采用分页加载，每页显示20条记录
- 提供'加载更多'的无限滚动选项
- 每5分钟自动刷新一次列表数据
- 支持手动点击刷新按钮

#### 验收标准

* 只显示状态为`ACTIVE`且有效期限大于当前时间的供应信息
* 列表包含完整的药品信息和供应商企业名称
* 支持按药品通用名或商品名进行关键词搜索
* 列表采用分页加载，每页显示20条记录
* 药店用户无法看到供应商的非公开联系信息
* 列表每5分钟自动刷新一次，同时支持手动刷新

### 3.3 模拟下单

#### 功能描述

药店用户可以对供应信息进行下单并跟踪订单全流程，完成药品采购。

#### 功能需求

**FR-3.3.1 订单状态管理**

- `PENDING` (待确认) - 药店已下单，等待供应商确认
- `CONFIRMED` (已确认) - 供应商确认接受订单
- `SHIPPED` (已发货) - 供应商已发货，等待物流接收
- `IN_TRANSIT` (运输中) - 物流已接收，正在运输途中
- `DELIVERED` (已送达) - 药品已送达目的地
- `COMPLETED` (已完成) - 药店已确认收到药品，订单完成
- `CANCELLED_BY_PHARMACY` (药店取消) - 药店在待确认期间取消
- `CANCELLED_BY_SUPPLIER` (供应商取消) - 供应商拒绝接受订单
- `EXPIRED_CANCELLED` (超时取消) - 供应商24小时内未响应

**FR-3.3.2 订单状态流转规则**

- `PENDING` → `CONFIRMED` (供应商确认)
- `PENDING` → `CANCELLED_BY_SUPPLIER` (供应商拒绝)
- `PENDING` → `CANCELLED_BY_PHARMACY` (药店取消)
- `PENDING` → `EXPIRED_CANCELLED` (系统超时)
- `CONFIRMED` → `SHIPPED` (供应商发货)
- `SHIPPED` → `IN_TRANSIT` (物流开始运输)
- `IN_TRANSIT` → `DELIVERED` (物流送达)
- `DELIVERED` → `COMPLETED` (药店确认收货)

**FR-3.3.3 订单信息管理**

- 订单基本信息：订单ID、创建时间、状态
- 关联信息：供应信息ID、药品详情、供应商企业信息
- 采购信息：订购数量、期望交付时间（可选）
- 双方信息：药店企业信息、联系人、备注
- 物流信息：物流公司、运单号、发货时间、预计到达时间
- 收货信息：实际收货时间、收货人签字（图片上传）
- 位置信息：发货地址、收货地址（从企业信息自动带出）

**FR-3.3.4 供应商确认机制**

- 药店下单后，状态为`PENDING`，供应商立即收到系统通知
- 供应商有24小时响应时间
- 供应商确认后状态变为`CONFIRMED`，药店收到确认通知
- 供应商拒绝后状态变为`CANCELLED`，药店收到拒绝通知及原因
- 24小时内无响应，系统自动取消订单，状态为`EXPIRED_CANCELLED`

**FR-3.3.5 订单取消规则**

- 药店用户可以在`PENDING`状态时主动取消，状态变为`CANCELLED_BY_PHARMACY`
- 订单进入`CONFIRMED`状态后，药店不能单方面取消
- 除'备注'字段外，订单生成后其他信息均不可修改

#### 验收标准

* 成功生成状态为`PENDING`的模拟订单
* 订单与供应信息正确关联
* 订单包含所有约定的核心字段
* 供应商立即收到订单通知
* 药店用户可以在订单`PENDING`状态时取消订单
* 供应商可以在24小时内确认或拒绝订单
* 24小时内无响应，系统自动取消订单
* 订单状态严格按照完整的9种状态流转
* 下单数量超过可用数量时，系统阻止下单并提示"库存不足"
* 最终状态（COMPLETED和各种CANCELLED）不允许再修改

## :bar_chart: 流通监管子系统

### 4.1 流通数据上报

#### 功能描述

企业用户（药店、供应商或物流公司）可以上报药品的运输状态，实现药品流通情况的实时掌握。

#### 功能需求

**FR-4.1.1 上报信息字段**

- 必填：流通记录ID（即订单运单号）、运输状态、时间戳
- 可选：当前位置（GPS坐标或文字地址）、备注信息
- 运输状态枚举值：`SHIPPED`, `IN_TRANSIT`, `DELIVERED`

**FR-4.1.2 上报方式和权限**

- 提供Web页面表单手动录入，支持下拉选择状态
- 用户必须已登录并且角色为药店、供应商或物流公司
- 第一期仅支持单条上报，避免复杂度

**FR-4.1.3 状态流转规则**

- 状态流转规则：`SHIPPED` → `IN_TRANSIT` → `DELIVERED`（正向流转）
- `DELIVERED`状态不可逆，表示配送已完成
- `IN_TRANSIT`状态允许重复上报以更新位置信息
- 状态变更会自动同步更新关联的订单状态

**FR-4.1.4 异常处理和日志**

- 订单ID不存在返回`404`错误
- 状态流转非法返回`400`错误
- 权限不足返回`403`错误
- 所有异常都返回友好的错误提示
- 每一次上报成功/失败都写入operation_logs

#### 验收标准

* 用户必须已登录并且角色为药店、供应商或物流公司
* 上报状态成功写入circulation_records表并持久化
* 运输状态变更自动同步更新关联的订单状态
* 状态流转符合业务规则（不可逆、正确顺序）
* 界面上能收到"状态更新成功"的确认
* 异常输入返回友好错误提示
* API响应时间≤3秒

### 4.2 药品全生命周期追溯

#### 功能描述

监管用户输入药品批号后能查看药品从出厂到药店的完整流向链路，确保药品来源合法。

#### 功能需求

**FR-4.2.1 追溯查询功能**

- 必须输入：药品批号
- 可选输入：时间范围（如近三个月）、区域范围
- 数据来源：circulation_records表、logistics_records表、drugs表

**FR-4.2.2 展示方式**

- 提供时间轴视图（出厂 → 仓库 → 在途 → 药店），每个节点标注时间、状态
- 提供Sankey流向图/地图可视化，直观展示药品的流转路径
- 查询响应时间≤5秒

**FR-4.2.3 性能和导出**

- 对circulation_records建立索引，保证查询性能
- 第一版仅在前端展示，后续可扩展PDF/Excel导出
- 若批号不存在，提示"未查询到相关流通记录"

#### 验收标准

* 输入药品批号后，能得到完整的流通链条
* 时间轴包含每个运输状态和时间点
* 流向图准确展示起点、途径和终点
* 查询响应时间≤5秒
* 若批号不存在，提示"未查询到相关流通记录"

## :chart_with_upwards_trend: 监管分析子系统

### 5.1 监管看板

#### 功能描述

监管用户通过可视化看板查看药品流通全局情况和关键指标，快速发现风险和异常。

#### 功能需求

**FR-5.1.1 核心指标展示**

- 当前药品总库存量
- 在途药品数量
- 各区域流通量对比
- 异常上报数量（如延迟上报、数据不一致）

**FR-5.1.2 图表展示**

- 折线图（时间序列）
- 柱状图（区域对比）
- 地图热点分布（地理维度）

**FR-5.1.3 筛选和刷新**

- 至少支持时间范围（如近7天、近1月）、区域范围（按行政区划）两个筛选维度
- 默认每5分钟自动刷新一次
- 用户可手动点击刷新按钮

**FR-5.1.4 数据准确性和性能**

- 统计数据来自circulation_records、inventory_items
- 保证与数据库实时数据保持一致
- 前端图表渲染时间≤3秒

#### 验收标准

* 看板数据与后台数据库保持一致
* 图表渲染时间≤3秒
* 支持至少2个维度筛选（时间、区域）
* 自动刷新+手动刷新均能触发更新

### 5.2 合规分析报告

#### 功能描述

监管用户可以生成合规分析报告，为政策制定和应急调度提供数据支持。

#### 功能需求

**FR-5.2.1 报告类型**

- **库存合规分析**：检查企业库存异常（库存不足、缺货、药品过期等），提供异常比例统计
- **流通合规分析**：评估运输状态异常（延迟上报、状态不一致），生成时效性对比图表
- **企业合规分析**：从租户维度统计企业合规率，标记违规次数较多的企业

**FR-5.2.2 导出格式**

- **PDF**：用于正式归档和汇报，内容排版美观，图表清晰
- **Excel**：用于监管人员后续做二次分析，方便筛选、计算和制图

**FR-5.2.3 生成方式和性能**

- 用户输入时间范围和区域范围，点击"生成报告"按钮后系统自动汇总数据
- 生成的报告可以在浏览器中直接查看，也可以下载保存
- 第一版仅支持手动生成，未来可扩展定时任务功能
- 在标准数据量（≤5000条流通记录）下，报告生成时间≤10秒

**FR-5.2.4 安全性**

- 报告仅限具有监管权限的用户下载
- 普通企业用户无权访问
- 所有下载操作必须写入日志，包括操作用户、时间、参数

#### 验收标准

* 报告数据完整且准确，涵盖指定范围
* 支持PDF与Excel导出
* 报告生成时间≤10秒
* 报告下载需验证用户角色
* 所有下载操作写入操作日志，保证可追溯性

## :truck: 智能调度子系统

### 6.1 药品定位与就近推荐

#### 功能描述

药店用户可以根据所在位置获得最近的供应商推荐，快速找到合适的供货渠道。

#### 功能需求

**FR-6.1.1 推荐逻辑**

- 输入：药店坐标（自动获取或手动输入）+ 搜索半径
- 系统计算药店与供应商的距离，按距离升序排序
- 第一版仅按距离排序，后续可加入库存条件作为加权因子

**FR-6.1.2 结果显示内容**

- 供应商企业名称
- 与药店的距离
- 预计配送时间
- 公开的联系方式（电话/地址）

**FR-6.1.3 技术实现**

- 调用第三方地图API（初步考虑高德地图API）
- 保证距离计算准确度≥95%
- 系统响应时间≤2秒

#### 验收标准

* 距离计算误差≤5%
* 系统响应时间≤2秒
* 返回结果列表至少包含：企业名称、与药店的距离、预计配送时间
* 支持显示供应商公开的联系方式

### 6.2 最优配送路径规划

#### 功能描述

物流公司用户可以为多目的地配送获得最优路径，降低运输成本并提高效率。

#### 功能需求

**FR-6.2.1 输入条件**

- 必填：起点位置（仓库坐标/地址）、多个配送目的地坐标（至少2个）
- 可选：各目的地的时间窗口（如必须上午送达）
- 车辆约束（载重/运行时长）第一版暂不做

**FR-6.2.2 算法与数据源**

- 集成第三方实时交通API（初步考虑高德地图API）
- 路径计算需考虑当前路况
- 算法采用"最短路径+实时交通速度"综合计算
- 优先选择ETA（预计到达时间）最短的路径
- API不可用时，使用静态最短路径计算作为fallback

**FR-6.2.3 输出内容**

- 最优配送顺序（如：仓库 → 药店A → 药店C → 药店B）
- 每一段的预计行驶时间与里程
- 总行程时间与总距离
- 路线在地图上直观高亮展示，节点清晰标注
- 若目的地有时间窗口，标记是否满足/超时

**FR-6.2.4 性能要求**

- 计算时间≤30秒（10个目的地以内）
- 调用第三方API的超时时间≤5秒，超时则切换fallback
- 用户界面需提示"正在规划路线，请稍候"
- 与人工规划相比，系统路径应至少减少20%的总时长或里程

#### 验收标准

* 系统输出路径顺序合理
* 提供总时长、每段时间和总距离
* 在地图界面清晰展示线路

### 6.3 实时运输监控

#### 功能描述

监管或企业用户可以在地图上实时查看运输车辆的位置和状态，随时掌握药品运输进度。

#### 功能需求

**FR-6.3.1 数据来源和显示**

- 车辆GPS，每30秒推送一次位置
- 显示内容：实时轨迹（折线图）、当前车辆位置（标注点）、预计到达时间（ETA）

**FR-6.3.2 刷新方式**

- WebSocket推送
- Fallback：定时轮询（30秒）
- 位置更新延迟≤30秒

**FR-6.3.3 未来扩展**

- 异常报警：延误/绕路时提示
- 历史轨迹回放
- 地图加载时间≤3秒

#### 验收标准

* 位置更新延迟≤30秒
* 地图加载时间≤3秒
* 显示运输轨迹、当前位置和ETA

## :clipboard: 非功能性需求

### 性能需求

- **响应时间**：页面加载≤3秒，API响应≤2秒
- **并发支持**：10+用户同时在线
- **数据容量**：支持5000+流通记录
- **可用性**：核心功能可用性≥95%

### 安全需求

- **认证授权**：JWT Token认证 + RBAC权限控制
- **数据隔离**：多租户架构，严格的数据隔离
- **传输安全**：HTTPS/TLS加密传输
- **审计日志**：完整的操作审计记录

### 兼容性需求

- **浏览器**：Chrome 90+/Firefox 88+/Edge 90+
- **移动端**：V1.0仅支持桌面端访问
- **操作系统**：跨平台Web应用

### 可维护性需求

- **代码质量**：ESLint + Prettier代码规范
- **文档完整性**：完整的API文档和用户手册
- **测试覆盖**：核心功能单元测试覆盖率≥80%

# 技术规范

## API设计
- **协议：** RESTful API
- **数据格式：** JSON
- **认证：** 所有非公开API需携带JWT Token
- **实时通信：** WebSocket用于位置推送

# 开发规范

## :art: 通用编码规范

### 基本原则

1. **可读性优先**：代码应该易于阅读和理解
2. **一致性**：保持项目内部编码风格的一致性
3. **简洁性**：避免过度复杂的设计和实现
4. **可维护性**：编写易于维护和扩展的代码
5. **安全性**：确保代码安全，防止常见漏洞

### 命名规范

#### 通用命名规则

- **英文命名**：所有标识符使用英文，禁止拼音或中文
- **语义明确**：名称要能清晰表达其用途和含义
- **避免缩写**：除非是广泛接受的缩写（如id、url、api等）
- **避免误导**：不要使用与功能不符的名称

#### 命名风格

```javascript
// 好的命名
const userAccountInfo = {};
const calculateTotalAmount = () => {};
const IS_PRODUCTION = true;

// 不好的命名  
const data = {};  // 太泛化
const calc = () => {};  // 缩写不明确
const flag = true;  // 无意义命名
```

### 注释规范

#### 注释原则

1. **代码即文档**：优先编写自解释的代码
2. **解释Why不是What**：注释说明为什么这样做，而不是做什么
3. **保持更新**：代码变更时同步更新注释
4. **避免废话**：不要写显而易见的注释

#### 注释格式

```javascript
/**
 * 计算药品库存预警
 * 根据库存数量和有效期判断是否需要预警
 * @param {Object} inventory - 库存项信息
 * @param {number} inventory.quantity - 库存数量
 * @param {string} inventory.expiryDate - 有效期日期
 * @returns {Object} 预警信息 {isWarning: boolean, type: string, message: string}
 */
function calculateInventoryWarning(inventory) {
    // 检查库存数量预警（低于10件）
    if (inventory.quantity < 10) {
        return {
            isWarning: true,
            type: 'LOW_STOCK',
            message: '库存不足，需要补货'
        };
    }
    
    // 检查效期预警（30天内到期）
    const expiryDate = new Date(inventory.expiryDate);
    const thirtyDaysLater = new Date();
    thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 30);
    
    if (expiryDate <= thirtyDaysLater) {
        return {
            isWarning: true,
            type: 'NEAR_EXPIRY',
            message: '药品即将过期，请及时处理'
        };
    }
    
    return { isWarning: false };
}
```

## :computer: 前端代码规范（Vue.js）

### 项目结构

```
src/
├── assets/          # 静态资源
│   ├── images/     # 图片资源
│   ├── styles/     # 全局样式
│   └── icons/      # 图标文件
├── components/      # 公共组件
│   ├── common/     # 通用组件
│   ├── forms/      # 表单组件
│   └── charts/     # 图表组件
├── views/           # 页面组件
│   ├── auth/       # 认证相关页面
│   ├── inventory/  # 库存管理页面
│   ├── orders/     # 订单管理页面
│   └── analytics/  # 数据分析页面
├── router/          # 路由配置
├── stores/          # Pinia状态管理
├── services/        # API服务
├── utils/           # 工具函数
├── constants/       # 常量定义
└── types/           # TypeScript类型定义
```

### Vue组件规范

#### 组件命名

```javascript
// 组件文件命名：PascalCase
// 文件：UserProfileCard.vue
// 使用：<UserProfileCard />

// 页面组件：Page后缀
// 文件：InventoryManagePage.vue

// 基础组件：Base前缀
// 文件：BaseButton.vue
// 使用：<BaseButton />
```

#### 组件结构

```vue
<template>
  <!-- 模板内容保持简洁，复杂逻辑抽取到computed或methods -->
  <div class="inventory-card">
    <div class="inventory-card__header">
      <h3 class="inventory-card__title">{{ drug.genericName }}</h3>
      <span class="inventory-card__status" :class="statusClass">
        {{ statusText }}
      </span>
    </div>
    
    <div class="inventory-card__content">
      <div class="inventory-card__info">
        <p>批号：{{ inventory.batchNumber }}</p>
        <p>数量：{{ inventory.quantity }}</p>
        <p>有效期：{{ formattedExpiryDate }}</p>
      </div>
      
      <div class="inventory-card__actions">
        <BaseButton 
          type="primary" 
          @click="handleEdit"
          :disabled="!canEdit"
        >
          编辑
        </BaseButton>
        <BaseButton 
          type="danger" 
          @click="handleDelete"
          :disabled="!canDelete"
        >
          删除
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { formatDate } from '@/utils/date';
import BaseButton from '@/components/common/BaseButton.vue';
import type { Drug, Inventory } from '@/types/inventory';

// Props定义
interface Props {
  drug: Drug;
  inventory: Inventory;
  readonly?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false
});

// Emits定义
interface Emits {
  edit: [inventory: Inventory];
  delete: [id: number];
}

const emit = defineEmits<Emits>();

// 计算属性
const formattedExpiryDate = computed(() => {
  return formatDate(props.inventory.expiryDate, 'YYYY-MM-DD');
});

const statusClass = computed(() => {
  const { quantity, expiryDate } = props.inventory;
  
  if (quantity < 10) return 'status--warning';
  
  const isNearExpiry = new Date(expiryDate) <= new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
  if (isNearExpiry) return 'status--danger';
  
  return 'status--normal';
});

const statusText = computed(() => {
  const { quantity, expiryDate } = props.inventory;
  
  if (quantity < 10) return '库存不足';
  
  const isNearExpiry = new Date(expiryDate) <= new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
  if (isNearExpiry) return '即将过期';
  
  return '正常';
});

const canEdit = computed(() => !props.readonly);
const canDelete = computed(() => !props.readonly && props.inventory.quantity === 0);

// 事件处理
const handleEdit = () => {
  if (canEdit.value) {
    emit('edit', props.inventory);
  }
};

const handleDelete = () => {
  if (canDelete.value && confirm('确定删除此库存记录？')) {
    emit('delete', props.inventory.id);
  }
};
</script>

<style lang="scss" scoped>
.inventory-card {
  @apply border border-gray-200 rounded-lg p-4 bg-white shadow-sm;
  
  &__header {
    @apply flex justify-between items-center mb-3;
  }
  
  &__title {
    @apply text-lg font-semibold text-gray-800;
  }
  
  &__status {
    @apply px-2 py-1 rounded text-sm font-medium;
    
    &.status--normal {
      @apply bg-green-100 text-green-800;
    }
    
    &.status--warning {
      @apply bg-yellow-100 text-yellow-800;
    }
    
    &.status--danger {
      @apply bg-red-100 text-red-800;
    }
  }
  
  &__content {
    @apply space-y-3;
  }
  
  &__info {
    @apply space-y-1 text-sm text-gray-600;
  }
  
  &__actions {
    @apply flex space-x-2;
  }
}
</style>
```

### Pinia状态管理规范

```typescript
// stores/inventory.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { inventoryApi } from '@/services/inventory';
import type { Inventory, CreateInventoryRequest } from '@/types/inventory';

export const useInventoryStore = defineStore('inventory', () => {
  // State
  const inventories = ref<Inventory[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const warningInventories = computed(() => 
    inventories.value.filter(inv => inv.quantity < 10 || isNearExpiry(inv.expiryDate))
  );

  const totalInventoryValue = computed(() =>
    inventories.value.reduce((sum, inv) => sum + (inv.quantity * inv.unitPrice), 0)
  );

  // Actions
  const fetchInventories = async (tenantId: number) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await inventoryApi.getInventories(tenantId);
      inventories.value = response.data;
    } catch (err) {
      error.value = '获取库存列表失败';
      console.error('Failed to fetch inventories:', err);
    } finally {
      loading.value = false;
    }
  };

  const createInventory = async (data: CreateInventoryRequest) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await inventoryApi.createInventory(data);
      inventories.value.push(response.data);
      return response.data;
    } catch (err) {
      error.value = '创建库存记录失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateInventory = async (id: number, data: Partial<Inventory>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await inventoryApi.updateInventory(id, data);
      const index = inventories.value.findIndex(inv => inv.id === id);
      if (index !== -1) {
        inventories.value[index] = response.data;
      }
      return response.data;
    } catch (err) {
      error.value = '更新库存记录失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteInventory = async (id: number) => {
    loading.value = true;
    error.value = null;
    
    try {
      await inventoryApi.deleteInventory(id);
      inventories.value = inventories.value.filter(inv => inv.id !== id);
    } catch (err) {
      error.value = '删除库存记录失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Helper functions
  const isNearExpiry = (expiryDate: string) => {
    const expiry = new Date(expiryDate);
    const thirtyDaysLater = new Date();
    thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 30);
    return expiry <= thirtyDaysLater;
  };

  return {
    // State
    inventories,
    loading,
    error,
    
    // Getters
    warningInventories,
    totalInventoryValue,
    
    // Actions
    fetchInventories,
    createInventory,
    updateInventory,
    deleteInventory
  };
});
```

### API服务规范

```typescript
// services/inventory.ts
import { apiClient } from './api-client';
import type { 
  Inventory, 
  CreateInventoryRequest, 
  UpdateInventoryRequest,
  InventoryListResponse 
} from '@/types/inventory';

export const inventoryApi = {
  /**
   * 获取库存列表
   */
  getInventories: (tenantId: number, params?: {
    page?: number;
    pageSize?: number;
    drugId?: number;
    searchTerm?: string;
  }) => {
    return apiClient.get<InventoryListResponse>('/inventory/items', {
      params: { tenantId, ...params }
    });
  },

  /**
   * 获取库存详情
   */
  getInventory: (id: number) => {
    return apiClient.get<Inventory>(`/inventory/items/${id}`);
  },

  /**
   * 创建库存记录
   */
  createInventory: (data: CreateInventoryRequest) => {
    return apiClient.post<Inventory>('/inventory/items', data);
  },

  /**
   * 更新库存记录
   */
  updateInventory: (id: number, data: UpdateInventoryRequest) => {
    return apiClient.put<Inventory>(`/inventory/items/${id}`, data);
  },

  /**
   * 删除库存记录
   */
  deleteInventory: (id: number) => {
    return apiClient.delete(`/inventory/items/${id}`);
  },

  /**
   * 获取库存预警
   */
  getWarnings: (tenantId: number) => {
    return apiClient.get<Inventory[]>('/inventory/warnings', {
      params: { tenantId }
    });
  }
};
```

## :gear: 后端代码规范（Flask）

### 项目结构

```
app/
├── __init__.py          # 应用工厂函数
├── models/              # 数据模型
│   ├── __init__.py
│   ├── user.py         # 用户模型
│   ├── inventory.py    # 库存模型
│   └── order.py        # 订单模型
├── api/                 # API路由
│   ├── __init__.py
│   ├── auth.py         # 认证相关路由
│   ├── inventory.py    # 库存管理路由
│   └── orders.py       # 订单管理路由
├── services/            # 业务逻辑服务
│   ├── __init__.py
│   ├── auth_service.py
│   ├── inventory_service.py
│   └── order_service.py
├── utils/               # 工具函数
│   ├── __init__.py
│   ├── validators.py   # 数据验证
│   ├── decorators.py   # 装饰器
│   └── helpers.py      # 辅助函数
├── schemas/             # 数据序列化
│   ├── __init__.py
│   ├── user_schema.py
│   └── inventory_schema.py
└── config/              # 配置文件
    ├── __init__.py
    ├── development.py
    ├── production.py
    └── testing.py
```

### 模型定义规范

```python
# models/inventory.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates
from app.models import db


class InventoryItem(db.Model):
    """库存项模型"""
    
    __tablename__ = 'inventory_items'
    
    # 主键
    id = Column(Integer, primary_key=True)
    
    # 外键关联
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
    drug_id = Column(Integer, ForeignKey('drugs.id'), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # 业务字段
    batch_number = Column(String(50), nullable=False, index=True)
    production_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    unit_price = Column(Numeric(10, 2), nullable=True)
    storage_location = Column(String(100), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    drug = relationship("Drug", backref="inventory_items")
    supplier = relationship("Tenant", foreign_keys=[supplier_id])
    
    # 约束条件
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_quantity_non_negative'),
        CheckConstraint('expiry_date > production_date', name='check_expiry_after_production'),
    )
    
    def __repr__(self):
        return f'<InventoryItem {self.id}: {self.drug.generic_name} - {self.batch_number}>'
    
    @validates('quantity')
    def validate_quantity(self, key, value):
        """验证库存数量不能为负数"""
        if value < 0:
            raise ValueError("库存数量不能为负数")
        return value
    
    @validates('expiry_date')
    def validate_expiry_date(self, key, value):
        """验证有效期必须晚于生产日期"""
        if self.production_date and value <= self.production_date:
            raise ValueError("有效期必须晚于生产日期")
        return value
    
    @property
    def is_low_stock(self):
        """判断是否低库存"""
        return self.quantity < 10
    
    @property
    def is_near_expiry(self):
        """判断是否近效期（30天内）"""
        from datetime import timedelta
        threshold = datetime.utcnow() + timedelta(days=30)
        return self.expiry_date <= threshold
    
    @property
    def is_expired(self):
        """判断是否已过期"""
        return self.expiry_date <= datetime.utcnow()
    
    def to_dict(self, include_relations=False):
        """转换为字典"""
        result = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'drug_id': self.drug_id,
            'supplier_id': self.supplier_id,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'storage_location': self.storage_location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_low_stock': self.is_low_stock,
            'is_near_expiry': self.is_near_expiry,
            'is_expired': self.is_expired
        }
        
        if include_relations:
            result.update({
                'drug': self.drug.to_dict() if self.drug else None,
                'tenant': self.tenant.to_dict() if self.tenant else None,
                'supplier': self.supplier.to_dict() if self.supplier else None
            })
        
        return result
```

### API路由规范

```python
# api/inventory.py
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.services.inventory_service import InventoryService
from app.schemas.inventory_schema import InventorySchema, CreateInventorySchema, UpdateInventorySchema
from app.utils.decorators import require_roles, tenant_required
from app.utils.validators import validate_json
from app.utils.response import success_response, error_response
from app.models.user import RoleEnum


# 创建蓝图
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/v1/inventory')

# 初始化服务和Schema
inventory_service = InventoryService()
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
create_inventory_schema = CreateInventorySchema()
update_inventory_schema = UpdateInventorySchema()


@inventory_bp.route('/items', methods=['GET'])
@jwt_required()
@tenant_required
@require_roles([RoleEnum.PHARMACY, RoleEnum.SUPPLIER, RoleEnum.ADMIN])
def get_inventories():
    """
    获取库存列表
    
    Query Parameters:
        page (int): 页码，默认1
        per_page (int): 每页数量，默认20
        drug_id (int): 药品ID筛选
        search_term (str): 搜索关键词
        low_stock (bool): 只显示低库存
        near_expiry (bool): 只显示近效期
    
    Returns:
        200: 库存列表
        400: 参数错误
        403: 权限不足
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # 限制最大100
        drug_id = request.args.get('drug_id', type=int)
        search_term = request.args.get('search_term', type=str)
        low_stock = request.args.get('low_stock', type=bool)
        near_expiry = request.args.get('near_expiry', type=bool)
        
        # 构建筛选条件
        filters = {
            'tenant_id': g.current_user.tenant_id,
            'drug_id': drug_id,
            'search_term': search_term,
            'low_stock': low_stock,
            'near_expiry': near_expiry
        }
        
        # 调用服务层
        result = inventory_service.get_inventories(
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        return success_response(
            data={
                'items': inventories_schema.dump(result.items),
                'pagination': {
                    'page': result.page,
                    'per_page': result.per_page,
                    'total': result.total,
                    'pages': result.pages,
                    'has_next': result.has_next,
                    'has_prev': result.has_prev
                }
            },
            message="获取库存列表成功"
        )
        
    except Exception as e:
        return error_response(
            message="获取库存列表失败",
            error=str(e),
            status_code=500
        )


@inventory_bp.route('/items', methods=['POST'])
@jwt_required()
@tenant_required
@require_roles([RoleEnum.PHARMACY, RoleEnum.SUPPLIER, RoleEnum.ADMIN])
@validate_json
def create_inventory():
    """
    创建库存记录
    
    Request Body:
        drug_id (int): 药品ID
        batch_number (str): 生产批号
        production_date (str): 生产日期 (YYYY-MM-DD)
        expiry_date (str): 有效期 (YYYY-MM-DD)
        quantity (int): 库存数量
        unit_price (float, optional): 单价
        storage_location (str, optional): 存储位置
        supplier_id (int, optional): 供应商ID
    
    Returns:
        201: 创建成功
        400: 参数错误或业务规则验证失败
        403: 权限不足
        409: 批号冲突
    """
    try:
        # 验证请求数据
        data = create_inventory_schema.load(request.json)
        
        # 添加租户ID
        data['tenant_id'] = g.current_user.tenant_id
        data['created_by'] = g.current_user.id
        
        # 调用服务层创建
        inventory = inventory_service.create_inventory(data)
        
        return success_response(
            data=inventory_schema.dump(inventory),
            message="库存记录创建成功",
            status_code=201
        )
        
    except ValidationError as e:
        return error_response(
            message="数据验证失败",
            error=e.messages,
            status_code=400
        )
    except ValueError as e:
        return error_response(
            message="业务规则验证失败",
            error=str(e),
            status_code=400
        )
    except Exception as e:
        return error_response(
            message="创建库存记录失败",
            error=str(e),
            status_code=500
        )


@inventory_bp.route('/items/<int:inventory_id>', methods=['PUT'])
@jwt_required()
@tenant_required
@require_roles([RoleEnum.PHARMACY, RoleEnum.SUPPLIER, RoleEnum.ADMIN])
@validate_json
def update_inventory(inventory_id):
    """
    更新库存记录
    
    Path Parameters:
        inventory_id (int): 库存记录ID
    
    Request Body:
        quantity (int, optional): 库存数量
        unit_price (float, optional): 单价
        storage_location (str, optional): 存储位置
        notes (str, optional): 更新说明
    
    Returns:
        200: 更新成功
        400: 参数错误
        403: 权限不足
        404: 记录不存在
    """
    try:
        # 验证请求数据
        data = update_inventory_schema.load(request.json)
        
        # 添加更新信息
        data['updated_by'] = g.current_user.id
        
        # 调用服务层更新
        inventory = inventory_service.update_inventory(
            inventory_id=inventory_id,
            tenant_id=g.current_user.tenant_id,
            data=data
        )
        
        if not inventory:
            return error_response(
                message="库存记录不存在或无权限访问",
                status_code=404
            )
        
        return success_response(
            data=inventory_schema.dump(inventory),
            message="库存记录更新成功"
        )
        
    except ValidationError as e:
        return error_response(
            message="数据验证失败",
            error=e.messages,
            status_code=400
        )
    except ValueError as e:
        return error_response(
            message="业务规则验证失败",
            error=str(e),
            status_code=400
        )
    except Exception as e:
        return error_response(
            message="更新库存记录失败",
            error=str(e),
            status_code=500
        )


@inventory_bp.route('/warnings', methods=['GET'])
@jwt_required()
@tenant_required
@require_roles([RoleEnum.PHARMACY, RoleEnum.SUPPLIER, RoleEnum.ADMIN])
def get_inventory_warnings():
    """
    获取库存预警列表
    
    Returns:
        200: 预警列表
        403: 权限不足
    """
    try:
        warnings = inventory_service.get_inventory_warnings(g.current_user.tenant_id)
        
        return success_response(
            data=inventories_schema.dump(warnings),
            message="获取预警列表成功"
        )
        
    except Exception as e:
        return error_response(
            message="获取预警列表失败",
            error=str(e),
            status_code=500
        )
```

### 服务层规范

```python
# services/inventory_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from app.models import db
from app.models.inventory import InventoryItem
from app.models.drug import Drug
from app.utils.exceptions import BusinessError, NotFoundError
from app.utils.logger import get_logger


logger = get_logger(__name__)


class InventoryService:
    """库存管理服务"""
    
    def get_inventories(self, filters: Dict[str, Any], page: int = 1, per_page: int = 20):
        """
        获取库存列表
        
        Args:
            filters: 筛选条件
            page: 页码
            per_page: 每页数量
            
        Returns:
            Pagination对象
        """
        try:
            # 构建基础查询
            query = InventoryItem.query.options(
                joinedload(InventoryItem.drug),
                joinedload(InventoryItem.supplier)
            )
            
            # 添加租户过滤
            if filters.get('tenant_id'):
                query = query.filter(InventoryItem.tenant_id == filters['tenant_id'])
            
            # 添加药品过滤
            if filters.get('drug_id'):
                query = query.filter(InventoryItem.drug_id == filters['drug_id'])
            
            # 添加搜索条件
            if filters.get('search_term'):
                search_term = f"%{filters['search_term']}%"
                query = query.join(Drug).filter(
                    or_(
                        Drug.generic_name.like(search_term),
                        Drug.brand_name.like(search_term),
                        InventoryItem.batch_number.like(search_term)
                    )
                )
            
            # 添加低库存过滤
            if filters.get('low_stock'):
                query = query.filter(InventoryItem.quantity < 10)
            
            # 添加近效期过滤
            if filters.get('near_expiry'):
                threshold_date = datetime.utcnow() + timedelta(days=30)
                query = query.filter(InventoryItem.expiry_date <= threshold_date)
            
            # 按更新时间倒序排序
            query = query.order_by(InventoryItem.updated_at.desc())
            
            # 执行分页查询
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            logger.info(f"Retrieved {len(pagination.items)} inventory items for tenant {filters.get('tenant_id')}")
            return pagination
            
        except Exception as e:
            logger.error(f"Failed to get inventories: {str(e)}")
            raise BusinessError("获取库存列表失败")
    
    def create_inventory(self, data: Dict[str, Any]) -> InventoryItem:
        """
        创建库存记录
        
        Args:
            data: 库存数据
            
        Returns:
            创建的库存记录
            
        Raises:
            BusinessError: 业务规则验证失败
        """
        try:
            # 检查批号唯一性（同一租户下同一药品的批号不能重复）
            existing = InventoryItem.query.filter_by(
                tenant_id=data['tenant_id'],
                drug_id=data['drug_id'],
                batch_number=data['batch_number']
            ).first()
            
            if existing:
                raise BusinessError("该药品的批号已存在")
            
            # 验证有效期
            production_date = datetime.fromisoformat(data['production_date'])
            expiry_date = datetime.fromisoformat(data['expiry_date'])
            
            if expiry_date <= production_date:
                raise BusinessError("有效期必须晚于生产日期")
            
            if expiry_date <= datetime.utcnow():
                raise BusinessError("不能添加已过期的药品")
            
            # 创建库存记录
            inventory = InventoryItem(
                tenant_id=data['tenant_id'],
                drug_id=data['drug_id'],
                batch_number=data['batch_number'],
                production_date=production_date,
                expiry_date=expiry_date,
                quantity=data['quantity'],
                unit_price=data.get('unit_price'),
                storage_location=data.get('storage_location'),
                supplier_id=data.get('supplier_id')
            )
            
            db.session.add(inventory)
            db.session.commit()
            
            # 记录操作日志
            self._log_inventory_operation(
                inventory_id=inventory.id,
                action='CREATE',
                user_id=data.get('created_by'),
                old_quantity=0,
                new_quantity=inventory.quantity
            )
            
            logger.info(f"Created inventory item {inventory.id} for tenant {data['tenant_id']}")
            return inventory
            
        except BusinessError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create inventory: {str(e)}")
            raise BusinessError("创建库存记录失败")
    
    def update_inventory(self, inventory_id: int, tenant_id: int, data: Dict[str, Any]) -> Optional[InventoryItem]:
        """
        更新库存记录
        
        Args:
            inventory_id: 库存记录ID
            tenant_id: 租户ID
            data: 更新数据
            
        Returns:
            更新后的库存记录，如果不存在返回None
        """
        try:
            # 查找库存记录
            inventory = InventoryItem.query.filter_by(
                id=inventory_id,
                tenant_id=tenant_id
            ).first()
            
            if not inventory:
                return None
            
            # 记录原始数量用于日志
            old_quantity = inventory.quantity
            
            # 更新字段
            if 'quantity' in data:
                new_quantity = data['quantity']
                if new_quantity < 0:
                    raise BusinessError("库存数量不能为负数")
                inventory.quantity = new_quantity
            
            if 'unit_price' in data:
                inventory.unit_price = data['unit_price']
            
            if 'storage_location' in data:
                inventory.storage_location = data['storage_location']
            
            inventory.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 记录操作日志
            self._log_inventory_operation(
                inventory_id=inventory.id,
                action='UPDATE',
                user_id=data.get('updated_by'),
                old_quantity=old_quantity,
                new_quantity=inventory.quantity,
                notes=data.get('notes')
            )
            
            logger.info(f"Updated inventory item {inventory_id} for tenant {tenant_id}")
            return inventory
            
        except BusinessError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update inventory {inventory_id}: {str(e)}")
            raise BusinessError("更新库存记录失败")
    
    def get_inventory_warnings(self, tenant_id: int) -> List[InventoryItem]:
        """
        获取库存预警列表
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            预警库存列表
        """
        try:
            threshold_date = datetime.utcnow() + timedelta(days=30)
            
            warnings = InventoryItem.query.options(
                joinedload(InventoryItem.drug)
            ).filter(
                and_(
                    InventoryItem.tenant_id == tenant_id,
                    or_(
                        InventoryItem.quantity < 10,  # 低库存
                        InventoryItem.expiry_date <= threshold_date  # 近效期
                    )
                )
            ).order_by(InventoryItem.expiry_date.asc()).all()
            
            logger.info(f"Found {len(warnings)} inventory warnings for tenant {tenant_id}")
            return warnings
            
        except Exception as e:
            logger.error(f"Failed to get inventory warnings: {str(e)}")
            raise BusinessError("获取库存预警失败")
    
    def _log_inventory_operation(self, inventory_id: int, action: str, user_id: int, 
                               old_quantity: int, new_quantity: int, notes: str = None):
        """记录库存操作日志"""
        from app.models.operation_log import OperationLog
        
        try:
            log = OperationLog(
                user_id=user_id,
                action=action,
                resource_type='inventory',
                resource_id=inventory_id,
                old_values={'quantity': old_quantity},
                new_values={'quantity': new_quantity},
                notes=notes
            )
            
            db.session.add(log)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log inventory operation: {str(e)}")
            # 不抛出异常，避免影响主要业务流程
```

## :floppy_disk: 数据库规范

### 命名规范

```sql
-- 表名：snake_case，复数形式
-- 好的示例
CREATE TABLE users (...)
CREATE TABLE inventory_items (...)
CREATE TABLE operation_logs (...)

-- 不好的示例
CREATE TABLE User (...)
CREATE TABLE inventoryItem (...)
CREATE TABLE log (...)

-- 字段名：snake_case
-- 好的示例
user_id, created_at, is_active, unified_social_credit_code

-- 不好的示例
userId, createdAt, isActive, USCC

-- 索引名：idx_表名_字段名
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_inventory_items_tenant_id ON inventory_items(tenant_id);

-- 外键约束名：fk_表名_引用表名
ALTER TABLE orders ADD CONSTRAINT fk_orders_users FOREIGN KEY (user_id) REFERENCES users(id);

-- 检查约束名：ck_表名_描述
ALTER TABLE inventory_items ADD CONSTRAINT ck_inventory_items_quantity_positive CHECK (quantity >= 0);
```

### 表设计规范

```sql
-- 标准表结构模板
CREATE TABLE table_name (
    -- 主键（必需）
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 业务字段
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    
    -- 外键字段（如果需要）
    tenant_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    
    -- 时间戳字段（推荐）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    
    -- 检查约束
    CHECK (LENGTH(name) > 0),
    CHECK (status IN ('ACTIVE', 'INACTIVE', 'DELETED'))
);

-- 创建必要的索引
CREATE INDEX idx_table_name_tenant_id ON table_name(tenant_id);
CREATE INDEX idx_table_name_status ON table_name(status);
CREATE INDEX idx_table_name_created_at ON table_name(created_at);
```

## :test_tube: 测试规范

### 测试文件组织

```
tests/
├── unit/                    # 单元测试
│   ├── test_models.py      # 模型测试
│   ├── test_services.py    # 服务层测试
│   └── test_utils.py       # 工具函数测试
├── integration/            # 集成测试
│   ├── test_api.py        # API测试
│   └── test_database.py   # 数据库测试
├── e2e/                   # 端到端测试
│   ├── test_user_flow.py  # 用户流程测试
│   └── test_business.py   # 业务流程测试
├── fixtures/              # 测试数据
│   ├── users.json
│   └── inventory.json
└── conftest.py           # 测试配置
```

### 单元测试示例

```python
# tests/unit/test_inventory_service.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.services.inventory_service import InventoryService
from app.models.inventory import InventoryItem
from app.utils.exceptions import BusinessError


class TestInventoryService:
    """库存服务测试"""
    
    @pytest.fixture
    def inventory_service(self):
        """创建库存服务实例"""
        return InventoryService()
    
    @pytest.fixture
    def sample_inventory_data(self):
        """样例库存数据"""
        return {
            'tenant_id': 1,
            'drug_id': 1,
            'batch_number': 'B20241025001',
            'production_date': '2024-10-01',
            'expiry_date': '2026-10-01',
            'quantity': 100,
            'unit_price': 25.50,
            'storage_location': 'A1-B2-C3'
        }
    
    @patch('app.services.inventory_service.db.session')
    @patch('app.services.inventory_service.InventoryItem')
    def test_create_inventory_success(self, mock_inventory, mock_db, inventory_service, sample_inventory_data):
        """测试成功创建库存记录"""
        # 模拟查询结果（不存在重复记录）
        mock_inventory.query.filter_by.return_value.first.return_value = None
        
        # 模拟创建的库存对象
        mock_inventory_instance = Mock()
        mock_inventory_instance.id = 1
        mock_inventory.return_value = mock_inventory_instance
        
        # 执行测试
        result = inventory_service.create_inventory(sample_inventory_data)
        
        # 验证结果
        assert result == mock_inventory_instance
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('app.services.inventory_service.InventoryItem')
    def test_create_inventory_duplicate_batch(self, mock_inventory, inventory_service, sample_inventory_data):
        """测试创建重复批号的库存记录"""
        # 模拟查询结果（存在重复记录）
        mock_inventory.query.filter_by.return_value.first.return_value = Mock()
        
        # 执行测试并验证异常
        with pytest.raises(BusinessError, match="该药品的批号已存在"):
            inventory_service.create_inventory(sample_inventory_data)
    
    def test_create_inventory_invalid_expiry_date(self, inventory_service, sample_inventory_data):
        """测试无效有效期的库存记录"""
        # 设置无效的有效期（早于生产日期）
        sample_inventory_data['expiry_date'] = '2024-09-01'
        
        # 执行测试并验证异常
        with pytest.raises(BusinessError, match="有效期必须晚于生产日期"):
            inventory_service.create_inventory(sample_inventory_data)
    
    @patch('app.services.inventory_service.InventoryItem')
    def test_get_inventory_warnings(self, mock_inventory, inventory_service):
        """测试获取库存预警"""
        # 模拟预警数据
        low_stock_item = Mock()
        low_stock_item.quantity = 5
        low_stock_item.expiry_date = datetime.utcnow() + timedelta(days=60)
        
        near_expiry_item = Mock()
        near_expiry_item.quantity = 50
        near_expiry_item.expiry_date = datetime.utcnow() + timedelta(days=15)
        
        mock_inventory.query.options.return_value.filter.return_value.order_by.return_value.all.return_value = [
            low_stock_item, near_expiry_item
        ]
        
        # 执行测试
        warnings = inventory_service.get_inventory_warnings(tenant_id=1)
        
        # 验证结果
        assert len(warnings) == 2
        assert low_stock_item in warnings
        assert near_expiry_item in warnings


# tests/integration/test_inventory_api.py
import pytest
import json
from datetime import datetime, timedelta

from app import create_app
from app.models import db
from app.models.user import User, RoleEnum
from app.models.tenant import Tenant
from app.models.drug import Drug
from app.models.inventory import InventoryItem


class TestInventoryAPI:
    """库存API集成测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, app):
        """创建认证头部"""
        with app.app_context():
            # 创建测试租户
            tenant = Tenant(name="测试药店", unified_social_credit_code="91310000123456789X")
            db.session.add(tenant)
            db.session.flush()
            
            # 创建测试用户
            user = User(
                username="test_pharmacy",
                email="test@pharmacy.com",
                tenant_id=tenant.id
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            
            # 分配角色
            from app.models.user import UserRole, Role
            pharmacy_role = Role.query.filter_by(name=RoleEnum.PHARMACY.value).first()
            user_role = UserRole(user_id=user.id, role_id=pharmacy_role.id)
            db.session.add(user_role)
            db.session.commit()
            
            # 生成JWT Token
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=user.id)
            
            return {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
    
    @pytest.fixture
    def sample_drug(self, app):
        """创建样例药品"""
        with app.app_context():
            drug = Drug(
                generic_name="阿司匹林片",
                brand_name="拜阿司匹林",
                approval_number="H12345678",
                dosage_form="片剂",
                specification="100mg",
                manufacturer="拜耳医药"
            )
            db.session.add(drug)
            db.session.commit()
            return drug
    
    def test_get_inventories_success(self, client, auth_headers, sample_drug):
        """测试成功获取库存列表"""
        # 发送请求
        response = client.get('/api/v1/inventory/items', headers=auth_headers)
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_create_inventory_success(self, client, auth_headers, sample_drug):
        """测试成功创建库存记录"""
        inventory_data = {
            'drug_id': sample_drug.id,
            'batch_number': 'B20241025001',
            'production_date': '2024-10-01',
            'expiry_date': '2026-10-01',
            'quantity': 100,
            'unit_price': 25.50,
            'storage_location': 'A1-B2-C3'
        }
        
        # 发送请求
        response = client.post('/api/v1/inventory/items', 
                             headers=auth_headers, 
                             data=json.dumps(inventory_data))
        
        # 验证响应
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['batch_number'] == inventory_data['batch_number']
        assert data['data']['quantity'] == inventory_data['quantity']
    
    def test_create_inventory_validation_error(self, client, auth_headers):
        """测试创建库存记录时的验证错误"""
        invalid_data = {
            'drug_id': 999,  # 不存在的药品ID
            'batch_number': '',  # 空批号
            'quantity': -10  # 负数数量
        }
        
        # 发送请求
        response = client.post('/api/v1/inventory/items',
                             headers=auth_headers,
                             data=json.dumps(invalid_data))
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get('/api/v1/inventory/items')
        
        assert response.status_code == 401
```

## :clipboard: 代码审查清单

### 提交前检查

**功能性检查：**
- [ ] 代码实现符合需求规格
- [ ] 所有业务规则得到正确实现
- [ ] 异常情况得到妥善处理
- [ ] 数据验证完整且严格

**代码质量检查：**
- [ ] 命名规范清晰且一致
- [ ] 代码结构合理，职责分离
- [ ] 避免重复代码（DRY原则）
- [ ] 注释完整且有意义

**安全性检查：**
- [ ] 输入数据得到验证和净化
- [ ] SQL注入等安全漏洞已防范
- [ ] 权限控制正确实现
- [ ] 敏感数据得到保护

**性能检查：**
- [ ] 数据库查询已优化
- [ ] 避免N+1查询问题
- [ ] 大数据量场景已考虑
- [ ] 缓存策略合理

**测试覆盖：**
- [ ] 单元测试覆盖率≥80%
- [ ] 关键业务流程有集成测试
- [ ] 异常情况有对应测试用例
- [ ] 测试用例运行通过

### 代码审查要点

1. **架构设计**：是否遵循分层架构原则
2. **业务逻辑**：是否正确理解和实现业务需求
3. **数据安全**：是否存在数据泄露风险
4. **错误处理**：是否全面处理各种异常情况
5. **代码维护性**：是否易于理解和修改



## 安全要求
- 密码加密存储
- JWT Token有效期管理
- API访问权限校验
- 租户数据严格隔离

## 错误处理
- 统一异常处理机制
- 友好的错误信息提示
- 完整的操作日志记录

# 开发环境设置

## 本地开发
1. **前端环境：**
   ```bash
   npm install
   npm run dev
   ```

2. **后端环境：**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

## 数据库
- **开发环境：** SQLite
- **初始化：** 执行数据库迁移脚本
- **测试数据：** 提供基础测试数据集

# 部署与运维

## 部署要求
- Web服务器（Nginx/Apache）
- WSGI服务器（Gunicorn/uWSGI）
- 数据库服务器（生产环境可使用PostgreSQL/MySQL）

## 监控指标
- 系统响应时间
- API调用成功率
- 数据库性能
- 用户活跃度

# 项目边界与约束

## 功能排除
- ❌ 真实在线支付功能
- ❌ 与国家药监局系统直连
- ❌ B2C功能（仅支持B2B）

## 业务约束
- 所有交易均为模拟性质
- 不可用于真实商业交易
- 监管数据仅供分析使用

# 优先级标准

## 优先级定义
- **高（High）：** 核心功能，必须实现
- **中（Medium）：** 重要功能，不影响核心流程
- **低（Low）：** 辅助功能，后续迭代

## 开发优先级
1. **第一优先级：** 账户信息管理（用户注册、企业认证、权限管理）、库存管理、B2B基础功能
2. **第二优先级：** 流通监管、数据分析
3. **第三优先级：** 智能调度、高级分析功能

# 文档与测试

## 文档要求
- API文档自动生成
- 数据库设计文档
- 用户操作手册
- 系统部署指南

## 测试要求
- 单元测试覆盖率≥80%
- 集成测试覆盖核心流程
- 性能测试验证响应时间
- 安全测试确保数据隔离