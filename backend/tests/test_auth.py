"""
测试认证系统
"""
import pytest
import json
from app import create_app
from extensions import db
from models import User, Tenant


@pytest.fixture
def app():
    """创建测试应用"""
    import os
    
    # 设置测试环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    from config import TestingConfig
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # 创建测试租户
        tenant = Tenant(
            name='测试公司',
            type='LOGISTICS',
            unified_social_credit_code='TEST001',
            legal_representative='张三',
            contact_person='李四',
            contact_phone='13800000001',
            contact_email='test@example.com',
            address='测试地址',
            business_scope='物流运输'
        )
        db.session.add(tenant)
        db.session.flush()
        
        # 创建测试用户
        user = User(
            username='testuser',
            email='test@example.com',
            role='logistics',
            tenant_id=tenant.id
        )
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestAuth:
    """测试认证功能"""
    
    def test_login_success(self, client):
        """测试成功登录"""
        response = client.post('/api/auth/login', 
                              json={'username': 'testuser', 'password': 'testpass'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert data['user']['role'] == 'logistics'
        
    def test_login_invalid_credentials(self, client):
        """测试无效凭证登录"""
        response = client.post('/api/auth/login',
                              json={'username': 'testuser', 'password': 'wrongpass'})
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['msg'] == 'bad username or password'  # 修复字段名
        
    def test_login_nonexistent_user(self, client):
        """测试不存在用户登录"""
        response = client.post('/api/auth/login',
                              json={'username': 'nonexistent', 'password': 'password'})
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['msg'] == 'bad username or password'  # 修复字段名
        
    def test_login_missing_data(self, client):
        """测试缺少登录数据"""
        # 测试缺少用户名
        response = client.post('/api/auth/login', json={
            'password': 'password123'
        })
        assert response.status_code == 400
        
        # 测试缺少密码
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
        })
        assert response.status_code == 400
        
        # 测试空请求
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400
        
    def test_protected_route_with_valid_token(self, client):
        """测试使用有效token访问受保护路由"""
        # 首先登录获取token
        login_response = client.post('/api/auth/login',
                                   json={'username': 'testuser', 'password': 'testpass'})
        login_data = json.loads(login_response.data)
        token = login_data['access_token']
        
        # 使用token访问受保护路由
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/orders', headers=headers)
        
        assert response.status_code == 200
        
    def test_protected_route_without_token(self, client):
        """测试未提供token访问受保护路由"""
        response = client.get('/api/orders')
        
        assert response.status_code == 401
        
    def test_protected_route_with_invalid_token(self, client):
        """测试使用无效token访问受保护路由"""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/orders', headers=headers)
        
        assert response.status_code == 422
        
    def test_token_refresh(self, client):
        """测试token刷新"""
        # 首先登录获取refresh token
        login_response = client.post('/api/auth/login',
                                   json={'username': 'testuser', 'password': 'testpass'})
        login_data = json.loads(login_response.data)
        refresh_token = login_data['refresh_token']
        
        # 使用refresh token获取新的access token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/api/auth/refresh', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        
    def test_user_info(self, client):
        """测试获取用户信息"""
        # 首先登录获取token
        login_response = client.post('/api/auth/login',
                                   json={'username': 'testuser', 'password': 'testpass'})
        login_data = json.loads(login_response.data)
        token = login_data['access_token']
        
        # 获取用户信息
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['user']['username'] == 'testuser'
        assert data['user']['role'] == 'logistics'
        assert 'tenant' in data['user']
        assert data['user']['tenant']['name'] == '测试公司'
