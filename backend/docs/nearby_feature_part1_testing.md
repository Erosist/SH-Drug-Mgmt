# 高德地图定位与就近推荐功能 - 第一部分测试指南

## 已完成功能

### 1. 配置高德地图 API
- ✅ 在 `config.py` 中配置了 AMAP_WEB_KEY 和 AMAP_REST_KEY
- ✅ API Keys 已设置好，可直接使用

### 2. 核心功能模块 (amap.py)
- ✅ **地理编码**: 将地址转换为经纬度坐标
- ✅ **距离计算**: 支持两种方式
  - Haversine 公式（快速，本地计算，不需要 API）
  - 高德地图 API（精确，考虑道路实际距离）
- ✅ **就近供应商推荐**: 根据药店位置查找最近的供应商
- ✅ **距离格式化**: 自动转换为友好的显示格式（如 1.5km, 500m）

### 3. 数据库模型更新
- ✅ 为 `Tenant` 表添加了 `latitude` 和 `longitude` 字段
- ✅ 在 `to_dict()` 方法中包含坐标信息

## 测试方法

### 方法一：运行自动化测试脚本（推荐）

```bash
# 进入 backend 目录
cd backend

# 运行测试脚本
python test_amap.py
```

**测试内容包括:**
1. 地理编码测试 - 将北京、上海、广州的地址转换为坐标
2. 距离计算测试 - 计算北京天安门到北京站的距离
3. 就近供应商推荐测试 - 模拟 3 个场景
4. 距离格式化测试 - 验证显示格式

**预期输出:**
```
############################################################
# 高德地图 API 功能测试
############################################################

============================================================
测试 1: 地理编码（地址转坐标）
============================================================

查询地址: 北京市朝阳区望京SOHO, 北京市
✓ 成功获取坐标:
  经度: 116.470697
  纬度: 40.000565
  详细地址: 北京市朝阳区望京...
  ...

============================================================
测试 2: 距离计算
============================================================

起点: 天安门 (116.397128, 39.916527)
终点: 北京站 (116.427281, 39.903738)

直线距离（Haversine）: 2.8km
驾车距离（高德 API）: 3.2km
差值: 400m

============================================================
测试 3: 就近供应商推荐
============================================================

药店位置: (116.470697, 40.000565)

测试场景 1: 搜索所有供应商（不限距离）
找到 4 个供应商:
1. 供应商B - 望京分部
   距离: 1.3km (1289.45米)
   地址: 北京市朝阳区望京
2. 供应商A - 北京总部
   距离: 10.5km (10523.67米)
   ...
```

### 方法二：手动单元测试

可以在 Python 交互式环境中逐个测试功能：

```bash
cd backend
python
```

```python
from app import create_app
from amap import AmapService, find_nearby_suppliers

# 创建应用上下文
app = create_app()
with app.app_context():
    # 测试 1: 地理编码
    result = AmapService.geocode_address("北京市朝阳区望京SOHO", "北京市")
    print(result)
    
    # 测试 2: 距离计算
    distance = AmapService.calculate_distance_haversine(
        116.397128, 39.916527,  # 天安门
        116.427281, 39.903738   # 北京站
    )
    print(f"距离: {distance}米")
    print(f"格式化: {AmapService.format_distance(distance)}")
    
    # 测试 3: 就近供应商推荐
    pharmacy_location = (116.470697, 40.000565)
    suppliers = [
        {
            'id': 1,
            'name': '供应商A',
            'longitude': 116.397128,
            'latitude': 39.916527,
            'address': '北京市东城区'
        },
        {
            'id': 2,
            'name': '供应商B',
            'longitude': 116.480697,
            'latitude': 40.010565,
            'address': '北京市朝阳区望京'
        }
    ]
    
    results = find_nearby_suppliers(
        pharmacy_location=pharmacy_location,
        suppliers=suppliers,
        max_distance=50000,  # 50公里
        limit=10,
        use_api=False
    )
    
    for supplier in results:
        print(f"{supplier['name']}: {supplier['distance_text']}")
```

### 方法三：使用 pytest 单元测试

创建正式的单元测试文件：

```bash
cd backend
pytest tests/test_amap.py -v
```

## 常见问题排查

### 1. 地理编码失败
**症状**: 返回 None 或 "地理编码失败"

**可能原因:**
- 网络连接问题
- API Key 错误或失效
- API 配额用尽
- 地址格式不正确

**解决方法:**
```bash
# 检查 API Key 配置
cd backend
python -c "from app import create_app; app = create_app(); print(app.config['AMAP_REST_KEY'])"

# 测试网络连接
curl "https://restapi.amap.com/v3/geocode/geo?key=YOUR_KEY&address=北京市"

# 检查 .env 文件
cat .env | grep AMAP
```

### 2. 距离计算为 None
**症状**: API 距离计算返回 None

**可能原因:**
- API Key 问题
- 网络问题
- 坐标格式错误

**解决方法:**
- 优先使用 Haversine 直线距离（不依赖 API）
- 设置 `use_api=False` 使用本地计算

### 3. 导入错误
**症状**: `ModuleNotFoundError: No module named 'requests'`

**解决方法:**
```bash
cd backend
pip install -r requirements.txt

# 或单独安装
pip install requests
```

### 4. Flask 应用上下文错误
**症状**: `RuntimeError: Working outside of application context`

**解决方法:**
确保在 Flask 应用上下文中运行：
```python
from app import create_app
app = create_app()
with app.app_context():
    # 你的代码
    pass
```

## 数据库迁移

如果数据库中还没有 latitude 和 longitude 字段：

```bash
cd backend

# 方法 1: 使用 Flask-Migrate
flask db migrate -m "add latitude longitude to tenant"
flask db upgrade

# 方法 2: 手动 SQL（如果使用 SQLite）
sqlite3 instance/data.db
ALTER TABLE tenants ADD COLUMN latitude FLOAT;
ALTER TABLE tenants ADD COLUMN longitude FLOAT;
.quit
```

## 验证数据库字段

```bash
cd backend
python -c "
from app import create_app
from models import Tenant

app = create_app()
with app.app_context():
    # 检查表结构
    from extensions import db
    columns = Tenant.__table__.columns
    print('Tenant 表字段:')
    for col in columns:
        print(f'  - {col.name}: {col.type}')
"
```

## 下一步计划

当前已完成第一部分：**基础 API 集成和距离计算**

等待你的确认后，将继续实现：
- 第二部分：创建 REST API 接口（nearby.py）
- 第三部分：前端界面集成
- 第四部分：自动更新供应商坐标
- 第五部分：完整的集成测试

## 成功标准

✅ 第一部分测试通过标准：
1. `test_amap.py` 运行成功，无报错
2. 地理编码能够返回正确的经纬度
3. 距离计算结果合理（直线距离 < 实际驾车距离）
4. 就近供应商能按距离正确排序
5. 距离格式化显示友好（km/m）

---

如有任何问题，请提供错误信息以便排查。
