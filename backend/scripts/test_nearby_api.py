"""
测试就近供应商推荐 API
测试所有新增的 REST API 端点
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User, Tenant
from extensions import db
from flask_jwt_extended import create_access_token


def get_test_token(username='pharmacy_user'):
    """获取测试用户的 JWT token"""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"警告: 用户 {username} 不存在，将使用第一个用户")
            # 使用第一个用户
            user = User.query.first()
            if not user:
                print("错误: 数据库中没有任何用户")
                return None
        
        # JWT identity 必须是字符串类型
        token = create_access_token(identity=str(user.id))
        print(f"使用用户: {user.username} (ID: {user.id})")
        return token


def test_geocode_api(client, token):
    """测试地理编码 API"""
    print("\n" + "="*60)
    print("测试 1: 地理编码 API (/api/nearby/geocode)")
    print("="*60)
    
    test_cases = [
        {
            "address": "北京市朝阳区望京SOHO",
            "city": "北京市"
        },
        {
            "address": "上海市浦东新区陆家嘴",
            "city": "上海市"
        }
    ]
    
    for i, data in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"  地址: {data['address']}")
        
        response = client.post(
            '/api/nearby/geocode',
            json=data,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.get_json()
            if result['success']:
                print(f"  ✓ 成功")
                print(f"    经度: {result['result']['longitude']}")
                print(f"    纬度: {result['result']['latitude']}")
                print(f"    详细地址: {result['result']['formatted_address']}")
            else:
                print(f"  ✗ 失败: {result.get('message')}")
        else:
            print(f"  ✗ HTTP 错误: {response.get_json()}")


def test_distance_api(client, token):
    """测试距离计算 API"""
    print("\n" + "="*60)
    print("测试 2: 距离计算 API (/api/nearby/distance)")
    print("="*60)
    
    test_cases = [
        {
            "name": "北京天安门到北京站（直线距离）",
            "origin": {"longitude": 116.397128, "latitude": 39.916527},
            "destination": {"longitude": 116.427281, "latitude": 39.903738},
            "use_api": False
        },
        {
            "name": "北京天安门到北京站（驾车距离）",
            "origin": {"longitude": 116.397128, "latitude": 39.916527},
            "destination": {"longitude": 116.427281, "latitude": 39.903738},
            "use_api": True
        }
    ]
    
    for i, data in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {data['name']}")
        
        response = client.post(
            '/api/nearby/distance',
            json={k: v for k, v in data.items() if k != 'name'},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.get_json()
            if result['success']:
                print(f"  ✓ 成功")
                print(f"    距离: {result['distance_text']} ({result['distance']}米)")
                print(f"    方法: {result['method']}")
            else:
                print(f"  ✗ 失败: {result.get('message')}")
        else:
            print(f"  ✗ HTTP 错误: {response.get_json()}")


def test_my_location_api(client, token):
    """测试获取当前用户位置 API"""
    print("\n" + "="*60)
    print("测试 3: 获取我的位置 API (/api/nearby/my-location)")
    print("="*60)
    
    response = client.get(
        '/api/nearby/my-location',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.get_json()
        if result['success']:
            print(f"✓ 成功")
            tenant = result['tenant']
            print(f"  租户名称: {tenant['name']}")
            print(f"  租户类型: {tenant['type']}")
            print(f"  地址: {tenant['address']}")
            print(f"  经度: {tenant.get('longitude', 'N/A')}")
            print(f"  纬度: {tenant.get('latitude', 'N/A')}")
            print(f"  是否已设置位置: {tenant['has_location']}")
        else:
            print(f"✗ 失败: {result.get('message')}")
    else:
        print(f"✗ HTTP 错误: {response.get_json()}")


def test_update_location_api(client, token):
    """测试更新位置 API"""
    print("\n" + "="*60)
    print("测试 4: 更新位置 API (/api/nearby/update-location)")
    print("="*60)
    
    test_cases = [
        {
            "name": "通过经纬度更新",
            "data": {
                "longitude": 116.470697,
                "latitude": 40.000565
            }
        },
        {
            "name": "通过地址更新",
            "data": {
                "address": "北京市朝阳区望京SOHO",
                "city": "北京市"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_case['name']}")
        
        response = client.put(
            '/api/nearby/update-location',
            json=test_case['data'],
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.get_json()
            if result['success']:
                print(f"  ✓ 成功: {result['message']}")
                print(f"    经度: {result['tenant']['longitude']}")
                print(f"    纬度: {result['tenant']['latitude']}")
            else:
                print(f"  ✗ 失败: {result.get('message')}")
        else:
            print(f"  ✗ HTTP 错误: {response.get_json()}")


def test_nearby_suppliers_api(client, token):
    """测试就近供应商推荐 API"""
    print("\n" + "="*60)
    print("测试 5: 就近供应商推荐 API (/api/nearby/suppliers)")
    print("="*60)
    
    test_cases = [
        {
            "name": "按经纬度搜索",
            "data": {
                "longitude": 116.470697,
                "latitude": 40.000565,
                "max_distance": 50000,  # 50公里
                "limit": 10,
                "use_api": False
            }
        },
        {
            "name": "按地址搜索",
            "data": {
                "address": "北京市朝阳区望京SOHO",
                "city": "北京市",
                "max_distance": 100000,  # 100公里
                "limit": 5,
                "use_api": False
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_case['name']}")
        
        response = client.post(
            '/api/nearby/suppliers',
            json=test_case['data'],
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.get_json()
            if result['success']:
                print(f"  ✓ 成功")
                print(f"    药店位置: ({result['pharmacy_location']['longitude']}, "
                      f"{result['pharmacy_location']['latitude']})")
                print(f"    总供应商数: {result['total']}")
                print(f"    符合条件: {result['filtered']}")
                
                if result['suppliers']:
                    print(f"\n    最近的供应商:")
                    for j, supplier in enumerate(result['suppliers'][:3], 1):
                        print(f"      {j}. {supplier['name']}")
                        print(f"         距离: {supplier['distance_text']}")
                        print(f"         地址: {supplier['address']}")
                else:
                    print(f"    未找到符合条件的供应商")
            else:
                print(f"  ✗ 失败: {result.get('message')}")
        else:
            print(f"  ✗ HTTP 错误: {response.get_json()}")


def prepare_test_data():
    """准备测试数据（创建一些测试供应商）"""
    print("\n准备测试数据...")
    
    app = create_app()
    with app.app_context():
        # 检查是否已有供应商
        supplier_count = Tenant.query.filter_by(type='SUPPLIER', is_active=True).count()
        
        if supplier_count == 0:
            print("警告: 数据库中没有供应商，将创建测试供应商...")
            
            test_suppliers = [
                {
                    'name': '测试供应商A - 北京',
                    'address': '北京市东城区东直门',
                    'longitude': 116.434446,
                    'latitude': 39.939629
                },
                {
                    'name': '测试供应商B - 北京',
                    'address': '北京市海淀区中关村',
                    'longitude': 116.327390,
                    'latitude': 39.978134
                },
                {
                    'name': '测试供应商C - 上海',
                    'address': '上海市黄浦区南京路',
                    'longitude': 121.473701,
                    'latitude': 31.230416
                }
            ]
            
            for supplier_data in test_suppliers:
                tenant = Tenant(
                    name=supplier_data['name'],
                    type='SUPPLIER',
                    unified_social_credit_code=f'TEST{supplier_data["name"][-1]}123456789012345',
                    legal_representative='测试代表',
                    contact_person='测试联系人',
                    contact_phone='13800138000',
                    contact_email='test@example.com',
                    address=supplier_data['address'],
                    business_scope='药品批发',
                    longitude=supplier_data['longitude'],
                    latitude=supplier_data['latitude'],
                    is_active=True
                )
                db.session.add(tenant)
            
            db.session.commit()
            print(f"✓ 创建了 {len(test_suppliers)} 个测试供应商")
        else:
            print(f"✓ 数据库中已有 {supplier_count} 个供应商")


def main():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# 就近供应商推荐 API 测试")
    print("#"*60)
    
    app = create_app()
    
    # 准备测试数据
    prepare_test_data()
    
    # 获取测试 token
    print("\n获取测试 token...")
    token = get_test_token()
    
    if not token:
        print("✗ 无法获取测试 token，测试终止")
        return
    
    print(f"✓ Token 获取成功")
    
    # 创建测试客户端
    client = app.test_client()
    
    try:
        # 运行各项测试
        test_geocode_api(client, token)
        test_distance_api(client, token)
        test_my_location_api(client, token)
        test_update_location_api(client, token)
        test_nearby_suppliers_api(client, token)
        
        print("\n" + "#"*60)
        print("# 测试完成")
        print("#"*60)
        print("\n✓ 所有 API 测试已完成")
        print("\n如果某些测试失败，请检查:")
        print("1. 数据库中是否有测试用户和供应商")
        print("2. 高德地图 API Key 是否正确配置")
        print("3. 网络连接是否正常")
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
