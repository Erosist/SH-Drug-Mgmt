# 就近供应商地址搜索功能 - 更新说明

## 🎉 新功能

现在**就近供应商推荐**支持通过供应商的**文字地址**进行搜索，无需预先设置经纬度坐标！

系统会自动调用**高德地图地理编码API**，将地址转换为坐标，然后计算距离并推荐最近的供应商。

## 🔄 主要改动

### 后端 (backend/nearby.py)

1. **`/api/nearby/suppliers` 接口**
   - ✅ 移除了供应商必须有坐标的限制
   - ✅ 自动通过地址进行地理编码
   - ✅ 返回地理编码失败统计

2. **`/api/nearby/all-suppliers` 接口**
   - ✅ 返回所有有地址的供应商
   - ✅ 动态解析地址获取坐标

### 前端 (frontend/src/views/NearbySuppliers.vue)

1. **搜索结果**
   - ✅ 显示地理编码失败统计
   - ✅ 地图标记显示"📍 地址解析"标识

2. **用户提示**
   - ✅ 加载时提示地理编码情况
   - ✅ 搜索结果包含失败信息

## 📁 新增文件

```
backend/
  └── test_nearby_address_search.py      # 自动化测试脚本

文档/
  ├── NEARBY_ADDRESS_GEOCODING.md        # 功能详细文档
  ├── NEARBY_ADDRESS_SEARCH_SUMMARY.md   # 实现总结
  └── NEARBY_ADDRESS_SEARCH_QUICK_GUIDE.md  # 快速使用指南
```

## 🚀 快速使用

### 前端界面

1. 访问 http://localhost:8080
2. 点击"就近推荐"
3. 输入药品名称和位置信息
4. 查看搜索结果

### API调用

```bash
curl -X POST http://localhost:5000/api/nearby/suppliers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "drug_name": "阿莫西林",
    "address": "北京市朝阳区望京SOHO",
    "max_distance": 50000,
    "limit": 10
  }'
```

### 测试

```bash
cd backend
python test_nearby_address_search.py
```

## ✨ 核心优势

| 特性 | 改进前 | 改进后 |
|------|--------|--------|
| 供应商要求 | 必须手动设置经纬度 | 只需填写地址 |
| 数据维护 | 手动维护坐标 | 自动地理编码 |
| 覆盖范围 | 仅有坐标的供应商 | 所有有地址的供应商 |
| 灵活性 | 低 | 高 |
| 地址更新 | 需同步更新坐标 | 自动适应 |

## ⚠️ 注意事项

1. **高德API Key**：确保在 `backend/config.py` 中配置了有效的API Key
2. **API限制**：注意高德API调用次数限制（个人版：5000次/日）
3. **地址质量**：地址越详细，解析越准确
4. **性能**：首次访问会调用API，响应时间稍长

## 📚 详细文档

- [快速使用指南](NEARBY_ADDRESS_SEARCH_QUICK_GUIDE.md) - 如何使用新功能
- [功能详细文档](NEARBY_ADDRESS_GEOCODING.md) - 技术实现细节
- [实现总结](NEARBY_ADDRESS_SEARCH_SUMMARY.md) - 完整的修改说明

## 🎯 响应示例

```json
{
  "success": true,
  "drug_name": "阿莫西林",
  "suppliers": [
    {
      "name": "北京医药公司",
      "address": "北京市朝阳区...",
      "geocoded": true,        // 标识：坐标通过地址解析
      "distance": 1289.45,
      "distance_text": "1.3km",
      "inventory": { ... }
    }
  ],
  "geocode_failed": 2         // 地理编码失败的供应商数量
}
```

## 🔧 故障排除

### 地理编码失败率高？
- 检查API Key配置
- 改进地址数据质量
- 查看 `geocode_failed` 统计

### 搜索结果为空？
- 扩大搜索半径
- 检查药品库存
- 验证地址数据

更多帮助请查看 [快速使用指南](NEARBY_ADDRESS_SEARCH_QUICK_GUIDE.md)

---

**更新日期**: 2025年12月9日  
**版本**: v1.0  
**状态**: ✅ 已完成并测试
