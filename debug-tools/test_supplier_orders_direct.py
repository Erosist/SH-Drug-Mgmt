#!/usr/bin/env python3
"""
测试供应商订单查看功能
"""
import sys
sys.path.append('backend')

import requests
import json

def test_supplier_order_viewing():
    """测试供应商查看订单"""
    print("=== 测试供应商订单查看功能 ===")
    
    base_url = "http://127.0.0.1:5000"
    
    # 1. 登录供应商
    print("\n1. 登录供应商用户 supplier1:")
    login_data = {
        "username": "supplier1",
        "password": "supplier1"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()['access_token']
            print("✓ 登录成功")
            print(f"Token: {token[:20]}...")
        else:
            print(f"✗ 登录失败: {response.json()}")
            return
    except Exception as e:
        print(f"✗ 登录异常: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 获取供应商信息（检查租户ID）
    print("\n2. 获取用户信息:")
    try:
        response = requests.get(f"{base_url}/api/auth/info", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✓ 用户: {user_info.get('username')}")
            print(f"  角色: {user_info.get('role')}")
            print(f"  租户ID: {user_info.get('tenant_id')}")
        else:
            print(f"✗ 获取用户信息失败: {response.json()}")
    except Exception as e:
        print(f"✗ 获取用户信息异常: {e}")
    
    # 3. 获取订单列表
    print("\n3. 获取订单列表:")
    try:
        response = requests.get(f"{base_url}/api/orders", headers=headers)
        if response.status_code == 200:
            orders_data = response.json()
            print(f"✓ API调用成功")
            print(f"响应结构: {list(orders_data.keys())}")
            
            if 'data' in orders_data:
                items = orders_data['data'].get('items', [])
                total = orders_data['data'].get('pagination', {}).get('total', 0)
                print(f"订单数量: {len(items)}")
                print(f"总记录数: {total}")
                
                for i, order in enumerate(items[:3]):  # 只显示前3个
                    print(f"\n  订单 {i+1}:")
                    print(f"    ID: {order.get('id')}")
                    print(f"    订单号: {order.get('order_number')}")
                    print(f"    状态: {order.get('status')}")
                    print(f"    买方租户ID: {order.get('buyer_tenant_id')}")
                    print(f"    卖方租户ID: {order.get('supplier_tenant_id')}")
                    print(f"    创建时间: {order.get('created_at')}")
                    
                    items = order.get('items', [])
                    if items:
                        print(f"    药品: {items[0].get('drug', {}).get('generic_name', '未知')}")
                        print(f"    数量: {items[0].get('quantity', 0)}")
            else:
                print(f"无效的响应格式: {orders_data}")
        else:
            print(f"✗ 获取订单失败: {response.status_code}")
            print(f"错误信息: {response.json()}")
    except Exception as e:
        print(f"✗ 获取订单异常: {e}")
    
    # 4. 测试订单统计
    print("\n4. 获取订单统计:")
    try:
        response = requests.get(f"{base_url}/api/orders/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ 统计API调用成功")
            print(f"统计数据: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        else:
            print(f"✗ 获取统计失败: {response.status_code}")
            print(f"错误信息: {response.json()}")
    except Exception as e:
        print(f"✗ 获取统计异常: {e}")

if __name__ == "__main__":
    test_supplier_order_viewing()
