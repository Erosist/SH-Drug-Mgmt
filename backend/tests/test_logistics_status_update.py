"""
测试订单状态更新API
"""
import pytest
import json
from app import create_app
from extensions import db
from models import User, Order, Tenant


@pytest.fixture
def app():
    """创建测试应用"""
    import os
    
    # 设置测试环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    from config import TestingConfig
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # 创建测试数据
        # 创建物流公司租户
        logistics_tenant = Tenant(
            name='测试物流公司',
            type='LOGISTICS',
            unified_social_credit_code='TEST001',
            legal_representative='张三',
            contact_person='李四',
            contact_phone='13800000001',
            contact_email='logistics@test.com',
            address='测试地址',
            business_scope='物流运输'
        )
        db.session.add(logistics_tenant)
        db.session.flush()
        
        # 创建药店租户
        pharmacy_tenant = Tenant(
            name='测试药店',
            type='PHARMACY',
            unified_social_credit_code='TEST002',
            legal_representative='王五',
            contact_person='赵六',
            contact_phone='13800000002',
            contact_email='pharmacy@test.com',
            address='测试药店地址',
            business_scope='药品零售'
        )
        db.session.add(pharmacy_tenant)
        db.session.flush()
        
        # 创建供应商租户
        supplier_tenant = Tenant(
            name='测试供应商',
            type='SUPPLIER',
            unified_social_credit_code='TEST003',
            legal_representative='孙七',
            contact_person='周八',
            contact_phone='13800000003',
            contact_email='supplier@test.com',
            address='测试供应商地址',
            business_scope='药品批发'
        )
        db.session.add(supplier_tenant)
        db.session.flush()
        
        # 创建物流用户
        logistics_user = User(
            username='test_logistics',
            email='logistics@test.com',
            role='logistics',
            tenant_id=logistics_tenant.id
        )
        logistics_user.set_password('password')
        db.session.add(logistics_user)
        
        # 创建药店用户
        pharmacy_user = User(
            username='test_pharmacy',
            email='pharmacy@test.com',
            role='pharmacy',
            tenant_id=pharmacy_tenant.id
        )
        pharmacy_user.set_password('password')
        db.session.add(pharmacy_user)
        
        # 创建测试订单
        order = Order(
            buyer_tenant_id=pharmacy_tenant.id,
            supplier_tenant_id=supplier_tenant.id,
            status='SHIPPED',
            logistics_tenant_id=logistics_tenant.id,
            created_by=pharmacy_user.id,  # 添加必需的 created_by 字段
            notes='测试订单'
        )
        db.session.add(order)
        
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def logistics_token(client):
    """获取物流用户的认证token"""
    response = client.post('/api/auth/login', 
                          json={'username': 'test_logistics', 'password': 'password'})
    data = json.loads(response.data)
    return data['access_token']


@pytest.fixture
def pharmacy_token(client):
    """获取药店用户的认证token"""
    response = client.post('/api/auth/login',
                          json={'username': 'test_pharmacy', 'password': 'password'})
    data = json.loads(response.data)
    return data['access_token']


class TestOrderStatusUpdate:
    """测试订单状态更新功能"""
    
    def test_logistics_update_shipped_to_in_transit(self, client, logistics_token):
        """测试物流用户将订单从SHIPPED更新为IN_TRANSIT"""
        headers = {'Authorization': f'Bearer {logistics_token}'}
        
        # 获取订单列表，找到测试订单
        response = client.get('/api/orders', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        orders = data['data']['items']
        assert len(orders) > 0
        
        order = orders[0]
        assert order['status'] == 'SHIPPED'
        
        # 更新订单状态
        response = client.patch(
            f'/api/orders/status/{order["id"]}',
            headers=headers,
            json={'status': 'IN_TRANSIT'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'IN_TRANSIT' in data['message']
        
    def test_logistics_update_in_transit_to_delivered(self, client, logistics_token):
        """测试物流用户将订单从IN_TRANSIT更新为DELIVERED"""
        headers = {'Authorization': f'Bearer {logistics_token}'}
        
        # 先将订单更新为IN_TRANSIT
        response = client.get('/api/orders', headers=headers)
        data = json.loads(response.data)
        order = data['data']['items'][0]
        
        # 确保订单是IN_TRANSIT状态
        client.patch(
            f'/api/orders/status/{order["id"]}',
            headers=headers,
            json={'status': 'IN_TRANSIT'}
        )
        
        # 然后更新为DELIVERED
        response = client.patch(
            f'/api/orders/status/{order["id"]}',
            headers=headers,
            json={'status': 'DELIVERED'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'DELIVERED' in data['message']
        
    def test_idempotent_status_update(self, client, logistics_token):
        """测试幂等状态更新（重复更新相同状态应该成功）"""
        headers = {'Authorization': f'Bearer {logistics_token}'}
        
        response = client.get('/api/orders', headers=headers)
        data = json.loads(response.data)
        order = data['data']['items'][0]
        
        # 第一次更新
        response = client.patch(
            f'/api/orders/status/{order["id"]}',
            headers=headers,
            json={'status': 'IN_TRANSIT'}
        )
        assert response.status_code == 200
        
        # 第二次更新相同状态（幂等操作）
        response = client.patch(
            f'/api/orders/status/{order["id"]}',
            headers=headers,
            json={'status': 'IN_TRANSIT'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert '已经是' in data['message']
        
    def test_invalid_status_transition(self, client, logistics_token):
        """测试无效的状态转换"""
        headers = {'Authorization': f'Bearer {logistics_token}'}
        
        response = client.get('/api/orders', headers=headers)
        data = json.loads(response.data)
        order = data['data']['items'][0]
        
        # 尝试从SHIPPED直接跳转到DELIVERED（应该失败）
        response = client.patch(
            f'/api/orders/status/{order["id"]}',
            headers=headers,
            json={'status': 'DELIVERED'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '无效的状态转换' in data['message']
        
    def test_unauthorized_status_update(self, client, pharmacy_token):
        """测试未授权用户更新状态（药店用户不能更新物流状态）"""
        headers = {'Authorization': f'Bearer {pharmacy_token}'}
        
        # 尝试更新订单状态（药店用户不应该有权限）
        response = client.patch(
            '/api/orders/status/1',
            headers=headers,
            json={'status': 'IN_TRANSIT'}
        )
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['success'] is False
        assert '权限不足' in data['message']
        
    def test_order_stats_for_logistics(self, client, logistics_token):
        """测试物流用户获取订单统计"""
        headers = {'Authorization': f'Bearer {logistics_token}'}
        
        response = client.get('/api/orders/stats', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        stats = data['data']
        
        # 检查统计数据结构
        expected_keys = ['total', 'shipped', 'in_transit', 'delivered']
        for key in expected_keys:
            assert key in stats
            assert isinstance(stats[key], int)
