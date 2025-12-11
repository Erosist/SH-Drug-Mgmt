# 高德地图驾车路线功能配置说明

## 功能概述

智能调度界面现已支持显示**真实驾车路线**（而非简单直线）。该功能通过后端安全调用高德地图API实现，避免在浏览器端暴露敏感密钥。

## 实现方案

### 架构设计
- **前端**：`SmartDispatch.vue` 在用户选择"驾车距离（精确）"时，调用后端API获取路径坐标
- **后端**：`backend/dispatch.py` 新增 `/api/dispatch/get_driving_route` 端点
- **签名**：`backend/amap.py` 的 `AmapService.get_driving_route()` 使用安全密钥生成请求签名
- **优点**：
  - API密钥和安全密钥不暴露到前端
  - 支持高德API的签名验证机制
  - 便于统一管理、限流和缓存

## 配置步骤

### 1. 获取高德API安全密钥

1. 登录 [高德开放平台控制台](https://console.amap.com/)
2. 进入"应用管理" → 找到你的应用
3. 在应用详情中找到 **"JS API 安全密钥"** 或 **"安全密钥"** 设置
4. 复制该密钥（通常是一个32位字符串）

> **注意**：安全密钥（secret）与API Key不同，它用于对请求参数进行MD5签名验证

### 2. 配置后端环境变量

在 `backend/.env` 文件中添加以下配置：

```bash
# 高德地图API配置
AMAP_WEB_KEY=你的Web端Key（用于前端地图显示）
AMAP_REST_KEY=你的REST服务Key（用于后端API调用）
AMAP_API_SECRET=你的JS_API安全密钥（用于请求签名）
```

**示例**：
```bash
AMAP_WEB_KEY=7fdb9359ad81879b1f935cfa51dc43f0
AMAP_REST_KEY=143117d600102600e70696533eb39a5b
AMAP_API_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### 3. 如果没有安全密钥怎么办？

如果你在高德控制台找不到"安全密钥"选项，或者该功能未开启：

**方案A：不使用签名（仅适用于测试环境）**
- 确保 `AMAP_API_SECRET` 留空或不设置
- 后端代码会自动跳过签名步骤
- **注意**：这种方式可能在生产环境中被高德限制或拒绝

**方案B：使用不同的Key**
- 在高德控制台创建一个新的应用/Key
- 为该Key启用"Web服务"类型
- 确保该Key的"IP白名单"或"服务器域名"设置允许你的后端服务器访问

**方案C：联系高德技术支持**
- 如果你的账号类型不支持安全密钥，可能需要申请企业认证或升级账号

## 验证功能是否生效

### 1. 重启后端服务

配置完 `.env` 后，重启Flask后端：

```bash
cd backend
python run.py
```

### 2. 在前端测试

1. 打开浏览器，访问智能调度页面（`/service`）
2. 在左侧控制面板选择 **"驾车距离（精确）"**
3. 输入起点和目的地，点击 **"计算最优配送顺序"**
4. 打开浏览器开发者工具（F12） → Console

### 3. 观察日志输出

**成功的标志**：
```
绘制路段 1: [121.48, 31.23] -> [121.50, 31.22]
路段 1 调用后端API获取驾车路径
路段 1 驾车路径获取成功，点数: 245
路段 1 距离: 3.2km, 预计耗时: 8分钟
路段 1 驾车路线绘制成功
```

**失败的标志**：
```
路段 1 调用后端API失败: Error: Request failed with status code 400
后端返回错误: {success: false, message: "..."}
路段 1 使用直线绘制
```

如果看到失败，检查：
- 后端控制台是否有错误日志
- `.env` 文件中的 `AMAP_REST_KEY` 和 `AMAP_API_SECRET` 是否正确
- 高德控制台中该Key的配额是否用尽

## 常见问题排查

### Q1: 后端报错 "INVALID_USER_SCODE"

**原因**：高德API要求签名，但签名不正确或缺失

**解决**：
1. 确认已在 `.env` 中正确配置 `AMAP_API_SECRET`
2. 重启后端服务使配置生效
3. 检查高德控制台中该Key是否启用了"数字签名"或"安全验证"

### Q2: 后端报错 "INVALID_USER_KEY"

**原因**：`AMAP_REST_KEY` 无效或未启用Web服务

**解决**：
1. 在高德控制台检查该Key的类型，确保启用了"Web服务API"
2. 检查Key的"IP白名单"或"服务器域名"设置
3. 尝试使用另一个Key（确保该Key有"驾车路径规划"服务权限）

### Q3: 前端仍显示直线

**原因**：后端API调用失败或返回空路径

**解决**：
1. 打开浏览器Console，查看详细错误信息
2. 检查Network面板，查看 `/api/dispatch/get_driving_route` 请求的响应
3. 检查后端控制台日志，确认是否成功调用了高德API
4. 确认用户已登录且角色为"logistics"（物流公司）

### Q4: 路径点数很少或不准确

**原因**：高德API返回的路径精度较低

**可能的改进**：
- 在后端API调用时添加 `extensions=all` 参数（已实现）
- 尝试使用更精确的坐标输入
- 检查高德账号的服务等级和配额

## 技术细节

### 签名算法（已在代码中实现）

高德API签名流程：
1. 按参数名升序排列所有请求参数（不含sig）
2. 拼接为 `key1=value1&key2=value2` 格式
3. 在末尾追加安全密钥：`param_string + secret`
4. 计算MD5哈希值作为签名

示例代码（已在 `backend/amap.py` 中实现）：
```python
def generate_signature(params: Dict[str, str], secret: str) -> str:
    sorted_params = sorted(params.items())
    param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_str = param_str + secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest()
```

### API端点说明

**后端新增端点**：`POST /api/dispatch/get_driving_route`

**请求示例**：
```json
{
  "origin": "121.48,31.23",
  "destination": "121.50,31.22",
  "waypoints": ["121.49,31.23"]  // 可选
}
```

**响应示例**：
```json
{
  "success": true,
  "distance": 3245,
  "distance_text": "3.2km",
  "duration": 480,
  "duration_text": "8分钟",
  "path": [
    [121.48, 31.23],
    [121.481, 31.231],
    ...
    [121.50, 31.22]
  ]
}
```

## 相关文件

- `backend/amap.py` - 高德API集成，包含签名和驾车路径获取方法
- `backend/dispatch.py` - 配送路径规划API，包含新增的 `/get_driving_route` 端点
- `backend/config.py` - 配置管理，新增 `AMAP_API_SECRET` 配置项
- `frontend/src/views/SmartDispatch.vue` - 智能调度界面，修改为调用后端API

## 后续优化建议

1. **缓存机制**：对频繁查询的路径进行缓存，降低API调用次数和费用
2. **批量查询**：使用高德API的waypoints参数一次性获取多段路径
3. **降级策略**：当API配额用尽时自动降级为直线距离
4. **监控告警**：记录API调用次数和失败率，及时发现配额或密钥问题

---

**配置完成后**，请重启后端并在浏览器中测试。如有问题，请查看后端控制台和浏览器Console的详细日志。
