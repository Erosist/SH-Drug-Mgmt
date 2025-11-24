#!/usr/bin/env python3
"""
测试当前用户的实际下单情况
"""
import requests
import json

def test_current_order():
    print('=== 测试当前用户实际下单情况 ===')
    
    # 登录pharmacy_dev
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
    
    if login_resp.status_code != 200:
        print(f'❌ 登录失败: {login_resp.status_code}')
        return
        
    data = login_resp.json()
    token = data['access_token']
    user = data['user']
    
    print(f'✅ 登录成功: {user["username"]}')
    print(f'   用户角色: {user["role"]}')
    print(f'   企业ID: {user.get("tenant_id")}')
    print(f'   企业名称: {user.get("tenant", {}).get("name", "无")}')
    
    # 模拟前端的实际下单请求（根据截图）
    print(f'\n=== 模拟前端下单请求 ===')
    order_data = {
        'supply_info_id': 1,  # 阿莫西林胶囊
        'quantity': 100,      # 用户输入的数量
        'expected_delivery_date': '2025-11-22',  # 期望交付日期
        'notes': '请输入订单备注（可选）'  # 备注
    }
    
    print(f'下单数据: {json.dumps(order_data, indent=2, ensure_ascii=False)}')
    
    # 发送下单请求
    order_resp = requests.post('http://127.0.0.1:5000/api/orders',
                              json=order_data,
                              headers={
                                  'Authorization': f'Bearer {token}',
                                  'Content-Type': 'application/json'
                              })
    
    print(f'\n下单响应状态: {order_resp.status_code}')
    
    if order_resp.status_code == 201:
        result = order_resp.json()
        print('✅ 下单成功!')
        print(f'   订单号: {result["data"]["order_number"]}')
        print(f'   总金额: ¥{result["data"]["total_amount"]}')
        print(f'   订单状态: {result["data"]["status"]}')
    else:
        print('❌ 下单失败!')
        print(f'   响应内容: {order_resp.text}')
        
        try:
            error_data = order_resp.json()
            print(f'   错误信息: {error_data.get("msg", "未知错误")}')
            if 'error' in error_data:
                print(f'   详细错误: {error_data["error"]}')
        except:
            pass
    
    # 检查用户的JWT Token是否有问题
    print(f'\n=== 验证JWT Token ===')
    me_resp = requests.get('http://127.0.0.1:5000/api/auth/me',
                          headers={'Authorization': f'Bearer {token}'})
    
    print(f'me接口状态: {me_resp.status_code}')
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        me_user = me_data.get('user', {})
        print(f'JWT解析结果: 用户ID={me_user.get("id")}, 企业ID={me_user.get("tenant_id")}, 角色={me_user.get("role")}')
    else:
        print(f'me接口失败: {me_resp.text}')

if __name__ == "__main__":
    test_current_order()
