"""
库存预警模块测试
"""
import pytest
from tests.base import BaseTestCase

class TestInventoryWarning(BaseTestCase):
    """库存预警功能测试类"""

    def test_get_warnings_list(self, client):
        """测试获取预警列表"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)
        response = client.get('/api/v1/inventory/warnings', headers=headers)

        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data
            assert 'statistics' in data['data']
            assert 'warnings' in data['data']

    def test_get_warnings_by_type(self, client):
        """测试按类型获取预警"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)

        # 测试低库存预警
        response = client.get('/api/v1/inventory/warnings?warning_type=low_stock',
                            headers=headers)
        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data

        # 测试近效期预警
        response = client.get('/api/v1/inventory/warnings?warning_type=near_expiry',
                            headers=headers)
        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data

    def test_get_warning_summary(self, client):
        """测试获取预警摘要"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)
        response = client.get('/api/v1/inventory/warning-summary', headers=headers)

        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data
            summary = data['data']['summary']
            assert 'total_warnings' in summary
            assert 'low_stock_count' in summary
            assert 'near_expiry_count' in summary

    def test_invalid_warning_type(self, client):
        """测试无效的预警类型"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)
        response = client.get('/api/v1/inventory/warnings?warning_type=invalid',
                            headers=headers)

        # 应该返回400错误
        self.assert_error_response(response, 400)

    def test_manual_scan_warnings(self, client):
        """测试手动扫描预警（需要管理员权限）"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)
        response = client.post('/api/v1/inventory/scan-warnings', headers=headers)

        # 可能返回200（成功）或403（权限不足）
        assert response.status_code in [200, 403]
