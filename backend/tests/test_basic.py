"""
基础测试 - 确保测试环境工作正常
"""
import pytest
import json
from app import create_app
from extensions import db


class TestBasic:
    """基础测试类"""
    
    def test_app_creation(self, app):
        """测试应用创建"""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_index_route(self, client):
        """测试首页路由"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'msg' in data
        assert data['msg'] == 'Flask auth backend is running'
    
    def test_404_route(self, client):
        """测试404响应"""
        response = client.get('/nonexistent')
        assert response.status_code == 404


class TestEnvironment:
    """环境配置测试"""
    
    def test_testing_config(self, app):
        """验证测试环境配置"""
        assert app.config['TESTING'] is True
        assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_DATABASE_URI']
        assert app.config['WTF_CSRF_ENABLED'] is False
    
    def test_database_connection(self, app):
        """测试数据库连接"""
        with app.app_context():
            # 简单的数据库连接测试
            from sqlalchemy import text
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test")).fetchone()
                assert result[0] == 1


class TestAPI:
    """API基础测试"""
    
    def test_cors_headers(self, client):
        """测试CORS配置"""
        response = client.options('/', headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET'
        })
        # CORS应该允许这个请求
        assert response.status_code in [200, 204]
    
    def test_json_response(self, client):
        """测试JSON响应格式"""
        response = client.get('/')
        assert response.is_json
        assert response.content_type == 'application/json'