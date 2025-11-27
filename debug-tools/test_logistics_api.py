#!/usr/bin/env python3
"""
直接测试物流用户API调用
"""
import sys
sys.path.append('backend')

from app import create_app
from models import User
from config import Config
import requests
import json

def test_logistics_api():
    """测试物流用户API"""
    print("=== 测试物流用户API ===")
    
    app = create_app(Config)
    
    with app.app_context():
        # 获取物流用户
        logistics_user = User.query.filter_by(username='sfexpress').first()
        if not logistics_user:
            print("❌ 找不到物流用户")
            return
        
        print(f"物流用户: {logistics_user.username} (ID: {logistics_user.id})")
        print(f"角色: {logistics_user.role}")
        print(f"租户ID: {logistics_user.tenant_id}")
    
    # 模拟登录获取token
    print("\n=== 模拟登录 ===")
    try:
        response = requests.post('http://127.0.0.1:5000/api/auth/login', 
                                json={'username': 'sfexpress', 'password': 'sf123456'})
        
        if response.status_code == 200:
            login_data = response.json()
            token = login_data.get('data', {}).get('access_token')
            print(f"✓ 登录成功，token: {token[:50]}...")
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return
    
    # 测试获取订单列表
    print("\n=== 测试订单列表API ===")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://127.0.0.1:5000/api/orders', headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 请求成功")
            print(f"订单数量: {len(data.get('data', {}).get('items', []))}")
        else:
            print("❌ 请求失败")
            
    except Exception as e:
        print(f"❌ API请求失败: {e}")
    
    # 测试获取统计信息
    print("\n=== 测试订单统计API ===")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://127.0.0.1:5000/api/orders/stats', headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
    except Exception as e:
        print(f"❌ 统计API请求失败: {e}")

if __name__ == "__main__":
    test_logistics_api()
