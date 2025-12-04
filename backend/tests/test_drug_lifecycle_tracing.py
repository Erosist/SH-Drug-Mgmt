"""
药品全生命周期追溯测试 (US-013)
利用流通记录提供追溯查询功能
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Tenant, Order, InventoryItem, CirculationRecord
from base import BaseTestCase


class TestDrugLifecycleTracing(BaseTestCase):
    """药品全生命周期追溯测试类"""
    
    def setUp(self):
        """设置测试数据"""
        super().setUp()
        
        # 创建生产企业
        self.manufacturer_user = User(
            username='manufacturer_trace',
            email='manufacturer@trace.com',
            phone='13800138001'
        )
        self.manufacturer_user.set_password('password123')
        db.session.add(self.manufacturer_user)
        
        # 创建批发企业
        self.wholesaler_user = User(
            username='wholesaler_trace',
            email='wholesaler@trace.com',
            phone='13800138002'
        )
        self.wholesaler_user.set_password('password123')
        db.session.add(self.wholesaler_user)
        
        # 创建零售企业
        self.retailer_user = User(
            username='retailer_trace',
            email='retailer@trace.com',
            phone='13800138003'
        )
        self.retailer_user.set_password('password123')
        db.session.add(self.retailer_user)
        
        # 创建监管用户
        self.regulator_user = User(
            username='regulator_trace',
            email='regulator@trace.com',
            phone='13800138000',
            role='admin'
        )
        self.regulator_user.set_password('regulator123')
        db.session.add(self.regulator_user)
        
        db.session.commit()
        
        # 创建企业信息
        enterprises = [
            (self.manufacturer_user, '生产制药有限公司', '药品生产'),
            (self.wholesaler_user, '批发医药有限公司', '药品批发'), 
            (self.retailer_user, '零售药店有限公司', '药品零售')
        ]
        
        self.tenant_infos = []
        for i, (user, company_name, scope) in enumerate(enterprises):
            tenant = Tenant(
                user_id=user.id,
                company_name=company_name,
                business_license=f'9131000012345678{i+1}',
                legal_representative=f'法人{i+1}',
                registered_address=f'上海市浦东新区追溯路{i+1}号',
                contact_person=f'联系人{i+1}',
                contact_phone=f'021-1234567{i+1}',
                business_scope=scope,
                registration_capital=f'{2000+i*1000}万元',
                status='approved'
            )
            self.tenant_infos.append(tenant)
            db.session.add(tenant)
        
        db.session.commit()
        
        # 创建具有完整生命周期的药品批次
        self.drug_batch = 'TRACE20241201'
        self.drug_name = '阿莫西林胶囊'
        self.manufacturer_name = '上海制药厂'
        
        # 生产阶段 - 创建初始库存记录
        self.production_inventory = InventoryItem(
            tenant_id=self.tenant_infos[0].id,  # 生产企业
            drug_name=self.drug_name,
            manufacturer=self.manufacturer_name,
            current_stock=10000,  # 初始生产量
            min_stock_threshold=1000,
            unit_price=8.0,
            batch_number=self.drug_batch,
            expiry_date=datetime(2026, 12, 31),
            production_date=datetime(2024, 1, 15),
            last_updated=datetime(2024, 1, 15)
        )
        db.session.add(self.production_inventory)
        
        # 流通阶段 - 生产商到批发商的订单
        self.order_manufacturer_to_wholesaler = Order(
            supplier_id=self.manufacturer_user.id,
            buyer_id=self.wholesaler_user.id,
            drug_name=self.drug_name,
            manufacturer=self.manufacturer_name,
            quantity=5000,
            unit_price=10.0,
            total_price=50000.0,
            batch_number=self.drug_batch,
            expiry_date=datetime(2026, 12, 31),
            status='delivered',
            created_at=datetime(2024, 2, 1),
            updated_at=datetime(2024, 2, 15)
        )
        db.session.add(self.order_manufacturer_to_wholesaler)
        
        # 批发商库存
        self.wholesaler_inventory = InventoryItem(
            tenant_id=self.tenant_infos[1].id,  # 批发企业
            drug_name=self.drug_name,
            manufacturer=self.manufacturer_name,
            current_stock=5000,
            min_stock_threshold=500,
            unit_price=10.0,
            batch_number=self.drug_batch,
            expiry_date=datetime(2026, 12, 31),
            received_date=datetime(2024, 2, 15),
            last_updated=datetime(2024, 2, 15)
        )
        db.session.add(self.wholesaler_inventory)
        
        # 批发商到零售商的订单
        self.order_wholesaler_to_retailer = Order(
            supplier_id=self.wholesaler_user.id,
            buyer_id=self.retailer_user.id,
            drug_name=self.drug_name,
            manufacturer=self.manufacturer_name,
            quantity=1000,
            unit_price=15.0,
            total_price=15000.0,
            batch_number=self.drug_batch,
            expiry_date=datetime(2026, 12, 31),
            status='delivered',
            created_at=datetime(2024, 3, 1),
            updated_at=datetime(2024, 3, 10)
        )
        db.session.add(self.order_wholesaler_to_retailer)
        
        # 零售商库存
        self.retailer_inventory = InventoryItem(
            tenant_id=self.tenant_infos[2].id,  # 零售企业
            drug_name=self.drug_name,
            manufacturer=self.manufacturer_name,
            current_stock=1000,
            min_stock_threshold=100,
            unit_price=15.0,
            batch_number=self.drug_batch,
            expiry_date=datetime(2026, 12, 31),
            received_date=datetime(2024, 3, 10),
            last_updated=datetime(2024, 3, 10)
        )
        db.session.add(self.retailer_inventory)
        
        db.session.commit()
        
        # 创建详细的流通记录
        self.circulation_records = [
            # 生产商发货记录
            CirculationRecord(
                order_id=self.order_manufacturer_to_wholesaler.id,
                action='ship',
                reporter_id=self.manufacturer_user.id,
                tracking_number='MFG2024001',
                carrier_name='冷链物流',
                current_location='生产工厂',
                status='completed',
                temperature_log='2-8℃',
                created_at=datetime(2024, 2, 2)
            ),
            # 运输过程记录
            CirculationRecord(
                order_id=self.order_manufacturer_to_wholesaler.id,
                action='transit',
                reporter_id=self.manufacturer_user.id,
                tracking_number='MFG2024001',
                current_location='冷链配送中心',
                transit_status='in_transit',
                status='completed',
                temperature_log='4℃',
                created_at=datetime(2024, 2, 5)
            ),
            # 批发商收货记录
            CirculationRecord(
                order_id=self.order_manufacturer_to_wholesaler.id,
                action='delivered',
                reporter_id=self.wholesaler_user.id,
                tracking_number='MFG2024001',
                received_by='批发仓库管理员',
                package_condition='good',
                temperature_on_arrival='3℃',
                quality_check_result='passed',
                status='completed',
                created_at=datetime(2024, 2, 15)
            ),
            # 批发商到零售商的流通记录
            CirculationRecord(
                order_id=self.order_wholesaler_to_retailer.id,
                action='ship',
                reporter_id=self.wholesaler_user.id,
                tracking_number='WSL2024001',
                carrier_name='城市配送',
                current_location='批发仓库',
                status='completed',
                created_at=datetime(2024, 3, 2)
            ),
            CirculationRecord(
                order_id=self.order_wholesaler_to_retailer.id,
                action='delivered',
                reporter_id=self.retailer_user.id,
                tracking_number='WSL2024001',
                received_by='药店店长',
                package_condition='good',
                quality_check_result='passed',
                status='completed',
                created_at=datetime(2024, 3, 10)
            )
        ]
        
        for record in self.circulation_records:
            db.session.add(record)
        
        db.session.commit()

    def test_trace_by_batch_number(self):
        """测试按批次号追溯"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_trace',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 按批次号追溯
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/tracing/batch/{self.drug_batch}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证追溯结果结构
        self.assertIn('batch_info', data)
        self.assertIn('lifecycle_timeline', data)
        self.assertIn('current_locations', data)
        self.assertIn('quality_records', data)
        
        # 验证批次基本信息
        batch_info = data['batch_info']
        self.assertEqual(batch_info['batch_number'], self.drug_batch)
        self.assertEqual(batch_info['drug_name'], self.drug_name)
        self.assertEqual(batch_info['manufacturer'], self.manufacturer_name)
        
        # 验证生命周期时间线
        timeline = data['lifecycle_timeline']
        self.assertIsInstance(timeline, list)
        self.assertGreater(len(timeline), 0)
        
        # 验证时间线包含关键阶段
        timeline_actions = [event['action'] for event in timeline]
        expected_actions = ['production', 'ship', 'delivered']
        for action in expected_actions:
            self.assertIn(action, timeline_actions)
        
        # 验证当前位置信息
        current_locations = data['current_locations']
        self.assertIsInstance(current_locations, list)
        
        # 验证质量记录
        quality_records = data['quality_records']
        self.assertIsInstance(quality_records, list)

    def test_trace_by_order_id(self):
        """测试按订单ID追溯"""
        # 任意相关企业用户登录
        login_data = {
            'username': 'wholesaler_trace',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 按订单追溯
        order_id = self.order_manufacturer_to_wholesaler.id
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/tracing/order/{order_id}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证订单追溯信息
        self.assertIn('order_info', data)
        self.assertIn('circulation_records', data)
        self.assertIn('supply_chain', data)
        
        # 验证订单基本信息
        order_info = data['order_info']
        self.assertEqual(order_info['batch_number'], self.drug_batch)
        self.assertEqual(order_info['quantity'], 5000)
        self.assertEqual(order_info['status'], 'delivered')
        
        # 验证流通记录完整性
        circulation_records = data['circulation_records']
        self.assertGreaterEqual(len(circulation_records), 2)  # 至少包含发货和收货
        
        # 验证供应链信息
        supply_chain = data['supply_chain']
        self.assertIn('supplier', supply_chain)
        self.assertIn('buyer', supply_chain)
        
        supplier_info = supply_chain['supplier']
        self.assertEqual(supplier_info['company_name'], '生产制药有限公司')
        
        buyer_info = supply_chain['buyer']
        self.assertEqual(buyer_info['company_name'], '批发医药有限公司')

    def test_trace_drug_current_distribution(self):
        """测试药品当前分布追溯"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_trace',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 查询药品当前分布
        headers = {'Authorization': f'Bearer {token}'}
        params = {
            'drug_name': self.drug_name,
            'batch_number': self.drug_batch
        }
        response = self.client.get('/api/tracing/current-distribution', 
                                 params=params, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证分布数据结构
        self.assertIn('total_produced', data)
        self.assertIn('total_distributed', data)
        self.assertIn('current_locations', data)
        self.assertIn('distribution_summary', data)
        
        # 验证生产和分发总量
        self.assertEqual(data['total_produced'], 10000)
        self.assertEqual(data['total_distributed'], 6000)  # 5000给批发商 + 1000给零售商
        
        # 验证当前位置分布
        current_locations = data['current_locations']
        self.assertIsInstance(current_locations, list)
        self.assertGreaterEqual(len(current_locations), 2)  # 至少在批发商和零售商处
        
        # 验证分布汇总
        distribution_summary = data['distribution_summary']
        expected_stages = ['production', 'wholesale', 'retail']
        for stage in expected_stages:
            if stage in distribution_summary:
                self.assertIn('quantity', distribution_summary[stage])
                self.assertIn('percentage', distribution_summary[stage])

    def test_trace_quality_inspection_records(self):
        """测试质量检验记录追溯"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_trace',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 查询质量检验记录
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/tracing/quality-records/{self.drug_batch}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证质量记录结构
        self.assertIn('batch_number', data)
        self.assertIn('quality_tests', data)
        self.assertIn('inspection_timeline', data)
        self.assertIn('compliance_status', data)
        
        # 验证批次信息
        self.assertEqual(data['batch_number'], self.drug_batch)
        
        # 验证质量测试记录
        quality_tests = data['quality_tests']
        self.assertIsInstance(quality_tests, list)
        
        # 验证检验时间线
        inspection_timeline = data['inspection_timeline']
        self.assertIsInstance(inspection_timeline, list)
        
        # 验证合规状态
        compliance_status = data['compliance_status']
        self.assertIn('overall_status', compliance_status)
        self.assertIn('test_results', compliance_status)

    def test_trace_temperature_chain_monitoring(self):
        """测试冷链温度监控追溯"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_trace',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 查询温度链追溯
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/tracing/temperature-chain/{self.drug_batch}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证温度链数据结构
        self.assertIn('batch_number', data)
        self.assertIn('temperature_requirements', data)
        self.assertIn('temperature_records', data)
        self.assertIn('compliance_analysis', data)
        
        # 验证温度要求
        temp_requirements = data['temperature_requirements']
        self.assertIn('min_temp', temp_requirements)
        self.assertIn('max_temp', temp_requirements)
        
        # 验证温度记录
        temp_records = data['temperature_records']
        self.assertIsInstance(temp_records, list)
        
        # 验证有温度记录（从流通记录中提取）
        if len(temp_records) > 0:
            temp_record = temp_records[0]
            expected_fields = ['timestamp', 'temperature', 'location', 'recorder']
            for field in expected_fields:
                self.assertIn(field, temp_record)
        
        # 验证合规分析
        compliance_analysis = data['compliance_analysis']
        self.assertIn('compliance_rate', compliance_analysis)
        self.assertIn('violations', compliance_analysis)

    def test_trace_supply_chain_visualization(self):
        """测试供应链可视化追溯"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_trace',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取供应链可视化数据
        headers = {'Authorization': f'Bearer {token}'}
        params = {
            'drug_name': self.drug_name,
            'batch_number': self.drug_batch,
            'visualization_type': 'flow_diagram'
        }
        response = self.client.get('/api/tracing/supply-chain-visualization', 
                                 params=params, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证可视化数据结构
        self.assertIn('nodes', data)
        self.assertIn('edges', data)
        self.assertIn('flow_data', data)
        self.assertIn('metadata', data)
        
        # 验证节点信息
        nodes = data['nodes']
        self.assertIsInstance(nodes, list)
        self.assertGreaterEqual(len(nodes), 3)  # 至少包含生产商、批发商、零售商
        
        # 验证节点包含必要信息
        if len(nodes) > 0:
            node = nodes[0]
            expected_node_fields = ['id', 'type', 'name', 'inventory', 'location']
            for field in expected_node_fields:
                self.assertIn(field, node)
        
        # 验证边（连接）信息
        edges = data['edges']
        self.assertIsInstance(edges, list)
        self.assertGreaterEqual(len(edges), 2)  # 至少包含两个流转关系
        
        # 验证边包含必要信息
        if len(edges) > 0:
            edge = edges[0]
            expected_edge_fields = ['from', 'to', 'quantity', 'date', 'order_id']
            for field in expected_edge_fields:
                self.assertIn(field, edge)

    def test_trace_batch_recall_simulation(self):
        """测试批次召回模拟追溯"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_trace',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 模拟批次召回追溯
        headers = {'Authorization': f'Bearer {token}'}
        recall_data = {
            'batch_number': self.drug_batch,
            'recall_reason': '质量问题',
            'recall_level': 'consumer_level',  # 消费者级别召回
            'simulation_mode': True
        }
        response = self.client.post('/api/tracing/recall-simulation', 
                                  json=recall_data, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证召回模拟结果
        self.assertIn('recall_scope', data)
        self.assertIn('affected_enterprises', data)
        self.assertIn('affected_quantities', data)
        self.assertIn('notification_list', data)
        self.assertIn('estimated_timeline', data)
        
        # 验证召回范围
        recall_scope = data['recall_scope']
        self.assertIn('total_quantity', recall_scope)
        self.assertIn('distribution_levels', recall_scope)
        
        # 验证受影响企业
        affected_enterprises = data['affected_enterprises']
        self.assertIsInstance(affected_enterprises, list)
        self.assertGreaterEqual(len(affected_enterprises), 3)  # 生产商、批发商、零售商
        
        # 验证通知清单
        notification_list = data['notification_list']
        self.assertIsInstance(notification_list, list)
        
        for notification in notification_list:
            expected_fields = ['enterprise_id', 'company_name', 'contact_info', 'quantity_affected']
            for field in expected_fields:
                self.assertIn(field, notification)

    def test_unauthorized_tracing_access(self):
        """测试未授权追溯访问"""
        # 创建非相关用户
        other_user = User(
            username='other_user_trace',
            email='other@trace.com',
            phone='13900139000'
        )
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        # 非相关用户登录
        login_data = {
            'username': 'other_user_trace',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 尝试访问批次追溯（非监管用户应该有限制）
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/tracing/batch/{self.drug_batch}', headers=headers)
        
        # 根据权限设计，可能返回403或有限的信息
        self.assertIn(response.status_code, [200, 403])
        
        if response.status_code == 403:
            self.assertIn('权限', response.json['message'])

    def test_tracing_data_integrity(self):
        """测试追溯数据完整性验证"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_trace',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 验证追溯数据完整性
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/tracing/data-integrity/{self.drug_batch}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证完整性检查结果
        self.assertIn('integrity_status', data)
        self.assertIn('missing_records', data)
        self.assertIn('inconsistencies', data)
        self.assertIn('completeness_score', data)
        
        # 验证完整性评分
        completeness_score = data['completeness_score']
        self.assertIsInstance(completeness_score, (int, float))
        self.assertGreaterEqual(completeness_score, 0)
        self.assertLessEqual(completeness_score, 100)
        
        # 验证缺失记录
        missing_records = data['missing_records']
        self.assertIsInstance(missing_records, list)
        
        # 验证不一致性
        inconsistencies = data['inconsistencies']
        self.assertIsInstance(inconsistencies, list)