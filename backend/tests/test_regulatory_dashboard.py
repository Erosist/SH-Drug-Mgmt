"""
监管看板测试 (US-014)
测试面向监管的基础可视化功能（聚合、筛选、刷新）
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Tenant, Order, InventoryItem, CirculationRecord
from base import BaseTestCase


class TestRegulatoryDashboard(BaseTestCase):
    """监管看板测试类"""
    
    def setUp(self):
        """设置测试数据"""
        super().setUp()
        
        # 创建监管用户(管理员权限)
        self.regulator_user = User(
            username='regulator_dashboard',
            email='regulator@dashboard.com',
            phone='13800138000',
            role='admin'
        )
        self.regulator_user.set_password('regulator123')
        db.session.add(self.regulator_user)
        
        # 创建多个企业用户用于生成测试数据
        self.enterprise_users = []
        for i in range(3):
            user = User(
                username=f'enterprise_{i}',
                email=f'enterprise{i}@test.com',
                phone=f'1380013800{i+1}',
                role='user'
            )
            user.set_password('password123')
            self.enterprise_users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # 创建企业信息
        self.tenant_infos = []
        for i, user in enumerate(self.enterprise_users):
            tenant = Tenant(
                user_id=user.id,
                company_name=f'监管测试企业{i}',
                business_license=f'9131000012345678{i}',
                legal_representative=f'法人{i}',
                registered_address=f'上海市测试区监管路{i}号',
                contact_person=f'联系人{i}',
                contact_phone=f'021-1234567{i}',
                business_scope='药品批发' if i < 2 else '药品零售',
                registration_capital=f'{1000+i*500}万元',
                status='approved'
            )
            self.tenant_infos.append(tenant)
            db.session.add(tenant)
        
        # 创建测试订单数据
        self.test_orders = []
        order_statuses = ['pending', 'confirmed', 'shipped', 'delivered']
        for i in range(8):  # 创建8个订单
            order = Order(
                supplier_id=self.enterprise_users[i % 2].id,  # 前两个用户作为供应商
                buyer_id=self.enterprise_users[2].id,         # 第三个用户作为采购商
                drug_name=f'监管测试药品{i % 3}',
                manufacturer=f'制药厂{i % 2}',
                quantity=100 + i * 50,
                unit_price=10.0 + i * 2.5,
                total_price=(100 + i * 50) * (10.0 + i * 2.5),
                batch_number=f'REG2024{i:03d}',
                expiry_date=datetime(2025, 6 + i % 6, 15),
                status=order_statuses[i % 4],
                created_at=datetime.now() - timedelta(days=i*2)
            )
            self.test_orders.append(order)
            db.session.add(order)
        
        # 创建库存数据
        self.inventory_items = []
        for i in range(6):
            item = InventoryItem(
                tenant_id=self.tenant_infos[i % 2].id,  # 前两个企业有库存
                drug_name=f'库存药品{i}',
                manufacturer=f'生产厂家{i % 3}',
                current_stock=1000 - i * 150,  # 递减的库存量
                min_stock_threshold=200,
                unit_price=15.0 + i * 3.0,
                batch_number=f'INV2024{i:03d}',
                expiry_date=datetime(2025, 3 + i % 9, 10),
                last_updated=datetime.now() - timedelta(days=i)
            )
            self.inventory_items.append(item)
            db.session.add(item)
        
        # 创建流通记录
        self.circulation_records = []
        for i in range(5):  # 为前5个订单创建流通记录
            record = CirculationRecord(
                order_id=self.test_orders[i].id,
                action='ship' if i < 3 else 'delivered',
                reporter_id=self.enterprise_users[i % 2].id,
                tracking_number=f'TRK2024{i:03d}',
                carrier_name='顺丰速运',
                status='completed',
                created_at=datetime.now() - timedelta(days=i)
            )
            self.circulation_records.append(record)
            db.session.add(record)
        
        db.session.commit()

    def test_dashboard_overview_statistics(self):
        """测试监管看板总览统计"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取看板总览数据
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/regulatory/dashboard/overview', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证关键统计指标
        expected_metrics = [
            'total_enterprises', 'active_enterprises', 'total_orders',
            'completed_orders', 'total_inventory_value', 'circulation_records',
            'compliance_rate', 'warning_items'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, data)
            self.assertIsInstance(data[metric], (int, float))
        
        # 验证数据准确性
        self.assertEqual(data['total_enterprises'], 3)
        self.assertEqual(data['total_orders'], 8)
        self.assertEqual(data['circulation_records'], 5)
        
        # 验证合规率计算
        self.assertGreaterEqual(data['compliance_rate'], 0)
        self.assertLessEqual(data['compliance_rate'], 100)

    def test_enterprise_distribution_analysis(self):
        """测试企业分布分析"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取企业分布数据
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/regulatory/dashboard/enterprise-distribution', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证分布数据结构
        self.assertIn('by_business_scope', data)
        self.assertIn('by_registration_capital', data)
        self.assertIn('by_status', data)
        self.assertIn('by_region', data)
        
        # 验证业务范围分布
        scope_distribution = data['by_business_scope']
        self.assertIsInstance(scope_distribution, list)
        
        # 验证包含预期的业务范围类型
        scope_types = [item['scope'] for item in scope_distribution]
        self.assertIn('药品批发', scope_types)
        self.assertIn('药品零售', scope_types)
        
        # 验证统计数量
        total_count = sum(item['count'] for item in scope_distribution)
        self.assertEqual(total_count, 3)  # 总共3个企业

    def test_order_trend_analysis(self):
        """测试订单趋势分析"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取订单趋势数据（最近30天）
        headers = {'Authorization': f'Bearer {token}'}
        params = {
            'period': '30d',
            'group_by': 'day'
        }
        response = self.client.get('/api/regulatory/dashboard/order-trends', 
                                 params=params, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证趋势数据结构
        self.assertIn('timeline', data)
        self.assertIn('summary', data)
        
        # 验证时间线数据
        timeline = data['timeline']
        self.assertIsInstance(timeline, list)
        
        if len(timeline) > 0:
            timeline_item = timeline[0]
            expected_fields = ['date', 'order_count', 'total_value', 'status_breakdown']
            for field in expected_fields:
                self.assertIn(field, timeline_item)
        
        # 验证汇总数据
        summary = data['summary']
        expected_summary_fields = ['total_orders', 'total_value', 'average_order_value', 'growth_rate']
        for field in expected_summary_fields:
            self.assertIn(field, summary)

    def test_circulation_monitoring(self):
        """测试流通监控"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取流通监控数据
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/regulatory/dashboard/circulation-monitor', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证流通监控结构
        self.assertIn('circulation_summary', data)
        self.assertIn('active_shipments', data)
        self.assertIn('completion_rate', data)
        self.assertIn('average_delivery_time', data)
        
        # 验证流通汇总
        summary = data['circulation_summary']
        expected_summary_fields = ['total_shipments', 'in_transit', 'delivered', 'delayed']
        for field in expected_summary_fields:
            self.assertIn(field, summary)
            self.assertIsInstance(summary[field], int)
        
        # 验证活跃货运列表
        active_shipments = data['active_shipments']
        self.assertIsInstance(active_shipments, list)
        
        if len(active_shipments) > 0:
            shipment = active_shipments[0]
            expected_shipment_fields = ['order_id', 'tracking_number', 'status', 'estimated_delivery']
            for field in expected_shipment_fields:
                self.assertIn(field, shipment)

    def test_inventory_monitoring(self):
        """测试库存监控"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取库存监控数据
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/regulatory/dashboard/inventory-monitor', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证库存监控结构
        self.assertIn('inventory_summary', data)
        self.assertIn('low_stock_alerts', data)
        self.assertIn('expiry_alerts', data)
        self.assertIn('total_inventory_value', data)
        
        # 验证库存汇总
        summary = data['inventory_summary']
        expected_fields = ['total_items', 'total_value', 'low_stock_items', 'expiring_items']
        for field in expected_fields:
            self.assertIn(field, summary)
        
        # 验证低库存预警
        low_stock_alerts = data['low_stock_alerts']
        self.assertIsInstance(low_stock_alerts, list)
        
        # 验证过期预警
        expiry_alerts = data['expiry_alerts']
        self.assertIsInstance(expiry_alerts, list)

    def test_compliance_analysis(self):
        """测试合规性分析"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取合规性分析数据
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/regulatory/dashboard/compliance-analysis', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证合规性分析结构
        self.assertIn('overall_compliance_score', data)
        self.assertIn('compliance_breakdown', data)
        self.assertIn('non_compliant_enterprises', data)
        self.assertIn('improvement_suggestions', data)
        
        # 验证总体合规评分
        overall_score = data['overall_compliance_score']
        self.assertIsInstance(overall_score, (int, float))
        self.assertGreaterEqual(overall_score, 0)
        self.assertLessEqual(overall_score, 100)
        
        # 验证合规性分解
        breakdown = data['compliance_breakdown']
        expected_categories = ['enterprise_certification', 'circulation_reporting', 'inventory_management']
        for category in expected_categories:
            self.assertIn(category, breakdown)
            self.assertIn('score', breakdown[category])
            self.assertIn('total', breakdown[category])
            self.assertIn('compliant', breakdown[category])

    def test_dashboard_data_filtering(self):
        """测试看板数据筛选功能"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 按时间范围筛选订单数据
        headers = {'Authorization': f'Bearer {token}'}
        filter_params = {
            'start_date': '2024-11-01',
            'end_date': '2024-12-31',
            'status': 'delivered'
        }
        
        response = self.client.get('/api/regulatory/dashboard/orders-filtered', 
                                 params=filter_params, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证筛选结果
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertIn('filters_applied', data)
        
        # 验证筛选条件应用
        filters_applied = data['filters_applied']
        self.assertEqual(filters_applied['status'], 'delivered')
        
        # 按企业类型筛选
        enterprise_filter_params = {
            'business_scope': '药品批发',
            'status': 'approved'
        }
        
        response = self.client.get('/api/regulatory/dashboard/enterprises-filtered', 
                                 params=enterprise_filter_params, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证企业筛选结果
        if data['total'] > 0:
            for enterprise in data['items']:
                self.assertEqual(enterprise['business_scope'], '药品批发')
                self.assertEqual(enterprise['status'], 'approved')

    def test_dashboard_real_time_refresh(self):
        """测试看板实时刷新功能"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取初始看板数据
        headers = {'Authorization': f'Bearer {token}'}
        initial_response = self.client.get('/api/regulatory/dashboard/overview', headers=headers)
        initial_data = initial_response.json
        initial_order_count = initial_data['total_orders']
        
        # 模拟新增数据（创建新订单）
        new_order = Order(
            supplier_id=self.enterprise_users[0].id,
            buyer_id=self.enterprise_users[1].id,
            drug_name='实时测试药品',
            manufacturer='实时测试厂',
            quantity=200,
            unit_price=30.0,
            total_price=6000.0,
            batch_number='RT2024001',
            expiry_date=datetime(2025, 12, 31),
            status='pending'
        )
        db.session.add(new_order)
        db.session.commit()
        
        # 刷新看板数据
        refresh_response = self.client.get('/api/regulatory/dashboard/overview', headers=headers)
        refresh_data = refresh_response.json
        refreshed_order_count = refresh_data['total_orders']
        
        # 验证数据已更新
        self.assertEqual(refreshed_order_count, initial_order_count + 1)
        
        # 测试带时间戳的数据刷新
        timestamp_params = {'last_update': datetime.now().isoformat()}
        response = self.client.get('/api/regulatory/dashboard/check-updates', 
                                 params=timestamp_params, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        update_data = response.json
        self.assertIn('has_updates', update_data)
        self.assertIn('last_update_time', update_data)

    def test_dashboard_export_functionality(self):
        """测试看板数据导出功能"""
        # 监管用户登录
        login_data = {
            'username': 'regulator_dashboard',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 导出订单数据
        headers = {'Authorization': f'Bearer {token}'}
        export_params = {
            'export_type': 'orders',
            'format': 'json',
            'date_range': '30d'
        }
        
        response = self.client.get('/api/regulatory/dashboard/export', 
                                 params=export_params, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证导出数据格式
        if response.content_type == 'application/json':
            data = response.json
            self.assertIn('export_data', data)
            self.assertIn('export_info', data)
            
            export_info = data['export_info']
            self.assertIn('total_records', export_info)
            self.assertIn('export_time', export_info)
            self.assertIn('filters_applied', export_info)

    def test_unauthorized_dashboard_access(self):
        """测试未授权访问监管看板"""
        # 创建普通用户
        regular_user = User(
            username='regular_user_dash',
            email='regular@dash.com',
            phone='13700137000',
            role='user'
        )
        regular_user.set_password('password123')
        db.session.add(regular_user)
        db.session.commit()
        
        # 普通用户登录
        login_data = {
            'username': 'regular_user_dash',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 尝试访问监管看板
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/regulatory/dashboard/overview', headers=headers)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('权限不足', response.json['message'])
        
        # 尝试访问其他监管接口
        response = self.client.get('/api/regulatory/dashboard/compliance-analysis', headers=headers)
        self.assertEqual(response.status_code, 403)