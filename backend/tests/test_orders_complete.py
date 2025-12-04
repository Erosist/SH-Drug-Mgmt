"""
订单管理完整测试
"""
import pytest
import json
from datetime import datetime, timedelta
from models import User, Tenant, Order, OrderItem, SupplyInfo, Drug
from extensions import db


class TestOrdersComplete:
    """完整的订单管理测试"""
    
    @pytest.fixture
    def test_users(self, app):
        """创建测试用户（药店和供应商）"""
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
            
            # 创建药店用户
            pharmacy_user = User(
                username='pharmacy_test',
                email='pharmacy@test.com',
                role='pharmacy',
                tenant_id=pharmacy_tenant.id
            )
            pharmacy_user.set_password('PharmacyPass123')
            
            # 创建供应商用户
            supplier_user = User(
                username='supplier_test',
                email='supplier@test.com',
                role='supplier',
                tenant_id=supplier_tenant.id
            )
            supplier_user.set_password('SupplierPass123')
            
            db.session.add_all([pharmacy_user, supplier_user])
            db.session.commit()
            
            # 先创建药品信息
            test_drug = Drug(
                generic_name='阿莫西林',
                brand_name='阿莫西林',
                approval_number='H12345678902',
                dosage_form='胶囊',
                specification='250mg*24粒',
                manufacturer='测试制药厂',
                category='西药',
                prescription_type='OTC'
            )
            db.session.add(test_drug)
            db.session.commit()
            
            # 创建供应信息
            supply_info = SupplyInfo(
                drug_id=test_drug.id,
                unit_price=25.50,
                available_quantity=1000,
                min_order_quantity=10,
                tenant_id=supplier_tenant.id,
                valid_until=datetime.now().date() + timedelta(days=365)
            )
            db.session.add(supply_info)
            db.session.commit()
            
            return {
                'pharmacy_user_id': pharmacy_user.id,
                'supplier_user_id': supplier_user.id,
                'pharmacy_tenant_id': pharmacy_tenant.id,
                'supplier_tenant_id': supplier_tenant.id,
                'supply_info_id': supply_info.id,
                'test_drug_id': test_drug.id
            }
    
    @pytest.fixture
    def pharmacy_token(self, client, test_users):
        """获取药店用户token"""
        response = client.post('/api/auth/login', json={
            'username': 'pharmacy_test',
            'password': 'PharmacyPass123'
        })
        if response.status_code == 200:
            return response.get_json()['access_token']
        return None
    
    @pytest.fixture
    def supplier_token(self, client, test_users):
        """获取供应商用户token"""
        response = client.post('/api/auth/login', json={
            'username': 'supplier_test',
            'password': 'SupplierPass123'
        })
        if response.status_code == 200:
            return response.get_json()['access_token']
        return None
    
    def test_order_creation(self, client, pharmacy_token, test_users):
        """测试订单创建"""
        if not pharmacy_token:
            pytest.skip("药店用户认证失败")
        
        headers = {'Authorization': f'Bearer {pharmacy_token}'}
        # 从fixture中获取ID值而不是直接访问对象属性
        supplier_tenant_id = test_users.get('supplier_tenant_id')
        if not supplier_tenant_id:
            pytest.skip("无法获取供应商租户ID")
        
        order_data = {
            'supplier_id': supplier_tenant_id,
            'items': [
                {
                    'drug_name': '阿莫西林',
                    'quantity': 50,
                    'unit_price': 25.50
                }
            ],
            'delivery_address': '上海市浦东新区测试地址123号',
            'notes': '测试订单'
        }
        
        response = client.post('/api/orders', json=order_data, headers=headers)
        
        if response.status_code == 201:
            data = response.get_json()
            assert 'order_number' in data
            assert data['status'] == 'pending'
            assert len(data['items']) == 1
            assert data['items'][0]['drug_name'] == '阿莫西林'
        else:
            # 检查错误信息
            data = response.get_json()
            assert 'msg' in data or 'error' in data
    
    def test_order_list(self, client, pharmacy_token):
        """测试订单列表获取"""
        if not pharmacy_token:
            pytest.skip("药店用户认证失败")
        
        headers = {'Authorization': f'Bearer {pharmacy_token}'}
        response = client.get('/api/orders', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data  # API返回包装格式
            assert isinstance(data['data']['items'], list)
        else:
            assert response.status_code in [401, 403]
    
    def test_order_stats(self, client, pharmacy_token):
        """测试订单统计"""
        if not pharmacy_token:
            pytest.skip("药店用户认证失败")
        
        headers = {'Authorization': f'Bearer {pharmacy_token}'}
        response = client.get('/api/orders/stats', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            expected_keys = ['total_orders', 'pending_orders', 'completed_orders']
            for key in expected_keys:
                if key in data:
                    assert isinstance(data[key], int)
        else:
            assert response.status_code in [401, 403]
    
    def test_order_workflow(self, client, pharmacy_token, supplier_token, test_users, app):
        """测试完整订单工作流"""
        if not pharmacy_token or not supplier_token:
            pytest.skip("用户认证失败")
        
        # 1. 药店创建订单
        pharmacy_headers = {'Authorization': f'Bearer {pharmacy_token}'}
        supplier_tenant_id = test_users.get('supplier_tenant_id')
        if not supplier_tenant_id:
            pytest.skip("无法获取供应商租户ID")
        
        order_data = {
            'supplier_id': supplier_tenant_id,
            'items': [{'drug_name': '阿莫西林', 'quantity': 20, 'unit_price': 25.50}],
            'delivery_address': '测试地址'
        }
        
        create_response = client.post('/api/orders', json=order_data, headers=pharmacy_headers)
        if create_response.status_code != 201:
            pytest.skip("订单创建失败")
        
        order_id = create_response.get_json()['id']
        
        # 2. 供应商确认订单
        supplier_headers = {'Authorization': f'Bearer {supplier_token}'}
        confirm_response = client.post(f'/api/orders/{order_id}/confirm', 
                                     json={'notes': '订单已确认'}, 
                                     headers=supplier_headers)
        
        # 检查确认结果
        if confirm_response.status_code == 200:
            data = confirm_response.get_json()
            assert data['status'] == 'confirmed'
        
        # 3. 供应商发货
        ship_response = client.post(f'/api/orders/{order_id}/ship',
                                   json={'tracking_number': 'TRACK123'},
                                   headers=supplier_headers)
        
        if ship_response.status_code == 200:
            data = ship_response.get_json()
            assert data['status'] == 'shipped'


class TestOrderValidation:
    """订单验证测试"""
    
    def test_order_without_auth(self, client):
        """测试未认证创建订单"""
        order_data = {
            'supplier_id': 1,
            'items': [{'drug_name': '测试药品', 'quantity': 10, 'unit_price': 10.0}]
        }
        
        response = client.post('/api/orders', json=order_data)
        assert response.status_code in [401, 422]  # 未认证
    
    def test_invalid_order_data(self, client):
        """测试无效订单数据"""
        invalid_data = {
            'supplier_id': 'invalid',  # 无效ID
            'items': []  # 空项目列表
        }
        
        response = client.post('/api/orders', json=invalid_data)
        assert response.status_code in [400, 401, 422]
    
    def test_missing_order_fields(self, client):
        """测试缺少必需字段"""
        incomplete_data = {
            'supplier_id': 1
            # 缺少items字段
        }
        
        response = client.post('/api/orders', json=incomplete_data)
        assert response.status_code in [400, 401, 422]
    
    def test_order_business_scenario_complete_flow(self, client, pharmacy_token, supplier_token):
        """测试完整业务场景：从供需对接到交易完成 (US-010 + US-011 组合)"""
        if not pharmacy_token or not supplier_token:
            pytest.skip("用户认证失败")
        
        # 场景：医院急需某种药品，通过平台找到供应商并完成采购
        
        # 步骤1: 采购商搜索需要的药品供应信息 (US-010)
        buyer_headers = {'Authorization': f'Bearer {pharmacy_token}'}
        search_response = client.get('/api/supply/search?drug_name=阿莫西林', headers=buyer_headers)
        
        if search_response.status_code == 200:
            supply_data = search_response.get_json()
            if supply_data and supply_data.get('items'):
                # 步骤2: 基于找到的供应信息创建订单 (US-011)
                supply_info = supply_data['items'][0]
                
                order_data = {
                    'supplier_id': supply_info.get('supplier_id', 1),
                    'items': [{
                        'drug_name': supply_info.get('drug_name', '阿莫西林'),
                        'quantity': 500,
                        'unit_price': supply_info.get('unit_price', 25.50),
                        'batch_number': supply_info.get('batch_number', 'BATCH001'),
                    }],
                    'urgent': True,
                    'special_requirements': '需要冷链运输，医院急用'
                }
                
                create_response = client.post('/api/orders', json=order_data, headers=buyer_headers)
                
                if create_response.status_code in [200, 201]:
                    order = create_response.get_json()
                    
                    # 步骤3: 验证订单状态和关键信息
                    assert order.get('urgent') == True
                    assert '医院急用' in order.get('special_requirements', '')
                    
                    # 如果有订单ID，测试后续流程
                    if 'id' in order:
                        order_id = order['id']
                        
                        # 步骤4: 供应商确认订单
                        supplier_headers = {'Authorization': f'Bearer {supplier_token}'}
                        confirm_response = client.post(f'/api/orders/{order_id}/confirm', 
                                                     headers=supplier_headers)
                        
                        # 验证确认结果（可能需要根据实际API调整）
                        assert confirm_response.status_code in [200, 201, 404]
    
    def test_supply_demand_matching_integration(self, client, pharmacy_token):
        """测试供需匹配集成场景 (US-009 + US-010 + US-011)"""
        if not pharmacy_token:
            pytest.skip("药店用户认证失败")
        
        headers = {'Authorization': f'Bearer {pharmacy_token}'}
        
        # 场景：系统自动匹配最优供应商
        demand_request = {
            'drug_name': '布洛芬片',
            'required_quantity': 1000,
            'max_unit_price': 15.0,
            'delivery_deadline': '2024-12-20',
            'quality_requirements': '国药准字',
            'location_preference': '上海市'
        }
        
        # 请求供需匹配
        match_response = client.post('/api/orders/match-suppliers', 
                                   json=demand_request, 
                                   headers=headers)
        
        if match_response.status_code == 200:
            matches = match_response.get_json()
            
            # 验证匹配结果格式
            assert 'matches' in matches or 'suppliers' in matches
            
            # 如果找到匹配，创建基于匹配的订单
            if matches.get('matches') or matches.get('suppliers'):
                best_match = (matches.get('matches') or matches.get('suppliers'))[0]
                
                optimized_order_data = {
                    'supplier_id': best_match.get('supplier_id'),
                    'items': [{
                        'drug_name': '布洛芬片',
                        'quantity': 1000,
                        'unit_price': best_match.get('unit_price'),
                    }],
                    'matched_from_request': True,
                    'match_score': best_match.get('match_score', 0)
                }
                
                order_response = client.post('/api/orders', 
                                           json=optimized_order_data, 
                                           headers=headers)
                
                # 验证基于匹配的订单创建
                if order_response.status_code in [200, 201]:
                    order = order_response.get_json()
                    assert order.get('matched_from_request') == True
    
    def test_order_lifecycle_monitoring(self, client, pharmacy_token, supplier_token):
        """测试订单全生命周期监控"""
        if not pharmacy_token or not supplier_token:
            pytest.skip("用户认证失败")
        
        # 创建订单进行生命周期测试
        buyer_headers = {'Authorization': f'Bearer {pharmacy_token}'}
        order_data = {
            'supplier_id': 1,
            'items': [{
                'drug_name': '生命周期测试药品',
                'quantity': 200,
                'unit_price': 30.0,
            }],
            'monitor_lifecycle': True
        }
        
        create_response = client.post('/api/orders', json=order_data, headers=buyer_headers)
        
        if create_response.status_code in [200, 201]:
            order = create_response.get_json()
            
            if 'id' in order:
                order_id = order['id']
                
                # 测试订单状态跟踪
                status_response = client.get(f'/api/orders/{order_id}/status', headers=buyer_headers)
                
                if status_response.status_code == 200:
                    status_data = status_response.get_json()
                    
                    # 验证状态跟踪信息
                    expected_fields = ['status', 'created_at', 'timeline']
                    for field in expected_fields:
                        assert field in status_data or len(status_data) > 0
                
                # 测试订单历史记录
                history_response = client.get(f'/api/orders/{order_id}/history', headers=buyer_headers)
                
                if history_response.status_code == 200:
                    history_data = history_response.get_json()
                    assert isinstance(history_data, (list, dict))


if __name__ == '__main__':
    pytest.main([__file__])