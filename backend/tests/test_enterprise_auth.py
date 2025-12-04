"""
企业认证相关功能测试 (US-002, US-006)
测试企业信息认证和审核流程
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Tenant
from base import BaseTestCase


class TestEnterpriseAuth(BaseTestCase):
    """企业认证测试类"""

    def test_enterprise_info_submission(self):
        """测试企业信息提交 (US-002)"""
        # 创建测试用户
        user = User(
            username='test_enterprise_user',
            email='enterprise@test.com',
            phone='13800138000'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # 登录获取token
        login_data = {
            'username': 'test_enterprise_user',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 提交企业认证信息
        enterprise_data = {
            'company_name': '测试制药有限公司',
            'business_license': '91310000123456789X',
            'legal_representative': '张三',
            'registered_address': '上海市浦东新区测试路123号',
            'contact_person': '李四',
            'contact_phone': '021-12345678',
            'business_scope': '药品批发；药品零售',
            'registration_capital': '1000万元',
            'license_file_path': '/uploads/license_test.pdf'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/enterprise/submit-info', 
                                  json=enterprise_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['message'], '企业信息提交成功，等待审核')
        
        # 验证数据库中的企业信息
        tenant = Tenant.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(tenant)
        self.assertEqual(tenant.company_name, '测试制药有限公司')
        self.assertEqual(tenant.status, 'pending')  # 待审核状态

    def test_enterprise_info_validation(self):
        """测试企业信息验证规则"""
        # 创建测试用户
        user = User(
            username='test_validation_user',
            email='validation@test.com',
            phone='13900139000'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # 登录获取token
        login_data = {
            'username': 'test_validation_user',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 测试必填字段缺失
        incomplete_data = {
            'company_name': '测试公司',
            # 缺少business_license等必填字段
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/enterprise/submit-info', 
                                  json=incomplete_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('营业执照号码为必填项', response.json['message'])
        
        # 测试营业执照格式验证
        invalid_license_data = {
            'company_name': '测试制药有限公司',
            'business_license': 'invalid_license_format',
            'legal_representative': '张三',
            'registered_address': '上海市浦东新区测试路123号',
            'contact_person': '李四',
            'contact_phone': '021-12345678',
            'business_scope': '药品批发；药品零售',
            'registration_capital': '1000万元'
        }
        
        response = self.client.post('/api/enterprise/submit-info', 
                                  json=invalid_license_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('营业执照号码格式不正确', response.json['message'])

    def test_admin_enterprise_review_process(self):
        """测试管理员企业认证审核流程 (US-006)"""
        # 创建管理员用户
        admin_user = User(
            username='admin_reviewer',
            email='admin@test.com',
            phone='13700137000',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # 创建待审核的企业用户
        enterprise_user = User(
            username='pending_enterprise',
            email='pending@test.com',
            phone='13600136000'
        )
        enterprise_user.set_password('password123')
        db.session.add(enterprise_user)
        db.session.commit()
        
        # 创建待审核的企业信息
        tenant_info = Tenant(
            user_id=enterprise_user.id,
            company_name='待审核制药公司',
            business_license='91310000987654321Y',
            legal_representative='王五',
            registered_address='上海市徐汇区待审核路456号',
            contact_person='赵六',
            contact_phone='021-87654321',
            business_scope='药品研发；药品生产',
            registration_capital='2000万元',
            status='pending'
        )
        db.session.add(tenant_info)
        db.session.commit()
        
        # 管理员登录
        admin_login_data = {
            'username': 'admin_reviewer',
            'password': 'admin123'
        }
        admin_login_response = self.client.post('/api/auth/login', json=admin_login_data)
        admin_token = admin_login_response.json['access_token']
        
        # 获取待审核企业列表
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = self.client.get('/api/admin/pending-enterprises', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(len(data['items']) > 0)
        self.assertEqual(data['items'][0]['company_name'], '待审核制药公司')
        self.assertEqual(data['items'][0]['status'], 'pending')
        
        # 审核通过
        review_data = {
            'tenant_id': tenant_info.id,
            'action': 'approve',
            'review_notes': '企业资质完整，审核通过'
        }
        response = self.client.post('/api/admin/review-enterprise', 
                                  json=review_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], '企业认证审核完成')
        
        # 验证状态更新
        updated_tenant = Tenant.query.get(tenant_info.id)
        self.assertEqual(updated_tenant.status, 'approved')
        self.assertEqual(updated_tenant.review_notes, '企业资质完整，审核通过')
        self.assertIsNotNone(updated_tenant.reviewed_at)

    def test_enterprise_review_rejection(self):
        """测试企业认证审核拒绝流程"""
        # 创建管理员和企业用户
        admin_user = User(
            username='admin_reject',
            email='admin_reject@test.com', 
            phone='13500135000',
            role='admin'
        )
        admin_user.set_password('admin123')
        
        enterprise_user = User(
            username='reject_enterprise',
            email='reject@test.com',
            phone='13400134000'
        )
        enterprise_user.set_password('password123')
        
        db.session.add_all([admin_user, enterprise_user])
        db.session.commit()
        
        # 创建有问题的企业信息
        tenant_info = Tenant(
            user_id=enterprise_user.id,
            company_name='问题企业',
            business_license='invalid_license_123',
            legal_representative='张三',
            registered_address='地址不完整',
            contact_person='李四',
            contact_phone='12345',  # 格式错误
            business_scope='范围模糊',
            registration_capital='未知',
            status='pending'
        )
        db.session.add(tenant_info)
        db.session.commit()
        
        # 管理员登录并拒绝审核
        admin_login_data = {
            'username': 'admin_reject',
            'password': 'admin123'
        }
        admin_login_response = self.client.post('/api/auth/login', json=admin_login_data)
        admin_token = admin_login_response.json['access_token']
        
        review_data = {
            'tenant_id': tenant_info.id,
            'action': 'reject',
            'review_notes': '营业执照格式错误，联系电话格式不正确，请重新提交'
        }
        
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = self.client.post('/api/admin/review-enterprise', 
                                  json=review_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], '企业认证审核完成')
        
        # 验证拒绝状态
        updated_tenant = Tenant.query.get(tenant_info.id)
        self.assertEqual(updated_tenant.status, 'rejected')
        self.assertIn('营业执照格式错误', updated_tenant.review_notes)

    def test_enterprise_status_access_control(self):
        """测试基于企业认证状态的访问控制"""
        # 创建未认证企业用户
        unverified_user = User(
            username='unverified_user',
            email='unverified@test.com',
            phone='13300133000'
        )
        unverified_user.set_password('password123')
        db.session.add(unverified_user)
        db.session.commit()
        
        # 创建已认证企业用户
        verified_user = User(
            username='verified_user',
            email='verified@test.com',
            phone='13200132000'
        )
        verified_user.set_password('password123')
        db.session.add(verified_user)
        db.session.commit()
        
        verified_tenant = Tenant(
            user_id=verified_user.id,
            company_name='已认证制药公司',
            business_license='91310000111222333A',
            legal_representative='王五',
            registered_address='上海市黄浦区认证路789号',
            contact_person='赵六',
            contact_phone='021-11122233',
            business_scope='药品批发；药品零售',
            registration_capital='5000万元',
            status='approved'
        )
        db.session.add(verified_tenant)
        db.session.commit()
        
        # 未认证用户登录
        unverified_login = {
            'username': 'unverified_user',
            'password': 'password123'
        }
        unverified_response = self.client.post('/api/auth/login', json=unverified_login)
        unverified_token = unverified_response.json['access_token']
        
        # 已认证用户登录
        verified_login = {
            'username': 'verified_user',
            'password': 'password123'
        }
        verified_response = self.client.post('/api/auth/login', json=verified_login)
        verified_token = verified_response.json['access_token']
        
        # 测试访问需要认证的接口
        supply_data = {
            'drug_name': '测试药品',
            'manufacturer': '测试制药厂',
            'quantity': 100,
            'unit_price': 25.5,
            'expiry_date': '2025-12-31',
            'batch_number': 'TEST2024001'
        }
        
        # 未认证用户访问 - 应该被拒绝
        unverified_headers = {'Authorization': f'Bearer {unverified_token}'}
        response = self.client.post('/api/supply/publish', 
                                  json=supply_data, 
                                  headers=unverified_headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn('企业认证', response.json['message'])
        
        # 已认证用户访问 - 应该成功
        verified_headers = {'Authorization': f'Bearer {verified_token}'}
        response = self.client.post('/api/supply/publish', 
                                  json=supply_data, 
                                  headers=verified_headers)
        # 这里期望成功或者至少不是认证问题
        self.assertNotEqual(response.status_code, 403)