#!/usr/bin/env python3
"""
创建物流公司用户和租户数据
"""
import sys
sys.path.append('backend')

from app import create_app, db
from models import User, Tenant
from config import Config
from werkzeug.security import generate_password_hash

def create_logistics_companies():
    """创建物流公司用户和租户"""
    print("=== 创建物流公司用户 ===")
    
    app = create_app(Config)
    with app.app_context():
        # 检查是否已存在物流租户
        existing_logistics = Tenant.query.filter_by(type='LOGISTICS').all()
        if existing_logistics:
            print(f"已存在 {len(existing_logistics)} 个物流公司，跳过创建")
            for logistics in existing_logistics:
                print(f"  - {logistics.name} (ID: {logistics.id})")
            return
        
        # 创建物流公司租户
        logistics_companies = [
            {
                'name': '顺丰速运',
                'username': 'sfexpress',
                'password': 'sf123456',
                'unified_social_credit_code': '91440300708461136X',
                'legal_representative': '王卫',
                'contact_person': '张经理',
                'contact_phone': '400-811-1111',
                'contact_email': 'service@sf-express.com',
                'address': '深圳市福田区福年广场A座',
                'business_scope': '快递服务、物流配送、仓储管理'
            },
            {
                'name': '申通快递',
                'username': 'stoexpress',
                'password': 'sto123456',
                'unified_social_credit_code': '91310000631203303F',
                'legal_representative': '陈德军',
                'contact_person': '李经理',
                'contact_phone': '95543',
                'contact_email': 'service@sto.cn',
                'address': '上海市青浦区华新镇华志路1685号',
                'business_scope': '快递服务、物流配送、供应链管理'
            },
            {
                'name': '圆通速递',
                'username': 'ytoexpress',
                'password': 'yto123456',
                'unified_social_credit_code': '91310000132306681L',
                'legal_representative': '喻渭蛟',
                'contact_person': '王经理',
                'contact_phone': '95554',
                'contact_email': 'service@yto.net.cn',
                'address': '上海市青浦区华新镇中心路1号',
                'business_scope': '快递服务、物流配送、电商物流'
            },
            {
                'name': '中通快递',
                'username': 'ztoexpress',
                'password': 'zto123456',
                'unified_social_credit_code': '91330000553108341D',
                'legal_representative': '赖梅松',
                'contact_person': '赵经理',
                'contact_phone': '95311',
                'contact_email': 'service@zto.com',
                'address': '上海市青浦区华新镇华志路1999号',
                'business_scope': '快递服务、物流配送、仓储服务'
            }
        ]
        
        created_tenants = []
        for company_data in logistics_companies:
            # 创建租户
            tenant = Tenant(
                name=company_data['name'],
                type='LOGISTICS',
                unified_social_credit_code=company_data['unified_social_credit_code'],
                legal_representative=company_data['legal_representative'],
                contact_person=company_data['contact_person'],
                contact_phone=company_data['contact_phone'],
                contact_email=company_data['contact_email'],
                address=company_data['address'],
                business_scope=company_data['business_scope'],
                is_active=True
            )
            
            db.session.add(tenant)
            db.session.flush()  # 获取tenant.id
            created_tenants.append(tenant)
            
            # 创建对应的用户账号
            username = company_data['username']
            password = company_data['password']
            user = User(
                username=username,
                email=company_data['contact_email'],
                phone=company_data['contact_phone'],
                real_name=company_data['contact_person'],
                company_name=company_data['name'],
                password_hash=generate_password_hash(password),
                role='logistics',
                tenant_id=tenant.id,
                is_authenticated=True,
                is_active=True
            )
            
            db.session.add(user)
            
            print(f"创建物流公司: {company_data['name']}")
            print(f"  租户ID: {tenant.id}")
            print(f"  用户名: {username}")
            print(f"  密码: {password}")
            print(f"  联系人: {company_data['contact_person']}")
            print()
        
        # 提交所有更改
        db.session.commit()
        
        print(f"✓ 成功创建了 {len(created_tenants)} 个物流公司")
        
        # 验证创建结果
        print("\n=== 验证创建结果 ===")
        all_logistics_users = User.query.filter_by(role='logistics').all()
        for user in all_logistics_users:
            tenant = Tenant.query.get(user.tenant_id)
            print(f"用户: {user.username}, 公司: {tenant.name if tenant else '未知'}")

if __name__ == "__main__":
    create_logistics_companies()
