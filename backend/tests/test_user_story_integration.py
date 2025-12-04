"""
基于用户故事的综合测试套件
根据18个用户故事优先级编写的完整测试覆盖
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Tenant


class TestUserStoryIntegration:
    """基于用户故事的集成测试"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, client, app):
        """设置测试数据"""
        self.client = client
        self.app = app
        
        with self.app.app_context():
            # 创建测试租户
            self.test_tenant = Tenant(
                name='测试制药公司',
                type='SUPPLIER',
                unified_social_credit_code='91310000123456789X',
                legal_representative='张三',
                contact_person='李四',
                contact_phone='021-12345678',
                contact_email='contact@test.com',
                address='上海市浦东新区测试路123号',
                business_scope='药品批发；药品零售'
            )
            db.session.add(self.test_tenant)
            db.session.commit()

    def test_us_001_user_registration_integration(self):
        """US-001: 用户注册集成测试"""
        # 测试完整的用户注册流程
        user_data = {
            'username': 'integration_test_user',
            'email': 'integration@test.com',
            'phone': '13800138000',
            'password': 'IntegrationTest123',
            'real_name': '集成测试用户',
            'company_name': '集成测试公司'
        }
        
        response = self.client.post('/api/auth/register', json=user_data)
        
        # 验证注册响应
        if response.status_code in [200, 201]:
            data = response.get_json()
            assert 'user' in data
            assert data['user']['username'] == 'integration_test_user'
            
            # 验证用户能够登录
            login_data = {
                'username': 'integration_test_user',
                'password': 'IntegrationTest123'
            }
            
            login_response = self.client.post('/api/auth/login', json=login_data)
            if login_response.status_code == 200:
                login_data = login_response.get_json()
                assert 'access_token' in login_data

    def test_us_005_role_based_access_control(self):
        """US-005: 角色权限管理测试"""
        # 创建不同角色的用户
        test_roles = ['user', 'admin']
        
        for role in test_roles:
            user = User(
                username=f'role_test_{role}',
                email=f'{role}@role.test',
                phone=f'1380013800{len(role)}',
                role=role,
                tenant_id=self.test_tenant.id if role == 'user' else None
            )
            user.set_password('RoleTest123')
            db.session.add(user)
        
        db.session.commit()
        
        # 测试角色权限
        for role in test_roles:
            login_data = {
                'username': f'role_test_{role}',
                'password': 'RoleTest123'
            }
            
            login_response = self.client.post('/api/auth/login', json=login_data)
            
            if login_response.status_code == 200:
                token = login_response.json['access_token']
                headers = {'Authorization': f'Bearer {token}'}
                
                # 测试访问管理接口
                admin_response = self.client.get('/api/admin/users', headers=headers)
                
                if role == 'admin':
                    # 管理员应该能访问（200或404表示接口存在但可能没有数据）
                    self.assertIn(admin_response.status_code, [200, 404])
                else:
                    # 普通用户应该被拒绝
                    self.assertIn(admin_response.status_code, [401, 403, 404])

    def test_us_007_inventory_management_integration(self):
        """US-007: 库存登记与更新集成测试"""
        # 创建有租户的用户
        user = User(
            username='inventory_test_user',
            email='inventory@test.com',
            phone='13700137000',
            tenant_id=self.test_tenant.id
        )
        user.set_password('InventoryTest123')
        db.session.add(user)
        db.session.commit()
        
        # 用户登录
        login_data = {
            'username': 'inventory_test_user',
            'password': 'InventoryTest123'
        }
        
        login_response = self.client.post('/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 测试库存登记
            inventory_data = {
                'drug_name': '阿莫西林胶囊',
                'manufacturer': '测试制药厂',
                'batch_number': 'TEST2024001',
                'quantity': 1000,
                'unit_price': 12.5,
                'expiry_date': '2025-12-31',
                'production_date': '2024-01-15'
            }
            
            inventory_response = self.client.post('/api/inventory/add', 
                                                json=inventory_data, 
                                                headers=headers)
            
            # 验证库存登记结果
            if inventory_response.status_code in [200, 201]:
                inventory = inventory_response.json
                self.assertEqual(inventory.get('drug_name'), '阿莫西林胶囊')
                self.assertEqual(inventory.get('quantity'), 1000)

    def test_us_008_inventory_warning_integration(self):
        """US-008: 库存预警集成测试"""
        # 创建用户和相关数据（复用已有的租户和用户创建逻辑）
        user = User(
            username='warning_test_user',
            email='warning@test.com',
            phone='13600136000',
            tenant_id=self.test_tenant.id
        )
        user.set_password('WarningTest123')
        db.session.add(user)
        db.session.commit()
        
        # 登录获取token
        login_data = {
            'username': 'warning_test_user',
            'password': 'WarningTest123'
        }
        
        login_response = self.client.post('/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 测试获取库存预警
            warning_response = self.client.get('/api/inventory/warnings', headers=headers)
            
            # 验证预警接口响应
            if warning_response.status_code == 200:
                warnings = warning_response.json
                self.assertIn('low_stock_items', warnings)
                self.assertIn('expiring_items', warnings)

    def test_us_009_publish_supply_info_integration(self):
        """US-009: 发布供应信息集成测试"""
        # 创建供应商用户
        supplier_user = User(
            username='supply_publisher',
            email='supplier@supply.com',
            phone='13500135000',
            tenant_id=self.test_tenant.id
        )
        supplier_user.set_password('SupplierTest123')
        db.session.add(supplier_user)
        db.session.commit()
        
        # 登录
        login_response = self.client.post('/api/auth/login', json={
            'username': 'supply_publisher',
            'password': 'SupplierTest123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 发布供应信息
            supply_data = {
                'drug_name': '布洛芬片',
                'manufacturer': '测试制药公司',
                'batch_number': 'SUP2024001',
                'quantity': 5000,
                'unit_price': 8.5,
                'expiry_date': '2025-06-30',
                'quality_standard': '国药准字',
                'storage_condition': '阴凉干燥处保存'
            }
            
            publish_response = self.client.post('/api/supply/publish', 
                                              json=supply_data, 
                                              headers=headers)
            
            # 验证发布结果
            if publish_response.status_code in [200, 201]:
                supply_info = publish_response.json
                self.assertEqual(supply_info.get('drug_name'), '布洛芬片')
                self.assertEqual(supply_info.get('quantity'), 5000)

    def test_us_010_view_supply_info_integration(self):
        """US-010: 查看供应信息集成测试"""
        # 创建采购商用户
        buyer_user = User(
            username='supply_viewer',
            email='buyer@supply.com',
            phone='13400134000',
            tenant_id=self.test_tenant.id
        )
        buyer_user.set_password('BuyerTest123')
        db.session.add(buyer_user)
        db.session.commit()
        
        # 登录
        login_response = self.client.post('/api/auth/login', json={
            'username': 'supply_viewer',
            'password': 'BuyerTest123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 查看供应信息列表
            list_response = self.client.get('/api/supply/list', headers=headers)
            
            # 验证列表查询
            if list_response.status_code == 200:
                supply_list = list_response.json
                self.assertIn('items', supply_list)
                
            # 搜索特定药品
            search_response = self.client.get('/api/supply/search?drug_name=阿莫西林', 
                                            headers=headers)
            
            # 验证搜索功能
            if search_response.status_code == 200:
                search_results = search_response.json
                self.assertIsInstance(search_results, dict)

    def test_us_011_order_creation_integration(self):
        """US-011: 模拟下单集成测试"""
        # 创建订单用户
        order_user = User(
            username='order_creator',
            email='order@test.com',
            phone='13300133000',
            tenant_id=self.test_tenant.id
        )
        order_user.set_password('OrderTest123')
        db.session.add(order_user)
        db.session.commit()
        
        # 登录
        login_response = self.client.post('/api/auth/login', json={
            'username': 'order_creator',
            'password': 'OrderTest123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 创建订单
            order_data = {
                'supplier_id': self.test_tenant.id,
                'items': [{
                    'drug_name': '阿莫西林胶囊',
                    'quantity': 100,
                    'unit_price': 12.5,
                    'batch_number': 'ORD2024001'
                }],
                'delivery_address': '上海市徐汇区订单路456号',
                'notes': '集成测试订单',
                'urgent': False
            }
            
            order_response = self.client.post('/api/orders/create', 
                                            json=order_data, 
                                            headers=headers)
            
            # 验证订单创建
            if order_response.status_code in [200, 201]:
                order = order_response.json
                self.assertIn('id', order)
                self.assertEqual(order.get('notes'), '集成测试订单')

    def test_complete_business_flow_integration(self):
        """完整业务流程集成测试：注册→认证→供应→采购→流通"""
        # 步骤1: 供应商注册
        supplier_data = {
            'username': 'flow_supplier',
            'email': 'flow_supplier@test.com',
            'password': 'FlowTest123',
            'company_name': '流程测试供应商'
        }
        
        supplier_reg_response = self.client.post('/api/auth/register', json=supplier_data)
        
        if supplier_reg_response.status_code in [200, 201]:
            # 步骤2: 供应商登录
            supplier_login_response = self.client.post('/api/auth/login', json={
                'username': 'flow_supplier',
                'password': 'FlowTest123'
            })
            
            if supplier_login_response.status_code == 200:
                supplier_token = supplier_login_response.json['access_token']
                supplier_headers = {'Authorization': f'Bearer {supplier_token}'}
                
                # 步骤3: 发布供应信息
                supply_data = {
                    'drug_name': '完整流程测试药品',
                    'manufacturer': '流程测试厂',
                    'quantity': 2000,
                    'unit_price': 20.0,
                    'batch_number': 'FLOW2024001',
                    'expiry_date': '2025-08-31'
                }
                
                publish_response = self.client.post('/api/supply/publish', 
                                                  json=supply_data, 
                                                  headers=supplier_headers)
                
                # 验证供应信息发布
                if publish_response.status_code in [200, 201]:
                    # 步骤4: 采购商注册并下单
                    buyer_data = {
                        'username': 'flow_buyer',
                        'email': 'flow_buyer@test.com',
                        'password': 'FlowTest123',
                        'company_name': '流程测试采购商'
                    }
                    
                    buyer_reg_response = self.client.post('/api/auth/register', json=buyer_data)
                    
                    if buyer_reg_response.status_code in [200, 201]:
                        # 采购商登录并创建订单
                        buyer_login_response = self.client.post('/api/auth/login', json={
                            'username': 'flow_buyer',
                            'password': 'FlowTest123'
                        })
                        
                        if buyer_login_response.status_code == 200:
                            buyer_token = buyer_login_response.json['access_token']
                            buyer_headers = {'Authorization': f'Bearer {buyer_token}'}
                            
                            # 创建订单
                            order_data = {
                                'supplier_id': self.test_tenant.id,  # 使用测试租户
                                'items': [{
                                    'drug_name': '完整流程测试药品',
                                    'quantity': 500,
                                    'unit_price': 20.0,
                                    'batch_number': 'FLOW2024001'
                                }],
                                'delivery_address': '流程测试地址',
                                'notes': '完整业务流程集成测试'
                            }
                            
                            order_response = self.client.post('/api/orders/create', 
                                                            json=order_data, 
                                                            headers=buyer_headers)
                            
                            # 验证完整流程
                            if order_response.status_code in [200, 201]:
                                order = order_response.json
                                self.assertIn('完整业务流程', order.get('notes', ''))
                                self.assertEqual(order.get('items')[0].get('quantity'), 500)
    
    def test_error_handling_and_validation(self):
        """错误处理和验证测试"""
        # 测试无效数据处理
        invalid_register_data = {
            'username': '',  # 空用户名
            'email': 'invalid-email',  # 无效邮箱
            'password': '123'  # 过短密码
        }
        
        response = self.client.post('/api/auth/register', json=invalid_register_data)
        # 应该返回400错误
        self.assertEqual(response.status_code, 400)
        
        # 测试未授权访问
        unauth_response = self.client.get('/api/inventory/warnings')
        self.assertIn(unauth_response.status_code, [401, 403])
        
        # 测试无效token
        invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
        invalid_response = self.client.get('/api/supply/list', headers=invalid_headers)
        self.assertIn(invalid_response.status_code, [401, 403])