#!/usr/bin/env python
"""
测试供应信息API的脚本
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_login_and_get_supply_info():
    """测试登录并获取供应信息"""
    
    # 1. 药店用户登录
    print("=== 1. 药店用户登录 ===")
    login_data = {
        "username": "pharmacy1",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"登录状态码: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        pharmacy_token = login_result["access_token"]
        print(f"登录成功，用户: {login_result['user']['username']}")
        print(f"Token: {pharmacy_token[:50]}...")
    else:
        print(f"登录失败: {login_response.text}")
        return
    
    # 2. 获取供应信息列表
    print("\n=== 2. 获取供应信息列表 ===")
    headers = {"Authorization": f"Bearer {pharmacy_token}"}
    
    supply_response = requests.get(f"{BASE_URL}/api/supply/info", headers=headers)
    print(f"获取供应信息状态码: {supply_response.status_code}")
    
    if supply_response.status_code == 200:
        supply_result = supply_response.json()
        print(f"获取成功: {supply_result['msg']}")
        print(f"总数: {supply_result['data']['pagination']['total']}")
        print("前5条供应信息:")
        for item in supply_result["data"]["items"][:5]:
            print(f"  - ID: {item['id']}, 药品: {item['drug']['generic_name']}, "
                  f"供应商: {item['tenant']['name']}, 数量: {item['available_quantity']}, "
                  f"单价: ¥{item['unit_price']}")
    else:
        print(f"获取供应信息失败: {supply_response.text}")
    
    # 3. 测试搜索功能
    print("\n=== 3. 测试药品名称搜索 ===")
    search_params = {"drug_name": "布洛芬"}
    search_response = requests.get(f"{BASE_URL}/api/supply/info", 
                                 headers=headers, params=search_params)
    
    if search_response.status_code == 200:
        search_result = search_response.json()
        print(f"搜索结果数量: {len(search_result['data']['items'])}")
        for item in search_result["data"]["items"]:
            print(f"  - 药品: {item['drug']['generic_name']}, 供应商: {item['tenant']['name']}")
    else:
        print(f"搜索失败: {search_response.text}")
    
    # 4. 测试供应商名称搜索
    print("\n=== 4. 测试供应商名称搜索 ===")
    search_params = {"supplier_name": "上海医药"}
    search_response = requests.get(f"{BASE_URL}/api/supply/info", 
                                 headers=headers, params=search_params)
    
    if search_response.status_code == 200:
        search_result = search_response.json()
        print(f"搜索结果数量: {len(search_result['data']['items'])}")
        for item in search_result["data"]["items"]:
            print(f"  - 药品: {item['drug']['generic_name']}, 供应商: {item['tenant']['name']}")
    else:
        print(f"搜索失败: {search_response.text}")
    
    # 5. 获取特定供应信息详情
    print("\n=== 5. 获取供应信息详情 ===")
    detail_response = requests.get(f"{BASE_URL}/api/supply/info/2", headers=headers)
    
    if detail_response.status_code == 200:
        detail_result = detail_response.json()
        item = detail_result["data"]
        print(f"详情获取成功:")
        print(f"  - ID: {item['id']}")
        print(f"  - 药品: {item['drug']['generic_name']} ({item['drug']['specification']})")
        print(f"  - 供应商: {item['tenant']['name']}")
        print(f"  - 可供数量: {item['available_quantity']}")
        print(f"  - 单价: ¥{item['unit_price']}")
        print(f"  - 最小起订量: {item['min_order_quantity']}")
        print(f"  - 有效期至: {item['valid_until']}")
        if item['description']:
            print(f"  - 备注: {item['description']}")
    else:
        print(f"获取详情失败: {detail_response.text}")

if __name__ == "__main__":
    print("开始测试供应信息API...")
    try:
        test_login_and_get_supply_info()
        print("\n✅ 测试完成!")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保Flask服务器正在运行 (python run.py)")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
