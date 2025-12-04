#!/usr/bin/env python3
"""
测试前端显示问题 - 检查用户状态和数据
"""
import requests
import json

def test_frontend_issues():
    print('=== 前端"下单"界面问题调试 ===')
    
    # 1. 测试不同用户登录状态
    test_users = [
        ('pharmacy_dev', 'pharmacy123', '药店用户'),
        ('supplier_dev', 'supplier123', '供应商用户'),
        ('admin_dev', 'admin123', '管理员用户')
    ]
    
    for username, password, desc in test_users:
        print(f'\n--- 测试 {desc} ({username}) ---')
        
        # 登录
        login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                                  json={'username': username, 'password': password})
        
        if login_resp.status_code != 200:
            print(f'❌ {desc}登录失败: {login_resp.status_code}')
            continue
            
        data = login_resp.json()
        token = data['access_token']
        user = data['user']
        
        print(f'✅ {desc}登录成功')
        print(f'   用户名: {user["username"]}')
        print(f'   角色: {user["role"]}')
        print(f'   企业ID: {user.get("tenant_id")}')
        print(f'   企业名称: {user.get("tenant", {}).get("name", "无")}')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 检查订单列表
        orders_resp = requests.get('http://127.0.0.1:5000/api/orders', headers=headers)
        print(f'   订单列表API: {orders_resp.status_code}')
        
        if orders_resp.status_code == 200:
            orders_data = orders_resp.json()
            items = orders_data.get('data', {}).get('items', [])
            print(f'   订单数量: {len(items)}')
            
            if items:
                order = items[0]
                print(f'   第一个订单: {order["order_number"]} ({order["status"]})')
        else:
            print(f'   ❌ 订单列表失败: {orders_resp.text[:100]}')
        
        # 检查订单统计
        stats_resp = requests.get('http://127.0.0.1:5000/api/orders/stats', headers=headers)
        print(f'   订单统计API: {stats_resp.status_code}')
        
        if stats_resp.status_code == 200:
            stats_data = stats_resp.json()
            stats = stats_data.get('data', {})
            print(f'   统计数据: 总计={stats.get("total", 0)}, 待确认={stats.get("pending", 0)}')
        else:
            print(f'   ❌ 统计失败: {stats_resp.text[:100]}')
    
    # 2. 检查供应信息数据
    print(f'\n--- 检查供应信息数据 ---')
    
    # 用药店用户查看供应信息
    login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                              json={'username': 'pharmacy_dev', 'password': 'pharmacy123'})
    
    if login_resp.status_code == 200:
        token = login_resp.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        supply_resp = requests.get('http://127.0.0.1:5000/api/supply/info', headers=headers)
        print(f'供应信息API: {supply_resp.status_code}')
        
        if supply_resp.status_code == 200:
            supply_data = supply_resp.json()
            supply_items = supply_data.get('data', {}).get('items', [])
            print(f'供应信息数量: {len(supply_items)}')
            
            if supply_items:
                supply = supply_items[0]
                drug_name = supply.get('drug', {}).get('generic_name', '未知')
                supplier_name = supply.get('tenant', {}).get('name', '未知')
                print(f'第一个供应信息: {drug_name} by {supplier_name}')
        else:
            print(f'❌ 供应信息失败: {supply_resp.text[:100]}')
    
    print(f'\n=== 调试建议 ===')
    print(f'1. 前端"下单"界面问题:')
    print(f'   - 检查浏览器localStorage中的current_user和access_token是否正确')
    print(f'   - 确认用户角色是pharmacy、supplier或admin')
    print(f'   - 打开浏览器F12控制台查看API请求是否成功')
    print(f'')
    print(f'2. "最新发布记录"问题:')
    print(f'   - 这部分是本地模拟数据，需要修改B2B.vue来显示真实数据')
    print(f'   - 可以调用supply/info API或orders API获取真实记录')

if __name__ == "__main__":
    test_frontend_issues()
