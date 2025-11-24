"""
基础测试类和工具函数
"""
import json
from flask import url_for

class BaseTestCase:
    """基础测试类，提供通用的测试方法"""

    def login_user(self, client, username='testuser', password='password123'):
        """用户登录，返回JWT token"""
        response = client.post('/api/auth/login',
                             json={'username': username, 'password': password})

        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('access_token')
        return None

    def get_auth_headers(self, token):
        """获取认证headers"""
        return {'Authorization': f'Bearer {token}'}

    def assert_status_code(self, response, expected_code):
        """断言状态码"""
        assert response.status_code == expected_code, \
            f"Expected status code {expected_code}, got {response.status_code}. Response: {response.data}"

    def assert_json_response(self, response):
        """断言响应是JSON格式"""
        assert response.content_type == 'application/json'
        return json.loads(response.data)

    def assert_success_response(self, response):
        """断言成功响应"""
        self.assert_status_code(response, 200)
        data = self.assert_json_response(response)
        return data

    def assert_error_response(self, response, expected_code=400):
        """断言错误响应"""
        self.assert_status_code(response, expected_code)
        data = self.assert_json_response(response)
        assert 'error' in data or 'msg' in data
        return data
