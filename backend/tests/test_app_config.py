"""
测试配置和应用启动
"""
import pytest
import os
import tempfile
from app import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig


class TestAppConfiguration:
    """测试应用配置"""
    
    def test_development_config(self):
        """测试开发环境配置"""
        os.environ['FLASK_ENV'] = 'development'
        app = create_app()
        
        assert app.config['DEBUG'] is True
        assert 'sqlite:///data.db' in app.config['SQLALCHEMY_DATABASE_URI']
        assert app.config['TESTING'] is False
    
    def test_production_config(self):
        """测试生产环境配置"""
        os.environ['FLASK_ENV'] = 'production'
        app = create_app()
        
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False
    
    def test_testing_config(self):
        """测试测试环境配置"""
        os.environ['FLASK_ENV'] = 'testing'
        app = create_app()
        
        assert app.config['TESTING'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    
    def test_config_from_environment(self):
        """测试从环境变量加载配置"""
        # 设置环境变量
        os.environ['SECRET_KEY'] = 'test-secret-123'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-456'
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        
        app = create_app()
        
        assert app.config['SECRET_KEY'] == 'test-secret-123'
        assert app.config['JWT_SECRET_KEY'] == 'test-jwt-456'
        
        # 清理环境变量
        del os.environ['SECRET_KEY']
        del os.environ['JWT_SECRET_KEY'] 
        del os.environ['DATABASE_URL']


class TestAppCreation:
    """测试应用创建"""
    
    def test_app_creation(self):
        """测试应用实例创建"""
        app = create_app()
        
        assert app is not None
        assert app.name == 'app'
        assert 'db' in app.extensions
        assert 'jwt' in app.extensions
    
    def test_app_routes_registration(self):
        """测试路由注册"""
        app = create_app()
        
        # 检查基本路由
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            data = response.get_json()
            assert data['msg'] == 'Flask auth backend is running'
    
    def test_blueprints_registration(self):
        """测试蓝图注册"""
        app = create_app()
        
        # 检查已注册的蓝图
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        expected_blueprints = [
            'auth', 'supply', 'catalog', 'enterprise', 
            'admin', 'orders', 'inventory_warning', 'circulation'
        ]
        
        for blueprint in expected_blueprints:
            assert blueprint in blueprint_names
    
    def test_cors_configuration(self):
        """测试CORS配置"""
        app = create_app()
        
        with app.test_client() as client:
            # 测试OPTIONS请求
            response = client.options('/', headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET'
            })
            
            # CORS应该允许来自localhost:5173的请求
            assert response.status_code in [200, 204]
    
    def test_database_initialization(self):
        """测试数据库初始化"""
        os.environ['FLASK_ENV'] = 'testing'
        app = create_app()
        
        with app.app_context():
            # 检查数据库连接
            from extensions import db
            assert db.engine is not None
            
            # 检查是否可以创建表
            db.create_all()
            
            # 验证表已创建
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert len(tables) > 0


class TestEnvironmentDetection:
    """测试环境检测功能"""
    
    def test_default_environment_is_development(self):
        """测试默认环境是开发环境"""
        # 清除环境变量
        if 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
        
        app = create_app()
        assert app.config['DEBUG'] is True
    
    def test_production_environment_detection(self):
        """测试生产环境检测"""
        os.environ['FLASK_ENV'] = 'production'
        
        app = create_app()
        assert app.config['DEBUG'] is False
        
        # 清理
        del os.environ['FLASK_ENV']
    
    def test_testing_environment_detection(self):
        """测试测试环境检测"""
        os.environ['FLASK_ENV'] = 'testing'
        
        app = create_app()
        assert app.config['TESTING'] is True
        
        # 清理
        del os.environ['FLASK_ENV']


class TestDatabasePath:
    """测试数据库路径配置"""
    
    def test_development_database_path(self):
        """测试开发环境数据库路径"""
        os.environ['FLASK_ENV'] = 'development'
        app = create_app()
        
        # 开发环境应使用相对路径
        assert 'sqlite:///data.db' in app.config['SQLALCHEMY_DATABASE_URI']
        
        del os.environ['FLASK_ENV']
    
    def test_production_database_path(self):
        """测试生产环境数据库路径"""
        os.environ['FLASK_ENV'] = 'production'
        app = create_app()
        
        # 生产环境应使用绝对路径
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        assert 'sqlite:////var/www/SH-Drug-Mgmt/backend/data.db' in db_uri
        
        del os.environ['FLASK_ENV']
    
    def test_custom_database_url_from_env(self):
        """测试从环境变量自定义数据库URL"""
        custom_db_url = 'sqlite:///custom_test.db'
        os.environ['DATABASE_URL'] = custom_db_url
        
        app = create_app()
        assert app.config['SQLALCHEMY_DATABASE_URI'] == custom_db_url
        
        del os.environ['DATABASE_URL']


if __name__ == '__main__':
    pytest.main([__file__])