#!/usr/bin/env python3
"""
测试阿莫西林胶囊下单
"""
import requests
import json

def test_amoxicillin_order():
    print('=== 测试阿莫西林胶囊下单 ===')
    
    # 登录
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
    
    if login_resp.status_code != 200:
        print(f'❌ 登录失败: {login_resp.status_code}')
        return
        
    data = login_resp.json()
    token = data['access_token']
    print('✅ 登录成功')
    
    # 测试1: 数量不足的情况 (50 < 100最小起订量)
    print('\n=== 测试数量不足的情况 (数量: 50, 起订量: 100) ===')
    order_data = {
        'supply_info_id': 1,  # 阿莫西林胶囊
        'quantity': 50,       # 小于最小起订量100
        'notes': '测试数量不足'
    }
    
    order_resp = requests.post('http://127.0.0.1:5000/api/orders',
                              json=order_data,
                              headers={'Authorization': f'Bearer {token}'})
    
    print(f'状态码: {order_resp.status_code}')
    print(f'响应: {order_resp.text}')
    
    if order_resp.status_code == 400:
        try:
            error_data = order_resp.json()
            print(f'错误信息: {error_data.get("msg", "未知错误")}')
        except:
            pass
    
    # 测试2: 正确数量的情况 (100满足最小起订量)
    print('\n=== 测试正确数量的情况 (数量: 100) ===')
    order_data = {
        'supply_info_id': 1,  # 阿莫西林胶囊
        'quantity': 100,      # 满足最小起订量
        'notes': '测试正确数量'
    }
    
    order_resp = requests.post('http://127.0.0.1:5000/api/orders',
                              json=order_data,
                              headers={'Authorization': f'Bearer {token}'})
    
    print(f'状态码: {order_resp.status_code}')
    
    if order_resp.status_code == 201:
        result = order_resp.json()
        print(f'✅ 下单成功! 订单号: {result["data"]["order_number"]}')
        print(f'   总金额: ¥{result["data"]["total_amount"]}')
    else:
        print(f'❌ 下单失败: {order_resp.text}')
        try:
            error_data = order_resp.json()
            print(f'错误信息: {error_data.get("msg", "未知错误")}')
        except:
            pass

if __name__ == "__main__":
    test_amoxicillin_order()
