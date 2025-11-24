"""
应用基础功能测试
"""
import pytest
from tests.base import BaseTestCase

class TestApp(BaseTestCase):
    """应用基础功能测试类"""

    def test_app_exists(self, app):
        """测试应用实例存在"""
        assert app is not None

    def test_app_is_testing(self, app):
        """测试应用在测试模式"""
        assert app.config.get('TESTING') is True

    def test_index_route(self, client):
        """测试根路由"""
        response = client.get('/')
        self.assert_status_code(response, 200)
        data = self.assert_json_response(response)
        assert 'msg' in data
        assert 'Flask' in data['msg']

    def test_nonexistent_route(self, client):
        """测试不存在的路由"""
        response = client.get('/nonexistent')
        self.assert_status_code(response, 404)

    def test_options_request(self, client):
        """测试OPTIONS请求（CORS相关）"""
        response = client.options('/')
        # OPTIONS请求应该被允许
        assert response.status_code in [200, 405]
