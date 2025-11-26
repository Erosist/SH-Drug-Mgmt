#!/usr/bin/env python3
"""
详细测试前端请求的所有可能情况
"""
import requests
import json

def test_frontend_scenarios():
    print('=== 测试各种前端请求场景 ===')
    
    # 首先测试正常登录
    print('1. 测试正常登录...')
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
    
    if login_resp.status_code != 200:
        print(f'❌ 登录失败: {login_resp.status_code}')
        return
        
    data = login_resp.json()
    token = data['access_token']
    user = data['user']
    print(f'✅ 登录成功: 用户={user["username"]}, 企业ID={user.get("tenant_id")}')
    
    # 2. 测试无效的supply_info_id
    print('\n2. 测试无效的supply_info_id...')
    test_invalid_supply_id(token)
    
    # 3. 测试数量小于最小订购量
    print('\n3. 测试数量小于最小订购量...')
    test_quantity_too_small(token)
    
    # 4. 测试正确的下单请求
    print('\n4. 测试正确的下单请求...')
    test_correct_order(token)
    
    # 5. 测试token过期的情况
    print('\n5. 测试无效token...')
    test_invalid_token()

def test_invalid_supply_id(token):
    order_data = {
        'supply_info_id': 999,  # 不存在的ID
        'quantity': 100,
        'expected_delivery_date': '2025-11-22',
        'notes': '测试无效supply_info_id'
    }
    
    resp = requests.post('http://127.0.0.1:5000/api/orders',
                        json=order_data,
                        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    
    print(f'   状态码: {resp.status_code}')
    print(f'   响应: {resp.text}')

def test_quantity_too_small(token):
    order_data = {
        'supply_info_id': 1,
        'quantity': 10,  # 小于最小订购量100
        'expected_delivery_date': '2025-11-22',
        'notes': '测试数量过小'
    }
    
    resp = requests.post('http://127.0.0.1:5000/api/orders',
                        json=order_data,
                        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    
    print(f'   状态码: {resp.status_code}')
    print(f'   响应: {resp.text}')

def test_correct_order(token):
    order_data = {
        'supply_info_id': 1,
        'quantity': 100,
        'expected_delivery_date': '2025-11-22',
        'notes': '测试正确下单'
    }
    
    resp = requests.post('http://127.0.0.1:5000/api/orders',
                        json=order_data,
                        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    
    print(f'   状态码: {resp.status_code}')
    print(f'   响应: {resp.text}')

def test_invalid_token():
    order_data = {
        'supply_info_id': 1,
        'quantity': 100,
        'expected_delivery_date': '2025-11-22',
        'notes': '测试无效token'
    }
    
    resp = requests.post('http://127.0.0.1:5000/api/orders',
                        json=order_data,
                        headers={'Authorization': f'Bearer invalid_token', 'Content-Type': 'application/json'})
    
    print(f'   状态码: {resp.status_code}')
    print(f'   响应: {resp.text}')

if __name__ == "__main__":
    test_frontend_scenarios()
