#!/usr/bin/env python3
"""
登录功能测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from app import create_app


def test_login(username, password, base_url="http://127.0.0.1:5000"):
    """测试登录功能"""
    login_url = f"{base_url}/api/auth/login"
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        print(f"正在测试登录: {username}")
        response = requests.post(
            login_url, 
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print(f"✅ 登录成功!")
                print(f"Token: {data['access_token'][:50]}...")
                return True
            else:
                print(f"❌ 登录失败: 响应中没有token")
                return False
        else:
            print(f"❌ 登录失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败: 无法连接到 {base_url}")
        print("请确保Flask应用正在运行 (python run.py)")
        return False
    except Exception as e:
        print(f"❌ 登录测试失败: {str(e)}")
        return False


def check_auth_endpoints():
    """检查认证相关的API端点"""
    print("=== 检查认证API端点 ===")
    
    app = create_app()
    with app.app_context():
        # 打印所有路由
        print("已注册的路由:")
        for rule in app.url_map.iter_rules():
            if '/auth/' in rule.rule:
                print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")


def main():
    """主函数"""
    print("登录功能测试")
    print("=" * 50)
    
    # 1. 检查API端点
    check_auth_endpoints()
    
    # 2. 测试登录
    print(f"\n=== 测试登录功能 ===")
    
    # 测试新创建的admin账号
    print("1. 测试admin账号登录:")
    test_login("admin", "admin123")
    
    print("\n2. 测试pharmacy_user账号登录:")
    test_login("pharmacy_user", "password123")  # 使用默认密码
    
    print("\n3. 测试supplier_user账号登录:")
    test_login("supplier_user", "password123")  # 使用默认密码
    
    print("\n注意:")
    print("- 如果连接失败，请先启动Flask应用: python run.py")
    print("- 如果登录失败，可能需要检查用户密码或认证逻辑")


if __name__ == '__main__':
    main()
