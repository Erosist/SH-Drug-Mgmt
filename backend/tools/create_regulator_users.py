#!/usr/bin/env python3
"""
创建监管者账号脚本

在数据库中创建两个监管者（regulator）角色的用户账号。

用法：
  cd backend
  python tools/create_regulator_users.py
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


def create_regulator_user(username, email, real_name, password):
    """创建监管者用户"""
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"用户 `{username}` 已存在 (id={existing.id}, role={existing.role})")
        return existing

    user = User(
        username=username,
        email=email,
        phone=None,
        real_name=real_name,
        role='regulator',
        is_authenticated=True,
        is_active=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"✓ 创建监管者用户 `{username}` (id={user.id}, 姓名={real_name})")
    return user


def main():
    app = create_app()
    with app.app_context():
        print('开始创建监管者账号...\n')
        
        # 监管者账号1
        create_regulator_user(
            username='regulator01',
            email='regulator01@sh-drug-mgmt.com',
            real_name='张监管',
            password='Regulator123!'
        )
        
        # 监管者账号2
        create_regulator_user(
            username='regulator02',
            email='regulator02@sh-drug-mgmt.com',
            real_name='李监管',
            password='Regulator123!'
        )
        
        print('\n监管者账号创建完成！')
        print('=' * 60)
        print('账号信息：')
        print('  账号1: regulator01 / Regulator123!  (姓名: 张监管)')
        print('  账号2: regulator02 / Regulator123!  (姓名: 李监管)')
        print('=' * 60)


if __name__ == '__main__':
    main()
