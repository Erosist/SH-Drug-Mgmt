#!/usr/bin/env python3
"""
详细权限调试脚本 - 深入诊断订单API权限问题
"""
import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://127.0.0.1:5000"

def login():
    """登录获取token"""
    login_data = {
        "username": "pharmacy1",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"登录状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"登录成功，Token: {token[:50]}...")
        return token, data
    else:
        print(f"登录失败: {response.text}")
        return None, None

def test_user_info(token):
    """测试用户信息API"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"\n用户信息API状态码: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"用户信息: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
        return user_data
    else:
        print(f"用户信息API错误: {response.text}")
        return None

def test_orders_detailed(token):
    """详细测试订单API的不同调用方式"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    test_cases = [
        {
            "name": "基本订单列表",
            "url": "/api/orders"
        },
        {
            "name": "带分页参数",
            "url": "/api/orders?page=1&per_page=20"
        },
        {
            "name": "前端具体调用(my_purchases)",
            "url": "/api/orders?page=1&per_page=20&role_filter=my_purchases"
        },
        {
            "name": "订单统计",
            "url": "/api/orders/stats"
        }
    ]
    
    for case in test_cases:
        print(f"\n测试: {case['name']}")
        print(f"URL: {case['url']}")
        
        response = requests.get(f"{BASE_URL}{case['url']}", headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功响应: {data.get('msg', '获取成功')}")
            if 'orders' in data:
                print(f"订单数量: {len(data.get('orders', []))}")
            if 'total' in data:
                print(f"总数: {data.get('total', 0)}")
        else:
            print(f"错误响应: {response.text}")
            # 打印响应头信息用于调试
            print(f"响应头: {dict(response.headers)}")

def test_token_validity(token):
    """测试token的有效性和解码信息"""
    import jwt
    try:
        # 不验证签名，只解码查看内容
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"\nToken内容: {json.dumps(decoded, indent=2, ensure_ascii=False)}")
        
        # 检查过期时间
        exp_timestamp = decoded.get('exp')
        if exp_timestamp:
            exp_time = datetime.fromtimestamp(exp_timestamp)
            current_time = datetime.now()
            print(f"Token过期时间: {exp_time}")
            print(f"当前时间: {current_time}")
            print(f"Token是否过期: {current_time > exp_time}")
    except Exception as e:
        print(f"Token解码失败: {e}")

if __name__ == "__main__":
    print("=== 详细权限调试工具 ===")
    
    # 登录
    token, login_data = login()
    if not token:
        exit(1)
    
    # 测试token有效性
    test_token_validity(token)
    
    # 测试用户信息
    user_data = test_user_info(token)
    
    # 详细测试订单API
    print("\n=== 详细测试订单API ===")
    test_orders_detailed(token)
