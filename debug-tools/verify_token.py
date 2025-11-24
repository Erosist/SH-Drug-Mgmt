#!/usr/bin/env python3
"""
Token验证工具 - 帮助用户检查他们的token状态
"""
import requests
import json
import sys

def verify_token(token):
    """验证给定的token"""
    print(f'=== 验证Token ===')
    print(f'Token: {token[:20]}...{token[-10:]}' if len(token) > 30 else f'Token: {token}')
    
    # 1. 调用 /api/auth/me
    print('\n1. 验证token有效性...')
    me_resp = requests.get('http://127.0.0.1:5000/api/auth/me',
                          headers={'Authorization': f'Bearer {token}'})
    
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        user = me_data.get('user', {})
        
        print(f'✅ Token有效')
        print(f'   用户ID: {user.get("id")}')
        print(f'   用户名: {user.get("username")}')
        print(f'   角色: {user.get("role")}')
        print(f'   企业ID: {user.get("tenant_id")}')
        print(f'   是否认证: {user.get("is_authenticated")}')
        
        # 检查关键字段
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            print(f'❌ 问题发现: tenant_id为空! ({tenant_id})')
            print(f'   这就是"用户未关联企业，无法下单"错误的原因')
            return False
        else:
            print(f'✅ 企业关联正常')
            
        # 2. 尝试下单测试
        print(f'\n2. 测试下单能力...')
        order_data = {
            'supply_info_id': 1,
            'quantity': 100,
            'expected_delivery_date': '2025-11-22',
            'notes': 'Token验证测试'
        }
        
        order_resp = requests.post('http://127.0.0.1:5000/api/orders',
                                  json=order_data,
                                  headers={
                                      'Authorization': f'Bearer {token}',
                                      'Content-Type': 'application/json'
                                  })
        
        print(f'   下单测试状态: {order_resp.status_code}')
        
        if order_resp.status_code == 201:
            print(f'✅ 下单成功! 该token可以正常下单')
            result = order_resp.json()
            print(f'   订单号: {result["data"]["order_number"]}')
            return True
        elif order_resp.status_code == 400:
            try:
                error_data = order_resp.json()
                error_msg = error_data.get('msg', '未知错误')
                print(f'❌ 下单失败: {error_msg}')
                return False
            except:
                print(f'❌ 下单失败: {order_resp.text}')
                return False
        else:
            print(f'❌ 下单失败: 状态码{order_resp.status_code}')
            print(f'   响应: {order_resp.text}')
            return False
            
    else:
        print(f'❌ Token无效: {me_resp.status_code}')
        if me_resp.status_code == 422:
            print(f'   错误: Token格式错误')
        elif me_resp.status_code == 401:
            print(f'   错误: Token过期或无效')
        print(f'   响应: {me_resp.text}')
        return False

def main():
    if len(sys.argv) > 1:
        token = sys.argv[1]
        verify_token(token)
    else:
        print('使用方法:')
        print('python verify_token.py <your_token>')
        print('')
        print('或者您可以从前端获取token:')
        print('1. 打开浏览器开发者工具 (F12)')
        print('2. 在Console中运行: localStorage.getItem("access_token")')
        print('3. 复制token并运行: python verify_token.py <复制的token>')
        
        # 提供快速测试pharmacy_dev
        print('\n也可以测试我们已知的好用户:')
        print('登录pharmacy_dev用户...')
        login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                                  json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
        
        if login_resp.status_code == 200:
            data = login_resp.json()
            token = data['access_token']
            print(f'获得pharmacy_dev的token: {token[:20]}...{token[-10:]}')
            verify_token(token)
        else:
            print(f'无法登录pharmacy_dev: {login_resp.text}')

if __name__ == "__main__":
    main()
