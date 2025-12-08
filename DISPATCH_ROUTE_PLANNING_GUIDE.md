# 配送路径规划功能使用指南

## 功能概述

为物流公司用户提供多目的地配送路径优化服务，支持：
- 自动地理编码（地址转坐标）
- 智能路径优化（贪心算法 / 动态规划）
- 地图可视化展示
- 从订单数据自动获取配送点

## 后端实现

### 核心文件

1. **backend/amap.py** - 高德地图集成
   - 地理编码（地址 → 坐标）
   - 距离计算（直线距离 / 驾车距离）
   - 距离矩阵计算
   - TSP 路径优化算法

2. **backend/dispatch.py** - 配送路径规划 API
   - `POST /api/dispatch/optimize_route` - 路径优化
   - `GET /api/dispatch/orders_destinations` - 获取订单配送点
   - `POST /api/dispatch/geocode` - 地理编码

### 核心算法

#### 1. 贪心最近邻算法（Greedy Nearest Neighbor）
- **适用场景**: 配送点较多（> 15 个）
- **时间复杂度**: O(n²)
- **特点**: 快速，效果较好（通常在最优解的 1.2 倍以内）

#### 2. 动态规划算法（Dynamic Programming）
- **适用场景**: 配送点较少（≤ 15 个）
- **时间复杂度**: O(n² × 2ⁿ)
- **特点**: 精确最优解，但数量多时性能较差

### API 使用示例

#### 1. 路径优化

```bash
curl -X POST http://127.0.0.1:5000/api/dispatch/optimize_route \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "121.48,31.23",
    "destinations": [
      {"name": "药店 A", "location": "121.50,31.22"},
      {"name": "药店 B", "location": "121.51,31.21"},
      {"name": "药店 C", "location": "121.49,31.24"}
    ],
    "use_api": false,
    "algorithm": "greedy"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "start": {
    "longitude": 121.48,
    "latitude": 31.23
  },
  "route": [
    {
      "name": "药店 A",
      "longitude": 121.5,
      "latitude": 31.22,
      "order": 1,
      "distance_from_prev": 2534.5,
      "distance_from_prev_text": "2.5km"
    },
    {
      "name": "药店 C",
      "longitude": 121.49,
      "latitude": 31.24,
      "order": 2,
      "distance_from_prev": 2892.3,
      "distance_from_prev_text": "2.9km"
    },
    {
      "name": "药店 B",
      "longitude": 121.51,
      "latitude": 31.21,
      "order": 3,
      "distance_from_prev": 3845.7,
      "distance_from_prev_text": "3.8km"
    }
  ],
  "total_distance": 9272.5,
  "total_distance_text": "9.3km",
  "algorithm": "greedy",
  "use_api": false
}
```

#### 2. 地理编码

```bash
curl -X POST http://127.0.0.1:5000/api/dispatch/geocode \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "上海市浦东新区张江高科",
    "city": "上海市"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "longitude": 121.60491,
  "latitude": 31.209492,
  "formatted_address": "上海市浦东新区张江高科技园区",
  "province": "上海市",
  "city": "上海市",
  "district": "浦东新区"
}
```

#### 3. 获取待配送订单目的地

```bash
curl -X GET "http://127.0.0.1:5000/api/dispatch/orders_destinations?status=pending,confirmed&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "success": true,
  "destinations": [
    {
      "order_id": 123,
      "name": "某某药店",
      "address": "上海市徐汇区xxx路",
      "longitude": 121.5,
      "latitude": 31.22,
      "contact_phone": "021-12345678",
      "order_created_at": "2025-12-07T10:30:00"
    }
  ],
  "count": 1
}
```

## 前端使用

### 页面访问

物流公司用户登录后，点击导航栏 **"智能调度"** 进入配送路径规划页面。

### 功能操作

1. **输入起点**
   - 支持经纬度格式：`121.48,31.23`
   - 支持地址格式：`上海市浦东新区张江高科`

2. **添加目的地**
   - 点击"+ 添加目的地"按钮
   - 输入目的地名称和位置
   - 支持多个目的地

3. **计算路径**
   - 点击"计算最优配送顺序"按钮
   - 系统自动调用后端API进行路径优化
   - 结果显示在右侧列表和地图上

4. **查看结果**
   - 左侧显示配送顺序和距离信息
   - 右侧地图高亮显示路径
   - 节点标注清晰

### 地图功能

- **起点标记**: 特殊图标标记仓库位置
- **目的地标记**: 数字标签显示访问顺序
- **路线绘制**: 蓝色线条连接各配送点（实际道路路径）
- **自动缩放**: 地图自动调整到合适的视野范围

## 配置说明

### 高德地图 API Key

需要在 `backend/config.py` 中配置高德地图 API Key：

```python
class Config:
    # 高德地图 REST API Key
    AMAP_REST_KEY = 'your_amap_rest_key_here'
```

获取 API Key 的步骤：
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并登录
3. 创建应用，选择 "Web服务" 类型
4. 获取 Key 并配置到项目中

### 权限控制

- 仅物流公司用户（role='logistics'）可访问配送路径规划功能
- 其他角色用户访问会返回 403 Forbidden

## 测试

运行后端测试：

```bash
cd backend
python test_dispatch.py
```

测试内容包括：
- 高德地图函数（距离计算、地理编码）
- TSP 算法（贪心、动态规划）
- API 接口（路径优化、权限验证）

## 技术特点

### 1. 灵活的输入方式
- 支持经纬度坐标（快速）
- 支持地址文本（自动地理编码）
- 混合输入（部分坐标、部分地址）

### 2. 智能路径优化
- 贪心算法：O(n²)，适合大规模
- 动态规划：O(n² × 2ⁿ)，精确最优解
- 自动选择算法

### 3. 距离计算
- 直线距离：Haversine 公式（快速）
- 驾车距离：高德 API（准确，需要 API 额外调用）

### 4. 可视化
- 地图标记清晰
- 路线高亮展示
- 实时更新

## 扩展功能建议

1. **从订单自动导入**
   - 一键导入待配送订单的目的地
   - 自动填充配送点信息

2. **配送时间窗**
   - 支持指定每个配送点的时间窗口
   - 优化算法考虑时间约束

3. **车辆容量**
   - 支持多车辆配送
   - 考虑车辆载重限制

4. **实时路况**
   - 使用高德 API 获取实时路况
   - 动态调整路径

5. **历史记录**
   - 保存配送路径规划历史
   - 支持导出和复用

6. **导航导出**
   - 导出为导航软件可识别的格式
   - 生成配送任务单

## 性能优化

1. **缓存地理编码结果**
   - 对常用地址建立缓存
   - 减少 API 调用次数

2. **异步处理**
   - 大量配送点时使用后台任务
   - WebSocket 实时推送结果

3. **批量查询**
   - 使用高德批量距离查询 API
   - 减少网络请求次数

## 故障排查

### 问题 1: 地理编码失败
- **原因**: 未配置高德 API Key 或 Key 无效
- **解决**: 检查 `config.py` 中的 `AMAP_REST_KEY` 配置

### 问题 2: 路径优化超时
- **原因**: 配送点过多，动态规划算法性能不足
- **解决**: 配送点 > 15 个时使用贪心算法

### 问题 3: 地图不显示
- **原因**: 前端高德地图 JS API Key 未配置
- **解决**: 检查 `frontend/index.html` 中的高德地图 JS API 引入

### 问题 4: 403 权限错误
- **原因**: 当前用户不是物流公司角色
- **解决**: 使用物流公司账号登录

## 相关文档

- [高德地图 Web 服务 API 文档](https://lbs.amap.com/api/webservice/summary)
- [高德地图 JavaScript API 文档](https://lbs.amap.com/api/javascript-api/summary)
- [TSP 问题介绍](https://en.wikipedia.org/wiki/Travelling_salesman_problem)

## 更新日志

### v1.0.0 (2025-12-07)
- ✅ 基础路径优化功能
- ✅ 地理编码支持
- ✅ 地图可视化
- ✅ 贪心和动态规划算法
- ✅ 权限控制
- ✅ 单元测试
