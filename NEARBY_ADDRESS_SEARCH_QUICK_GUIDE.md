# 🚀 就近供应商地址搜索 - 快速使用指南

## 概述

现在系统支持**通过供应商的文字地址信息进行搜索**，无需手动设置经纬度坐标！

系统会自动调用高德地图API，将供应商的地址转换为坐标，然后计算距离并进行推荐。

## ✨ 主要特性

### ✅ 自动地理编码
- 供应商只需填写地址，无需手动设置坐标
- 系统自动通过高德地图API获取经纬度
- 支持所有有地址信息的供应商

### ✅ 智能容错
- 地理编码失败不影响其他供应商
- 明确显示失败数量和原因
- 自动跳过无效数据

### ✅ 清晰标识
- 地图上显示"📍 地址解析"标签
- 区分预存坐标和动态解析坐标
- 统计信息包含地理编码失败数量

## 🎯 使用方法

### 方式1：前端界面使用

1. **登录系统**
   - 访问 http://localhost:8080
   - 使用您的账号登录

2. **进入就近推荐页面**
   - 点击顶部导航的"就近推荐"

3. **搜索药品**
   - 输入药品名称（如：阿莫西林）
   - 选择搜索方式：
     - 使用我的位置
     - 输入地址
     - 输入坐标
   - 设置搜索半径（可选）
   - 点击"搜索"

4. **查看结果**
   - 地图上显示所有匹配的供应商
   - 列表按距离排序
   - 显示库存、价格、联系方式
   - 如果有"📍 地址解析"标识，说明坐标是通过地址自动获取的

### 方式2：API调用

#### 搜索就近供应商（使用地址）

```bash
curl -X POST http://localhost:5000/api/nearby/suppliers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "drug_name": "阿莫西林",
    "address": "北京市朝阳区望京SOHO",
    "city": "北京市",
    "max_distance": 50000,
    "limit": 10
  }'
```

#### 搜索就近供应商（使用坐标）

```bash
curl -X POST http://localhost:5000/api/nearby/suppliers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "drug_name": "布洛芬",
    "longitude": 116.470697,
    "latitude": 40.000565,
    "max_distance": 30000,
    "limit": 10
  }'
```

#### 获取所有供应商

```bash
curl -X GET http://localhost:5000/api/nearby/all-suppliers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 响应格式

```json
{
  "success": true,
  "drug_name": "阿莫西林",
  "pharmacy_location": {
    "longitude": 116.470697,
    "latitude": 40.000565
  },
  "suppliers": [
    {
      "id": 1,
      "name": "北京医药公司",
      "address": "北京市朝阳区...",
      "longitude": 116.480697,
      "latitude": 40.010565,
      "geocoded": true,        // 坐标通过地址解析
      "distance": 1289.45,
      "distance_text": "1.3km",
      "inventory": {
        "quantity": 100,
        "unit_price": 25.50,
        "drug_info": {
          "generic_name": "阿莫西林",
          "brand_name": "阿莫西林胶囊",
          "specification": "0.25g*24粒"
        }
      }
    }
  ],
  "total": 10,              // 总供应商数
  "filtered": 5,            // 符合条件的供应商数
  "geocode_failed": 2       // 地理编码失败数
}
```

## 🧪 测试

运行自动化测试：

```bash
cd backend
python test_nearby_address_search.py
```

测试将验证：
1. ✅ 登录功能
2. ✅ 获取所有供应商（含地理编码）
3. ✅ 使用地址搜索
4. ✅ 使用坐标搜索
5. ✅ 地理编码失败统计

## 💡 使用技巧

### 1. 提高地址解析成功率
- 使用完整地址：省市区 + 街道 + 门牌号
- 避免缩写和简称
- 使用标准地址格式

**好的地址示例**：
- ✅ "北京市朝阳区望京街道望京SOHO T1座"
- ✅ "上海市浦东新区张江高科技园区碧波路690号"

**不好的地址示例**：
- ❌ "北京望京"（太简略）
- ❌ "朝阳区某某路"（不完整）

### 2. 合理设置搜索半径
- 市区：10-20公里
- 郊区：30-50公里
- 全市：50-100公里

### 3. 查看地理编码结果
- 有"📍 地址解析"标识 = 坐标通过地址获取
- 无标识 = 使用数据库预存坐标

### 4. 处理失败情况
- 查看 `geocode_failed` 数量
- 如果失败率高，检查地址数据质量
- 考虑手动设置坐标

## ⚠️ 注意事项

### 1. 高德API配置
确保配置了有效的高德地图API Key：

```python
# backend/config.py
AMAP_REST_KEY = "your_amap_rest_api_key"
```

获取API Key：https://console.amap.com/

### 2. API调用限制
- 个人开发者：5000次/日
- 企业开发者：根据套餐不同
- 注意监控使用量

### 3. 响应时间
- 地理编码会增加响应时间（约0.5-1秒/供应商）
- 建议后续优化：缓存或持久化坐标

### 4. 数据质量
- 地址不准确可能导致解析失败
- 建议定期检查供应商地址数据
- 可以手动设置坐标作为备选方案

## 🔧 故障排除

### 问题1：搜索结果为空
**可能原因**：
- 没有供应商有该药品库存
- 搜索半径太小
- 所有供应商地理编码失败

**解决方案**：
- 检查 `geocode_failed` 数量
- 扩大搜索半径
- 验证供应商地址数据

### 问题2：地理编码失败率高
**可能原因**：
- 地址数据质量差
- 高德API Key无效
- API调用超限

**解决方案**：
- 检查API Key配置
- 查看API调用日志
- 改进地址数据质量
- 考虑手动设置坐标

### 问题3：地图不显示供应商
**可能原因**：
- 前端地图未正确加载
- 所有供应商都没有有效坐标
- JavaScript控制台有错误

**解决方案**：
- 检查浏览器控制台
- 验证高德地图Web API Key
- 检查网络连接

## 📚 相关文档

- [功能详细文档](NEARBY_ADDRESS_GEOCODING.md) - 技术实现细节
- [实现总结](NEARBY_ADDRESS_SEARCH_SUMMARY.md) - 完整修改说明
- [快速开始指南](NEARBY_SUPPLIERS_QUICK_START.md) - 系统安装和配置
- [使用指南](NEARBY_SUPPLIERS_USAGE_GUIDE.md) - 详细使用说明

## 📞 需要帮助？

如果遇到问题：
1. 查看相关文档
2. 检查API Key配置
3. 运行测试脚本
4. 查看错误日志
5. 提交Issue

---

**更新时间**: 2025年12月9日  
**版本**: v1.0  
**状态**: ✅ 已完成
