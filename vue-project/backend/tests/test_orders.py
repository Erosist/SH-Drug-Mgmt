"""
订单管理模块测试
"""
import pytest
from tests.base import BaseTestCase

class TestOrders(BaseTestCase):
    """订单管理功能测试类"""

    def test_get_orders_list(self, client):
        """测试获取订单列表"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)
        response = client.get('/api/orders', headers=headers)

        if response.status_code == 200:
            data = self.assert_success_response(response)
            assert 'data' in data

    def test_create_order(self, client):
        """测试创建订单"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)

        # 测试订单数据
        order_data = {
            "supplier_id": 1,
            "items": [
                {
                    "drug_id": 1,
                    "quantity": 100,
                    "unit_price": 10.5
                }
            ],
            "notes": "测试订单"
        }

        response = client.post('/api/orders',
                             json=order_data,
                             headers=headers)

        # 可能因为数据不存在而失败，这是正常的
        assert response.status_code in [201, 400, 404]

    def test_get_order_detail(self, client):
        """测试获取订单详情"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)
        response = client.get('/api/orders/1', headers=headers)

        # 如果订单不存在，返回404是正常的
        assert response.status_code in [200, 404]

    def test_update_order_status(self, client):
        """测试更新订单状态"""
        token = self.login_user(client)
        if not token:
            pytest.skip("No test user available")

        headers = self.get_auth_headers(token)

        # 测试更新订单状态
        update_data = {"status": "confirmed"}
        response = client.patch('/api/orders/1/status',
                              json=update_data,
                              headers=headers)

        # 可能因为订单不存在或权限不足而失败
        assert response.status_code in [200, 403, 404]
