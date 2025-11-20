#!/usr/bin/env python3
"""
调试前端下单问题
"""
import requests
import json

def debug_order_issue():
    print('=== 调试下单问题 ===')
    
    # 1. 测试登录
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code} - {login_resp.text}")
        return
        
    data = login_resp.json()
    token = data['access_token']
    user = data['user']
    
    print(f"✅ 登录成功: {user['username']}")
    print(f"   企业ID: {user.get('tenant_id')}")
    print(f"   角色: {user['role']}")
    
    if user.get('tenant'):
        print(f"   企业名称: {user['tenant']['name']}")
    else:
        print("   ⚠️ 企业信息: 无")
    
    # 2. 测试JWT Token的用户查询
    me_resp = requests.get('http://127.0.0.1:5000/api/auth/me',
                          headers={'Authorization': f'Bearer {token}'})
    
    print(f"\n=== JWT Token验证 ===")
    print(f"me接口状态: {me_resp.status_code}")
    
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        me_user = me_data.get('user', {})
        print(f"JWT解析的用户: {me_user.get('username')}")
        print(f"JWT解析的企业ID: {me_user.get('tenant_id')}")
        print(f"JWT解析的角色: {me_user.get('role')}")
    else:
        print(f"❌ me接口失败: {me_resp.text}")
        return
    
    # 3. 直接测试订单API的权限检查
    print(f"\n=== 测试订单API权限 ===")
    
    # 先测试一个简单的订单列表获取
    orders_resp = requests.get('http://127.0.0.1:5000/api/orders',
                              headers={'Authorization': f'Bearer {token}'})
    
    print(f"订单列表API: {orders_resp.status_code}")
    if orders_resp.status_code != 200:
        print(f"❌ 订单列表失败: {orders_resp.text}")
    
    # 4. 测试具体的下单API
    print(f"\n=== 测试下单API ===")
    
    # 获取供应信息
    supply_resp = requests.get('http://127.0.0.1:5000/api/supply/info?per_page=1',
                              headers={'Authorization': f'Bearer {token}'})
    
    if supply_resp.status_code != 200:
        print(f"❌ 获取供应信息失败: {supply_resp.status_code}")
        print(f"   错误: {supply_resp.text}")
        return
    
    supply_data = supply_resp.json()
    items = supply_data.get('data', {}).get('items', [])
    
    if not items:
        print("❌ 没有找到供应信息")
        return
    
    supply_info = items[0]
    print(f"✅ 找到供应信息: {supply_info['drug']['generic_name']}")
    print(f"   供应商企业ID: {supply_info['tenant_id']}")
    print(f"   最小起订量: {supply_info.get('min_order_quantity', 1)}")
    
    # 检查是否向自己下单
    if user.get('tenant_id') == supply_info['tenant_id']:
        print("⚠️ 警告: 这是向自己企业下单，会被阻止")
    
    # 构造下单请求
    min_qty = supply_info.get('min_order_quantity', 1)
    order_quantity = max(min_qty, 10)
    
    order_data = {
        'supply_info_id': supply_info['id'],
        'quantity': order_quantity,
        'notes': '调试测试订单'
    }
    
    print(f"\n下单数据: {json.dumps(order_data, indent=2)}")
    
    # 发送下单请求
    order_resp = requests.post('http://127.0.0.1:5000/api/orders',
                              json=order_data,
                              headers={
                                  'Authorization': f'Bearer {token}',
                                  'Content-Type': 'application/json'
                              })
    
    print(f"\n下单结果: {order_resp.status_code}")
    
    if order_resp.status_code == 201:
        print("✅ 下单成功!")
        result = order_resp.json()
        print(f"   订单号: {result['data']['order_number']}")
    else:
        print("❌ 下单失败!")
        try:
            error_data = order_resp.json()
            print(f"   错误信息: {error_data.get('msg', '未知错误')}")
            if 'error' in error_data:
                print(f"   详细错误: {error_data['error']}")
        except:
            print(f"   原始响应: {order_resp.text}")

if __name__ == "__main__":
    debug_order_issue()
