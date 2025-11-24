#!/usr/bin/env python3
"""
权限调试脚本 - 测试API权限问题
"""
import requests
import json

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
        return token
    else:
        print(f"登录失败: {response.text}")
        return None

def test_orders_api(token):
    """测试订单API"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 测试不同的订单API调用
    test_cases = [
        "/api/orders",
        "/api/orders?page=1&per_page=20",
        "/api/orders?page=1&per_page=20&role_filter=my_purchases",
        "/api/orders/stats"
    ]
    
    for endpoint in test_cases:
        print(f"\n测试: {endpoint}")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"错误响应: {response.text}")
        else:
            data = response.json()
            print(f"成功响应: {data.get('msg', '数据长度: ' + str(len(str(data))))}")

def test_inventory_api(token):
    """测试库存预警API"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 测试不同的库存API调用
    test_cases = [
        "/api/v1/inventory/warnings",
        "/api/v1/inventory/warnings?warning_type=all&page=1&per_page=20",
        "/api/v1/inventory/warning-summary"
    ]
    
    for endpoint in test_cases:
        print(f"\n测试: {endpoint}")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"错误响应: {response.text}")
        else:
            data = response.json()
            print(f"成功响应: {data.get('msg', '数据长度: ' + str(len(str(data))))}")

if __name__ == "__main__":
    print("=== API权限调试工具 ===")
    
    # 登录
    token = login()
    if not token:
        exit(1)
    
    # 测试订单API
    print("\n=== 测试订单API ===")
    test_orders_api(token)
    
    # 测试库存预警API  
    print("\n=== 测试库存预警API ===")
    test_inventory_api(token)
