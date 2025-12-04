"""
测试高德地图 API 功能
测试内容：
1. 地理编码（地址转坐标）
2. 距离计算（Haversine 公式和 API）
3. 就近供应商推荐
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from amap import AmapService, find_nearby_suppliers


def test_geocoding():
    """测试地理编码功能"""
    print("\n" + "="*60)
    print("测试 1: 地理编码（地址转坐标）")
    print("="*60)
    
    test_addresses = [
        ("北京市朝阳区望京SOHO", "北京市"),
        ("上海市浦东新区陆家嘴", "上海市"),
        ("广州市天河区天河路", "广州市"),
    ]
    
    for address, city in test_addresses:
        print(f"\n查询地址: {address}, {city}")
        result = AmapService.geocode_address(address, city)
        
        if result:
            print(f"✓ 成功获取坐标:")
            print(f"  经度: {result['longitude']}")
            print(f"  纬度: {result['latitude']}")
            print(f"  详细地址: {result['formatted_address']}")
            print(f"  省份: {result['province']}")
            print(f"  城市: {result['city']}")
            print(f"  区县: {result['district']}")
        else:
            print(f"✗ 地理编码失败")


def test_distance_calculation():
    """测试距离计算功能"""
    print("\n" + "="*60)
    print("测试 2: 距离计算")
    print("="*60)
    
    # 测试点：北京天安门 vs 北京站
    point1 = (116.397128, 39.916527)  # 天安门
    point2 = (116.427281, 39.903738)  # 北京站
    
    print(f"\n起点: 天安门 {point1}")
    print(f"终点: 北京站 {point2}")
    
    # 直线距离（Haversine 公式）
    distance_haversine = AmapService.calculate_distance_haversine(
        point1[0], point1[1], point2[0], point2[1]
    )
    print(f"\n直线距离（Haversine）: {AmapService.format_distance(distance_haversine)}")
    
    # API 驾车距离
    print("\n正在调用高德 API 计算驾车距离...")
    distance_api = AmapService.calculate_distance_api(
        point1, point2, distance_type=1
    )
    
    if distance_api:
        print(f"驾车距离（高德 API）: {AmapService.format_distance(distance_api)}")
        diff = abs(distance_api - distance_haversine)
        print(f"差值: {AmapService.format_distance(diff)}")
    else:
        print("✗ API 距离计算失败（可能是 API Key 无效或网络问题）")


def test_nearby_suppliers():
    """测试就近供应商推荐功能"""
    print("\n" + "="*60)
    print("测试 3: 就近供应商推荐")
    print("="*60)
    
    # 模拟药店位置（北京市朝阳区望京）
    pharmacy_location = (116.470697, 40.000565)
    print(f"\n药店位置: {pharmacy_location}")
    
    # 模拟供应商数据
    suppliers = [
        {
            'id': 1,
            'name': '供应商A - 北京总部',
            'longitude': 116.397128,
            'latitude': 39.916527,
            'address': '北京市东城区'
        },
        {
            'id': 2,
            'name': '供应商B - 望京分部',
            'longitude': 116.480697,
            'latitude': 40.010565,
            'address': '北京市朝阳区望京'
        },
        {
            'id': 3,
            'name': '供应商C - 上海仓库',
            'longitude': 121.473701,
            'latitude': 31.230416,
            'address': '上海市黄浦区'
        },
        {
            'id': 4,
            'name': '供应商D - 大兴仓库',
            'longitude': 116.338611,
            'latitude': 39.726929,
            'address': '北京市大兴区'
        },
    ]
    
    print(f"\n测试场景 1: 搜索所有供应商（不限距离）")
    results1 = find_nearby_suppliers(
        pharmacy_location=pharmacy_location,
        suppliers=suppliers,
        max_distance=None,
        limit=10,
        use_api=False  # 使用直线距离
    )
    
    print(f"找到 {len(results1)} 个供应商:")
    for i, supplier in enumerate(results1, 1):
        print(f"{i}. {supplier['name']}")
        print(f"   距离: {supplier['distance_text']} ({supplier['distance']}米)")
        print(f"   地址: {supplier['address']}")
    
    print(f"\n测试场景 2: 搜索 50km 范围内的供应商")
    results2 = find_nearby_suppliers(
        pharmacy_location=pharmacy_location,
        suppliers=suppliers,
        max_distance=50000,  # 50公里
        limit=10,
        use_api=False
    )
    
    print(f"找到 {len(results2)} 个供应商（50km内）:")
    for i, supplier in enumerate(results2, 1):
        print(f"{i}. {supplier['name']}")
        print(f"   距离: {supplier['distance_text']}")
    
    print(f"\n测试场景 3: 只返回最近的 2 个供应商")
    results3 = find_nearby_suppliers(
        pharmacy_location=pharmacy_location,
        suppliers=suppliers,
        max_distance=None,
        limit=2,
        use_api=False
    )
    
    print(f"最近的 {len(results3)} 个供应商:")
    for i, supplier in enumerate(results3, 1):
        print(f"{i}. {supplier['name']} - {supplier['distance_text']}")


def test_format_distance():
    """测试距离格式化"""
    print("\n" + "="*60)
    print("测试 4: 距离格式化")
    print("="*60)
    
    test_distances = [100, 500, 999, 1000, 1500, 5234, 10000, 123456]
    
    for distance in test_distances:
        formatted = AmapService.format_distance(distance)
        print(f"{distance}米 -> {formatted}")


def main():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# 高德地图 API 功能测试")
    print("#"*60)
    
    # 创建 Flask 应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            # 测试 1: 地理编码
            test_geocoding()
            
            # 测试 2: 距离计算
            test_distance_calculation()
            
            # 测试 3: 就近供应商推荐
            test_nearby_suppliers()
            
            # 测试 4: 距离格式化
            test_format_distance()
            
            print("\n" + "#"*60)
            print("# 测试完成")
            print("#"*60)
            print("\n✓ 所有基础功能测试已完成")
            print("\n注意事项:")
            print("1. 如果地理编码或 API 距离计算失败，请检查:")
            print("   - 网络连接是否正常")
            print("   - config.py 中的 AMAP_REST_KEY 是否正确")
            print("   - 高德地图 API 配额是否充足")
            print("2. Haversine 直线距离计算不依赖 API，始终可用")
            print("3. 建议使用直线距离进行快速筛选，精确导航时再调用 API")
            
        except Exception as e:
            print(f"\n✗ 测试过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
