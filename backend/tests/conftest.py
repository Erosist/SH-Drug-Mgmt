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

        # 添加测试数据
        from models import User, Tenant, Drug, SupplyInfo
        from werkzeug.security import generate_password_hash
        from datetime import date, datetime

        # 创建测试租户
        test_pharmacy = Tenant(
            name='测试药店',
            type='PHARMACY',
            unified_social_credit_code='TEST_PHARMACY_001',
            legal_representative='测试负责人',
            contact_person='测试联系人',
            contact_phone='13800000001',
            contact_email='test@pharmacy.com',
            address='测试地址',
            business_scope='测试业务范围'
        )
        
        test_supplier = Tenant(
            name='测试供应商',
            type='SUPPLIER',
            unified_social_credit_code='TEST_SUPPLIER_001',
            legal_representative='测试供应商负责人',
            contact_person='测试供应商联系人',
            contact_phone='13800000002',
            contact_email='test@supplier.com',
            address='测试供应商地址',
            business_scope='药品供应'
        )

        db.session.add(test_pharmacy)
        db.session.add(test_supplier)
        db.session.commit()

        # 创建测试用户
        test_user = User(
            username='testuser',
            password_hash=generate_password_hash('password123'),
            email='test@example.com',
            phone='13800000000',
            role='pharmacy',
            tenant_id=test_pharmacy.id,
            is_active=True,
            is_authenticated=True
        )
        
        test_admin = User(
            username='testadmin',
            password_hash=generate_password_hash('admin123'),
            email='admin@example.com',
            phone='13800000003',
            role='admin',
            tenant_id=None,
            is_active=True,
            is_authenticated=True
        )

        db.session.add(test_user)
        db.session.add(test_admin)
        db.session.commit()

        # 创建测试药品
        test_drug = Drug(
            generic_name='测试药品',
            brand_name='测试品牌',
            manufacturer='测试制造商',
            specification='1mg',
            dosage_form='片剂',
            prescription_type='处方药',
            approval_number='TEST123456',
            category='测试类别'
        )
        
        db.session.add(test_drug)
        db.session.commit()

        # 创建测试供应信息
        test_supply_info = SupplyInfo(
            tenant_id=test_supplier.id,
            drug_id=test_drug.id,
            unit_price=10.50,
            available_quantity=1000,
            min_order_quantity=100,
            valid_until=date(2025, 12, 31),
            status='ACTIVE',
            description='测试供应信息'
        )
        
        db.session.add(test_supply_info)
        db.session.commit()

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
