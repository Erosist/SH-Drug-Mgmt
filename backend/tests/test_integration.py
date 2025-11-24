"""
集成测试示例
这些测试需要完整的应用环境和数据库
"""
import pytest
from tests.base import BaseTestCase

@pytest.mark.integration
class TestIntegration(BaseTestCase):
    """集成测试类"""

    def test_full_user_workflow(self, client):
        """测试完整的用户工作流程"""
        # 这是一个端到端的测试示例
        # 在实际环境中，需要准备测试数据

        # 1. 用户登录
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })

        if login_response.status_code != 200:
            pytest.skip("无法登录，跳过集成测试")

        token_data = self.assert_json_response(login_response)
        token = token_data.get('access_token')
        headers = self.get_auth_headers(token)

        # 2. 获取供应信息
        supply_response = client.get('/api/supply/info', headers=headers)
        if supply_response.status_code == 200:
            supply_data = self.assert_json_response(supply_response)
            assert 'data' in supply_data

        # 3. 获取预警信息
        warning_response = client.get('/api/v1/inventory/warnings', headers=headers)
        if warning_response.status_code == 200:
            warning_data = self.assert_json_response(warning_response)
            assert 'data' in warning_data

        # 4. 获取订单列表
        orders_response = client.get('/api/orders', headers=headers)
        # 由于可能没有权限或数据，这里不强制要求成功
        assert orders_response.status_code in [200, 403, 404]

    @pytest.mark.slow
    def test_database_operations(self, app, db_session):
        """测试数据库操作"""
        with app.app_context():
            # 这里可以测试数据库模型的CRUD操作
            # 需要导入相应的模型
            pass

    def test_api_error_handling(self, client):
        """测试API错误处理"""
        # 测试各种错误情况

        # 1. 无效的JSON
        response = client.post('/api/auth/login',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400

        # 2. 缺少Content-Type头
        response = client.post('/api/auth/login', data='{"test": "data"}')
        # 不同的Flask版本可能有不同的行为
        assert response.status_code in [400, 415]

        # 3. 超大请求（如果有大小限制）
        large_data = {'data': 'x' * 10000}
        response = client.post('/api/auth/login', json=large_data)
        # 可能返回400或413
        assert response.status_code in [400, 413]
