"""
配送路径规划 API 测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models import User, Tenant
import json


def test_optimize_route():
    """测试路径优化 API"""
    app = create_app('testing')
    
    with app.app_context():
        # 创建测试用户（物流公司）
        db.create_all()
        
        # 检查是否已有测试用户
        test_user = User.query.filter_by(username='test_logistics').first()
        if not test_user:
            # 注意：User 表对 email 字段有 NOT NULL 约束，测试用户需提供 email
            test_user = User(username='test_logistics', role='logistics', email='test_logistics@example.com')
            test_user.set_password('Test123!')
            db.session.add(test_user)
            db.session.commit()
            print("✓ 创建测试物流用户 (含 email)")
        else:
            print("✓ 使用已有测试物流用户")
        
        # 获取 access token
        with app.test_client() as client:
            # 登录
            login_response = client.post('/api/auth/login', 
                json={
                    'username': 'test_logistics',
                    'password': 'Test123!'
                },
                content_type='application/json'
            )
            
            if login_response.status_code != 200:
                print(f"✗ 登录失败: {login_response.data}")
                return
            
            login_data = json.loads(login_response.data)
            token = login_data['access_token']
            print("✓ 登录成功，获取 token")
            
            # 测试1: 使用经纬度坐标
            print("\n=== 测试1: 使用经纬度坐标 ===")
            test_data = {
                "start": "121.48,31.23",
                "destinations": [
                    {"name": "药店 A", "location": "121.50,31.22"},
                    {"name": "药店 B", "location": "121.51,31.21"},
                    {"name": "药店 C", "location": "121.49,31.24"}
                ],
                "use_api": False,
                "algorithm": "greedy"
            }
            
            response = client.post('/api/dispatch/optimize_route',
                json=test_data,
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            
            print(f"状态码: {response.status_code}")
            result = json.loads(response.data)
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✓ 测试1 通过")
                print(f"  起点: ({result['start']['longitude']}, {result['start']['latitude']})")
                print(f"  配送顺序:")
                for dest in result['route']:
                    print(f"    {dest['order']}. {dest['name']} - "
                          f"距上一点: {dest['distance_from_prev_text']}")
                print(f"  总距离: {result['total_distance_text']}")
            else:
                print(f"✗ 测试1 失败: {result.get('message')}")
            
            # 测试2: 使用地址（需要高德 API key 配置）
            print("\n=== 测试2: 使用地址 ===")
            test_data2 = {
                "start": "上海市浦东新区张江高科",
                "destinations": [
                    {"name": "徐汇药店", "location": "上海市徐汇区漕溪北路"},
                    {"name": "静安药店", "location": "上海市静安区南京西路"}
                ],
                "use_api": False,
                "algorithm": "greedy"
            }
            
            response2 = client.post('/api/dispatch/optimize_route',
                json=test_data2,
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            
            print(f"状态码: {response2.status_code}")
            result2 = json.loads(response2.data)
            
            if result2.get('success'):
                print("✓ 测试2 通过（地理编码成功）")
                print(f"  起点: ({result2['start']['longitude']}, {result2['start']['latitude']})")
                for dest in result2['route']:
                    print(f"    {dest['order']}. {dest['name']}")
            else:
                print(f"⚠ 测试2: {result2.get('message')}")
                print("  (这可能是因为未配置高德地图 API key)")
            
            # 测试3: 动态规划算法（小规模数据）
            print("\n=== 测试3: 动态规划算法 ===")
            test_data3 = {
                "start": "121.48,31.23",
                "destinations": [
                    {"name": "药店 A", "location": "121.50,31.22"},
                    {"name": "药店 B", "location": "121.51,31.21"},
                    {"name": "药店 C", "location": "121.49,31.24"}
                ],
                "use_api": False,
                "algorithm": "dp"
            }
            
            response3 = client.post('/api/dispatch/optimize_route',
                json=test_data3,
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            
            print(f"状态码: {response3.status_code}")
            result3 = json.loads(response3.data)
            
            if result3.get('success'):
                print("✓ 测试3 通过（动态规划算法）")
                print(f"  总距离: {result3['total_distance_text']}")
            else:
                print(f"✗ 测试3 失败: {result3.get('message')}")
            
            # 测试4: 错误处理 - 非物流用户
            print("\n=== 测试4: 权限验证 ===")
            # 创建非物流用户
            test_pharmacy = User.query.filter_by(username='test_pharmacy').first()
            if not test_pharmacy:
                # 同样为药店测试用户提供必需的 email 字段
                test_pharmacy = User(username='test_pharmacy', role='pharmacy', email='test_pharmacy@example.com')
                test_pharmacy.set_password('Test123!')
                db.session.add(test_pharmacy)
                db.session.commit()
            
            # 药店用户登录
            pharmacy_login = client.post('/api/auth/login',
                json={'username': 'test_pharmacy', 'password': 'Test123!'},
                content_type='application/json'
            )
            pharmacy_token = json.loads(pharmacy_login.data)['access_token']
            
            # 尝试访问
            response4 = client.post('/api/dispatch/optimize_route',
                json=test_data,
                headers={'Authorization': f'Bearer {pharmacy_token}'},
                content_type='application/json'
            )
            
            if response4.status_code == 403:
                print("✓ 测试4 通过（正确拒绝非物流用户访问）")
            else:
                print(f"✗ 测试4 失败（应该返回 403，实际返回 {response4.status_code}）")


def test_amap_functions():
    """测试高德地图相关函数"""
    print("\n=== 测试高德地图函数 ===")
    
    from amap import (
        AmapService, 
        calculate_distance_matrix, 
        optimize_delivery_route,
        _tsp_greedy_nearest_neighbor,
        _tsp_dynamic_programming
    )
    
    # 测试距离计算
    print("\n1. 测试 Haversine 距离计算")
    distance = AmapService.calculate_distance_haversine(121.48, 31.23, 121.50, 31.22)
    print(f"   上海浦东 -> 徐汇距离: {distance} 米 ({AmapService.format_distance(distance)})")
    
    # 测试距离矩阵
    print("\n2. 测试距离矩阵计算")
    origin = (121.48, 31.23)
    destinations = [(121.50, 31.22), (121.51, 31.21), (121.49, 31.24)]
    matrix = calculate_distance_matrix(origin, destinations, use_api=False)
    
    print(f"   距离矩阵 ({len(matrix)}x{len(matrix)}):")
    for i, row in enumerate(matrix):
        print(f"   点{i}: {[f'{d:.0f}m' for d in row]}")
    
    # 测试贪心算法
    print("\n3. 测试贪心最近邻算法")
    route = _tsp_greedy_nearest_neighbor(matrix)
    print(f"   访问顺序: {route}")
    total = sum(matrix[0 if i == 0 else route[i-1]][route[i]] for i in range(len(route)))
    print(f"   总距离: {total:.0f} 米")
    
    # 测试动态规划
    print("\n4. 测试动态规划算法")
    route_dp = _tsp_dynamic_programming(matrix)
    print(f"   访问顺序: {route_dp}")
    total_dp = sum(matrix[0 if i == 0 else route_dp[i-1]][route_dp[i]] for i in range(len(route_dp)))
    print(f"   总距离: {total_dp:.0f} 米")
    
    # 测试完整优化流程
    print("\n5. 测试完整路径优化")
    dest_list = [
        {"name": "药店A", "longitude": 121.50, "latitude": 31.22},
        {"name": "药店B", "longitude": 121.51, "latitude": 31.21},
        {"name": "药店C", "longitude": 121.49, "latitude": 31.24}
    ]
    
    optimized = optimize_delivery_route(origin, dest_list, use_api=False, algorithm='greedy')
    print(f"   优化后的配送顺序:")
    for dest in optimized:
        print(f"   {dest['order']}. {dest['name']} - "
              f"距上一点: {dest['distance_from_prev_text']}")


if __name__ == '__main__':
    print("=" * 60)
    print("配送路径规划功能测试")
    print("=" * 60)
    
    # 测试高德地图函数
    test_amap_functions()
    
    # 测试 API
    print("\n" + "=" * 60)
    print("API 接口测试")
    print("=" * 60)
    test_optimize_route()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
