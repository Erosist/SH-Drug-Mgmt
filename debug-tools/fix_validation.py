#!/usr/bin/env python3
"""
完整的修复脚本 - 确保前端后端API连接正常工作
"""
import time
import requests

def wait_for_flask():
    """等待Flask服务器启动"""
    print("等待Flask服务器启动...")
    for i in range(10):
        try:
            response = requests.get("http://127.0.0.1:5000/api/catalog/tenants?page=1&per_page=10")
            if response.status_code in [200, 401]:  # 401表示服务器运行但需要认证
                print("✅ Flask服务器已启动")
                return True
        except:
            time.sleep(1)
            print(f"等待中... ({i+1}/10)")
    return False

def test_complete_flow():
    """测试完整的API流程"""
    print("\n=== 测试完整API流程 ===")
    
    # 1. 登录
    login_response = requests.post("http://127.0.0.1:5000/api/auth/login", json={
        "username": "pharmacy1",
        "password": "password123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return False
    
    token = login_response.json()['access_token']
    print(f"✅ 登录成功, Token: {token[:30]}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 2. 测试问题API
    problem_apis = [
        {
            "name": "订单列表(with my_purchases)",
            "url": "http://127.0.0.1:5000/api/orders?page=1&per_page=20&role_filter=my_purchases"
        },
        {
            "name": "订单统计", 
            "url": "http://127.0.0.1:5000/api/orders/stats"
        },
        {
            "name": "库存预警(with params)",
            "url": "http://127.0.0.1:5000/api/v1/inventory/warnings?warning_type=all&page=1&per_page=20"
        },
        {
            "name": "库存预警统计",
            "url": "http://127.0.0.1:5000/api/v1/inventory/warning-summary"
        }
    ]
    
    all_success = True
    for api in problem_apis:
        response = requests.get(api['url'], headers=headers)
        if response.status_code == 200:
            print(f"✅ {api['name']}: 200 OK")
        else:
            print(f"❌ {api['name']}: {response.status_code} - {response.text}")
            all_success = False
    
    return all_success

def main():
    print("🔧 前后端API连接修复验证脚本")
    
    # 等待Flask服务器
    if not wait_for_flask():
        print("❌ Flask服务器未能启动，请检查后端服务")
        return
    
    # 测试API流程
    success = test_complete_flow()
    
    if success:
        print("\n🎉 所有API测试通过！前端应该能正常连接后端了。")
        print("\n📋 下一步操作建议：")
        print("1. 打开前端应用: http://localhost:5174")
        print("2. 清除浏览器localStorage (F12 > Application > Local Storage > Clear All)")
        print("3. 重新登录用户 pharmacy1 / password123")
        print("4. 测试'模拟下单'和'库存管理'功能")
    else:
        print("\n⚠️  某些API仍有问题，需要进一步调试")

if __name__ == "__main__":
    main()
