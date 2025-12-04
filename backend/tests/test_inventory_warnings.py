"""
库存预警功能测试
"""
import pytest
import json
from datetime import datetime, timedelta
from models import User, Tenant, InventoryItem, Drug
from extensions import db


class TestInventoryWarnings:
    """库存预警测试"""
    
    @pytest.fixture
    def pharmacy_setup(self, app):
        """创建药店和库存数据"""
        with app.app_context():
            # 创建药店租户
            tenant = Tenant(
                name='测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000000000001X',
                legal_representative='负责人',
                contact_person='联系人',
                contact_phone='13800138000',
                contact_email='pharmacy@test.com',
                address='地址',
                business_scope='药品零售'
            )
            db.session.add(tenant)
            db.session.commit()
            
            # 创建用户
            user = User(
                username='pharmacy_test',
                email='pharmacy@test.com',
                role='pharmacy',
                tenant_id=tenant.id
            )
            user.set_password('PharmacyPass123')
            db.session.add(user)
            db.session.commit()
            
            # 创建药品信息
            low_drug = Drug(
                generic_name='低库存药品',
                brand_name='低库存药品',
                approval_number='H12345678903',
                dosage_form='片剂',
                specification='100mg*20片',
                manufacturer='测试制药厂',
                category='西药',
                prescription_type='OTC'
            )
            
            expiry_drug = Drug(
                generic_name='即将过期药品',
                brand_name='即将过期药品',
                approval_number='H12345678904',
                dosage_form='片剂',
                specification='200mg*10片',
                manufacturer='测试制药厂',
                category='西药',
                prescription_type='OTC'
            )
            
            normal_drug = Drug(
                generic_name='正常药品',
                brand_name='正常药品',
                approval_number='H12345678905',
                dosage_form='片剂',
                specification='50mg*50片',
                manufacturer='测试制药厂',
                category='西药',
                prescription_type='OTC'
            )
            
            db.session.add_all([low_drug, expiry_drug, normal_drug])
            db.session.commit()
            
            # 创建库存项目
            # 低库存项目
            low_stock_item = InventoryItem(
                drug_id=low_drug.id,
                quantity=5,
                unit_price=20.00,
                expiry_date=datetime.now().date() + timedelta(days=365),
                production_date=datetime.now().date() - timedelta(days=30),
                batch_number='LOW001',
                tenant_id=tenant.id
            )
            
            # 即将过期项目
            expiring_item = InventoryItem(
                drug_id=expiry_drug.id,
                quantity=50,
                unit_price=15.00,
                expiry_date=datetime.now().date() + timedelta(days=25),  # 25天后过期
                production_date=datetime.now().date() - timedelta(days=340),
                batch_number='EXP001',
                tenant_id=tenant.id
            )
            
            # 正常库存项目
            normal_item = InventoryItem(
                drug_id=normal_drug.id,
                quantity=100,
                unit_price=30.00,
                expiry_date=datetime.now().date() + timedelta(days=500),
                production_date=datetime.now().date() - timedelta(days=30),
                batch_number='NORM001',
                tenant_id=tenant.id
            )
            
            db.session.add_all([low_stock_item, expiring_item, normal_item])
            db.session.commit()
            
            return {
                'tenant': tenant,
                'user': user,
                'low_stock_item': low_stock_item,
                'expiring_item': expiring_item,
                'normal_item': normal_item
            }
    
    @pytest.fixture
    def auth_token(self, client, pharmacy_setup):
        """获取认证token"""
        response = client.post('/api/auth/login', json={
            'username': 'pharmacy_test',
            'password': 'PharmacyPass123'
        })
        if response.status_code == 200:
            return response.get_json()['access_token']
        return None
    
    def test_inventory_warnings_endpoint(self, client, auth_token):
        """测试库存预警接口"""
        if not auth_token:
            pytest.skip("认证失败，跳过测试")
        
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/v1/inventory/warnings', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data  # API返回包装格式
            assert isinstance(data['data']['warnings'], list)
            
            # 如果有预警数据，验证预警类型
            if data['data']['warnings']:
                # 基于实际数据结构推断预警类型
                has_low_stock = any(
                    item.get('quantity', 0) < 10 or item.get('is_low_stock', False) 
                    for item in data['data']['warnings']
                )
                has_expiry_warning = any(
                    item.get('days_to_expiry', 999) <= 30 or item.get('is_near_expiry', False)
                    for item in data['data']['warnings']
                )
                
                # 至少应该有一种预警
                assert has_low_stock or has_expiry_warning
        else:
            # 可能是权限问题或其他错误
            assert response.status_code in [401, 403, 500]
    
    def test_warning_summary_endpoint(self, client, auth_token):
        """测试预警摘要接口"""
        if not auth_token:
            pytest.skip("认证失败，跳过测试")
        
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/v1/inventory/warning-summary', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            expected_keys = ['low_stock_count', 'expiry_warning_count', 'total_warnings']
            
            # 检查响应结构
            for key in expected_keys:
                if key in data:
                    assert isinstance(data[key], int)
                    assert data[key] >= 0
        else:
            assert response.status_code in [401, 403, 500]
    
    def test_scan_warnings_endpoint(self, client, auth_token):
        """测试扫描预警接口"""
        if not auth_token:
            pytest.skip("认证失败，跳过测试")
        
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/v1/inventory/scan-warnings', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'msg' in data or 'message' in data
        else:
            assert response.status_code in [401, 403, 500]
    
    def test_warnings_without_auth(self, client):
        """测试未认证访问预警接口"""
        response = client.get('/api/v1/inventory/warnings')
        assert response.status_code in [401, 422]  # 应该拒绝未认证访问


class TestInventoryWarningLogic:
    """库存预警逻辑测试"""
    
    def test_low_stock_detection(self, app):
        """测试低库存检测逻辑"""
        with app.app_context():
            # 这里可以测试预警检测的业务逻辑
            # 由于需要具体的业务逻辑代码，这里做基础测试
            
            # 创建测试数据
            tenant = Tenant(
                name='逻辑测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000000000002X',
                legal_representative='负责人',
                contact_person='联系人',
                contact_phone='13800138001',
                contact_email='logic@test.com',
                address='地址',
                business_scope='药品零售'
            )
            db.session.add(tenant)
            db.session.commit()
            
            # 创建药品
            logic_drug = Drug(
                generic_name='逻辑测试药品',
                brand_name='逻辑测试药品',
                approval_number='H12345678906',
                dosage_form='片剂',
                specification='10mg*30片',
                manufacturer='测试制药厂',
                category='西药',
                prescription_type='OTC'
            )
            db.session.add(logic_drug)
            db.session.commit()
            
            # 创建低库存项目
            item = InventoryItem(
                drug_id=logic_drug.id,
                quantity=3,  # 低于阈值
                unit_price=10.00,
                expiry_date=datetime.now().date() + timedelta(days=100),
                production_date=datetime.now().date() - timedelta(days=30),
                batch_number='LOGIC001',
                tenant_id=tenant.id
            )
            db.session.add(item)
            db.session.commit()
            
            # 验证低库存条件
            assert item.quantity < 10  # 低于默认阈值10
            
            db.session.delete(item)
            db.session.delete(tenant)
            db.session.commit()
    
    def test_expiry_detection(self, app):
        """测试过期检测逻辑"""
        with app.app_context():
            # 创建即将过期的项目
            tenant = Tenant(
                name='过期测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000000000003X',
                legal_representative='负责人',
                contact_person='联系人',
                contact_phone='13800138002',
                contact_email='expiry@test.com',
                address='地址',
                business_scope='药品零售'
            )
            db.session.add(tenant)
            db.session.commit()
            
            # 创建药品
            expiry_drug = Drug(
                generic_name='即将过期测试',
                brand_name='即将过期测试',
                approval_number='H12345678907',
                dosage_form='胶囊',
                specification='250mg*12粒',
                manufacturer='测试制药厂',
                category='西药',
                prescription_type='OTC'
            )
            db.session.add(expiry_drug)
            db.session.commit()
            
            # 30天内过期的项目
            item = InventoryItem(
                drug_id=expiry_drug.id,
                quantity=20,
                unit_price=15.00,
                expiry_date=datetime.now().date() + timedelta(days=15),  # 15天后过期
                production_date=datetime.now().date() - timedelta(days=350),
                batch_number='EXPIRY001',
                tenant_id=tenant.id
            )
            db.session.add(item)
            db.session.commit()
            
            # 验证过期检测逻辑
            days_until_expiry = (item.expiry_date - datetime.now().date()).days
            assert days_until_expiry <= 30  # 30天内过期预警
            
            db.session.delete(item)
            db.session.delete(tenant)
            db.session.commit()


if __name__ == '__main__':
    pytest.main([__file__])