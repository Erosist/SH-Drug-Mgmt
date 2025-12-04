# 就近供应商推荐功能 - 第二部分完成文档

## 📋 第二部分：REST API 接口实现

### ✅ 已完成的功能

#### 1. **新增 API 路由模块** (`nearby.py`)

创建了完整的就近推荐 API，包含 5 个端点：

##### **1.1 POST /api/nearby/suppliers** - 获取就近供应商
查找并返回按距离排序的供应商列表。

**请求示例：**
```json
{
  "longitude": 116.470697,
  "latitude": 40.000565,
  "max_distance": 50000,
  "limit": 10,
  "use_api": false
}
```

**或使用地址：**
```json
{
  "address": "北京市朝阳区望京SOHO",
  "city": "北京市",
  "max_distance": 50000,
  "limit": 10
}
```

**响应：**
```json
{
  "success": true,
  "pharmacy_location": {
    "longitude": 116.470697,
    "latitude": 40.000565
  },
  "suppliers": [
    {
      "id": 1,
      "name": "供应商名称",
      "address": "供应商地址",
      "distance": 1289.45,
      "distance_text": "1.3km",
      "contact_person": "联系人",
      "contact_phone": "电话"
    }
  ],
  "total": 10,
  "filtered": 5
}
```

##### **1.2 POST /api/nearby/geocode** - 地理编码
将地址转换为经纬度坐标。

**请求：**
```json
{
  "address": "北京市朝阳区望京SOHO",
  "city": "北京市"
}
```

**响应：**
```json
{
  "success": true,
  "result": {
    "longitude": 116.470697,
    "latitude": 40.000565,
    "formatted_address": "北京市朝阳区望京街道...",
    "province": "北京市",
    "city": "北京市",
    "district": "朝阳区"
  }
}
```

##### **1.3 POST /api/nearby/distance** - 计算距离
计算两点之间的距离（支持直线和驾车距离）。

**请求：**
```json
{
  "origin": {
    "longitude": 116.397128,
    "latitude": 39.916527
  },
  "destination": {
    "longitude": 116.427281,
    "latitude": 39.903738
  },
  "use_api": false
}
```

**响应：**
```json
{
  "success": true,
  "distance": 2823.45,
  "distance_text": "2.8km",
  "method": "haversine"
}
```

##### **1.4 GET /api/nearby/my-location** - 获取当前用户位置
获取登录用户所属租户的位置信息。

**响应：**
```json
{
  "success": true,
  "tenant": {
    "id": 1,
    "name": "药店名称",
    "type": "PHARMACY",
    "address": "详细地址",
    "longitude": 116.470697,
    "latitude": 40.000565,
    "has_location": true
  }
}
```

##### **1.5 PUT /api/nearby/update-location** - 更新位置
更新当前用户所属租户的位置信息。

**请求（方式1 - 直接坐标）：**
```json
{
  "longitude": 116.470697,
  "latitude": 40.000565
}
```

**请求（方式2 - 地址自动转换）：**
```json
{
  "address": "北京市朝阳区望京SOHO",
  "city": "北京市"
}
```

**响应：**
```json
{
  "success": true,
  "tenant": {
    "id": 1,
    "name": "药店名称",
    "longitude": 116.470697,
    "latitude": 40.000565
  },
  "message": "位置更新成功"
}
```

#### 2. **企业管理 API 扩展** (`enterprise.py`)

##### **2.1 POST /api/enterprise/tenants/batch-update-location** - 批量更新租户坐标
管理员功能，批量为租户添加地理坐标。

**权限要求：** 管理员或监管用户

**请求：**
```json
{
  "auto_geocode": true,
  "tenant_ids": [1, 2, 3]
}
```

**响应：**
```json
{
  "success": true,
  "updated": 10,
  "failed": 2,
  "total": 12,
  "details": [
    {
      "tenant_id": 1,
      "name": "供应商A",
      "status": "success",
      "longitude": 116.470697,
      "latitude": 40.000565
    }
  ]
}
```

#### 3. **批量更新工具** (`tools/batch_update_locations.py`)

命令行工具，用于批量更新租户坐标。

**使用方法：**

```bash
# 查看坐标统计
python tools/batch_update_locations.py --stats

# 更新所有缺少坐标的租户
python tools/batch_update_locations.py

# 只更新供应商
python tools/batch_update_locations.py --type SUPPLIER

# 强制更新所有租户（包括已有坐标的）
python tools/batch_update_locations.py --force

# 设置 API 调用延迟（避免配额限制）
python tools/batch_update_locations.py --delay 1.0
```

**功能特性：**
- 自动跳过已有坐标的租户
- 显示详细进度信息
- 支持按类型过滤
- API 调用频率控制
- 统计报告

#### 4. **API 测试脚本** (`scripts/test_nearby_api.py`)

自动化测试所有新增的 API 端点。

**运行测试：**
```bash
cd backend
python scripts/test_nearby_api.py
```

**测试内容：**
1. ✅ 地理编码 API
2. ✅ 距离计算 API（直线 + 驾车）
3. ✅ 获取我的位置 API
4. ✅ 更新位置 API（两种方式）
5. ✅ 就近供应商推荐 API（两种方式）

---

## 🧪 测试指南

### 快速测试流程

#### 1. 启动后端服务
```bash
cd backend
python run.py
```

#### 2. 运行 API 测试
```bash
python scripts/test_nearby_api.py
```

#### 3. 使用工具更新坐标
```bash
# 查看统计
python tools/batch_update_locations.py --stats

# 批量更新
python tools/batch_update_locations.py
```

### 使用 Postman/Apifox 测试

#### 准备工作
1. 获取 JWT Token（登录）
2. 在请求头中添加：`Authorization: Bearer {token}`

#### 测试用例

**测试 1：查找就近供应商**
```http
POST http://localhost:5000/api/nearby/suppliers
Content-Type: application/json
Authorization: Bearer {your_token}

{
  "address": "北京市朝阳区望京SOHO",
  "city": "北京市",
  "max_distance": 50000,
  "limit": 10
}
```

**测试 2：地理编码**
```http
POST http://localhost:5000/api/nearby/geocode
Content-Type: application/json
Authorization: Bearer {your_token}

{
  "address": "北京市朝阳区望京SOHO",
  "city": "北京市"
}
```

**测试 3：更新我的位置**
```http
PUT http://localhost:5000/api/nearby/update-location
Content-Type: application/json
Authorization: Bearer {your_token}

{
  "longitude": 116.470697,
  "latitude": 40.000565
}
```

---

## 📊 数据准备

### 为现有数据添加坐标

如果数据库中已有租户但缺少坐标信息：

```bash
# 1. 查看统计
python tools/batch_update_locations.py --stats

# 输出示例：
# 类型            总数       有坐标     缺少坐标   完成率    
# --------------------------------------------------------------
# PHARMACY       5          2          3          40.0%
# SUPPLIER       10         1          9          10.0%
# LOGISTICS      3          0          3          0.0%

# 2. 批量更新
python tools/batch_update_locations.py

# 3. 再次查看统计确认
python tools/batch_update_locations.py --stats
```

### 手动添加测试数据

如果需要手动添加测试供应商：

```python
from app import create_app
from models import Tenant
from extensions import db

app = create_app()
with app.app_context():
    tenant = Tenant(
        name='测试供应商',
        type='SUPPLIER',
        unified_social_credit_code='TEST123456789012345',
        legal_representative='张三',
        contact_person='李四',
        contact_phone='13800138000',
        contact_email='test@example.com',
        address='北京市朝阳区望京SOHO',
        business_scope='药品批发',
        longitude=116.470697,
        latitude=40.000565,
        is_active=True
    )
    db.session.add(tenant)
    db.session.commit()
    print(f"✓ 创建测试供应商: {tenant.id}")
```

---

## ⚠️ 常见问题

### 1. API 返回 401 Unauthorized
**原因：** Token 过期或未提供

**解决：**
- 重新登录获取新 Token
- 检查请求头是否包含 `Authorization: Bearer {token}`

### 2. 地理编码返回 None
**原因：**
- 地址格式不正确
- API Key 无效
- 网络问题

**解决：**
```python
# 检查 API Key
from app import create_app
app = create_app()
print(app.config['AMAP_REST_KEY'])

# 手动测试地理编码
from amap import AmapService
result = AmapService.geocode_address("北京市朝阳区望京SOHO", "北京市")
print(result)
```

### 3. 找不到供应商
**原因：**
- 数据库中没有供应商
- 供应商没有坐标信息
- 搜索半径太小

**解决：**
```bash
# 查看供应商统计
python tools/batch_update_locations.py --stats

# 批量添加坐标
python tools/batch_update_locations.py --type SUPPLIER

# 或增大搜索半径
# "max_distance": 100000  // 100公里
```

### 4. 批量更新时 API 超限
**原因：** 调用频率过快，超出配额

**解决：**
```bash
# 增加延迟时间
python tools/batch_update_locations.py --delay 2.0

# 或分批更新
python tools/batch_update_locations.py --type SUPPLIER
python tools/batch_update_locations.py --type PHARMACY
```

---

## 📈 性能优化建议

### 1. 距离计算优化
- **优先使用直线距离**（Haversine）进行初步筛选
- 只在需要精确导航时才调用高德 API
- 缓存常用地点的坐标

### 2. API 调用优化
- 批量更新时设置合理的延迟（0.5-1秒）
- 只更新缺少坐标的租户
- 考虑使用后台任务异步更新

### 3. 数据库优化
```sql
-- 为经纬度字段添加索引（如果数据量大）
CREATE INDEX idx_tenant_location ON tenants(longitude, latitude);
```

---

## 🎯 API 端点总览

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| POST | /api/nearby/suppliers | 查找就近供应商 | 需要登录 |
| POST | /api/nearby/geocode | 地理编码 | 需要登录 |
| POST | /api/nearby/distance | 计算距离 | 需要登录 |
| GET | /api/nearby/my-location | 获取我的位置 | 需要登录 |
| PUT | /api/nearby/update-location | 更新我的位置 | 需要登录 |
| POST | /api/enterprise/tenants/batch-update-location | 批量更新坐标 | 管理员 |

---

## ✅ 验证清单

在继续下一部分之前，请确认：

- [ ] 后端服务能正常启动
- [ ] 所有 API 端点返回正确响应
- [ ] 地理编码功能正常工作
- [ ] 距离计算准确
- [ ] 就近供应商能正确排序
- [ ] 批量更新工具能成功运行
- [ ] 测试脚本全部通过

---

## 🚀 下一步

第二部分完成！准备就绪后，将继续实现：

- **第三部分**：前端界面集成
  - 创建就近推荐组件
  - 集成地图显示
  - 添加搜索和筛选功能
  
等待你的确认后继续！
