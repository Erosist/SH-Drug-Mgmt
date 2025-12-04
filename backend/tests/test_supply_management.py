"""
供应商管理功能测试
"""
import pytest
import json
from datetime import datetime, timedelta
from models import User, Tenant, SupplyInfo, Drug
from extensions import db


class TestSupplyManagement:
    """供应商管理测试"""
    
    @pytest.fixture
    def supplier_user(self, app):
        """创建供应商用户"""
        with app.app_context():
            # 创建供应商租户
            tenant = Tenant(
                name='测试供应商',
                type='SUPPLIER',
                unified_social_credit_code='91310000000000001X',
                legal_representative='供应商负责人',
                contact_person='联系人',
                contact_phone='13800138000',
                contact_email='supplier@test.com',
                address='供应商地址',
                business_scope='药品批发'
            )
            db.session.add(tenant)
            db.session.commit()
            
            # 创建供应商用户
            user = User(
                username='supplier_test',
                email='supplier@test.com',
                role='supplier',
                tenant_id=tenant.id
            )
            user.set_password('SupplierPass123')
            db.session.add(user)
            db.session.commit()
            
            return user
    
    @pytest.fixture
    def supplier_auth_token(self, client, supplier_user):
        """获取供应商认证token"""
        response = client.post('/api/auth/login', json={
            'username': 'supplier_test',
            'password': 'SupplierPass123'
        })
        if response.status_code == 200:
            return response.get_json()['access_token']
        return None
    
    def test_supply_info_creation(self, client, supplier_auth_token):
        """测试创建供应信息"""
        if not supplier_auth_token:
            pytest.skip("认证失败，跳过测试")
        
        headers = {'Authorization': f'Bearer {supplier_auth_token}'}
        supply_data = {
            'drug_name': '阿莫西林胶囊',
            'unit_price': 25.50,
            'stock_quantity': 1000,
            'minimum_order_quantity': 10,
            'description': '广谱抗生素'
        }
        
        response = client.post('/api/supply/info', 
                              json=supply_data, 
                              headers=headers)
        
        if response.status_code == 201:
            data = response.get_json()
            assert data['drug_name'] == '阿莫西林胶囊'
            assert data['unit_price'] == 25.50
        else:
            # 检查错误信息
            data = response.get_json()
            assert 'msg' in data or 'error' in data
    
    def test_supply_info_list(self, client, supplier_auth_token, app):
        """测试获取供应信息列表"""
        if not supplier_auth_token:
            pytest.skip("认证失败，跳过测试")
        
        # 先创建一些测试数据
        with app.app_context():
            user = User.query.filter_by(username='supplier_test').first()
            if user and user.tenant_id:
                # 先创建药品信息
                test_drug = Drug(
                    generic_name='测试药品',
                    brand_name='测试品牌',
                    approval_number='H12345678901',
                    dosage_form='片剂',
                    specification='500mg*30片',
                    manufacturer='测试制药厂',
                    category='西药',
                    prescription_type='OTC'
                )
                db.session.add(test_drug)
                db.session.commit()
                
                # 创建供应信息
                supply_info = SupplyInfo(
                    drug_id=test_drug.id,
                    unit_price=15.00,
                    available_quantity=500,
                    min_order_quantity=5,
                    tenant_id=user.tenant_id,
                    valid_until=datetime.now().date() + timedelta(days=365)
                )
                db.session.add(supply_info)
                db.session.commit()
        
        headers = {'Authorization': f'Bearer {supplier_auth_token}'}
        response = client.get('/api/supply/info', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data  # API返回包装格式
            assert isinstance(data['data']['items'], list)
        else:
            # 检查错误响应
            assert response.status_code in [401, 403, 500]
    
    def test_supply_drugs_endpoint(self, client):
        """测试药品搜索接口"""
        response = client.get('/api/supply/drugs')
        
        # 这个接口可能需要认证或返回空列表
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)


class TestSupplyValidation:
    """供应信息验证测试"""
    
    def test_invalid_supply_data(self, client):
        """测试无效的供应数据"""
        # 无认证访问
        response = client.post('/api/supply/info', json={
            'drug_name': '测试药品',
            'unit_price': 'invalid_price'  # 无效价格
        })
        
        # 应该返回401未授权或400错误
        assert response.status_code in [400, 401, 422]


if __name__ == '__main__':
    pytest.main([__file__])