# API文档中心

## 📚 API概览

上海药品信息管理与查询平台提供RESTful API接口，支持用户认证、库存管理、订单交易、物流跟踪等核心业务功能。

### 🌐 API基础信息
- **Base URL:** `http://localhost:5000/api/v1` (开发环境)
- **Base URL:** `https://api.shdrug-mgmt.com/v1` (生产环境)
- **协议:** HTTP/HTTPS
- **数据格式:** JSON
- **字符编码:** UTF-8
- **认证方式:** JWT Token

### 🔐 认证机制
```http
Authorization: Bearer <JWT_TOKEN>
```

### 📡 响应格式
所有API响应采用统一的JSON格式：

#### 成功响应
```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "message": "操作成功",
  "timestamp": "2024-10-25T10:30:00Z"
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
      "username": ["用户名不能为空"]
    }
  },
  "timestamp": "2024-10-25T10:30:00Z"
}
```

### 📋 HTTP状态码

| 状态码 | 说明 | 示例场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功，无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或认证失败 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如重复创建） |
| 422 | Unprocessable Entity | 业务规则验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

## 📂 API分类

### 1. 认证与用户管理
- **[认证接口](Authentication.md)** - 用户登录、注册、Token刷新
- **[用户管理](UserManagement.md)** - 用户信息、密码管理

### 2. 企业认证管理
- **[企业认证](EnterpriseCertification.md)** - 认证申请、审核查询

### 3. 库存管理
- **[库存操作](Inventory.md)** - 库存CRUD、库存预警

### 4. 药品信息
- **[药品管理](Drugs.md)** - 药品信息查询、药品分类

### 5. 供求平台
- **[供应信息](SupplyInfo.md)** - 供应信息发布、查询
- **[订单管理](Orders.md)** - 订单创建、状态管理

### 6. 物流管理
- **[流通记录](Circulation.md)** - 流通数据上报
- **[物流跟踪](Logistics.md)** - 运输状态更新

### 7. 监管分析
- **[数据分析](Analytics.md)** - 监管数据、统计报表
- **[系统监控](Monitoring.md)** - 系统状态、性能指标

## 🚀 快速开始

### 1. 获取访问令牌
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "pharmacy_user",
    "password": "password123"
  }'
```

### 2. 使用令牌访问API
```bash
curl -X GET http://localhost:5000/api/v1/inventory/items \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json"
```

## 🔧 开发工具

### 在线文档
- **Swagger UI:** `http://localhost:5000/docs`
- **ReDoc:** `http://localhost:5000/redoc`

### 测试工具
- **Postman Collection:** 下载API测试集合
- **OpenAPI Specification:** `http://localhost:5000/openapi.json`

### SDK支持
- **JavaScript SDK:** npm install `shdrug-mgmt-js`
- **Python SDK:** pip install `shdrug-mgmt-py`

## 📝 API变更日志

### v1.0.0 (2024-10-25)
- ✅ 初始版本发布
- ✅ 用户认证和基础CRUD接口
- ✅ 库存管理和订单系统
- ✅ 物流跟踪和监管分析

### 计划中的功能
- 🔄 WebSocket实时推送
- 🔄 批量操作接口
- 🔄 高级搜索和筛选
- 🔄 数据导出功能

## 🛡️ 安全说明

### 访问控制
- 所有API（除登录注册外）都需要JWT Token认证
- 基于角色的权限控制（RBAC）
- 租户数据严格隔离

### 请求限制
- **频率限制：** 每分钟100次请求
- **数据大小：** 请求体最大10MB
- **并发连接：** 每用户最多10个并发连接

### 数据保护
- HTTPS加密传输
- 敏感数据脱敏处理
- 操作日志完整记录

## 🆘 故障排除

### 常见错误
1. **401 Unauthorized**
   - 检查Token是否有效
   - 确认Token未过期

2. **403 Forbidden**
   - 检查用户权限
   - 确认租户访问权限

3. **422 Unprocessable Entity**
   - 检查请求数据格式
   - 确认业务规则约束

### 联系支持
- **技术支持邮箱：** support@shdrug-mgmt.com
- **API状态页面：** https://status.shdrug-mgmt.com
- **开发者社区：** https://community.shdrug-mgmt.com

---

**文档版本：** v1.0.0
**最后更新：** 2024-10-25
**维护团队：** API开发团队