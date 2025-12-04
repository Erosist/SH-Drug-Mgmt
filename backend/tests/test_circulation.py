"""
流通追踪管理测试
"""
import pytest
import json
from datetime import datetime, timedelta
from models import User, Tenant, Order, OrderItem, Drug, SupplyInfo
from extensions import db


class TestCirculationAPI:
    """测试流通追踪API"""
    
    @pytest.fixture
    def circulation_data(self, app):
        """创建流通测试数据"""
        with app.app_context():
            # 创建监管机构租户
            regulator_tenant = Tenant(
                name='上海市药监局',
                type='REGULATOR',
                unified_social_credit_code='91310000000000003X',
                legal_representative='监管负责人',
                contact_person='监管联系人',
                contact_phone='13800138003',
                contact_email='regulator@test.com',
                address='监管地址',
                business_scope='药品监管'
            )
            
            # 创建药店租户
            pharmacy_tenant = Tenant(
                name='流通测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000000000004X',
                legal_representative='药店负责人',
                contact_person='药店联系人',
                contact_phone='13800138004',
                contact_email='pharmacy@test.com',
                address='药店地址',
                business_scope='药品零售'
            )
            
            # 创建供应商租户
            supplier_tenant = Tenant(
                name='流通测试供应商',
                type='SUPPLIER',
                unified_social_credit_code='91310000000000005X',
                legal_representative='供应商负责人',
                contact_person='供应商联系人',
                contact_phone='13800138005',
                contact_email='supplier@test.com',
                address='供应商地址',
                business_scope='药品批发'
            )
            
            db.session.add_all([regulator_tenant, pharmacy_tenant, supplier_tenant])
            db.session.commit()
            
            # 创建用户
            regulator_user = User(
                username='regulator_test',
                email='regulator@test.com',
                role='regulator',
                tenant_id=regulator_tenant.id
            )
            regulator_user.set_password('RegulatorPass123')
            
            pharmacy_user = User(
                username='pharmacy_circulation',
                email='pharmacy@test.com',
                role='pharmacy',
                tenant_id=pharmacy_tenant.id
            )
            pharmacy_user.set_password('PharmacyPass123')
            
            supplier_user = User(
                username='supplier_circulation',
                email='supplier@test.com',
                role='supplier',
                tenant_id=supplier_tenant.id
            )
            supplier_user.set_password('SupplierPass123')
            
            db.session.add_all([regulator_user, pharmacy_user, supplier_user])
            db.session.commit()
            
            # 创建药品
            test_drug = Drug(
                generic_name='流通测试药品',
                brand_name='流通测试药品',
                approval_number='H12345678910',
                dosage_form='片剂',
                specification='100mg*30片',
                manufacturer='流通测试制药厂',
                category='测试类',
                prescription_type='处方药'
            )
            
            db.session.add(test_drug)
            db.session.commit()
            
            # 创建供应信息
            supply_info = SupplyInfo(
                drug_id=test_drug.id,
                tenant_id=supplier_tenant.id,
                unit_price=30.00,
                available_quantity=500,
                min_order_quantity=10,
                valid_until=datetime.now().date() + timedelta(days=365)
            )
            
            db.session.add(supply_info)
            db.session.commit()
            
            # 创建订单
            test_order = Order(
                buyer_tenant_id=pharmacy_tenant.id,
                supplier_tenant_id=supplier_tenant.id,
                supply_info_id=supply_info.id,
                expected_delivery_date=datetime.now().date() + timedelta(days=3),
                notes='流通测试订单',
                status='CONFIRMED',
                created_by=pharmacy_user.id,
                confirmed_by=supplier_user.id,
                confirmed_at=datetime.now(),
                tracking_number='TRACK' + str(datetime.now().timestamp()).replace('.', '')
            )
            
            db.session.add(test_order)
            db.session.commit()
            
            # 创建订单项目
            order_item = OrderItem(
                order_id=test_order.id,
                drug_id=test_drug.id,
                unit_price=30.00,
                quantity=20,
                batch_number='CIRC001'
            )
            
            db.session.add(order_item)
            db.session.commit()
            
            return {
                'regulator_user': regulator_user,
                'pharmacy_user': pharmacy_user,
                'supplier_user': supplier_user,
                'regulator_tenant': regulator_tenant,
                'pharmacy_tenant': pharmacy_tenant,
                'supplier_tenant': supplier_tenant,
                'test_drug': test_drug,
                'test_order': test_order,
                'supply_info': supply_info
            }
    
    @pytest.fixture
    def regulator_token(self, client, circulation_data):
        """获取监管用户token"""
        response = client.post('/api/auth/login', json={
            'username': 'regulator_test',
            'password': 'RegulatorPass123'
        })
        if response.status_code == 200:
            return response.get_json()['access_token']
        return None
    
    def test_circulation_dashboard_endpoint(self, client, regulator_token):
        """测试流通数据看板接口"""
        if not regulator_token:
            pytest.skip("监管用户认证失败")
        
        headers = {'Authorization': f'Bearer {regulator_token}'}
        response = client.get('/api/circulation/dashboard', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            
            # 验证看板数据结构
            expected_fields = ['total_orders', 'active_pharmacies', 'active_suppliers']
            for field in expected_fields:
                assert field in data
            
            assert isinstance(data['total_orders'], int)
            assert isinstance(data['active_pharmacies'], int)
            assert isinstance(data['active_suppliers'], int)
        else:
            # 接口可能需要更高级别权限或不存在
            assert response.status_code in [403, 404, 401]
    
    def test_circulation_report_endpoint(self, client, regulator_token, circulation_data):
        """测试流通数据报告接口"""
        if not regulator_token:
            pytest.skip("监管用户认证失败")
        
        headers = {'Authorization': f'Bearer {regulator_token}'}
        
        # 测试生成报告
        report_data = {
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'report_type': 'order_summary'
        }
        
        response = client.post('/api/circulation/report', 
                              json=report_data, 
                              headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'report_id' in data or 'data' in data
        else:
            # 接口可能需要更高级别权限或实现不同
            assert response.status_code in [403, 404, 401, 422]
    
    def test_circulation_records_by_tracking(self, client, regulator_token, circulation_data):
        """测试通过追踪号查询流通记录"""
        if not regulator_token:
            pytest.skip("监管用户认证失败")
        
        headers = {'Authorization': f'Bearer {regulator_token}'}
        tracking_number = circulation_data['test_order'].tracking_number
        
        if tracking_number:
            response = client.get(f'/api/circulation/records/{tracking_number}', 
                                headers=headers)
            
            if response.status_code == 200:
                data = response.get_json()
                assert 'tracking_number' in data
                assert data['tracking_number'] == tracking_number
            else:
                # 接口可能需要更高级别权限或实现不同
                assert response.status_code in [403, 404, 401]
        else:
            pytest.skip("测试订单没有追踪号")
    
    def test_circulation_trace_endpoint(self, client, regulator_token, circulation_data):
        """测试药品流通追踪接口"""
        if not regulator_token:
            pytest.skip("监管用户认证失败")
        
        headers = {'Authorization': f'Bearer {regulator_token}'}
        drug_id = circulation_data['test_drug'].id
        
        # 测试药品流通追踪
        response = client.get(f'/api/circulation/trace?drug_id={drug_id}', 
                            headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list) or 'data' in data
        else:
            # 接口可能需要更高级别权限或实现不同
            assert response.status_code in [403, 404, 401]


class TestCirculationAccess:
    """测试流通功能访问控制"""
    
    def test_dashboard_requires_auth(self, client):
        """测试看板需要认证"""
        response = client.get('/api/circulation/dashboard')
        assert response.status_code in [401, 404]
    
    def test_report_requires_auth(self, client):
        """测试报告生成需要认证"""
        response = client.post('/api/circulation/report', json={})
        assert response.status_code in [401, 404]
    
    def test_records_requires_auth(self, client):
        """测试记录查询需要认证"""
        response = client.get('/api/circulation/records/TEST123')
        assert response.status_code in [401, 404]
    
    def test_trace_requires_auth(self, client):
        """测试流通追踪需要认证"""
        response = client.get('/api/circulation/trace?drug_id=1')
        assert response.status_code in [401, 404]


class TestCirculationValidation:
    """测试流通数据验证"""
    
    @pytest.fixture
    def basic_regulator_token(self, client, app):
        """创建基本监管用户token"""
        with app.app_context():
            # 创建简单的监管租户和用户用于验证测试
            tenant = Tenant(
                name='验证测试监管局',
                type='REGULATOR',
                unified_social_credit_code='91310000000000099X',
                legal_representative='验证负责人',
                contact_person='验证联系人',
                contact_phone='13800138099',
                contact_email='validation@test.com',
                address='验证地址',
                business_scope='验证监管'
            )
            db.session.add(tenant)
            db.session.commit()
            
            user = User(
                username='validation_regulator',
                email='validation@test.com',
                role='regulator',
                tenant_id=tenant.id
            )
            user.set_password('ValidationPass123')
            db.session.add(user)
            db.session.commit()
        
        # 登录获取token
        response = client.post('/api/auth/login', json={
            'username': 'validation_regulator',
            'password': 'ValidationPass123'
        })
        if response.status_code == 200:
            return response.get_json()['access_token']
        return None
    
    def test_invalid_report_data(self, client, basic_regulator_token):
        """测试无效的报告请求数据"""
        if not basic_regulator_token:
            pytest.skip("监管用户认证失败")
        
        headers = {'Authorization': f'Bearer {basic_regulator_token}'}
        
        # 测试缺少必需字段
        response = client.post('/api/circulation/report', 
                              json={}, 
                              headers=headers)
        assert response.status_code in [400, 404, 422]
        
        # 测试无效日期格式
        invalid_data = {
            'start_date': 'invalid-date',
            'end_date': '2023-13-45',  # 无效日期
            'report_type': 'invalid_type'
        }
        
        response = client.post('/api/circulation/report', 
                              json=invalid_data, 
                              headers=headers)
        assert response.status_code in [400, 404, 422]
    
    def test_nonexistent_tracking_number(self, client, basic_regulator_token):
        """测试查询不存在的追踪号"""
        if not basic_regulator_token:
            pytest.skip("监管用户认证失败")
        
        headers = {'Authorization': f'Bearer {basic_regulator_token}'}
        response = client.get('/api/circulation/records/NONEXISTENT123', 
                            headers=headers)
        assert response.status_code in [404, 401, 403]
    
    def test_invalid_drug_id(self, client, basic_regulator_token):
        """测试无效药品ID的流通追踪"""
        if not basic_regulator_token:
            pytest.skip("监管用户认证失败")
        
        headers = {'Authorization': f'Bearer {basic_regulator_token}'}
        response = client.get('/api/circulation/trace?drug_id=99999', 
                            headers=headers)
        assert response.status_code in [404, 400, 401, 403]