#!/usr/bin/env python3
"""
在开发环境下创建预置用户脚本：
- 管理员用户（role='admin'）
- 物流公司租户和对应的物流用户（role='logistics'）

用法示例：
python backend/scripts/create_dev_users.py \
  --admin-username admin --admin-email admin@example.com --admin-password Admin1234 \
  --logistics-username logistics_dev --logistics-email logistics@example.com --logistics-password Logistics1234 \
  --logistics-company "Logistics Co" --logistics-uscc LOG123456
"""
import argparse
import sys
import os
from datetime import datetime

# Ensure parent directory (project backend root) is on sys.path so imports like `from app import create_app`
# work when this script is executed from the `backend` directory: e.g.
#   python scripts/create_dev_users.py
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create admin and logistics dev users')
    parser.add_argument('--admin-username', default='admin')
    parser.add_argument('--admin-email', default='admin@example.com')
    parser.add_argument('--admin-password', default='Admin1234')

    parser.add_argument('--logistics-username', default='logistics_dev')
    parser.add_argument('--logistics-email', default='logistics@example.com')
    parser.add_argument('--logistics-password', default='Logistics1234')
    parser.add_argument('--logistics-company', default='Logistics Co')
    parser.add_argument('--logistics-uscc', default='LOGISTICS-DEV-0001')
    
    # pharmacy (药店) 用户与租户
    parser.add_argument('--pharmacy-username', default='pharmacy_dev')
    parser.add_argument('--pharmacy-email', default='pharmacy@example.com')
    parser.add_argument('--pharmacy-password', default='Pharmacy1234')
    parser.add_argument('--pharmacy-company', default='Pharmacy Co')
    parser.add_argument('--pharmacy-uscc', default='PHARMACY-DEV-0001')

    args = parser.parse_args(argv)

    app = create_app()

    with app.app_context():
        try:
            from extensions import db
            from models import User, Tenant
        except Exception as e:
            print('导入项目模块失败，请确保在项目环境中运行本脚本：', e)
            sys.exit(2)

        created = []
        created_usernames = []

        # 创建管理员用户（如果不存在）
        admin = User.query.filter((User.username == args.admin_username) | (User.email == args.admin_email)).first()
        if admin:
            print(f"管理员用户已存在：username={admin.username}, email={admin.email}")
        else:
            admin = User(
                username=args.admin_username,
                email=args.admin_email,
                role='admin',
                is_authenticated=True,
                is_active=True,
            )
            admin.set_password(args.admin_password)
            db.session.add(admin)
            db.session.flush()
            created.append(('admin_user', admin.username))
            created_usernames.append(admin.username)
            print(f"已创建管理员用户: {admin.username} (id={admin.id})")

        # 创建物流租户（Tenant）和对应用户
        tenant = Tenant.query.filter_by(unified_social_credit_code=args.logistics_uscc).first()
        if tenant:
            print(f"物流租户已存在：{tenant.name} (id={tenant.id})")
        else:
            # Tenant 字段较多，尽量填充必需字段
            tenant = Tenant(
                name=args.logistics_company,
                type='LOGISTICS',
                unified_social_credit_code=args.logistics_uscc,
                legal_representative=args.logistics_company,
                contact_person=args.logistics_company,
                contact_phone='00000000000',
                contact_email=args.logistics_email,
                address='开发环境地址',
                business_scope='物流配送',
                is_active=True,
                latitude=None,
                longitude=None,
                created_at=datetime.utcnow(),
            )
            db.session.add(tenant)
            db.session.flush()
            created.append(('tenant', tenant.name))
            print(f"已创建物流租户: {tenant.name} (id={tenant.id})")

        # 创建物流用户
        logistics_user = User.query.filter((User.username == args.logistics_username) | (User.email == args.logistics_email)).first()
        if logistics_user:
            print(f"物流用户已存在：username={logistics_user.username}, email={logistics_user.email}")
        else:
            logistics_user = User(
                username=args.logistics_username,
                email=args.logistics_email,
                role='logistics',
                tenant_id=tenant.id if tenant else None,
                company_name=args.logistics_company,
                is_authenticated=False,
                is_active=True,
            )
            logistics_user.set_password(args.logistics_password)
            db.session.add(logistics_user)
            db.session.flush()
            created.append(('logistics_user', logistics_user.username))
            created_usernames.append(logistics_user.username)
            print(f"已创建物流用户: {logistics_user.username} (id={logistics_user.id})")

        # --- 创建药店租户与用户 ---
        pharmacy_tenant = None
        try:
            pharmacy_tenant = Tenant.query.filter_by(unified_social_credit_code=args.pharmacy_uscc).first()
        except Exception:
            pharmacy_tenant = None

        if pharmacy_tenant:
            print(f"药店租户已存在：{pharmacy_tenant.name} (id={pharmacy_tenant.id})")
        else:
            pharmacy_tenant = Tenant(
                name=args.pharmacy_company,
                type='PHARMACY',
                unified_social_credit_code=args.pharmacy_uscc,
                legal_representative=args.pharmacy_company,
                contact_person=args.pharmacy_company,
                contact_phone='00000000000',
                contact_email=args.pharmacy_email,
                address='开发环境地址',
                business_scope='零售药品',
                is_active=True,
                latitude=None,
                longitude=None,
                created_at=datetime.utcnow(),
            )
            db.session.add(pharmacy_tenant)
            db.session.flush()
            created.append(('tenant_pharmacy', pharmacy_tenant.name))
            print(f"已创建药店租户: {pharmacy_tenant.name} (id={pharmacy_tenant.id})")

        pharmacy_user = User.query.filter((User.username == args.pharmacy_username) | (User.email == args.pharmacy_email)).first()
        if pharmacy_user:
            print(f"药店用户已存在：username={pharmacy_user.username}, email={pharmacy_user.email}")
        else:
            pharmacy_user = User(
                username=args.pharmacy_username,
                email=args.pharmacy_email,
                role='pharmacy',
                tenant_id=pharmacy_tenant.id if pharmacy_tenant else None,
                company_name=args.pharmacy_company,
                is_authenticated=False,
                is_active=True,
            )
            pharmacy_user.set_password(args.pharmacy_password)
            db.session.add(pharmacy_user)
            db.session.flush()
            created.append(('pharmacy_user', pharmacy_user.username))
            created_usernames.append(pharmacy_user.username)
            print(f"已创建药店用户: {pharmacy_user.username} (id={pharmacy_user.id})")

        if created:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('提交数据库时发生错误，已回滚：', e)
                sys.exit(3)
        # 打印所有新创建用户的完整信息
        print('\n完成。已创建/确认项：')
        for kind, name in created:
            print(f' - {kind}: {name}')

        if created_usernames:
            print('\n新创建的用户详情：')
            try:
                import json
                users = User.query.filter(User.username.in_(created_usernames)).all()
                for u in users:
                    print(json.dumps(u.to_dict(include_relations=True), ensure_ascii=False, indent=2))
            except Exception as e:
                print('无法查询新创建用户详情：', e)


if __name__ == '__main__':
    main()
