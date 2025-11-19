# 上海药品流通管理系统 - 后端API文档

## 项目概述

本项目是上海药品流通管理系统的后端API服务，基于Flask框架开发，提供完整的药品流通管理功能，包括用户认证、供应信息发布、订单管理、库存预警等核心业务模块。

## 技术架构

- **框架**: Flask 2.x
- **数据库**: SQLAlchemy ORM + SQLite（开发）/ PostgreSQL（生产）
- **认证**: JWT (Flask-JWT-Extended)
- **文档**: OpenAPI/Swagger
- **任务调度**: schedule库
- **版本控制**: Git
- **部署**: Gunicorn + Nginx

## 快速开始

### 环境要求
- Python 3.8+
- pip

### 安装与运行

```bash
# 1. 克隆项目
git clone <repository-url>
cd vue-project/backend

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python init_db.py

# 5. 启动服务
python run.py
```

服务启动后访问：http://127.0.0.1:5000

## 核心功能模块

### 🔐 用户认证与授权
- JWT Token认证
- 多角色权限控制（药店、供应商、物流、监管）
- 密码安全策略
- 登录状态管理

### 📦 供应信息管理
- 供应商发布药品信息
- 库存数量管理
- 价格与规格管理
- 供应信息查询

### 🛒 订单管理系统
- 订单创建与确认
- 订单状态流转
- 发货与收货管理
- 订单统计与查询

### ⚠️ 库存预警系统
- 自动库存监控
- 低库存预警
- 近效期预警
- 定时扫描任务

### 📋 基础数据服务
- 药品目录查询
- 企业信息管理
- 库存信息查询

## API文档

### 基础信息

**服务地址**: http://127.0.0.1:5000
**API版本**: v1
**认证方式**: Bearer Token (JWT)
**数据格式**: JSON

### 通用响应格式

**成功响应**:
```json
{
    "success": true,
    "message": "操作成功",
    "data": {...}
}
```

**错误响应**:
```json
{
    "success": false,
    "error": "错误类型",
    "message": "详细错误信息"
}
```

### 📋 认证管理 `/api/auth`

#### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "pharmacy1",
    "email": "pharmacy1@example.com",
    "password": "password123",
    "role": "PHARMACY",
    "tenant_name": "仁济医院药房",
    "tenant_type": "PHARMACY",
    "contact_person": "张医生",
    "phone": "13800138001",
    "address": "上海市黄浦区人民路200号"
}
```

**角色类型**:
- `PHARMACY`: 药店
- `SUPPLIER`: 供应商  
- `LOGISTICS`: 物流商
- `REGULATOR`: 监管机构

#### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "pharmacy1",
    "password": "password123"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 1,
            "username": "pharmacy1",
            "role": "PHARMACY",
            "tenant_id": 1,
            "tenant_name": "仁济医院药房"
        }
    }
}
```

#### 3. 获取用户信息
```http
GET /api/auth/profile
Authorization: Bearer <access_token>
```

#### 4. 更新用户信息
```http
PUT /api/auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "email": "newemail@example.com",
    "phone": "13900139001"
}
```

#### 5. 修改密码
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "current_password": "oldpassword123",
    "new_password": "newpassword123"
}
```

#### 6. 登出
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

### 📦 供应信息管理 `/api/supply`

#### 1. 发布供应信息（供应商）
```http
POST /api/supply/info
Authorization: Bearer <supplier_token>
Content-Type: application/json

{
    "drug_id": 1,
    "available_quantity": 1000,
    "unit_price": 25.50,
    "description": "优质药品，现货充足",
    "expiry_date": "2025-12-31"
}
```

#### 2. 获取供应信息列表
```http
GET /api/supply/info?page=1&per_page=20&drug_name=阿司匹林
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）
- `drug_name`: 药品名称模糊搜索
- `supplier_id`: 供应商ID筛选

**响应示例**:
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": 1,
                "drug_name": "阿司匹林肠溶片",
                "supplier_name": "上海医药集团股份有限公司",
                "available_quantity": 800,
                "unit_price": 25.50,
                "description": "优质药品，现货充足",
                "created_at": "2024-11-19T10:30:00",
                "updated_at": "2024-11-19T15:20:00"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 15,
            "pages": 1
        }
    }
}
```

#### 3. 获取单个供应信息
```http
GET /api/supply/info/{supply_id}
Authorization: Bearer <access_token>
```

#### 4. 更新供应信息（供应商）
```http
PUT /api/supply/info/{supply_id}
Authorization: Bearer <supplier_token>
Content-Type: application/json

{
    "available_quantity": 800,
    "unit_price": 26.00,
    "description": "更新库存信息"
}
```

#### 5. 删除供应信息（供应商）
```http
DELETE /api/supply/info/{supply_id}
Authorization: Bearer <supplier_token>
```

### 🛒 订单管理 `/api/orders`

#### 订单状态流转图
```
PENDING → CONFIRMED → SHIPPED → IN_TRANSIT → DELIVERED → COMPLETED
   ↓           ↓
CANCELLED  CANCELLED
```

**状态说明**:
- `PENDING`: 待确认（药店已下单）
- `CONFIRMED`: 已确认（供应商确认）
- `SHIPPED`: 已发货
- `IN_TRANSIT`: 运输中
- `DELIVERED`: 已送达
- `COMPLETED`: 已完成（药店确认收货）
- `CANCELLED_BY_PHARMACY`: 药店取消
- `CANCELLED_BY_SUPPLIER`: 供应商拒绝
- `EXPIRED_CANCELLED`: 超时取消

#### 1. 创建订单（药店下单）
```http
POST /api/orders
Authorization: Bearer <pharmacy_token>
Content-Type: application/json

{
    "supply_info_id": 1,
    "quantity": 50,
    "expected_delivery_date": "2025-11-25",
    "notes": "紧急补货"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "订单创建成功",
    "data": {
        "id": 1,
        "order_number": "PH20251119001",
        "status": "PENDING",
        "total_amount": 1275.00,
        "supply_info": {
            "drug_name": "阿司匹林肠溶片",
            "supplier_name": "上海医药集团股份有限公司"
        }
    }
}
```

#### 2. 获取订单列表
```http
GET /api/orders?page=1&per_page=20&status=PENDING&role_filter=my_purchases
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）
- `status`: 订单状态筛选
- `role_filter`: 角色筛选
  - `my_purchases`: 我的采购订单（药店视角）
  - `my_sales`: 我的销售订单（供应商视角）
- `start_date`/`end_date`: 时间范围筛选（格式：YYYY-MM-DD）

#### 3. 获取订单详情
```http
GET /api/orders/{order_id}
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "order_number": "PH20251119001",
        "status": "CONFIRMED",
        "quantity": 50,
        "unit_price": 25.50,
        "total_amount": 1275.00,
        "expected_delivery_date": "2025-11-25",
        "notes": "紧急补货",
        "pharmacy": {
            "name": "仁济医院药房",
            "contact_person": "张医生"
        },
        "supplier": {
            "name": "上海医药集团股份有限公司",
            "contact_person": "李经理"
        },
        "drug": {
            "name": "阿司匹林肠溶片",
            "specification": "25mg*100片"
        },
        "created_at": "2024-11-19T09:30:00",
        "updated_at": "2024-11-19T10:15:00"
    }
}
```

#### 4. 供应商确认/拒绝订单
```http
POST /api/orders/{order_id}/confirm
Authorization: Bearer <supplier_token>
Content-Type: application/json

{
    "action": "accept",  // accept|reject
    "reason": "拒绝原因"  // action为reject时必填
}
```

#### 5. 药店取消订单
```http
POST /api/orders/{order_id}/cancel
Authorization: Bearer <pharmacy_token>
Content-Type: application/json

{
    "reason": "取消原因"  // 可选
}
```

#### 6. 供应商发货
```http
POST /api/orders/{order_id}/ship
Authorization: Bearer <supplier_token>
Content-Type: application/json

{
    "tracking_number": "SF1234567890",  // 可选
    "logistics_tenant_id": 5            // 可选
}
```

#### 7. 药店确认收货
```http
POST /api/orders/{order_id}/receive
Authorization: Bearer <pharmacy_token>
Content-Type: application/json

{
    "notes": "收货备注"  // 可选
}
```

#### 8. 获取订单统计
```http
GET /api/orders/stats
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "total_orders": 25,
        "pending_orders": 3,
        "completed_orders": 20,
        "cancelled_orders": 2,
        "total_amount": 125000.00,
        "recent_orders": [...]
    }
}
```

### ⚠️ 库存预警管理 `/api/v1/inventory`

#### 预警类型说明
- **低库存预警**: 当前库存数量 ≤ 10件
- **近效期预警**: 距离效期 ≤ 30天
- **过期预警**: 已超过效期的药品

#### 1. 获取预警列表
```http
GET /api/v1/inventory/warnings?warning_type=all&page=1&per_page=20
Authorization: Bearer <access_token>
```

**查询参数**:
- `warning_type`: 预警类型
  - `all`: 所有预警（默认）
  - `low_stock`: 仅低库存预警
  - `near_expiry`: 仅近效期预警
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20，最大100）

**响应示例**:
```json
{
    "success": true,
    "message": "获取预警列表成功",
    "data": {
        "warnings": [
            {
                "id": 1,
                "drug_name": "阿司匹林肠溶片",
                "batch_number": "20240502B01",
                "quantity": 5,
                "expiry_date": "2025-08-15",
                "days_to_expiry": 240,
                "warning_types": [
                    {
                        "type": "low_stock",
                        "message": "库存不足，当前数量：5件",
                        "severity": "warning"
                    }
                ]
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 6,
            "pages": 1
        },
        "statistics": {
            "total_warnings": 6,
            "low_stock_count": 4,
            "near_expiry_count": 4
        }
    }
}
```

#### 2. 获取预警摘要
```http
GET /api/v1/inventory/warning-summary
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_warnings": 8,
            "low_stock_count": 4,
            "near_expiry_count": 4,
            "critical_count": 2
        },
        "urgent_warnings": [
            {
                "drug_name": "阿莫西林胶囊",
                "message": "阿莫西林胶囊 已过期 10 天",
                "severity": "critical",
                "days_to_expiry": -10
            }
        ],
        "thresholds": {
            "low_stock_threshold": 10,
            "expiry_warning_days": 30
        }
    }
}
```

#### 3. 手动触发预警扫描（管理员）
```http
POST /api/v1/inventory/scan-warnings
Authorization: Bearer <admin_token>
```

**响应示例**:
```json
{
    "success": true,
    "message": "预警扫描完成",
    "data": {
        "scan_time": "2024-11-19T14:30:00",
        "items_scanned": 50,
        "warnings_found": 8,
        "new_warnings": 2
    }
}
```

### 📋 基础数据查询 `/api/catalog`

#### 1. 获取药品列表
```http
GET /api/catalog/drugs?search=阿司匹林&page=1&per_page=20
Authorization: Bearer <access_token>
```

**查询参数**:
- `search`: 药品名称模糊搜索
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）

**响应示例**:
```json
{
    "success": true,
    "data": {
        "drugs": [
            {
                "id": 1,
                "name": "阿司匹林肠溶片",
                "specification": "25mg*100片",
                "manufacturer": "上海医药股份有限公司",
                "approval_number": "国药准字H12345678"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 5,
            "pages": 1
        }
    }
}
```

#### 2. 获取企业列表
```http
GET /api/catalog/tenants?type=PHARMACY&search=医院
Authorization: Bearer <access_token>
```

**查询参数**:
- `type`: 企业类型（PHARMACY, SUPPLIER, LOGISTICS, REGULATOR）
- `search`: 企业名称模糊搜索

#### 3. 获取库存信息
```http
GET /api/catalog/inventory?tenant_id=1&drug_id=1
Authorization: Bearer <access_token>
```

## 定时任务

### 库存预警扫描任务
- **执行时间**: 每天凌晨02:00
- **任务内容**: 扫描所有库存项目，检测低库存和近效期情况
- **日志输出**: 记录扫描结果和预警数量

启动定时任务：
```bash
python task_inventory_warning.py
```

## 测试指南

### 测试账户
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

### ApiFox测试配置

#### 1. 环境配置
- **本地环境**: http://127.0.0.1:5000
- **Token变量**: `{{token}}`（用于存储JWT Token）
- **订单ID**: `{{order_id}}`（测试用订单ID）

#### 2. 测试流程

**获取Token**:
```bash
# 药店用户登录
POST {{baseUrl}}/api/auth/login
{
  "username": "pharmacy1", 
  "password": "password123"
}
# 将返回的access_token设置为环境变量{{token}}
```

**完整订单测试流程**:
1. **药店查看供应信息**: `GET /api/supply/info`
2. **药店下单**: `POST /api/orders` （记录order_id）
3. **切换供应商Token**: 重新登录supplier1
4. **查看待处理订单**: `GET /api/orders?status=PENDING`
5. **供应商确认订单**: `POST /api/orders/{id}/confirm`
6. **供应商发货**: `POST /api/orders/{id}/ship`
7. **切换药店Token**: 重新登录pharmacy1
8. **药店确认收货**: `POST /api/orders/{id}/receive`

#### 3. 导入API集合
- 订单管理: `docs/Order-Management-API.postman_collection.json`
- 供应信息: `docs/postman/Supply-Publish-API.postman_collection.json`

### 库存预警测试
1. **查看预警列表**: `GET /api/v1/inventory/warnings`
2. **查看预警摘要**: `GET /api/v1/inventory/warning-summary`
3. **手动触发扫描**: `POST /api/v1/inventory/scan-warnings`

## 部署说明

### 生产环境部署

#### 1. 环境变量配置
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/dbname
export JWT_SECRET_KEY=your-super-secret-jwt-key
export SECRET_KEY=your-flask-secret-key
```

#### 2. 使用Gunicorn部署
```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### 3. Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 数据库迁移
```bash
# 生成迁移文件
flask db migrate -m "描述信息"

# 应用迁移
flask db upgrade
```

## 开发指南

### 项目结构
```
backend/
├── app.py              # 应用工厂
├── run.py              # 启动文件
├── config.py           # 配置文件
├── extensions.py       # 扩展初始化
├── models.py           # 数据模型
├── auth.py             # 认证模块
├── supply.py           # 供应管理
├── orders.py           # 订单管理
├── inventory_warning.py # 库存预警
├── catalog.py          # 基础数据
├── init_db.py          # 数据库初始化
├── requirements.txt    # 依赖包
├── migrations/         # 数据库迁移
├── instance/           # 实例配置
├── docs/              # API文档
└── tools/             # 工具脚本
```

### 添加新功能模块

1. **创建蓝图文件**（如 `new_module.py`）:
```python
from flask import Blueprint
from flask_jwt_extended import jwt_required

new_module_bp = Blueprint('new_module', __name__)

@new_module_bp.route('/api/new-module/endpoint')
@jwt_required()
def endpoint():
    return {"success": True, "data": {}}
```

2. **注册蓝图**（在 `app.py` 中）:
```python
from new_module import new_module_bp
app.register_blueprint(new_module_bp)
```

3. **添加数据模型**（在 `models.py` 中）:
```python
class NewModel(db.Model):
    __tablename__ = 'new_models'
    
    id = db.Column(db.Integer, primary_key=True)
    # 其他字段...
```

### 代码规范
- 遵循PEP 8代码风格
- 使用类型提示
- 添加适当的注释和文档字符串
- API响应格式保持统一

## 常见问题

### Q1: Token过期怎么处理？
A: 当收到401错误时，需要重新登录获取新的Token。未来版本将支持refresh token。

### Q2: 如何处理跨域问题？
A: 已配置Flask-CORS，前端可以直接调用API。如有问题，检查CORS配置。

### Q3: 数据库连接失败？
A: 检查数据库配置和连接字符串，确保数据库服务正常运行。

### Q4: 库存预警不工作？
A: 检查定时任务是否正常运行，查看日志输出确认扫描结果。

## 更新日志

### v2.0.0 (2024-11-19)
- 🎉 新增库存预警功能
- 🔄 完善订单管理流程
- 📋 优化API响应格式
- 🛡️ 增强安全性验证
- 📖 完善API文档

### v1.1.0
- ✨ 新增供应信息管理
- 🔐 完善JWT认证
- 📊 添加订单统计功能

### v1.0.0
- 🚀 初始版本发布
- 👥 基础用户管理
- 🛒 订单管理功能

## 联系方式

如有问题或建议，请联系开发团队或提交Issue。

---

**© 2024 上海药品流通管理系统. All rights reserved.**
