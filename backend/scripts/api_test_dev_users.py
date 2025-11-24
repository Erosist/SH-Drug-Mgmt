#!/usr/bin/env python3
"""
测试新创建的开发用户账户
"""
import requests
import json

def test_user_login():
    """测试用户登录功能"""
    print('=== 测试新创建的用户账户 ===\n')
    
    # 测试用户列表
    test_users = [
        {'username': 'admin', 'password': 'admin123', 'description': '管理员'},   
        {'username': 'pharmacy_dev', 'password': 'pharmacy123', 'description': '开发药店用户'},
        {'username': 'supplier_dev', 'password': 'supplier123', 'description': '开发供应商用户'}
    ]
    
    for user in test_users:
        print(f'测试 {user["description"]} ({user["username"]}):')
        
        try:
            # 登录测试
            login_resp = requests.post('http://127.0.0.1:5000/api/auth/login',
                                      json={'username': user['username'], 'password': user['password']},
                                      timeout=10)
            
            if login_resp.status_code == 200:
                data = login_resp.json()
                print(f'  ✅ 登录成功')
                
                # 处理实际的响应格式
                if 'user' in data and 'access_token' in data:
                    user_info = data['user']
                    tenant_info = f"企业ID: {user_info.get('tenant_id', '无')}"
                    
                    # 如果有企业信息，显示企业名称
                    if user_info.get('tenant') and user_info['tenant'].get('name'):
                        tenant_name = user_info['tenant']['name']
                        tenant_info += f" ({tenant_name})"
                    
                    print(f'  👤 用户信息: {user_info["role"]} | {tenant_info}')
                    
                    # 测试获取用户详情
                    token = data['access_token']
                    me_resp = requests.get('http://127.0.0.1:5000/api/auth/me',
                                          headers={'Authorization': f'Bearer {token}'},
                                          timeout=10)
                    
                    if me_resp.status_code == 200:
                        print(f'  ✅ 用户详情获取成功')
                    else:
                        print(f'  ❌ 用户详情获取失败: {me_resp.status_code}')
                        if me_resp.text:
                            print(f'     错误信息: {me_resp.text[:100]}')
                else:
                    print(f'  ⚠️ 响应格式异常，无法解析用户信息')
                    
            else:
                print(f'  ❌ 登录失败: {login_resp.status_code}')
                try:
                    error_data = login_resp.json()
                    print(f'     错误信息: {error_data.get("message", login_resp.text[:100])}')
                except:
                    print(f'     错误信息: {login_resp.text[:100]}')
                    
        except requests.exceptions.RequestException as e:
            print(f'  ❌ 网络请求失败: {e}')
        except Exception as e:
            print(f'  ❌ 测试过程出错: {e}')
        
        print()

if __name__ == "__main__":
    test_user_login()
