#!/usr/bin/env python3
"""
测试JWT token解析和用户信息完整性
"""
import requests
import json

def test_token_user_info():
    print('=== 测试JWT Token和用户信息 ===')
    
    # 1. 正常登录获取token
    print('1. 正常登录获取token...')
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
    
    if login_resp.status_code != 200:
        print(f'❌ 登录失败: {login_resp.status_code}')
        return
        
    data = login_resp.json()
    token = data['access_token']
    print(f'✅ 获取token成功')
    
    # 2. 使用token调用/api/auth/me查看解析的用户信息
    print('\n2. 验证token解析的用户信息...')
    me_resp = requests.get('http://127.0.0.1:5000/api/auth/me',
                          headers={'Authorization': f'Bearer {token}'})
    
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        user = me_data.get('user', {})
        print(f'✅ Token解析成功:')
        print(f'   用户ID: {user.get("id")}')
        print(f'   用户名: {user.get("username")}')
        print(f'   角色: {user.get("role")}')
        print(f'   企业ID: {user.get("tenant_id")}')
        print(f'   是否认证: {user.get("is_authenticated")}')
        
        # 检查tenant_id是否为None或0
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            print(f'⚠️  警告: tenant_id为空! tenant_id={tenant_id}')
        else:
            print(f'✅ tenant_id正常: {tenant_id}')
            
    else:
        print(f'❌ Token验证失败: {me_resp.status_code} - {me_resp.text}')
        return
    
    # 3. 使用不同的header格式测试
    print('\n3. 测试不同的Authorization header格式...')
    
    # 测试小写bearer
    test_auth_format(f'bearer {token}', 'bearer (小写)')
    
    # 测试没有空格
    test_auth_format(f'Bearer{token}', 'Bearer无空格')
    
    # 测试多余的空格
    test_auth_format(f'Bearer  {token}', 'Bearer双空格')
    
    # 测试正确格式
    test_auth_format(f'Bearer {token}', 'Bearer正确格式')

def test_auth_format(auth_header, description):
    print(f'   测试 {description}...')
    
    # 调用需要认证的API
    me_resp = requests.get('http://127.0.0.1:5000/api/auth/me',
                          headers={'Authorization': auth_header})
    
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        user = me_data.get('user', {})
        tenant_id = user.get('tenant_id')
        print(f'      ✅ 成功, tenant_id={tenant_id}')
    else:
        print(f'      ❌ 失败: {me_resp.status_code}')

def test_with_empty_tenant_user():
    print('\n=== 测试创建没有tenant_id的用户 ===')
    
    # 这个测试需要直接操作数据库或创建特殊用户
    print('为了测试用户未关联企业的情况，我们可以：')
    print('1. 在数据库中创建一个tenant_id为NULL的用户')
    print('2. 或者修改现有用户的tenant_id为NULL')
    print('3. 然后用该用户登录并尝试下单')

if __name__ == "__main__":
    test_token_user_info()
    test_with_empty_tenant_user()
