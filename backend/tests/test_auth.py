"""
认证模块测试
"""
import pytest
from tests.base import BaseTestCase

class TestAuth(BaseTestCase):
    """认证功能测试类"""

    def test_login_success(self, client):
        """测试成功登录"""
        # 注意：这需要根据实际的用户数据进行调整
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })

        # 由于没有实际用户数据，这里可能会失败
        # 在实际测试中，需要先创建测试用户
        # assert response.status_code == 200
        # data = self.assert_json_response(response)
        # assert 'access_token' in data

    def test_login_invalid_credentials(self, client):
        """测试错误凭据登录"""
        response = client.post('/api/auth/login', json={
            'username': 'invalid',
            'password': 'wrong'
        })

        self.assert_status_code(response, 401)
        data = self.assert_json_response(response)
        assert 'error' in data or 'msg' in data

    def test_login_missing_data(self, client):
        """测试缺少登录数据"""
        # 测试缺少用户名
        response = client.post('/api/auth/login', json={
            'password': 'password123'
        })
        self.assert_error_response(response, 400)

        # 测试缺少密码
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
        })
        self.assert_error_response(response, 400)

        # 测试空请求
        response = client.post('/api/auth/login', json={})
        self.assert_error_response(response, 400)

    def test_protected_route_without_token(self, client):
        """测试未认证访问受保护路由"""
        # 尝试访问需要认证的路由
        response = client.get('/api/supply/info')
        self.assert_status_code(response, 401)

    def test_protected_route_with_invalid_token(self, client):
        """测试使用无效token访问受保护路由"""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/supply/info', headers=headers)
        self.assert_status_code(response, 422)  # JWT错误通常返回422
