import requests
import json

def test_order_status_mismatch():
    # 登录
    login_url = "http://localhost:5000/api/auth/login"
    login_data = {"username": "sfexpress", "password": "123456"}
    
    try:
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access_token')
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # 获取物流订单列表
            orders_url = "http://localhost:5000/api/orders"
            orders_response = requests.get(orders_url, headers=headers)
            print(f"获取订单列表状态码: {orders_response.status_code}")
            
            if orders_response.status_code == 200:
                orders_data = orders_response.json()
                orders = orders_data.get('data', {}).get('items', [])
                print(f"找到 {len(orders)} 个订单")
                
                for order in orders:
                    print(f"订单ID: {order['id']}, 订单号: {order['order_number']}, 状态: {order['status']}")
                    
                    # 如果找到订单24，测试状态更新
                    if order['id'] == 24:
                        print(f"\n测试更新订单24的状态，当前状态: {order['status']}")
                        
                        # 试图更新为IN_TRANSIT（应该会失败，因为已经是IN_TRANSIT了）
                        update_url = f"http://localhost:5000/api/orders/status/24"
                        update_data = {"status": "IN_TRANSIT"}
                        
                        update_response = requests.patch(update_url, json=update_data, headers=headers)
                        print(f"尝试更新为IN_TRANSIT - 状态码: {update_response.status_code}")
                        print(f"响应内容: {update_response.text}")
                        
                        # 试图更新为DELIVERED（这应该是正确的下一步）
                        update_data2 = {"status": "DELIVERED"}
                        update_response2 = requests.patch(update_url, json=update_data2, headers=headers)
                        print(f"尝试更新为DELIVERED - 状态码: {update_response2.status_code}")
                        print(f"响应内容: {update_response2.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_order_status_mismatch()
