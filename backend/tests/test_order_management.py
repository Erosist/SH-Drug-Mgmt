"""
测试订单管理系统
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import Order, OrderItem, User, Tenant, SupplyInfo


class TestOrderManagement:
    """测试订单管理"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        import os
        os.environ['FLASK_ENV'] = 'testing'
        app = create_app()
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def test_data(self, app):
        """创建测试数据"""
        with app.app_context():
            # 创建药店租户
            pharmacy_tenant = Tenant(
                name='测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000000000001X',
                legal_representative='药店负责人',
                contact_person='药店联系人',
                contact_phone='13800138001',
                contact_email='pharmacy@test.com',
                address='药店地址',
                business_scope='药品零售'
            )
            
            # 创建供应商租户
            supplier_tenant = Tenant(
                name='测试供应商',
                type='SUPPLIER',
                unified_social_credit_code='91310000000000002X',
                legal_representative='供应商负责人',
                contact_person='供应商联系人',
                contact_phone='13800138002',
                contact_email='supplier@test.com',
                address='供应商地址',
                business_scope='药品批发'
            )
            
            db.session.add_all([pharmacy_tenant, supplier_tenant])
            db.session.commit()
            
            # 创建用户
            pharmacy_user = User(
                username='pharmacy_user',
                email='pharmacy@test.com',
                role='pharmacy',
                tenant_id=pharmacy_tenant.id
            )
            pharmacy_user.set_password('password123')
            
            supplier_user = User(
                username='supplier_user',
                email='supplier@test.com',
                role='supplier',
                tenant_id=supplier_tenant.id
            )
            supplier_user.set_password('password123')
            
            db.session.add_all([pharmacy_user, supplier_user])
            db.session.commit()
            
            # 创建供应信息
            supply_info = SupplyInfo(
                drug_name='阿莫西林',
                unit_price=25.50,
                stock_quantity=1000,
                minimum_order_quantity=10,
                tenant_id=supplier_tenant.id
            )
            
            db.session.add(supply_info)
            db.session.commit()
            
            return {
                'pharmacy_tenant': pharmacy_tenant,
                'supplier_tenant': supplier_tenant,
                'pharmacy_user': pharmacy_user,
                'supplier_user': supplier_user,
                'supply_info': supply_info
            }
    
    @pytest.fixture
    def pharmacy_auth_headers(self, client, test_data):
        """获取药店用户认证头"""
        response = client.post('/auth/login', json={
            'username': 'pharmacy_user',
            'password': 'password123'
        })
        
        if response.status_code == 200:
            token = response.get_json()['token']
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    @pytest.fixture
    def supplier_auth_headers(self, client, test_data):
        """获取供应商用户认证头"""
        response = client.post('/auth/login', json={
            'username': 'supplier_user',
            'password': 'password123'
        })
        
        if response.status_code == 200:
            token = response.get_json()['token']
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def test_create_order(self, client, pharmacy_auth_headers, test_data):
        """测试创建订单"""
        order_data = {
            'supplier_id': test_data['supplier_tenant'].id,
            'items': [
                {
                    'drug_name': '阿莫西林',
                    'quantity': 50,
                    'unit_price': 25.50
                }
            ],
            'delivery_address': '上海市浦东新区张江路123号',
            'notes': '紧急采购订单'
        }
        
        response = client.post('/orders/', 
                             json=order_data,
                             headers=pharmacy_auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'order_number' in data
        assert data['status'] == 'pending'
        assert len(data['items']) == 1
        assert data['items'][0]['drug_name'] == '阿莫西林'
        assert data['total_amount'] == 1275.0  # 50 * 25.50
    
    def test_get_orders_list(self, client, pharmacy_auth_headers, test_data, app):
        """测试获取订单列表"""
        with app.app_context():
            # 创建测试订单
            order = Order(
                pharmacy_id=test_data['pharmacy_tenant'].id,
                supplier_id=test_data['supplier_tenant'].id,
                status='pending',
                total_amount=500.0,
                delivery_address='测试地址',
                created_by=test_data['pharmacy_user'].id
            )
            db.session.add(order)
            db.session.commit()
            
            # 添加订单项目
            order_item = OrderItem(
                order_id=order.id,
                drug_name='测试药品',
                quantity=20,
                unit_price=25.0
            )
            db.session.add(order_item)
            db.session.commit()
        
        response = client.get('/orders/', headers=pharmacy_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) >= 1
        assert data[0]['status'] == 'pending'
        assert data[0]['total_amount'] == 500.0
    
    def test_update_order_status(self, client, supplier_auth_headers, test_data, app):
        """测试更新订单状态"""
        with app.app_context():
            # 创建测试订单
            order = Order(
                pharmacy_id=test_data['pharmacy_tenant'].id,
                supplier_id=test_data['supplier_tenant'].id,
                status='pending',
                total_amount=300.0,
                delivery_address='测试地址',
                created_by=test_data['pharmacy_user'].id
            )
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        
        status_update = {
            'status': 'confirmed',
            'notes': '订单已确认，预计3天内发货'
        }
        
        response = client.put(f'/orders/{order_id}/status',
                            json=status_update,
                            headers=supplier_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'confirmed'
    
    def test_order_validation(self, client, pharmacy_auth_headers):
        """测试订单验证"""
        # 测试无效订单数据
        invalid_order = {
            'supplier_id': None,  # 缺少供应商ID
            'items': [],  # 空项目列表
            'delivery_address': ''  # 空地址
        }
        
        response = client.post('/orders/',
                             json=invalid_order,
                             headers=pharmacy_auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'message' in data
    
    def test_order_search(self, client, pharmacy_auth_headers, test_data, app):
        """测试订单搜索"""
        with app.app_context():
            # 创建多个测试订单
            orders = []
            for i in range(3):
                order = Order(
                    pharmacy_id=test_data['pharmacy_tenant'].id,
                    supplier_id=test_data['supplier_tenant'].id,
                    status='pending',
                    total_amount=100.0 * (i + 1),
                    delivery_address=f'测试地址{i+1}',
                    created_by=test_data['pharmacy_user'].id,
                    notes=f'测试订单{i+1}'
                )
                db.session.add(order)
                orders.append(order)
            
            db.session.commit()
            
            # 获取第一个订单号进行搜索
            search_order_number = orders[0].order_number
        
        response = client.get(f'/orders/search?q={search_order_number}',
                            headers=pharmacy_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['order_number'] == search_order_number
    
    def test_order_statistics(self, client, pharmacy_auth_headers, test_data, app):
        """测试订单统计"""
        with app.app_context():
            # 创建不同状态的订单
            statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            for status in statuses:
                order = Order(
                    pharmacy_id=test_data['pharmacy_tenant'].id,
                    supplier_id=test_data['supplier_tenant'].id,
                    status=status,
                    total_amount=200.0,
                    delivery_address='测试地址',
                    created_by=test_data['pharmacy_user'].id
                )
                db.session.add(order)
            
            db.session.commit()
        
        response = client.get('/orders/statistics', headers=pharmacy_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'total_orders' in data
        assert 'pending_orders' in data
        assert 'completed_orders' in data
        assert data['total_orders'] >= 4  # 至少4个订单


class TestOrderWorkflow:
    """测试订单工作流程"""
    
    @pytest.fixture
    def app(self):
        import os
        os.environ['FLASK_ENV'] = 'testing'
        app = create_app()
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_complete_order_lifecycle(self, app):
        """测试完整的订单生命周期"""
        with app.app_context():
            # 创建基础数据
            supplier = Tenant(name='供应商', type='SUPPLIER', 
                            unified_social_credit_code='123456789', 
                            legal_representative='负责人',
                            contact_person='联系人', contact_phone='123',
                            contact_email='test@test.com', address='地址',
                            business_scope='批发')
            pharmacy = Tenant(name='药店', type='PHARMACY',
                            unified_social_credit_code='987654321',
                            legal_representative='负责人2',
                            contact_person='联系人2', contact_phone='456',
                            contact_email='test2@test.com', address='地址2',
                            business_scope='零售')
            
            db.session.add_all([supplier, pharmacy])
            db.session.commit()
            
            user = User(username='testuser', email='test@test.com', 
                       role='pharmacy', tenant_id=pharmacy.id)
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            # 1. 创建订单 (pending)
            order = Order(
                pharmacy_id=pharmacy.id,
                supplier_id=supplier.id,
                status='pending',
                total_amount=500.0,
                delivery_address='交付地址',
                created_by=user.id
            )
            db.session.add(order)
            db.session.commit()
            
            assert order.status == 'pending'
            
            # 2. 确认订单 (confirmed)
            order.status = 'confirmed'
            order.confirmed_at = datetime.utcnow()
            db.session.commit()
            
            assert order.status == 'confirmed'
            assert order.confirmed_at is not None
            
            # 3. 发货 (shipped)
            order.status = 'shipped'
            order.shipped_at = datetime.utcnow()
            db.session.commit()
            
            assert order.status == 'shipped'
            
            # 4. 完成订单 (completed)
            order.status = 'completed'
            order.completed_at = datetime.utcnow()
            db.session.commit()
            
            assert order.status == 'completed'
            assert order.completed_at is not None


if __name__ == '__main__':
    pytest.main([__file__])