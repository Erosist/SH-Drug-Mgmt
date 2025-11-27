#!/usr/bin/env python3
"""
简单的API测试 - 直接curl命令测试
"""
import os

def test_api_with_curl():
    """使用curl测试API"""
    print("=== 使用curl测试API ===")
    
    # 测试登录
    print("\n1. 测试登录 supplier1:")
    os.system('curl -X POST http://127.0.0.1:5000/api/auth/login -H "Content-Type: application/json" -d "{\\"username\\": \\"supplier1\\", \\"password\\": \\"supplier1\\"}"')
    
    print("\n\n2. 测试供应商信息API (无token):")
    os.system('curl -X GET http://127.0.0.1:5000/api/supply/info')
    
    print("\n\n3. 测试订单API (无token):")
    os.system('curl -X GET "http://127.0.0.1:5000/api/orders?per_page=2"')
    
    print("\n\n4. 测试用户信息API (无token):")
    os.system('curl -X GET http://127.0.0.1:5000/api/auth/info')

if __name__ == "__main__":
    test_api_with_curl()
