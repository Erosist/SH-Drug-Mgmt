#!/usr/bin/env python3
"""
在开发环境下创建或确认一个供应商账户（及可选的租户）。

用法示例：
python backend/scripts/create_dev_supplier.py \
  --username supplier_dev --email supplier@example.com --password Supplier1234 \
  --company "Supplier Co" --uscc SUPPLIER-DEV-0001

脚本会：
- 在项目上下文中导入并使用数据库模型（User, Tenant）
- 如果指定的租户（by uscc）不存在则创建
- 如果用户名或邮箱已存在则输出已存在信息并退出
- 创建用户、设置密码并提交，最后打印出用户名和密码（仅供开发用途）
"""
import argparse
import sys
import os
import json
import secrets
import string
from datetime import datetime

# 确保 backend 目录在 sys.path 中，以便可以导入项目模块
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app


def gen_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create or ensure a supplier user and tenant (dev only)')
    parser.add_argument('--username', default='supplier_dev11')
    parser.add_argument('--email', default='supplier1@example.com')
    parser.add_argument('--password', help='如果不提供则随机生成')
    parser.add_argument('--company', default='Supplier Co')
    parser.add_argument('--uscc', default='SUPPLIER-DEV-0001')
    parser.add_argument('--no-tenant', action='store_true', help='只创建用户，不创建/查找租户')

    args = parser.parse_args(argv)

    # 生成随机密码（仅当未提供时）
    password = args.password or gen_password()

    app = create_app()

    with app.app_context():
        try:
            from extensions import db
            from models import User, Tenant
        except Exception as e:
            print('导入项目模块失败，请在项目环境中运行本脚本：', e)
            sys.exit(2)

        # 按用户要求：不要检测是否存在用户，直接创建一个新的账号。
        # 注意：如果数据库对 username/email 有唯一约束，提交时可能抛出 IntegrityError 并回滚。

        tenant = None
        if not args.no_tenant:
            # 查找或创建租户
            tenant = Tenant.query.filter_by(unified_social_credit_code=args.uscc).first()
            if tenant:
                print(f"找到已存在租户：{tenant.name} (id={tenant.id})")
            else:
                tenant = Tenant(
                    name=args.company,
                    type='SUPPLIER',
                    unified_social_credit_code=args.uscc,
                    legal_representative=args.company,
                    contact_person=args.company,
                    contact_phone='00000000000',
                    contact_email=args.email,
                    address='开发环境地址',
                    business_scope='供应',
                    is_active=True,
                    latitude=None,
                    longitude=None,
                    created_at=datetime.utcnow(),
                )
                db.session.add(tenant)
                db.session.flush()
                print(f"已创建租户: {tenant.name} (id={tenant.id})")

        # 创建供应商用户
        user = User(
            username=args.username,
            email=args.email,
            role='supplier',
            tenant_id=tenant.id if tenant else None,
            company_name=args.company,
            is_authenticated=False,
            is_active=True,
        )
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('提交数据库时发生错误，已回滚：', e)
            sys.exit(3)

        print('\n已创建供应商用户（开发环境）：')
        print(f'  username: {user.username}')
        print(f'  password: {password}  # 明文密码，仅供开发环境使用')
        print(f'  id: {user.id}')
        print(f'  tenant_id: {user.tenant_id}')

        # 尝试打印用户详情（to_dict）
        try:
            print('\n用户详情:')
            print(json.dumps(user.to_dict(include_relations=True), ensure_ascii=False, indent=2))
        except Exception:
            pass


if __name__ == '__main__':
    main()
