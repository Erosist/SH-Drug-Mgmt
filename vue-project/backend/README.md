# Flask Auth Backend (示例)

一个最小的 Flask 后端示例，实现注册、登录并返回 JWT token，方便与前端（例如你的 Vue 项目）对接。

快速开始

1. 进入 backend 目录：

   ```bash
   cd backend
   ```

2. 创建虚拟环境并安装依赖（Windows cmd 示例）：

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 复制环境文件并修改（可选）：

   ```cmd
   copy .env.example .env
   ```

4. 初始化数据库并运行：

   ```cmd
   (这个可能不成功，建议直接python run.py)
   set FLASK_APP=run.py
   set FLASK_ENV=development
   flask run
   ```

或者运行：

   ```cmd
   python run.py
   ```

## 数据库升级提示

- 2025.11 起新增 `users.phone` 字段以及 `password_reset_codes` 表。
- 仍使用 SQLite 的情况，可重新运行 `python run.py`，脚本会自动执行缺失列/索引与表的创建。
- 如果你在生产环境中使用其他数据库，建议通过 `Flask-Migrate` 生成并执行迁移脚本（`flask db migrate && flask db upgrade`）。

API 示例（含角色 & 密码管理）

- 注册

   POST /api/auth/register
    Body (application/json): { "username": "alice", "email": "a@b.com", "phone": "13800138000", "password": "Secret123", "role": "pharmacy|supplier|logistics|regulator|unauth" }

- 登录

   POST /api/auth/login
   Body (application/json): { "username": "alice", "password": "Secret123" }
   Response: { "access_token": "...", "user": { "id":1, "username":"alice", "email":"a@b.com", "role":"pharmacy", ... } }

- 获取当前用户

  GET /api/auth/me
  Header: Authorization: Bearer <access_token>

- 修改密码

   POST /api/auth/change-password
   Header: Authorization: Bearer <access_token>
   Body: { "old_password": "旧密码", "new_password": "新密码" }
   说明：新密码需至少8位并包含大小写字母与数字；修改成功后客户端需重新登录。

- 找回密码（发送验证码）

   POST /api/auth/request-reset-code
   Body: { "identifier": "用户名/邮箱/手机号", "channel": "email|phone", "contact": "注册时绑定的邮箱或手机号" }
   返回：`expires_in=600` 表示验证码10分钟有效，开发模式额外返回 `debug_code` 便于调试。

- 找回密码（验证并重置）

   POST /api/auth/reset-password
   Body: { "identifier": "alice", "channel": "email", "contact": "a@b.com", "code": "123456", "new_password": "Secret123" }
   验证成功后立即更新密码并使验证码失效。

## 订单管理API (新增)

### 1. 创建订单（药店下单）
```
POST /api/orders
Header: Authorization: Bearer <access_token>
Body: {
  "supply_info_id": 1,
  "quantity": 50,
  "expected_delivery_date": "2025-11-25",
  "notes": "紧急补货"
}
```

### 2. 获取订单列表
```
GET /api/orders?page=1&per_page=20&status=PENDING&role_filter=my_purchases
Header: Authorization: Bearer <access_token>
```

### 3. 获取订单详情
```
GET /api/orders/{order_id}
Header: Authorization: Bearer <access_token>
```

### 4. 供应商确认/拒绝订单
```
POST /api/orders/{order_id}/confirm
Header: Authorization: Bearer <supplier_token>
Body: {
  "action": "accept",  // 或 "reject"
  "reason": "拒绝原因"  // action为reject时必填
}
```

### 5. 药店取消订单
```
POST /api/orders/{order_id}/cancel
Header: Authorization: Bearer <pharmacy_token>
Body: {
  "reason": "取消原因"  // 可选
}
```

### 6. 供应商发货
```
POST /api/orders/{order_id}/ship
Header: Authorization: Bearer <supplier_token>
Body: {
  "tracking_number": "SF1234567890",  // 可选
  "logistics_tenant_id": 5  // 可选
}
```

### 7. 药店确认收货
```
POST /api/orders/{order_id}/receive
Header: Authorization: Bearer <pharmacy_token>
Body: {
  "notes": "收货备注"  // 可选
}
```

### 8. 获取订单统计
```
GET /api/orders/stats
Header: Authorization: Bearer <access_token>
```

## ApiFox测试配置

### 本地环境测试
- **服务器地址**: http://127.0.0.1:5000
- **启动命令**: `python run.py`

### 测试账户信息
```json
{
  "药店用户": {
    "username": "pharmacy1",
    "password": "password123",
    "企业": "仁济医院药房"
  },
  "药店用户2": {
    "username": "pharmacy2", 
    "password": "password123",
    "企业": "华山医院药房"
  },
  "供应商用户": {
    "username": "supplier1",
    "password": "password123", 
    "企业": "上海医药集团股份有限公司"
  },
  "供应商用户2": {
    "username": "supplier2",
    "password": "password123",
    "企业": "华润医药商业集团有限公司"
  }
}
```

### ApiFox测试步骤

1. **导入API集合**:
   - 订单管理: `docs/Order-Management-API.postman_collection.json` 
   - 供应信息: `docs/postman/Supply-Publish-API.postman_collection.json`

2. **配置环境变量**:
   - `baseUrl`: http://127.0.0.1:5000
   - `token`: 登录后获取的JWT Token（药店和供应商共用此变量）
   - `order_id`: 测试用的订单ID（如: 1）

3. **获取Token (重要)**:
   ```bash
   # 药店用户登录
   POST {{baseUrl}}/api/auth/login
   {
     "username": "pharmacy1", 
     "password": "password123"
   }
   # 将返回的access_token设置为环境变量{{token}}
   
   # 供应商用户登录
   POST {{baseUrl}}/api/auth/login  
   {
     "username": "supplier1",
     "password": "password123" 
   }
   # 将返回的access_token设置为环境变量{{token}}
   ```

4. **测试完整下单流程**:
   - **Step 1**: 药店查看供应信息 `GET /api/supply/info` 
   - **Step 2**: 药店下单 `POST /api/orders` (记录返回的order_id)
   - **Step 3**: 切换供应商Token，查看待处理订单 `GET /api/orders?status=PENDING`
   - **Step 4**: 供应商确认订单 `POST /api/orders/{id}/confirm` 
   - **Step 5**: 供应商发货 `POST /api/orders/{id}/ship`
   - **Step 6**: 切换药店Token，确认收货 `POST /api/orders/{id}/receive`

5. **Token切换注意事项**:
   - 药店操作: 下单、取消订单、确认收货
   - 供应商操作: 确认订单、拒绝订单、发货
   - 每次切换角色时需要重新登录获取对应的Token

### 云端Mock测试
1. **导入API集合**: 使用 `docs/Supply-Publish-API.postman_collection.json`
2. **开启Mock服务**: 项目设置 → Mock设置 → 智能Mock
3. **获取Mock地址**: 类似 `https://mock.apifox.cn/m1/xxxx-xxxx`
4. **环境变量设置**: 
   - `baseUrl`: 使用ApiFox提供的Mock地址
   - `token`: Mock环境会自动生成假数据

前端对接

- 在前端登录成功后，保存返回的 access_token（例如 localStorage），并在后续请求中通过 Authorization: Bearer <token> 发送。
- **开发环境**: 可切换使用本地服务器或Mock服务器进行测试

后续改进建议

- 使用 Flask-Migrate 管理数据库迁移
- 对验证码发送增加节流 / 接入真实邮箱或短信网关
- 添加邮箱验证、重置密码
- 使用 refresh token 来延长登录会话
- 将 SECRET_KEY、JWT_SECRET_KEY 存放到更安全的机密管理中
