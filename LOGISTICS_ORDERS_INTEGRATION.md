# 物流订单界面后端连接实现方案

## 📋 概述

本文档说明如何将 `LogisticsOrders.vue` 前端界面与后端 API 正确连接。

## 🔗 后端 API 详情

### 接口信息
- **URL**: `/api/logistics/orders`
- **方法**: `GET`
- **蓝图**: `logistics_bp` (已在 `backend/orders.py` 中定义)
- **注册位置**: `backend/app.py` 中通过 `register_logistics_blueprint(app)` 注册

### 权限要求
- 需要 JWT 认证 (`@jwt_required()`)
- 角色限制：`logistics` 或 `admin`
- 物流公司用户只能看到分配给自己的订单

### 返回数据结构
```json
{
  "success": true,
  "message": "获取物流订单列表成功",
  "data": [
    {
      "id": 1,
      "order_id": 1,
      "order_number": "PH20241208001",
      "pharmacy_name": "上海第一药店",
      "supplier_name": "上海医药供应商",
      "drug_name": "阿莫西林, 布洛芬",
      "quantity": 500,
      "total_amount": "5000.00",
      "status": "SHIPPED",  // SHIPPED, IN_TRANSIT, DELIVERED
      "logistics_company_id": 5,
      "logistics_company_name": "顺丰物流",
      "created_at": "2024-12-08T10:00:00",
      "updated_at": "2024-12-08T14:00:00"
    }
  ]
}
```

## 🎯 前端集成要点

### 1. API 请求配置

#### Axios 实例配置
前端需要配置带 JWT token 的 axios 实例：

```javascript
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动添加 JWT token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器：统一处理错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token 过期或无效，跳转登录
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

### 2. 数据字段映射

后端返回的字段与前端显示需要映射：

| 前端字段 | 后端字段 | 说明 |
|---------|---------|------|
| order_no | order_number | 订单号 |
| tracking_number | ❌ 缺失 | 运单号（需要后端补充） |
| batch_number | ❌ 缺失 | 药品批号（需要后端补充） |
| status | status | 订单状态 |
| address | ❌ 缺失 | 收货地址（需要后端补充） |
| updated_at | updated_at | 更新时间 |

### 3. 后端需要改进的地方

#### ⚠️ 缺失字段
当前后端接口缺少以下前端需要的字段：

1. **tracking_number**: 运单号
   - 已在 `Order` 模型中定义
   - 需要在接口中返回

2. **batch_number**: 批号
   - 存储在 `OrderItem` 模型中
   - 需要从订单明细中提取

3. **address**: 收货地址
   - 存储在药房 `Tenant` 的 `address` 字段
   - 需要从买方租户中获取

#### 建议的后端改进代码

```python
# backend/orders.py - get_logistics_orders 函数改进

@logistics_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_logistics_orders():
    """获取物流公司的订单列表"""
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        
        if current_user.role not in ['logistics', 'admin']:
            return jsonify({'msg': '权限不足'}), 403
        
        # 构建查询
        query = db.session.query(Order)
        
        # 如果是物流公司用户，只显示分配给该公司的订单
        if current_user.role == 'logistics':
            query = query.filter(Order.logistics_tenant_id == current_user.tenant_id)
        
        # 只显示物流相关的订单状态
        query = query.filter(Order.status.in_(['SHIPPED', 'IN_TRANSIT', 'DELIVERED']))
        
        # 支持筛选参数
        order_no = request.args.get('order_no')
        tracking_number = request.args.get('tracking_number')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if order_no:
            query = query.filter(Order.order_number.like(f'%{order_no}%'))
        if tracking_number:
            query = query.filter(Order.tracking_number.like(f'%{tracking_number}%'))
        if status:
            query = query.filter(Order.status == status)
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Order.updated_at >= start)
            except:
                pass
        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Order.updated_at <= end)
            except:
                pass
        
        # 按更新时间倒序排列
        query = query.order_by(desc(Order.updated_at))
        
        orders = query.all()
        
        orders_data = []
        for order in orders:
            # 获取药房信息
            pharmacy = Tenant.query.get(order.buyer_tenant_id)
            
            # 收集批号（从订单明细中获取第一个批号）
            batch_numbers = []
            for item in order.items:
                if item.batch_number:
                    batch_numbers.append(item.batch_number)
            
            orders_data.append({
                'id': order.id,
                'order_no': order.order_number,  # 前端使用的字段名
                'tracking_number': order.tracking_number,  # ✅ 新增
                'batch_number': batch_numbers[0] if batch_numbers else None,  # ✅ 新增
                'status': order.status,
                'address': pharmacy.address if pharmacy else None,  # ✅ 新增
                'updated_at': order.updated_at.isoformat() if order.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'message': '获取物流订单列表成功',
            'data': orders_data
        })
        
    except Exception as e:
        current_app.logger.error(f'获取物流订单列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': '获取物流订单列表失败',
            'error': str(e)
        }), 500
```

## 🔧 前端代码优化

### 主要改进点

1. **使用统一的 API 工具类**
   - 创建 `src/api/logistics.js` 统一管理物流相关接口
   - 自动处理 JWT token

2. **改进错误处理**
   - 区分网络错误和业务错误
   - 提供用户友好的错误提示

3. **优化数据处理**
   - 处理后端返回的数据格式
   - 添加数据验证

4. **改进加载状态**
   - 添加骨架屏或加载动画
   - 防止重复请求

### 实现步骤

#### 步骤 1: 创建 API 工具类
文件：`frontend/src/api/logistics.js`

#### 步骤 2: 创建统一的 axios 实例
文件：`frontend/src/utils/request.js`

#### 步骤 3: 更新 LogisticsOrders.vue
- 移除 mock 数据逻辑
- 使用 API 工具类
- 改进错误处理

## 📝 环境配置

### 前端环境变量
创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:5000
```

### 后端确认事项
1. ✅ 物流蓝图已注册（`app.py` 中已配置）
2. ✅ JWT 配置正确
3. ✅ CORS 允许前端域名
4. ⚠️ 需要补充接口返回字段（tracking_number, batch_number, address）

## 🧪 测试流程

### 1. 后端测试
```bash
# 测试物流订单接口
curl -X GET "http://localhost:5000/api/logistics/orders" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. 前端测试步骤
1. 以物流公司用户登录
2. 访问"订单查看"页面
3. 验证订单列表显示正确
4. 测试筛选功能
5. 测试刷新和重置功能

### 3. 权限测试
- 未登录用户：应重定向到登录页
- 非物流用户：应显示权限提示
- 物流用户：正常显示订单

## 🚀 部署注意事项

1. **生产环境 API 地址**
   - 修改 `.env.production` 中的 `VITE_API_BASE_URL`

2. **JWT Token 刷新**
   - 建议实现 token 自动刷新机制

3. **接口超时处理**
   - 设置合理的超时时间（10-30秒）

4. **日志监控**
   - 记录 API 调用失败情况

## 📚 相关文档

- 后端 API 文档：`backend/docs/`
- 认证流程：`backend/auth.py`
- 订单模型：`backend/models.py` - `Order` 类
- 路由注册：`backend/app.py`

## ❓ 常见问题

### Q1: 请求返回 401 Unauthorized
**原因**：JWT token 无效或过期
**解决**：检查 localStorage 中的 `access_token`，重新登录

### Q2: 请求返回 403 Forbidden
**原因**：当前用户不是物流角色
**解决**：确认用户角色为 `logistics`

### Q3: 返回空数组
**原因**：该物流公司没有分配的订单
**解决**：在数据库中创建测试订单，设置 `logistics_tenant_id`

### Q4: CORS 错误
**原因**：前端域名未在后端 CORS 配置中
**解决**：在 `app.py` 中添加前端域名到 `origins` 列表

## 🔄 下一步计划

- [ ] 实现订单详情查看功能
- [ ] 添加订单状态更新功能
- [ ] 实现运单号扫描功能
- [ ] 添加物流轨迹查询
- [ ] 支持导出订单列表
