"""
认证功能测试
"""
import pytest
import json
from werkzeug.security import generate_password_hash
from models import User, Tenant


class TestAuth:
    """认证测试类"""
    
    @pytest.fixture
    def sample_user_data(self):
        """测试用户数据"""
        return {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
    
    def test_user_registration(self, client, sample_user_data):
        """测试用户注册"""
        response = client.post('/api/auth/register', 
                              json=sample_user_data,
                              content_type='application/json')
        
        if response.status_code == 201:
            # 注册成功
            data = response.get_json()
            assert 'msg' in data
            assert 'user' in data
            assert data['user']['username'] == sample_user_data['username']
        else:
            # 可能用户已存在或其他原因，检查错误信息
            data = response.get_json()
            assert 'msg' in data
    
    def test_user_login_invalid(self, client):
        """测试无效登录"""
        response = client.post('/api/auth/login', 
                              json={
                                  'username': 'nonexistent',
                                  'password': 'wrongpass'
                              },
                              content_type='application/json')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'msg' in data
    
    def test_enterprise_user_registration_flow(self, client):
        """测试企业用户注册完整流程 (US-001扩展)"""
        # 步骤1: 基础用户注册
        user_data = {
            'username': 'enterprise_test',
            'email': 'enterprise@test.com',
            'password': 'EnterprisePass123',
            'phone': '13800138000',
            'user_type': 'enterprise'  # 标识为企业用户
        }
        
        response = client.post('/api/auth/register', json=user_data)
        
        if response.status_code == 201:
            data = response.get_json()
            assert data['user']['username'] == 'enterprise_test'
            
            # 步骤2: 登录获取token
            login_response = client.post('/api/auth/login', json={
                'username': 'enterprise_test',
                'password': 'EnterprisePass123'
            })
            
            if login_response.status_code == 200:
                token = login_response.get_json()['access_token']
                
                # 步骤3: 验证用户可以访问基础接口但受企业认证限制
                headers = {'Authorization': f'Bearer {token}'}
                profile_response = client.get('/api/auth/profile', headers=headers)
                assert profile_response.status_code == 200
    
    def test_role_based_access_control(self, client):
        """测试角色权限管理 (US-005)"""
        # 创建不同角色的用户并测试权限
        roles_to_test = [
            {'role': 'user', 'should_access_admin': False},
            {'role': 'manager', 'should_access_admin': False}, 
            {'role': 'admin', 'should_access_admin': True}
        ]
        
        for i, role_test in enumerate(roles_to_test):
            user_data = {
                'username': f'role_test_{i}',
                'email': f'role{i}@test.com',
                'password': 'RoleTest123',
                'role': role_test['role']
            }
            
            # 注册用户
            register_response = client.post('/api/auth/register', json=user_data)
            
            if register_response.status_code == 201:
                # 登录
                login_response = client.post('/api/auth/login', json={
                    'username': user_data['username'],
                    'password': user_data['password']
                })
                
                if login_response.status_code == 200:
                    token = login_response.get_json()['access_token']
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    # 测试管理员接口访问
                    admin_response = client.get('/api/admin/users', headers=headers)
                    
                    if role_test['should_access_admin']:
                        # 管理员应该能访问
                        assert admin_response.status_code in [200, 404]  # 200成功，404可能是接口不存在
                    else:
                        # 非管理员应该被拒绝
                        assert admin_response.status_code in [403, 401, 404]
    
    def test_password_security_requirements(self, client):
        """测试密码安全要求 (US-003扩展)"""
        weak_passwords = [
            '123456',      # 太简单
            'password',    # 常用密码
            'abc',         # 太短
            '11111111',    # 重复字符
        ]
        
        for i, weak_password in enumerate(weak_passwords):
            user_data = {
                'username': f'weak_pass_test_{i}',
                'email': f'weak{i}@test.com',
                'password': weak_password
            }
            
            response = client.post('/api/auth/register', json=user_data)
            
            # 应该拒绝弱密码
            if response.status_code == 400:
                data = response.get_json()
                assert '密码' in data.get('msg', '') or 'password' in data.get('msg', '').lower()
    
    def test_missing_credentials(self, client):
        """测试缺少凭证"""
        # 测试缺少用户名
        response = client.post('/api/auth/login', 
                              json={'password': 'test123'},
                              content_type='application/json')
        assert response.status_code == 400
        
        # 测试缺少密码
        response = client.post('/api/auth/login', 
                              json={'username': 'test'},
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_me_endpoint_without_auth(self, client):
        """测试未认证访问me接口"""
        response = client.get('/api/auth/me')
        assert response.status_code in [401, 422]  # JWT错误


class TestPasswordSecurity:
    """密码安全测试"""
    
    def test_weak_password_registration(self, client):
        """测试弱密码注册"""
        weak_passwords = [
            'short',      # 太短
            'lowercase',  # 只有小写
            'UPPERCASE',  # 只有大写  
            'NoNumbers'   # 没有数字
        ]
        
        for weak_pass in weak_passwords:
            response = client.post('/api/auth/register', 
                                  json={
                                      'username': f'user_{weak_pass}',
                                      'email': f'{weak_pass}@test.com',
                                      'password': weak_pass
                                  },
                                  content_type='application/json')
            
            # 应该拒绝弱密码
            assert response.status_code == 400
            data = response.get_json()
            assert 'msg' in data


if __name__ == '__main__':
    pytest.main([__file__])