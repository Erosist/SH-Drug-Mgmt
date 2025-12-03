"""
测试库存管理系统
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import InventoryItem, Tenant, User


class TestInventoryAPI:
    """测试库存API"""
    
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
        """创建测试客户端"""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, client, app):
        """创建认证头"""
        with app.app_context():
            # 创建测试租户
            tenant = Tenant(
                name='测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000000000001X',
                legal_representative='测试负责人',
                contact_person='联系人',
                contact_phone='13800138000',
                contact_email='test@example.com',
                address='测试地址',
                business_scope='药品零售'
            )
            db.session.add(tenant)
            db.session.commit()
            
            # 创建测试用户
            user = User(
                username='testuser',
                email='test@example.com',
                role='pharmacy',
                tenant_id=tenant.id
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # 登录获取token
            response = client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'password123'
            })
            
            if response.status_code == 200:
                token = response.get_json()['token']
                return {'Authorization': f'Bearer {token}'}
            else:
                return {}
    
    def test_get_inventory_list(self, client, auth_headers, app):
        """测试获取库存列表"""
        with app.app_context():
            # 创建测试库存项目
            tenant = Tenant.query.first()
            inventory_item = InventoryItem(
                drug_name='阿莫西林',
                quantity=100,
                unit_price=25.50,
                expiry_date=datetime.now() + timedelta(days=365),
                batch_number='AMX20241201',
                tenant_id=tenant.id
            )
            db.session.add(inventory_item)
            db.session.commit()
            
            response = client.get('/inventory/', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) >= 1
            assert data[0]['drug_name'] == '阿莫西林'
            assert data[0]['quantity'] == 100
    
    def test_add_inventory_item(self, client, auth_headers):
        """测试添加库存项目"""
        new_item = {
            'drug_name': '布洛芬',
            'quantity': 50,
            'unit_price': 18.90,
            'expiry_date': '2025-12-31',
            'batch_number': 'IBU20241201',
            'supplier': '测试供应商'
        }
        
        response = client.post('/inventory/', 
                             json=new_item, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['drug_name'] == '布洛芬'
        assert data['quantity'] == 50
        assert 'id' in data
    
    def test_update_inventory_item(self, client, auth_headers, app):
        """测试更新库存项目"""
        with app.app_context():
            # 创建测试项目
            tenant = Tenant.query.first()
            item = InventoryItem(
                drug_name='维生素C',
                quantity=30,
                unit_price=12.00,
                expiry_date=datetime.now() + timedelta(days=180),
                batch_number='VTC20241201',
                tenant_id=tenant.id
            )
            db.session.add(item)
            db.session.commit()
            item_id = item.id
        
        updated_data = {
            'drug_name': '维生素C片',
            'quantity': 35,
            'unit_price': 13.50
        }
        
        response = client.put(f'/inventory/{item_id}', 
                            json=updated_data, 
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['drug_name'] == '维生素C片'
        assert data['quantity'] == 35
        assert data['unit_price'] == 13.50
    
    def test_delete_inventory_item(self, client, auth_headers, app):
        """测试删除库存项目"""
        with app.app_context():
            tenant = Tenant.query.first()
            item = InventoryItem(
                drug_name='测试药品',
                quantity=10,
                unit_price=5.00,
                expiry_date=datetime.now() + timedelta(days=90),
                batch_number='TEST20241201',
                tenant_id=tenant.id
            )
            db.session.add(item)
            db.session.commit()
            item_id = item.id
        
        response = client.delete(f'/inventory/{item_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_search_inventory(self, client, auth_headers, app):
        """测试搜索库存"""
        with app.app_context():
            tenant = Tenant.query.first()
            
            # 创建多个测试项目
            items = [
                InventoryItem(drug_name='阿莫西林', quantity=50, unit_price=25.00, tenant_id=tenant.id),
                InventoryItem(drug_name='阿司匹林', quantity=30, unit_price=15.00, tenant_id=tenant.id),
                InventoryItem(drug_name='布洛芬', quantity=40, unit_price=20.00, tenant_id=tenant.id)
            ]
            
            for item in items:
                item.expiry_date = datetime.now() + timedelta(days=365)
                item.batch_number = f'TEST{item.drug_name[:3].upper()}'
                db.session.add(item)
            
            db.session.commit()
        
        response = client.get('/inventory/search?q=阿', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2  # 阿莫西林和阿司匹林
        
        drug_names = [item['drug_name'] for item in data]
        assert '阿莫西林' in drug_names
        assert '阿司匹林' in drug_names


class TestInventoryWarnings:
    """测试库存预警"""
    
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
    
    def test_low_stock_warning(self, client, app):
        """测试低库存预警"""
        with app.app_context():
            # 创建租户
            tenant = Tenant(
                name='测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000000000001X',
                legal_representative='负责人',
                contact_person='联系人',
                contact_phone='13800138000',
                contact_email='test@example.com',
                address='地址',
                business_scope='药品零售'
            )
            db.session.add(tenant)
            db.session.commit()
            
            # 创建低库存项目
            low_stock_item = InventoryItem(
                drug_name='紧急药品',
                quantity=5,  # 低于阈值
                unit_price=30.00,
                expiry_date=datetime.now() + timedelta(days=365),
                batch_number='URGENT001',
                tenant_id=tenant.id,
                warning_threshold=10
            )
            db.session.add(low_stock_item)
            db.session.commit()
            
            response = client.get('/inventory/warnings/low-stock')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) >= 1
            assert data[0]['drug_name'] == '紧急药品'
            assert data[0]['current_quantity'] == 5
            assert data[0]['warning_threshold'] == 10
    
    def test_expiry_warning(self, client, app):
        """测试过期预警"""
        with app.app_context():
            tenant = Tenant.query.first()
            if not tenant:
                tenant = Tenant(
                    name='测试药店',
                    type='PHARMACY',
                    unified_social_credit_code='91310000000000001X',
                    legal_representative='负责人',
                    contact_person='联系人',
                    contact_phone='13800138000',
                    contact_email='test@example.com',
                    address='地址',
                    business_scope='药品零售'
                )
                db.session.add(tenant)
                db.session.commit()
            
            # 创建即将过期的项目
            expiring_item = InventoryItem(
                drug_name='即将过期药品',
                quantity=20,
                unit_price=15.00,
                expiry_date=datetime.now() + timedelta(days=30),  # 30天后过期
                batch_number='EXP001',
                tenant_id=tenant.id
            )
            db.session.add(expiring_item)
            db.session.commit()
            
            response = client.get('/inventory/warnings/expiry')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) >= 1
            
            # 找到我们创建的项目
            found_item = next((item for item in data if item['drug_name'] == '即将过期药品'), None)
            assert found_item is not None
            assert found_item['days_until_expiry'] <= 30


if __name__ == '__main__':
    pytest.main([__file__])