# 配送路径规划功能 - 快速启动指南

## 🚀 5分钟快速体验

### 第一步：配置高德地图 API Key（可选）

如果需要使用地址解析功能，需要配置高德地图 API Key：

1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并创建应用（选择"Web服务"类型）
3. 获取 Key 并配置到 `backend/config.py`：

```python
class DevelopmentConfig(Config):
    # ... 其他配置 ...
    AMAP_REST_KEY = 'your_amap_rest_key_here'  # 替换为你的 Key
```

> **提示**: 如果只使用经纬度坐标输入，可以跳过此步骤！

### 第二步：启动后端服务

```bash
cd backend
python run.py
```

看到以下输出表示成功：
```
>>> Using DevelopmentConfig
* Running on http://127.0.0.1:5000
```

### 第三步：启动前端服务

打开新的终端窗口：

```bash
cd frontend
npm run dev
```

看到以下输出表示成功：
```
VITE ready in xxx ms
Local: http://localhost:5173/
```

### 第四步：登录物流用户

1. 打开浏览器访问 `http://localhost:5173`
2. 使用物流公司账号登录（如果没有，需要先注册并认证为物流公司）

### 第五步：使用智能调度功能

1. 点击顶部导航栏的 **"智能调度"**
2. 输入起点（仓库位置）
   - 方式1: 经纬度格式：`121.48,31.23`
   - 方式2: 地址格式：`上海市浦东新区张江高科`（需要配置 API Key）

3. 添加配送点（点击"+ 添加目的地"）
   - 输入名称：如 `药店 A`
   - 输入位置：如 `121.50,31.22` 或地址

4. 点击 **"计算最优配送顺序"**

5. 查看结果：
   - 左侧显示配送顺序和距离
   - 右侧地图显示路径

## 🧪 测试功能（可选）

### 运行后端测试

```bash
cd backend
python test_dispatch.py
```

### 运行演示脚本

```bash
cd backend
python demo_dispatch.py
```

演示脚本会展示：
- 距离计算
- 贪心算法 vs 动态规划
- 性能对比
- 完整优化流程

## 📝 快速示例数据

如果不知道输入什么数据，可以使用以下示例（上海市内）：

### 示例 1：使用经纬度

**起点（仓库）**: `121.48,31.23`

**配送点**:
- 药店 A: `121.50,31.22`
- 药店 B: `121.51,31.21`
- 药店 C: `121.49,31.24`
- 药店 D: `121.52,31.23`

### 示例 2：使用地址（需要 API Key）

**起点（仓库）**: `上海市浦东新区张江高科`

**配送点**:
- 徐汇药店: `上海市徐汇区漕溪北路`
- 静安药店: `上海市静安区南京西路`
- 黄浦药店: `上海市黄浦区南京东路`

## ✅ 验证功能正常工作

### 后端 API 测试

使用 curl 测试（需要先登录获取 token）：

```bash
# 登录获取 token
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_logistics_username", "password": "your_password"}'

# 使用返回的 access_token 测试路径优化
curl -X POST http://127.0.0.1:5000/api/dispatch/optimize_route \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "121.48,31.23",
    "destinations": [
      {"name": "药店A", "location": "121.50,31.22"},
      {"name": "药店B", "location": "121.51,31.21"}
    ]
  }'
```

期望看到包含 `"success": true` 的 JSON 响应。

### 前端功能测试

1. ✅ 能否看到"智能调度"导航项（仅物流用户可见）
2. ✅ 能否输入起点和配送点
3. ✅ 点击"计算最优配送顺序"后是否有响应
4. ✅ 左侧是否显示配送顺序列表
5. ✅ 右侧地图是否显示路径和标记

## ❓ 常见问题

### Q1: 无法看到"智能调度"导航项
**A**: 检查当前登录用户是否为物流公司角色（`role='logistics'`）

### Q2: 点击"计算"后提示"请先登录"
**A**: Token 可能已过期，请重新登录

### Q3: 提示"无法解析地址"
**A**: 
- 检查是否配置了高德地图 API Key
- 改用经纬度格式输入：`经度,纬度`

### Q4: 地图不显示
**A**: 
- 检查网络连接
- 确认高德地图 JS API 能正常加载
- 打开浏览器控制台查看错误信息

### Q5: 返回 403 权限错误
**A**: 只有物流公司用户可以使用此功能，请使用正确的账号登录

## 📚 进一步学习

- **详细使用指南**: `DISPATCH_ROUTE_PLANNING_GUIDE.md`
- **实现总结**: `DISPATCH_IMPLEMENTATION_SUMMARY.md`
- **API 文档**: 查看 `backend/dispatch.py` 中的接口注释

## 💡 使用技巧

1. **快速测试**: 使用经纬度格式可以快速测试，无需配置 API Key
2. **多点优化**: 配送点数量 ≤ 10 时可以尝试 `algorithm: "dp"` 获得精确最优解
3. **地图操作**: 可以缩放、拖动地图查看详细路径
4. **批量添加**: 可以先在文本编辑器准备好配送点数据，然后快速复制粘贴

## 🎉 享受使用！

配送路径规划功能可以帮助您：
- ✅ 节省配送时间和成本
- ✅ 提高配送效率
- ✅ 优化车辆调度
- ✅ 直观查看配送路径

如有问题，请查看详细文档或联系技术支持。
