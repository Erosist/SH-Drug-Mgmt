#!/usr/bin/env python3
"""
创建一个没有tenant_id的用户来测试"用户未关联企业"错误
"""
import os
import sys
sys.path.append('.')

from app import create_app
from extensions import db
from models import User, Tenant
from werkzeug.security import generate_password_hash
import requests

def create_user_without_tenant():
    """创建一个没有tenant_id的用户"""
    app = create_app()
    
    with app.app_context():
        # 创建一个没有关联企业的用户
        user = User(
            username='no_tenant_user',
            password_hash=generate_password_hash('test123'),
            email='no_tenant@test.com',
            phone='13900000000',  # 使用不同的手机号
            role='pharmacy',
            tenant_id=None,  # 关键：没有关联企业
            is_active=True,
            is_authenticated=False
        )
        
        db.session.add(user)
        db.session.commit()
        print(f'✅ 创建无企业关联用户成功: {user.username} (ID: {user.id})')

def test_user_without_tenant():
    """测试没有企业关联的用户下单"""
    print('=== 测试没有企业关联的用户 ===')
    
    # 1. 登录没有企业关联的用户
    print('1. 登录没有企业关联的用户...')
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'no_tenant_user', 'password': 'test123'})
    
    if login_resp.status_code != 200:
        print(f'❌ 登录失败: {login_resp.status_code} - {login_resp.text}')
        return
        
    data = login_resp.json()
    token = data['access_token']
    user = data['user']
    
    print(f'✅ 登录成功: {user["username"]}')
    print(f'   用户角色: {user["role"]}')
    print(f'   企业ID: {user.get("tenant_id")}')
    
    # 2. 验证用户信息
    print('\n2. 验证JWT解析的用户信息...')
    me_resp = requests.get('http://127.0.0.1:5000/api/auth/me',
                          headers={'Authorization': f'Bearer {token}'})
    
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        me_user = me_data.get('user', {})
        print(f'   JWT解析 - 用户ID: {me_user.get("id")}, tenant_id: {me_user.get("tenant_id")}')
    
    # 3. 尝试下单
    print('\n3. 尝试下单...')
    order_data = {
        'supply_info_id': 1,
        'quantity': 100,
        'expected_delivery_date': '2025-11-22',
        'notes': '测试没有企业关联的用户下单'
    }
    
    order_resp = requests.post('http://127.0.0.1:5000/api/orders',
                              json=order_data,
                              headers={
                                  'Authorization': f'Bearer {token}',
                                  'Content-Type': 'application/json'
                              })
    
    print(f'   下单响应状态: {order_resp.status_code}')
    
    if order_resp.status_code == 400:
        try:
            error_data = order_resp.json()
            print(f'   ✅ 成功重现错误! 错误信息: {error_data.get("msg")}')
        except:
            print(f'   响应内容: {order_resp.text}')
    else:
        print(f'   意外的响应: {order_resp.text}')

if __name__ == "__main__":
    print('创建测试用户...')
    create_user_without_tenant()
    print('\n测试没有企业关联的用户下单...')
    test_user_without_tenant()
