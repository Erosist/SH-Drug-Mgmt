import requests
import json

# 测试状态更新API
def test_update_order_status():
    # 先登录获取token
    login_url = "http://localhost:5000/api/auth/login"
    login_data = {
        "username": "sfexpress",
        "password": "123456"
    }
    
    try:
        # 登录
        print("正在登录...")
        login_response = requests.post(login_url, json=login_data)
        print(f"登录响应状态码: {login_response.status_code}")
        print(f"登录响应内容: {login_response.text}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access_token')
            print(f"获取到token: {access_token[:50]}...")
            
            # 测试更新订单状态
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # 假设订单ID是24（从前端错误中看到的）
            order_id = 24
            update_url = f"http://localhost:5000/api/orders/status/{order_id}"
            update_data = {"status": "IN_TRANSIT"}
            
            print(f"正在更新订单 {order_id} 状态...")
            update_response = requests.patch(update_url, json=update_data, headers=headers)
            print(f"更新响应状态码: {update_response.status_code}")
            print(f"更新响应内容: {update_response.text}")
            
        else:
            print("登录失败")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_update_order_status()
