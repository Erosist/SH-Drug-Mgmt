#!/usr/bin/env python3
"""
创建开发环境用户账户
包含管理员和药店用户账户，方便开发测试
"""
from pathlib import Path
import sys

# Ensure backend folder is on sys.path so local imports (app, models) work
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from models import db, User, Tenant
from werkzeug.security import generate_password_hash

def create_dev_users():
    """创建开发环境用户"""
    app = create_app()
    with app.app_context():
        print("=== 创建开发环境用户账户 ===")
        
        # 1. 创建管理员账户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@dev.com',
                phone='13800000000',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True,
                tenant_id=None  # 管理员不需要关联企业
            )
            db.session.add(admin_user)
            print("✅ 创建管理员账户: admin / admin123")
        else:
            print("⚠️ 管理员账户已存在")
        
        # 2. 创建开发用药店企业
        dev_pharmacy = Tenant.query.filter_by(name='开发测试药店').first()
        if not dev_pharmacy:
            dev_pharmacy = Tenant(
                name='开发测试药店',
                type='PHARMACY',
                unified_social_credit_code='91310000DEV00001X',
                legal_representative='开发者',
                contact_person='开发测试',
                contact_phone='13800001111',
                contact_email='dev@pharmacy.com',
                address='上海市开发区测试路100号',
                business_scope='药品零售、医疗服务',
                is_active=True
            )
            db.session.add(dev_pharmacy)
            db.session.flush()  # 获取ID
            print("✅ 创建开发测试药店企业")
        else:
            print("⚠️ 开发测试药店企业已存在")
        
        # 3. 创建药店用户账户
        pharmacy_dev_user = User.query.filter_by(username='pharmacy_dev').first()
        if not pharmacy_dev_user:
            pharmacy_dev_user = User(
                username='pharmacy_dev',
                email='pharmacy_dev@test.com',
                phone='13800001111',
                password_hash=generate_password_hash('pharmacy123'),
                role='pharmacy',
                is_active=True,
                tenant_id=dev_pharmacy.id
            )
            db.session.add(pharmacy_dev_user)
            print("✅ 创建药店用户账户: pharmacy_dev / pharmacy123")
        else:
            print("⚠️ 药店用户账户已存在")
        
        # 4. 创建开发用供应商企业
        dev_supplier = Tenant.query.filter_by(name='开发测试供应商').first()
        if not dev_supplier:
            dev_supplier = Tenant(
                name='开发测试供应商',
                type='SUPPLIER',
                unified_social_credit_code='91310000DEV00002Y',
                legal_representative='供应商负责人',
                contact_person='供应测试',
                contact_phone='13800002222',
                contact_email='dev@supplier.com',
                address='上海市开发区供应路200号',
                business_scope='药品批发、医疗器械销售',
                is_active=True
            )
            db.session.add(dev_supplier)
            db.session.flush()  # 获取ID
            print("✅ 创建开发测试供应商企业")
        else:
            print("⚠️ 开发测试供应商企业已存在")
        
        # 5. 创建供应商用户账户
        supplier_dev_user = User.query.filter_by(username='supplier_dev').first()
        if not supplier_dev_user:
            supplier_dev_user = User(
                username='supplier_dev',
                email='supplier_dev@test.com',
                phone='13800002222',
                password_hash=generate_password_hash('supplier123'),
                role='supplier',
                is_active=True,
                tenant_id=dev_supplier.id
            )
            db.session.add(supplier_dev_user)
            print("✅ 创建供应商用户账户: supplier_dev / supplier123")
        else:
            print("⚠️ 供应商用户账户已存在")
        
        # 提交所有更改
        try:
            db.session.commit()
            print("\n🎉 开发环境用户创建完成！")
            print("\n📋 可用账户列表：")
            print("1. 管理员账户：admin / admin123 (无企业关联)")
            print("2. 药店用户：pharmacy_dev / pharmacy123 (关联开发测试药店)")
            print("3. 供应商用户：supplier_dev / supplier123 (关联开发测试供应商)")
            print("4. 原有药店用户：pharmacy1 / password123 (关联仁济医院药房)")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建用户失败: {e}")

if __name__ == "__main__":
    create_dev_users()
