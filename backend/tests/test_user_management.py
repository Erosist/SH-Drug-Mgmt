"""
用户信息管理测试 (US-004)
测试管理端用户管理功能
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Tenant
from base import BaseTestCase


class TestUserManagement(BaseTestCase):
    """用户信息管理测试类"""
    
    def setUp(self):
        """设置测试数据"""
        super().setUp()
        
        # 创建管理员用户
        self.admin_user = User(
            username='admin_manager',
            email='admin@management.com',
            phone='13800138000',
            role='admin'
        )
        self.admin_user.set_password('admin123')
        db.session.add(self.admin_user)
        
        # 创建测试普通用户
        self.test_users = []
        for i in range(3):
            user = User(
                username=f'test_user_{i}',
                email=f'user{i}@test.com',
                phone=f'1380013800{i}',
                role='user',
                is_active=True if i < 2 else False  # 前两个激活，最后一个未激活
            )
            user.set_password('password123')
            self.test_users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # 为部分用户创建企业信息
        for i in range(2):
            tenant = Tenant(
                user_id=self.test_users[i].id,
                company_name=f'测试公司{i}',
                business_license=f'9131000012345678{i}',
                legal_representative=f'法人{i}',
                registered_address=f'上海市测试区测试路{i}号',
                contact_person=f'联系人{i}',
                contact_phone=f'021-1234567{i}',
                business_scope='药品经营',
                registration_capital=f'{1000+i*500}万元',
                status='approved' if i == 0 else 'pending'
            )
            db.session.add(tenant)
        
        db.session.commit()

    def test_admin_user_list(self):
        """测试管理员获取用户列表"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取用户列表
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/admin/users', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证返回格式
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('per_page', data)
        
        # 验证用户数量 (3个测试用户 + 1个管理员)
        self.assertEqual(data['total'], 4)
        self.assertTrue(len(data['items']) > 0)
        
        # 验证用户信息完整性
        user_item = data['items'][0]
        expected_fields = ['id', 'username', 'email', 'phone', 'role', 'is_active', 'created_at']
        for field in expected_fields:
            self.assertIn(field, user_item)

    def test_admin_user_search_and_filter(self):
        """测试用户搜索和过滤功能"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 按用户名搜索
        response = self.client.get('/api/admin/users?search=test_user_0', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['username'], 'test_user_0')
        
        # 按角色过滤
        response = self.client.get('/api/admin/users?role=admin', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['role'], 'admin')
        
        # 按激活状态过滤
        response = self.client.get('/api/admin/users?is_active=false', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json
        # 应该有1个未激活用户
        inactive_users = [item for item in data['items'] if not item['is_active']]
        self.assertEqual(len(inactive_users), 1)
        
        # 按邮箱搜索
        response = self.client.get('/api/admin/users?search=user1@test.com', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['email'], 'user1@test.com')

    def test_admin_user_detail(self):
        """测试获取用户详细信息"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取用户详细信息
        user_id = self.test_users[0].id
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/admin/users/{user_id}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证基本用户信息
        self.assertEqual(data['id'], user_id)
        self.assertEqual(data['username'], 'test_user_0')
        self.assertEqual(data['email'], 'user0@test.com')
        
        # 验证包含企业信息
        self.assertIn('tenant_info', data)
        tenant_info = data['tenant_info']
        self.assertIsNotNone(tenant_info)
        self.assertEqual(tenant_info['company_name'], '测试公司0')
        self.assertEqual(tenant_info['status'], 'approved')
        
        # 验证敏感信息不返回 (如密码哈希)
        self.assertNotIn('password_hash', data)

    def test_admin_user_status_toggle(self):
        """测试管理员切换用户激活状态"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取当前未激活用户
        inactive_user = self.test_users[2]  # 设置时未激活的用户
        self.assertFalse(inactive_user.is_active)
        
        # 激活用户
        headers = {'Authorization': f'Bearer {token}'}
        toggle_data = {'is_active': True}
        response = self.client.patch(f'/api/admin/users/{inactive_user.id}/status', 
                                   json=toggle_data, 
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], '用户状态更新成功')
        
        # 验证数据库中状态更新
        updated_user = User.query.get(inactive_user.id)
        self.assertTrue(updated_user.is_active)
        
        # 再次切换为未激活
        toggle_data = {'is_active': False}
        response = self.client.patch(f'/api/admin/users/{inactive_user.id}/status', 
                                   json=toggle_data, 
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态再次更新
        updated_user = User.query.get(inactive_user.id)
        self.assertFalse(updated_user.is_active)

    def test_admin_user_role_modification(self):
        """测试管理员修改用户角色"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 修改用户角色
        target_user = self.test_users[1]
        self.assertEqual(target_user.role, 'user')  # 初始角色
        
        role_data = {'role': 'manager'}
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.patch(f'/api/admin/users/{target_user.id}/role', 
                                   json=role_data, 
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], '用户角色更新成功')
        
        # 验证角色更新
        updated_user = User.query.get(target_user.id)
        self.assertEqual(updated_user.role, 'manager')
        
        # 测试无效角色
        invalid_role_data = {'role': 'invalid_role'}
        response = self.client.patch(f'/api/admin/users/{target_user.id}/role', 
                                   json=invalid_role_data, 
                                   headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('无效的角色', response.json['message'])

    def test_admin_reset_user_password(self):
        """测试管理员重置用户密码"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 重置用户密码
        target_user = self.test_users[0]
        old_password_hash = target_user.password_hash
        
        reset_data = {'new_password': 'new_password_123'}
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post(f'/api/admin/users/{target_user.id}/reset-password', 
                                  json=reset_data, 
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], '密码重置成功')
        
        # 验证密码已更改
        updated_user = User.query.get(target_user.id)
        self.assertNotEqual(updated_user.password_hash, old_password_hash)
        
        # 验证用户可以使用新密码登录
        new_login_data = {
            'username': 'test_user_0',
            'password': 'new_password_123'
        }
        login_response = self.client.post('/api/auth/login', json=new_login_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access_token', login_response.json)

    def test_admin_user_delete(self):
        """测试管理员删除用户"""
        # 创建一个临时用户用于删除测试
        temp_user = User(
            username='temp_delete_user',
            email='temp@delete.com',
            phone='13900139999',
            role='user'
        )
        temp_user.set_password('password123')
        db.session.add(temp_user)
        db.session.commit()
        
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 删除用户
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete(f'/api/admin/users/{temp_user.id}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], '用户删除成功')
        
        # 验证用户已删除
        deleted_user = User.query.get(temp_user.id)
        self.assertIsNone(deleted_user)
        
        # 尝试删除不存在的用户
        response = self.client.delete(f'/api/admin/users/999999', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('用户不存在', response.json['message'])

    def test_non_admin_access_control(self):
        """测试非管理员访问控制"""
        # 普通用户登录
        login_data = {
            'username': 'test_user_0',
            'password': 'password123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 尝试访问管理员功能
        headers = {'Authorization': f'Bearer {token}'}
        
        # 获取用户列表
        response = self.client.get('/api/admin/users', headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn('权限不足', response.json['message'])
        
        # 尝试修改其他用户状态
        response = self.client.patch(f'/api/admin/users/{self.test_users[1].id}/status', 
                                   json={'is_active': False}, 
                                   headers=headers)
        self.assertEqual(response.status_code, 403)
        
        # 尝试重置其他用户密码
        response = self.client.post(f'/api/admin/users/{self.test_users[1].id}/reset-password', 
                                  json={'new_password': 'hacked'}, 
                                  headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_user_management_statistics(self):
        """测试用户管理统计信息"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 获取用户统计信息
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/admin/users/statistics', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证统计项目
        expected_stats = ['total_users', 'active_users', 'inactive_users', 
                         'admin_users', 'regular_users', 'verified_enterprises', 
                         'pending_enterprises']
        
        for stat in expected_stats:
            self.assertIn(stat, data)
            self.assertIsInstance(data[stat], int)
            self.assertGreaterEqual(data[stat], 0)
        
        # 验证统计数据准确性
        self.assertEqual(data['total_users'], 4)  # 3个测试用户 + 1个管理员
        self.assertEqual(data['admin_users'], 1)
        self.assertEqual(data['regular_users'], 3)
        self.assertEqual(data['verified_enterprises'], 1)  # 一个approved状态的企业
        self.assertEqual(data['pending_enterprises'], 1)   # 一个pending状态的企业

    def test_user_activity_log(self):
        """测试用户活动日志查询"""
        # 管理员登录
        login_data = {
            'username': 'admin_manager',
            'password': 'admin123'
        }
        login_response = self.client.post('/api/auth/login', json=login_data)
        token = login_response.json['access_token']
        
        # 查询特定用户的活动日志
        user_id = self.test_users[0].id
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get(f'/api/admin/users/{user_id}/activity-log', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # 验证返回格式
        self.assertIn('items', data)
        self.assertIn('total', data)
        
        # 如果有活动记录，验证记录格式
        if data['total'] > 0:
            log_item = data['items'][0]
            expected_fields = ['id', 'action', 'timestamp', 'ip_address', 'user_agent']
            for field in expected_fields:
                self.assertIn(field, log_item)