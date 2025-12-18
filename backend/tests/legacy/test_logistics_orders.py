"""
物流订单接口测试脚本
用于验证 /api/logistics/orders 接口是否正常工作
"""
import requests
import json

# 配置
BASE_URL = 'http://localhost:5000'
LOGIN_URL = f'{BASE_URL}/api/auth/login'
ORDERS_URL = f'{BASE_URL}/api/logistics/orders'

# 测试用户凭据（需要先创建一个物流用户）
TEST_USER = {
    'username': 'logistics_test',
    'password': 'test123'
}

def print_section(title):
    """打印分隔线"""
    print('\n' + '=' * 60)
    print(f'  {title}')
    print('=' * 60)

def login(username, password):
    """登录获取 JWT token"""
    print_section('步骤 1: 用户登录')
    
    try:
        response = requests.post(LOGIN_URL, json={
            'username': username,
            'password': password
        })
        
        print(f'状态码: {response.status_code}')
        print(f'响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print(f'✓ 登录成功！Token: {token[:20]}...')
                return token
            else:
                print('✗ 登录失败：未获取到 token')
                return None
        else:
            print('✗ 登录失败')
            return None
    except Exception as e:
        print(f'✗ 登录请求失败: {e}')
        return None

def get_orders(token, filters=None):
    """获取物流订单列表"""
    print_section('步骤 2: 获取物流订单列表')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = filters or {}
    
    try:
        response = requests.get(ORDERS_URL, headers=headers, params=params)
        
        print(f'状态码: {response.status_code}')
        print(f'请求参数: {params}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'响应: {json.dumps(data, indent=2, ensure_ascii=False)}')
            
            if data.get('success'):
                orders = data.get('data', [])
                print(f'\n✓ 成功获取 {len(orders)} 条订单')
                
                if orders:
                    print('\n订单列表:')
                    for i, order in enumerate(orders, 1):
                        print(f'\n订单 {i}:')
                        print(f'  - 订单号: {order.get("order_no")}')
                        print(f'  - 运单号: {order.get("tracking_number", "无")}')
                        print(f'  - 批号: {order.get("batch_number", "无")}')
                        print(f'  - 状态: {order.get("status")}')
                        print(f'  - 地址: {order.get("address", "无")}')
                        print(f'  - 更新时间: {order.get("updated_at")}')
                else:
                    print('  (暂无订单数据)')
                
                return True
            else:
                print(f'✗ 获取失败: {data.get("message")}')
                return False
        else:
            print(f'✗ 请求失败: {response.text}')
            return False
    except Exception as e:
        print(f'✗ 请求异常: {e}')
        return False

def test_filters(token):
    """测试筛选功能"""
    print_section('步骤 3: 测试筛选功能')
    
    # 测试不同的筛选条件
    test_cases = [
        {'name': '按状态筛选 (SHIPPED)', 'filters': {'status': 'SHIPPED'}},
        {'name': '按状态筛选 (IN_TRANSIT)', 'filters': {'status': 'IN_TRANSIT'}},
        {'name': '按订单号筛选', 'filters': {'order_no': 'PH'}},
        {'name': '按运单号筛选', 'filters': {'tracking_number': 'TRK'}},
    ]
    
    for case in test_cases:
        print(f'\n测试: {case["name"]}')
        get_orders(token, case['filters'])

def main():
    """主函数"""
    print_section('物流订单接口测试')
    print(f'API 地址: {ORDERS_URL}')
    print(f'测试用户: {TEST_USER["username"]}')
    
    # 步骤 1: 登录
    token = login(TEST_USER['username'], TEST_USER['password'])
    
    if not token:
        print('\n✗ 无法获取 token，测试终止')
        print('\n提示:')
        print('  1. 确保后端服务已启动 (python backend/run.py)')
        print('  2. 确保已创建物流测试用户')
        print('  3. 检查用户名和密码是否正确')
        return
    
    # 步骤 2: 获取订单列表（无筛选）
    success = get_orders(token)
    
    if not success:
        print('\n✗ 获取订单失败，请检查:')
        print('  1. 用户角色是否为 logistics')
        print('  2. 数据库中是否有物流订单数据')
        print('  3. 后端日志是否有错误信息')
        return
    
    # 步骤 3: 测试筛选功能
    test_filters(token)
    
    print_section('测试完成')
    print('✓ 所有测试已完成')

if __name__ == '__main__':
    main()
