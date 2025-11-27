#!/usr/bin/env python3
"""
测试前端数据接口 - 模拟前端调用
"""
import sys
sys.path.append('backend')

from app import create_app
from config import Config
import requests
import json

def test_frontend_api_calls():
    """测试前端API调用"""
    app = create_app(Config)
    
    # 启动测试服务器
    with app.test_client() as client:
        print("=== 测试前端API调用 ===")
        
        # 1. 测试登录获取token
        print("\n1. 测试用户登录:")
        
        # 登录药店用户
        login_response = client.post('/api/auth/login', json={
            'username': 'pharmacy1',
            'password': 'pharmacy1'
        })
        print(f"药店用户登录状态: {login_response.status_code}")
        if login_response.status_code == 200:
            pharmacy_token = login_response.get_json()['access_token']
            print(f"药店用户Token获取成功")
        else:
            print(f"药店用户登录失败: {login_response.get_json()}")
            return
        
        # 登录供应商用户
        login_response = client.post('/api/auth/login', json={
            'username': 'supplier1',
            'password': 'supplier1'
        })
        login_response = client.post('/api/auth/login', json={
            'username': 'supplier1',
            'password': 'supplier1'
        })
        print(f"供应商用户登录状态: {login_response.status_code}")
        if login_response.status_code == 200:
            supplier_token = login_response.get_json()['access_token']
            print(f"供应商用户Token获取成功")
        else:
            print(f"供应商用户登录失败: {login_response.get_json()}")
            return
        
        # 2. 测试供应商信息API
        print("\n2. 测试供应商信息API (/api/supply/info):")
        response = client.get('/api/supply/info', headers={
            'Authorization': f'Bearer {supplier_token}'
        })
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"返回数据类型: {type(data)}")
            print(f"返回数据长度: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"第一条数据: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.get_json()}")
        
        # 3. 测试订单统计API
        print("\n3. 测试订单统计API (/api/orders/stats):")
        response = client.get('/api/orders/stats', headers={
            'Authorization': f'Bearer {pharmacy_token}'
        })
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"统计数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.get_json()}")
        
        # 4. 测试订单列表API
        print("\n4. 测试订单列表API (/api/orders):")
        response = client.get('/api/orders?per_page=5', headers={
            'Authorization': f'Bearer {pharmacy_token}'
        })
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            if isinstance(data, dict) and 'data' in data:
                items = data['data'].get('items', [])
                print(f"订单数量: {len(items)}")
                if len(items) > 0:
                    print(f"第一个订单: {json.dumps(items[0], indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.get_json()}")
        
        # 5. 测试供应商订单列表API
        print("\n5. 测试供应商订单列表API:")
        response = client.get('/api/orders?per_page=5', headers={
            'Authorization': f'Bearer {supplier_token}'
        })
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            if isinstance(data, dict) and 'data' in data:
                items = data['data'].get('items', [])
                print(f"供应商可见订单数量: {len(items)}")
                if len(items) > 0:
                    print(f"第一个订单: {json.dumps(items[0], indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.get_json()}")

if __name__ == "__main__":
    test_frontend_api_calls()
