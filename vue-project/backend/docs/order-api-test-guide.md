# 订单API测试指南

## 快速开始

### 1. 启动后端服务
```bash
cd vue-project/backend
.venv\Scripts\activate  # Windows
python run.py
```
服务将运行在: http://127.0.0.1:5000

### 2. 导入ApiFox集合
1. 打开ApiFox
2. 导入 `docs/Order-Management-API.postman_collection.json`
3. 设置环境变量:
   - `baseUrl`: http://127.0.0.1:5000

### 3. 测试完整流程

#### Step 1: 获取认证Token
```bash
# 药店用户登录
POST http://127.0.0.1:5000/api/auth/login
{
  "username": "pharmacy1",
  "password": "password123"
}

# 供应商用户登录  
POST http://127.0.0.1:5000/api/auth/login
{
  "username": "supplier1", 
  "password": "password123"
}
```

将返回的 `access_token` 设置为环境变量 `pharmacy_token` 和 `supplier_token`。

#### Step 2: 查看可用供应信息
```bash
GET http://127.0.0.1:5000/api/supply/info
Authorization: Bearer {pharmacy_token}
```

#### Step 3: 药店下单
```bash
POST http://127.0.0.1:5000/api/orders
Authorization: Bearer {pharmacy_token}
{
  "supply_info_id": 1,  # 从供应信息列表中获取
  "quantity": 50,
  "expected_delivery_date": "2025-11-25",
  "notes": "紧急补货"
}
```

#### Step 4: 供应商查看待处理订单
```bash
GET http://127.0.0.1:5000/api/orders?status=PENDING
Authorization: Bearer {supplier_token}
```

#### Step 5: 供应商确认订单
```bash
POST http://127.0.0.1:5000/api/orders/{order_id}/confirm
Authorization: Bearer {supplier_token}
{
  "action": "accept"
}
```

#### Step 6: 供应商发货
```bash
POST http://127.0.0.1:5000/api/orders/{order_id}/ship
Authorization: Bearer {supplier_token}
{
  "tracking_number": "SF1234567890"
}
```

#### Step 7: 药店确认收货
```bash
POST http://127.0.0.1:5000/api/orders/{order_id}/receive  
Authorization: Bearer {pharmacy_token}
{
  "notes": "药品质量良好"
}
```

## 测试数据

### 现有测试账户
- **药店1**: username: `pharmacy1`, password: `password123`
- **药店2**: username: `pharmacy2`, password: `password123`  
- **供应商1**: username: `supplier1`, password: `password123`
- **供应商2**: username: `supplier2`, password: `password123`

### 现有供应信息ID
- ID 1: 阿莫西林胶囊 (上海医药集团)
- ID 2: 布洛芬片 (上海医药集团)
- ID 3: 连花清瘟胶囊 (华润医药)
- ID 4: 头孢克肟胶囊 (华润医药)
- ID 5: 奥美拉唑肠溶胶囊 (复星医药)
- ID 6: 氨溴索口服溶液 (复星医药)

## 订单状态说明

- **PENDING**: 待确认 (药店下单后的初始状态)
- **CONFIRMED**: 已确认 (供应商接受订单)  
- **SHIPPED**: 已发货 (供应商发货)
- **IN_TRANSIT**: 运输中 (物流途中)
- **DELIVERED**: 已送达 (到达目的地)
- **COMPLETED**: 已完成 (药店确认收货)
- **CANCELLED_BY_PHARMACY**: 药店取消
- **CANCELLED_BY_SUPPLIER**: 供应商拒绝
- **EXPIRED_CANCELLED**: 超时取消 (24小时未确认)

## 常见测试场景

### 场景1: 正常下单流程
1. 药店登录 → 查看供应信息 → 下单 → 供应商确认 → 发货 → 收货

### 场景2: 供应商拒绝订单
1. 药店下单 → 供应商拒绝 (库存不足等原因)

### 场景3: 药店取消订单  
1. 药店下单 → 药店主动取消 (仅PENDING状态可取消)

### 场景4: 库存不足
1. 下单数量超过可用库存 → 系统拒绝

### 场景5: 不满足最小起订量
1. 下单数量低于最小起订量 → 系统拒绝

## 错误处理

所有API都有统一的错误格式:
```json
{
  "msg": "错误描述",
  "error": "详细错误信息" 
}
```

常见HTTP状态码:
- 200: 成功
- 201: 创建成功  
- 400: 请求参数错误
- 401: 未登录
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误
