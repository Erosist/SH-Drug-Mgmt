"""
测试就近供应商搜索 - 使用地址地理编码功能
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def login_and_get_token():
    """登录并获取token"""
    print("1. 登录获取token...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✓ 登录成功，token: {token[:20]}...")
        return token
    else:
        print(f"✗ 登录失败: {response.text}")
        return None


def test_get_all_suppliers(token):
    """测试获取所有供应商（包含地理编码）"""
    print("\n2. 测试获取所有供应商（使用地址地理编码）...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/nearby/all-suppliers",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取成功")
        print(f"  总供应商数: {data.get('total', 0)}")
        print(f"  地理编码失败: {data.get('geocode_failed', 0)}")
        
        # 显示前3个供应商的信息
        suppliers = data.get('suppliers', [])
        for i, supplier in enumerate(suppliers[:3], 1):
            print(f"\n  供应商 {i}:")
            print(f"    名称: {supplier['name']}")
            print(f"    地址: {supplier['address']}")
            print(f"    经纬度: ({supplier.get('longitude')}, {supplier.get('latitude')})")
            if supplier.get('geocoded'):
                print(f"    📍 坐标来源: 地址地理编码")
            else:
                print(f"    📍 坐标来源: 数据库预存")
        
        return data
    else:
        print(f"✗ 获取失败: {response.text}")
        return None


def test_nearby_search(token):
    """测试就近供应商搜索（供应商通过地址获取坐标）"""
    print("\n3. 测试就近供应商搜索（供应商使用地址地理编码）...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 搜索参数
    search_data = {
        "drug_name": "阿莫西林",  # 搜索药品
        "address": "北京市朝阳区望京SOHO",  # 药店地址
        "city": "北京市",
        "max_distance": 50000,  # 50公里
        "limit": 10,
        "use_api": False  # 使用直线距离
    }
    
    print(f"\n  搜索参数:")
    print(f"    药品: {search_data['drug_name']}")
    print(f"    药店地址: {search_data['address']}")
    print(f"    搜索半径: {search_data['max_distance']/1000}km")
    
    response = requests.post(
        f"{BASE_URL}/api/nearby/suppliers",
        headers=headers,
        json=search_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ 搜索成功")
        print(f"  药品名称: {data.get('drug_name')}")
        print(f"  药店位置: ({data['pharmacy_location']['longitude']:.6f}, {data['pharmacy_location']['latitude']:.6f})")
        print(f"  找到供应商: {data.get('filtered', 0)} 个")
        print(f"  地理编码失败: {data.get('geocode_failed', 0)} 个")
        
        # 显示前5个供应商
        suppliers = data.get('suppliers', [])
        for i, supplier in enumerate(suppliers[:5], 1):
            print(f"\n  供应商 {i}: {supplier['name']}")
            print(f"    距离: {supplier['distance_text']} ({supplier['distance']:.2f}米)")
            print(f"    地址: {supplier['address']}")
            
            if supplier.get('geocoded'):
                print(f"    📍 坐标来源: 地址地理编码")
            
            if supplier.get('inventory'):
                inv = supplier['inventory']
                drug_info = inv.get('drug_info', {})
                print(f"    药品: {drug_info.get('generic_name', '')} ({drug_info.get('brand_name', '')})")
                print(f"    库存: {inv['quantity']} | 价格: ¥{inv['unit_price']}")
        
        return data
    else:
        print(f"✗ 搜索失败: {response.text}")
        return None


def test_nearby_search_by_coords(token):
    """测试使用坐标搜索（但供应商仍使用地址地理编码）"""
    print("\n4. 测试使用坐标搜索...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 搜索参数 - 使用坐标
    search_data = {
        "drug_name": "布洛芬",
        "longitude": 116.470697,  # 直接提供坐标
        "latitude": 40.000565,
        "max_distance": 30000,  # 30公里
        "limit": 5,
        "use_api": False
    }
    
    print(f"\n  搜索参数:")
    print(f"    药品: {search_data['drug_name']}")
    print(f"    药店坐标: ({search_data['longitude']}, {search_data['latitude']})")
    print(f"    搜索半径: {search_data['max_distance']/1000}km")
    
    response = requests.post(
        f"{BASE_URL}/api/nearby/suppliers",
        headers=headers,
        json=search_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ 搜索成功")
        print(f"  找到供应商: {data.get('filtered', 0)} 个")
        print(f"  地理编码失败: {data.get('geocode_failed', 0)} 个")
        
        suppliers = data.get('suppliers', [])
        for i, supplier in enumerate(suppliers[:3], 1):
            print(f"\n  供应商 {i}: {supplier['name']}")
            print(f"    距离: {supplier['distance_text']}")
            if supplier.get('geocoded'):
                print(f"    📍 坐标通过地址解析获取")
        
        return data
    else:
        print(f"✗ 搜索失败: {response.text}")
        return None


def main():
    print("=" * 60)
    print("测试就近供应商搜索 - 地址地理编码功能")
    print("=" * 60)
    
    # 登录
    token = login_and_get_token()
    if not token:
        print("\n测试失败: 无法获取token")
        return
    
    # 测试获取所有供应商
    test_get_all_suppliers(token)
    
    # 测试就近搜索（药店使用地址，供应商使用地址地理编码）
    test_nearby_search(token)
    
    # 测试坐标搜索
    test_nearby_search_by_coords(token)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
