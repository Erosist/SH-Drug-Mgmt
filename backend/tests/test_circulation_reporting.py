"""
流通数据上报测试 (US-012) 
测试药品流通监管最小闭环：发货-在途-送达
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Tenant, Order, CirculationRecord
from base import BaseTestCase


class TestCirculationReporting(BaseTestCase):
    """流通数据上报测试类"""
    
    def setUp(self):
        """设置测试数据"""
        super().setUp()
        
        # 创建供应商用户(已认证)
        self.supplier_user = User(
            username='supplier_circulation',
            email='supplier@circulation.com',
            phone='13800138001'
        )
        self.supplier_user.set_password('password123')
        db.session.add(self.supplier_user)
        
        # 创建采购商用户(已认证)
        self.buyer_user = User(
            username='buyer_circulation',
            email='buyer@circulation.com',
            phone='13800138002'
        )
        self.buyer_user.set_password('password123')
        db.session.add(self.buyer_user)
        db.session.commit()
        
        # 创建供应商企业信息
        self.supplier_tenant = Tenant(
            user_id=self.supplier_user.id,
            company_name='供应商制药公司',
            business_license='91310000123456789S',
            legal_representative='供应商代表',
            registered_address='上海市浦东新区供应路123号',
            contact_person='供应联系人',
            contact_phone='021-12345678',
            business_scope='药品批发',
            registration_capital='3000万元',
            status='approved'
        )
        
        # 创建采购商企业信息
        self.buyer_tenant = Tenant(
            user_id=self.buyer_user.id,
            company_name='采购商医药公司',
            business_license='91310000987654321B',
            legal_representative='采购商代表',
            registered_address='上海市徐汇区采购路456号',
            contact_person='采购联系人',
            contact_phone='021-87654321',
            business_scope='药品零售',
            registration_capital='1000万元',
            status='approved'
        )
        
        db.session.add_all([self.supplier_tenant, self.buyer_tenant])
        db.session.commit()
        
        # 创建测试订单
        self.test_order = Order(
            supplier_id=self.supplier_user.id,
            buyer_id=self.buyer_user.id,
            drug_name='阿莫西林胶囊',
            manufacturer='测试制药厂',
            quantity=500,
            unit_price=12.5,
            total_price=6250.0,
            batch_number='AMX20241201',
            expiry_date=datetime(2025, 12, 31),
            status='confirmed'
        )
        db.session.add(self.test_order)
        db.session.commit()

    def test_shipment_reporting(self):
        """测试发货上报 (流通闭环第一步)"""
        # 供应商登录
        login_data = {
            'username': 'supplier_circulation',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 上报发货信息
        shipment_data = {
            'order_id': self.test_order.id,
            'action': 'ship',
            'tracking_number': 'SF1234567890',
            'carrier_name': '顺丰速运',
            'carrier_phone': '95338',
            'estimated_delivery': '2024-12-08',
            'shipping_address': '上海市徐汇区采购路456号',
            'special_requirements': '冷链运输，温度2-8℃',
            'notes': '请保持药品干燥，避免阳光直射'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/circulation/report', 
                                  json=shipment_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['message'], '发货信息上报成功')
        
        # 验证订单状态更新
        updated_order = Order.query.get(self.test_order.id)
        self.assertEqual(updated_order.status, 'shipped')
        self.assertEqual(updated_order.tracking_number, 'SF1234567890')
        
        # 验证流通记录创建
        circulation_record = CirculationRecord.query.filter_by(
            order_id=self.test_order.id,
            action='ship'
        ).first()
        
        self.assertIsNotNone(circulation_record)
        self.assertEqual(circulation_record.carrier_name, '顺丰速运')
        self.assertEqual(circulation_record.reporter_id, self.supplier_user.id)
        self.assertEqual(circulation_record.status, 'active')

    def test_in_transit_tracking(self):
        """测试在途跟踪上报 (流通闭环第二步)"""
        # 先创建已发货的订单状态
        self.test_order.status = 'shipped'
        self.test_order.tracking_number = 'SF1234567890'
        db.session.commit()
        
        # 创建发货记录
        ship_record = CirculationRecord(
            order_id=self.test_order.id,
            action='ship',
            reporter_id=self.supplier_user.id,
            tracking_number='SF1234567890',
            carrier_name='顺丰速运',
            status='active'
        )
        db.session.add(ship_record)
        db.session.commit()
        
        # 承运商或系统上报在途状态 (这里模拟供应商代为上报)
        login_data = {
            'username': 'supplier_circulation',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        transit_data = {
            'order_id': self.test_order.id,
            'action': 'transit',
            'tracking_number': 'SF1234567890',
            'current_location': '上海分拨中心',
            'location_code': 'SH-HUB-001',
            'transit_status': 'in_transit',
            'temperature_log': '3.2℃',
            'humidity_log': '65%',
            'estimated_arrival': '2024-12-07 14:30:00',
            'notes': '货物状态正常，继续运输中'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/circulation/report', 
                                  json=transit_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['message'], '在途状态上报成功')
        
        # 验证在途记录
        transit_record = CirculationRecord.query.filter_by(
            order_id=self.test_order.id,
            action='transit'
        ).first()
        
        self.assertIsNotNone(transit_record)
        self.assertEqual(transit_record.current_location, '上海分拨中心')
        self.assertEqual(transit_record.transit_status, 'in_transit')
        self.assertEqual(transit_record.temperature_log, '3.2℃')

    def test_delivery_confirmation(self):
        """测试送达确认上报 (流通闭环第三步)"""
        # 创建完整的流通链路前置状态
        self.test_order.status = 'shipped'
        self.test_order.tracking_number = 'SF1234567890'
        db.session.commit()
        
        # 创建发货和在途记录
        ship_record = CirculationRecord(
            order_id=self.test_order.id,
            action='ship',
            reporter_id=self.supplier_user.id,
            tracking_number='SF1234567890',
            carrier_name='顺丰速运',
            status='active'
        )
        
        transit_record = CirculationRecord(
            order_id=self.test_order.id,
            action='transit',
            reporter_id=self.supplier_user.id,
            tracking_number='SF1234567890',
            current_location='目的地配送中心',
            transit_status='out_for_delivery',
            status='active'
        )
        
        db.session.add_all([ship_record, transit_record])
        db.session.commit()
        
        # 采购商登录确认收货
        login_data = {
            'username': 'buyer_circulation',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        delivery_data = {
            'order_id': self.test_order.id,
            'action': 'delivered',
            'tracking_number': 'SF1234567890',
            'received_by': '采购联系人',
            'received_at': '2024-12-06 16:30:00',
            'delivery_address': '上海市徐汇区采购路456号',
            'package_condition': 'good',
            'temperature_on_arrival': '2.8℃',
            'quality_check_result': 'passed',
            'signature_file': '/uploads/signature_20241206.jpg',
            'notes': '药品包装完好，温度符合要求，质检合格'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/circulation/report', 
                                  json=delivery_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['message'], '送达确认上报成功')
        
        # 验证订单状态最终更新
        updated_order = Order.query.get(self.test_order.id)
        self.assertEqual(updated_order.status, 'delivered')
        
        # 验证送达记录
        delivery_record = CirculationRecord.query.filter_by(
            order_id=self.test_order.id,
            action='delivered'
        ).first()
        
        self.assertIsNotNone(delivery_record)
        self.assertEqual(delivery_record.received_by, '采购联系人')
        self.assertEqual(delivery_record.package_condition, 'good')
        self.assertEqual(delivery_record.reporter_id, self.buyer_user.id)
        
        # 验证前序记录状态更新
        updated_ship_record = CirculationRecord.query.filter_by(
            order_id=self.test_order.id,
            action='ship'
        ).first()
        self.assertEqual(updated_ship_record.status, 'completed')

    def test_circulation_record_query(self):
        """测试流通记录查询"""
        # 创建完整的流通记录链
        records = [
            CirculationRecord(
                order_id=self.test_order.id,
                action='ship',
                reporter_id=self.supplier_user.id,
                tracking_number='SF1234567890',
                carrier_name='顺丰速运',
                status='completed',
                created_at=datetime(2024, 12, 5, 10, 0, 0)
            ),
            CirculationRecord(
                order_id=self.test_order.id,
                action='transit',
                reporter_id=self.supplier_user.id,
                tracking_number='SF1234567890',
                current_location='中转站',
                transit_status='in_transit',
                status='completed',
                created_at=datetime(2024, 12, 5, 14, 30, 0)
            ),
            CirculationRecord(
                order_id=self.test_order.id,
                action='delivered',
                reporter_id=self.buyer_user.id,
                tracking_number='SF1234567890',
                received_by='收货人',
                package_condition='good',
                status='completed',
                created_at=datetime(2024, 12, 6, 16, 30, 0)
            )
        ]
        
        db.session.add_all(records)
        db.session.commit()
        
        # 供应商查询流通记录
        login_data = {
            'username': 'supplier_circulation',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/circulation/records/{self.test_order.id}', 
                                 headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证返回完整流通链路
        self.assertEqual(len(data['records']), 3)
        
        # 验证记录按时间顺序排列
        actions = [record['action'] for record in data['records']]
        self.assertEqual(actions, ['ship', 'transit', 'delivered'])
        
        # 验证关键信息完整
        ship_record = data['records'][0]
        self.assertEqual(ship_record['carrier_name'], '顺丰速运')
        self.assertEqual(ship_record['tracking_number'], 'SF1234567890')
        
        delivery_record = data['records'][2]
        self.assertEqual(delivery_record['received_by'], '收货人')
        self.assertEqual(delivery_record['package_condition'], 'good')

    def test_circulation_integrity_validation(self):
        """测试流通完整性验证"""
        # 尝试跳过发货直接上报送达 (应该失败)
        login_data = {
            'username': 'buyer_circulation',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        invalid_delivery_data = {
            'order_id': self.test_order.id,
            'action': 'delivered',
            'tracking_number': 'INVALID123',
            'received_by': '收货人',
            'received_at': '2024-12-06 16:30:00'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/circulation/report', 
                                  json=invalid_delivery_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('订单尚未发货', response.json['message'])
        
    def test_unauthorized_circulation_reporting(self):
        """测试未授权流通上报"""
        # 创建非相关用户
        other_user = User(
            username='other_user',
            email='other@test.com',
            phone='13900139000'
        )
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        # 其他用户尝试上报流通信息
        login_data = {
            'username': 'other_user',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        unauthorized_data = {
            'order_id': self.test_order.id,
            'action': 'ship',
            'tracking_number': 'UNAUTHORIZED123',
            'carrier_name': '测试物流'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/circulation/report', 
                                  json=unauthorized_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('无权限操作', response.json['message'])

    def test_circulation_regulatory_compliance(self):
        """测试流通监管合规检查"""
        # 创建完整流通记录
        self.test_order.status = 'delivered'
        db.session.commit()
        
        records = [
            CirculationRecord(
                order_id=self.test_order.id,
                action='ship',
                reporter_id=self.supplier_user.id,
                tracking_number='SF1234567890',
                carrier_name='顺丰速运',
                status='completed'
            ),
            CirculationRecord(
                order_id=self.test_order.id,
                action='delivered',
                reporter_id=self.buyer_user.id,
                tracking_number='SF1234567890',
                received_by='收货人',
                status='completed'
            )
        ]
        
        db.session.add_all(records)
        db.session.commit()
        
        # 监管方查询合规性报告
        # 这里模拟管理员查询
        admin_user = User(
            username='regulator',
            email='regulator@gov.com',
            phone='13000130000',
            role='admin'
        )
        admin_user.set_password('regulator123')
        db.session.add(admin_user)
        db.session.commit()
        
        login_data = {
            'username': 'regulator',
            'password': 'regulator123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/circulation/compliance-report', 
                                 headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证合规性指标
        self.assertIn('total_orders', data)
        self.assertIn('completed_circulation_orders', data)
        self.assertIn('compliance_rate', data)
        
        # 验证闭环完整性
        compliance_rate = data['compliance_rate']
        self.assertGreaterEqual(compliance_rate, 0)
        self.assertLessEqual(compliance_rate, 100)