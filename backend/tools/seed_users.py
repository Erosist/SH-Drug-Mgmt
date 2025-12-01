#!/usr/bin/env python3
"""
本地开发用脚本：在当前后端数据库中确保存在 admin 与 regulator 测试账户。

用法：
  cd backend
  python tools/seed_users.py

可通过环境变量覆盖默认凭据：
  SEED_ADMIN_USER SEED_ADMIN_PASS SEED_REGULATOR_USER SEED_REGULATOR_PASS

脚本会把项目根目录（backend 的上级）加入 `sys.path`，以便正确导入应用工厂和扩展。
"""
import os
import sys
from pathlib import Path

# 确保项目根路径在 sys.path 中
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from app import create_app
    from extensions import db
    from models import User
except Exception as e:
    print('导入应用失败，请在 backend 目录下运行本脚本，且确保已安装依赖。错误：', e)
    raise


def ensure_user(username, email, role, password, is_authenticated=True):
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"user `{username}` already exists (id={existing.id}, role={existing.role})")
        return existing

    user = User(
        username=username,
        email=email,
        phone=None,
        role=role,
        is_authenticated=bool(is_authenticated),
        is_active=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"created user `{username}` with role `{role}` (id={user.id})")
    return user


def seed():
    app = create_app()
    with app.app_context():
        admin_user = os.environ.get('SEED_ADMIN_USER', 'admin')
        admin_pass = os.environ.get('SEED_ADMIN_PASS', 'AdminPass123!')
        admin_email = os.environ.get('SEED_ADMIN_EMAIL', 'admin@example.test')

        regulator_user = os.environ.get('SEED_REGULATOR_USER', 'regulator')
        regulator_pass = os.environ.get('SEED_REGULATOR_PASS', 'RegulatorPass123!')
        regulator_email = os.environ.get('SEED_REGULATOR_EMAIL', 'regulator@example.test')

        print('Seeding users...')
        ensure_user(admin_user, admin_email, 'admin', admin_pass, is_authenticated=True)
        ensure_user(regulator_user, regulator_email, 'regulator', regulator_pass, is_authenticated=True)
        print('Seeding complete.')


if __name__ == '__main__':
    seed()
