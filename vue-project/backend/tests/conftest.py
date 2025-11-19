"""
测试配置文件
提供测试所需的配置和fixture
"""
import pytest
import os
import sys
from flask import Flask

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from extensions import db

class TestingConfig(object):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用内存数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope='session')
def app():
    """创建测试应用实例"""
    app = create_app(TestingConfig)

    with app.app_context():
        # 创建数据库表
        db.create_all()

        # 可以在这里添加测试数据
        yield app

        # 清理数据库
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """创建CLI测试runner"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def db_session(app):
    """创建数据库会话"""
    with app.app_context():
        # 开始事务
        db.session.begin()
        yield db.session
        # 回滚事务，确保测试之间的数据隔离
        db.session.rollback()
