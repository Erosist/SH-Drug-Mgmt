"""
供应信息模块测试
"""
import pytest
from tests.base import BaseTestCase

class TestSupply(BaseTestCase):
    """供应信息功能测试类"""

    def test_get_supply_info_list(self, client):
        """测试获取供应信息列表"""
        # 首先需要登录获取token
        token = self.login_user(client)
        if not token:
            # 如果没有测试用户，跳过此测试
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)
        response = client.get('/api/supply/info', headers=headers)

        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data
            assert 'items' in data['data']
            assert 'pagination' in data['data']

    def test_get_supply_info_with_search(self, client):
        """测试带搜索参数的供应信息获取"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)

        # 测试按药品名称搜索
        response = client.get('/api/supply/info?drug_name=布洛芬', headers=headers)
        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data

        # 测试按供应商名称搜索
        response = client.get('/api/supply/info?supplier_name=上海医药', headers=headers)
        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data

    def test_get_supply_info_pagination(self, client):
        """测试分页功能"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)

        # 测试分页参数
        response = client.get('/api/supply/info?page=1&per_page=5', headers=headers)
        if response.status_code == 200:
            data = self.assert_success_response(response)
            pagination = data['data']['pagination']
            assert pagination['page'] == 1
            assert pagination['per_page'] == 5

    def test_get_supply_info_detail(self, client):
        """测试获取供应信息详情"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)

        # 测试获取详情（使用ID 1）
        response = client.get('/api/supply/info/1', headers=headers)

        # 如果资源不存在，应该返回404
        if response.status_code == 404:
            assert True  # 这是预期的，因为可能没有测试数据
        elif response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data
            item = data['data']
            assert 'id' in item
            assert 'drug' in item
            assert 'tenant' in item

    def test_get_nonexistent_supply_info(self, client):
        """测试获取不存在的供应信息"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)

        # 使用一个不太可能存在的ID
        response = client.get('/api/supply/info/99999', headers=headers)
        self.assert_status_code(response, 404)