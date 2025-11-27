#!/usr/bin/env python3
"""
测试供应商查看订单功能
"""
import requests
import json

def test_supplier_orders():
    print('=== 测试供应商查看订单功能 ===')
    
    # 1. 供应商登录
    print('\n1. 供应商登录...')
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'supplier_dev', 'password': 'supplier123'})
    
    if login_resp.status_code != 200:
        print(f'❌ 供应商登录失败: {login_resp.status_code}')
        print(f'   错误信息: {login_resp.text}')
        return
        
    data = login_resp.json()
    supplier_token = data['access_token']
    supplier_user = data['user']
    
    print(f'✅ 供应商登录成功: {supplier_user["username"]}')
    print(f'   企业ID: {supplier_user.get("tenant_id")}')
    print(f'   企业名称: {supplier_user.get("tenant", {}).get("name", "无")}')
    
    # 2. 查看所有订单（供应商视角）
    print('\n2. 查看供应商的销售订单...')
    orders_resp = requests.get('http://127.0.0.1:5000/api/orders?role_filter=my_sales',
                              headers={'Authorization': f'Bearer {supplier_token}'})
    
    print(f'   订单列表API响应: {orders_resp.status_code}')
    
    if orders_resp.status_code == 200:
        orders_data = orders_resp.json()
        items = orders_data.get('data', {}).get('items', [])
        
        print(f'   找到 {len(items)} 个销售订单')
        
        if items:
            for idx, order in enumerate(items, 1):
                print(f'\n   订单 {idx}:')
                print(f'     订单号: {order["order_number"]}')
                print(f'     状态: {order["status"]}')
                print(f'     采购商: {order.get("buyer_tenant", {}).get("name", "未知")}')
                print(f'     创建时间: {order["created_at"]}')
                
                # 显示药品明细
                if order.get('items'):
                    print(f'     药品明细:')
                    for item in order['items']:
                        drug_name = item.get('drug', {}).get('generic_name', '未知药品')
                        print(f'       - {drug_name} × {item["quantity"]} (¥{item["unit_price"]}/单位)')
                
                # 如果是待确认订单，显示可进行的操作
                if order['status'] == 'PENDING':
                    print(f'     🔥 此订单待确认，可以进行以下操作:')
                    print(f'       - 确认订单: POST /api/orders/{order["id"]}/confirm (action: accept)')
                    print(f'       - 拒绝订单: POST /api/orders/{order["id"]}/confirm (action: reject)')
        else:
            print('   📝 暂无销售订单')
            print('   💡 提示: 需要药店用户先下单才能看到订单')
    else:
        print(f'❌ 获取订单列表失败: {orders_resp.status_code}')
        print(f'   错误内容: {orders_resp.text}')
    
    # 3. 获取订单统计
    print('\n3. 获取订单统计信息...')
    stats_resp = requests.get('http://127.0.0.1:5000/api/orders/stats',
                             headers={'Authorization': f'Bearer {supplier_token}'})
    
    print(f'   统计API响应: {stats_resp.status_code}')
    
    if stats_resp.status_code == 200:
        stats_data = stats_resp.json()
        stats = stats_data.get('data', {})
        
        print(f'   统计信息:')
        print(f'     总订单: {stats.get("total", 0)}')
        print(f'     待确认: {stats.get("pending", 0)}')
        print(f'     已确认: {stats.get("confirmed", 0)}')
        print(f'     已发货: {stats.get("shipped", 0)}')
        print(f'     已完成: {stats.get("completed", 0)}')
        print(f'     本月新增: {stats.get("this_month", 0)}')
    else:
        print(f'❌ 获取统计信息失败: {stats_resp.status_code}')
        print(f'   错误内容: {stats_resp.text}')
    
    # 4. 检查是否有药店下的订单
    print('\n4. 检查系统中的订单状态...')
    
    # 先用管理员身份查看所有订单
    admin_login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                                   json={'username': 'admin_dev', 'password': 'admin123'})
    
    if admin_login_resp.status_code == 200:
        admin_data = admin_login_resp.json()
        admin_token = admin_data['access_token']
        
        all_orders_resp = requests.get('http://127.0.0.1:5000/api/orders',
                                      headers={'Authorization': f'Bearer {admin_token}'})
        
        if all_orders_resp.status_code == 200:
            all_orders_data = all_orders_resp.json()
            all_items = all_orders_data.get('data', {}).get('items', [])
            
            print(f'   系统中共有 {len(all_items)} 个订单')
            
            # 找出与当前供应商相关的订单
            supplier_related_orders = [order for order in all_items 
                                     if order['supplier_tenant_id'] == supplier_user['tenant_id']]
            
            print(f'   其中 {len(supplier_related_orders)} 个与当前供应商相关')
            
            if supplier_related_orders:
                print(f'   供应商相关订单详情:')
                for order in supplier_related_orders:
                    buyer_name = order.get('buyer_tenant', {}).get('name', '未知')
                    print(f'     - {order["order_number"]} ({order["status"]}) from {buyer_name}')
            
            # 检查是否有PENDING状态的订单
            pending_orders = [order for order in supplier_related_orders if order['status'] == 'PENDING']
            if pending_orders:
                print(f'\n   🎯 发现 {len(pending_orders)} 个待确认订单!')
                print(f'   这些订单应该在供应商界面中显示')
            else:
                print(f'\n   📋 没有待确认订单')
                print(f'   💡 建议: 用药店用户(pharmacy_dev)先下单测试')

if __name__ == "__main__":
    test_supplier_orders()
