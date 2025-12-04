# 就近供应商推荐功能 - 快速开始

## 🚀 快速部署

### 1. 后端配置

#### 安装依赖（如果还没安装）
```bash
cd backend
pip install -r requirements.txt
```

#### 配置高德地图API Key
编辑 `backend/config.py`，添加你的高德地图API Key：
```python
AMAP_API_KEY = 'your_amap_api_key_here'
```

> 💡 如何获取高德地图API Key：
> 1. 访问 https://console.amap.com/
> 2. 注册/登录账号
> 3. 创建应用，选择"Web服务"类型
> 4. 复制API Key

### 2. 数据准备

#### 测试数据状态
```bash
cd backend
python test_nearby_drug_search.py
```

这会显示：
- 数据库中有多少药品
- 有多少供应商
- 哪些供应商有坐标
- 推荐测试的药品名称

#### 为供应商添加坐标（必需）
```bash
cd backend
python add_supplier_coordinates.py
```

按 `y` 确认，脚本会自动：
- 查找没有坐标的供应商
- 使用高德地图API进行地理编码
- 更新数据库中的经纬度

> ⚠️ 注意：这一步很重要！没有坐标的供应商不会在地图上显示。

### 3. 启动服务

#### 启动后端
```bash
cd backend
python run.py
```

后端服务将在 `http://localhost:5000` 运行

#### 启动前端
```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 运行

### 4. 使用功能

#### 登录系统
1. 打开浏览器访问 `http://localhost:5173`
2. 使用药店账号登录

#### 设置位置
1. 进入"就近推荐"页面
2. 如果是第一次使用，点击"更新我的位置"
3. 输入你的地址，如：`北京市朝阳区望京SOHO`
4. 确认后，地图上会显示你的位置（红色标记）

#### 查看地图
- 地图会自动显示所有供应商（灰色标记）
- 点击标记可以查看供应商信息
- 使用地图工具缩放和移动

#### 搜索药品
1. 输入药品名称，如：`阿莫西林`
2. 选择"使用我的位置"
3. 设置搜索半径（如50公里）
4. 点击"搜索供应商"

#### 查看结果
- 地图上匹配的供应商会变成蓝色大标记
- 蓝色线条显示从你到供应商的路径
- 点击蓝色标记查看库存和价格
- 下方列表显示详细的供应商信息

## 📝 示例测试流程

### 场景1：使用测试数据
```bash
# 1. 确保有测试数据
cd backend
python test_nearby_drug_search.py

# 2. 添加坐标
python add_supplier_coordinates.py

# 3. 启动服务
python run.py
```

打开前端，使用推荐的药品名称进行测试。

### 场景2：添加新数据
```python
# 在Python shell中添加测试数据
from app import create_app
from models import db, Drug, Tenant, SupplyInfo
from datetime import date, timedelta

app = create_app()
with app.app_context():
    # 添加药品
    drug = Drug(
        generic_name='阿莫西林',
        brand_name='安莫西林胶囊',
        approval_number='国药准字H12345678',
        dosage_form='胶囊剂',
        specification='0.5g*24粒',
        manufacturer='某某制药有限公司',
        category='抗生素',
        prescription_type='处方药'
    )
    db.session.add(drug)
    db.session.commit()
    
    # 添加供应商（假设已有供应商ID为1）
    supply = SupplyInfo(
        tenant_id=1,
        drug_id=drug.id,
        available_quantity=1000,
        unit_price=25.50,
        valid_until=date.today() + timedelta(days=180),
        min_order_quantity=10,
        status='ACTIVE'
    )
    db.session.add(supply)
    db.session.commit()
```

## 🔧 常见问题

### Q: 地图不显示？
**A:** 检查以下几点：
1. 浏览器控制台是否有错误
2. 高德地图API Key是否配置正确
3. 网络连接是否正常

### Q: 供应商不显示在地图上？
**A:** 
1. 运行 `python test_nearby_drug_search.py` 检查数据
2. 运行 `python add_supplier_coordinates.py` 添加坐标
3. 确认供应商的 `is_active` 字段为 `True`

### Q: 搜索没有结果？
**A:**
1. 确认输入的药品名称正确
2. 运行测试脚本查看可用的药品
3. 检查供应商是否有该药品的库存（supply_info表）
4. 尝试扩大搜索半径

### Q: 位置更新失败？
**A:**
1. 确认高德地图API Key有效
2. 输入完整准确的地址
3. 检查后端日志查看详细错误

### Q: 路径不显示？
**A:**
1. 确认药店位置已设置
2. 确认搜索到了匹配的供应商
3. 检查浏览器控制台是否有JavaScript错误

## 📊 数据检查清单

使用前确认以下数据完整：

- [ ] 数据库中有药品数据（drugs表）
- [ ] 数据库中有供应商数据（tenants表，type='SUPPLIER'）
- [ ] 供应商有地址信息（address字段）
- [ ] **供应商有坐标信息**（longitude和latitude字段）
- [ ] 有供应信息关联药品和供应商（supply_info表）
- [ ] 供应信息状态为活跃（status='ACTIVE'）
- [ ] 供应信息有库存（available_quantity > 0）

## 🎯 推荐测试步骤

### 第一次使用
1. ✅ 检查数据：`python test_nearby_drug_search.py`
2. ✅ 添加坐标：`python add_supplier_coordinates.py`
3. ✅ 启动后端：`python run.py`
4. ✅ 启动前端：`npm run dev`
5. ✅ 登录系统（药店账号）
6. ✅ 进入就近推荐页面
7. ✅ 更新我的位置
8. ✅ 查看地图上的供应商
9. ✅ 输入药品名称搜索
10. ✅ 查看高亮的匹配供应商和路径

### 日常使用
1. 打开就近推荐页面（地图自动显示）
2. 输入药品名称
3. 点击搜索
4. 查看结果和地图
5. 联系供应商或查看详情

## 📚 相关文档

- [完整使用指南](./NEARBY_SUPPLIERS_USAGE_GUIDE.md)
- [API文档](./docs/api/nearby.md)
- [后端实现](./backend/nearby.py)
- [前端组件](./frontend/src/views/NearbySuppliers.vue)

## 🆘 获取帮助

遇到问题？
1. 查看浏览器控制台错误
2. 查看后端日志
3. 运行测试脚本检查数据
4. 阅读完整使用指南

## 🎉 功能特性

- ✨ 地图自动显示所有供应商
- ✨ 按药品名称搜索
- ✨ 高亮显示匹配的供应商
- ✨ 显示药店到供应商的路径
- ✨ 显示库存和价格信息
- ✨ 支持多种定位方式
- ✨ 响应式设计，支持移动端

开始探索就近供应商推荐功能吧！🚀
