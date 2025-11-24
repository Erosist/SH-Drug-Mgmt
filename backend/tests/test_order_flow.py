#!/usr/bin/env python3
"""
测试下单流程
"""
import requests
import json

def test_order_creation():
    # 测试登录
    print("=== 测试下单流程 ===")
    
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
    
    if login_resp.status_code != 200:
        print(f"登录失败: {login_resp.status_code} - {login_resp.text}")
        return
        
    data = login_resp.json()
    print("✅ 登录成功!")
    
    user_info = data['user']
    print(f"  用户名: {user_info['username']}")
    print(f"  角色: {user_info['role']}")
    print(f"  企业ID: {user_info.get('tenant_id')}")
    
    if user_info.get('tenant'):
        print(f"  企业名称: {user_info['tenant']['name']}")
    else:
        print("  ⚠️ 企业信息: 无")
    
    token = data['access_token']
    print(f"\n获取到Token: {token[:50]}...")
    
    # 测试获取供应信息
    print("\n=== 获取供应信息 ===")
    supply_resp = requests.get('http://127.0.0.1:5000/api/supply/info',
                              headers={'Authorization': f'Bearer {token}'})
    
    print(f"供应信息API响应: {supply_resp.status_code}")
    
    if supply_resp.status_code == 200:
        supply_data = supply_resp.json()
        items = supply_data.get('data', {}).get('items', [])
        print(f"找到 {len(items)} 个供应信息")
        
        if items:
            supply_info = items[0]
            print(f"供应信息详情: {json.dumps(supply_info, indent=2, ensure_ascii=False)}")
            
            # 根据实际数据结构获取信息
            drug_info = supply_info.get('drug', {}) or {}
            drug_name = drug_info.get('name') or drug_info.get('generic_name') or supply_info.get('drug_name', 'Unknown Drug')
            supplier_name = supply_info.get('supplier_name') or supply_info.get('tenant', {}).get('name', 'Unknown Supplier')
            
            print(f"选择供应信息: {drug_name} (ID: {supply_info['id']})")
            print(f"供应商: {supplier_name}")
            print(f"可供数量: {supply_info['available_quantity']}")
            print(f"单价: ¥{supply_info['unit_price']}")
            print(f"最小起订量: {supply_info.get('min_order_quantity', 1)}")
            
            # 测试下单
            print(f"\n=== 测试下单 ===")
            min_quantity = supply_info.get('min_order_quantity', 1)
            order_quantity = max(min_quantity, 5)  # 使用最小起订量或5，取较大值
            
            order_data = {
                'supply_info_id': supply_info['id'],
                'quantity': order_quantity,
                'notes': '开发环境测试订单'
            }
            
            print(f"下单数据: {order_data}")
            
            order_resp = requests.post('http://127.0.0.1:5000/api/orders',
                                     json=order_data,
                                     headers={'Authorization': f'Bearer {token}'})
            
            print(f"下单响应状态: {order_resp.status_code}")
            print(f"下单响应内容: {order_resp.text}")
            
            if order_resp.status_code == 201:
                print("✅ 下单成功!")
            else:
                print("❌ 下单失败!")
                try:
                    error_data = order_resp.json()
                    print(f"错误信息: {error_data.get('msg', '未知错误')}")
                except:
                    print(f"原始错误: {order_resp.text}")
        else:
            print("❌ 没有找到可用的供应信息")
    else:
        print(f"❌ 获取供应信息失败: {supply_resp.status_code}")
        print(f"错误内容: {supply_resp.text}")

if __name__ == "__main__":
    test_order_creation()
