#!/usr/bin/env python3
from app import create_app
from models import User, Tenant
from extensions import db

app = create_app()
with app.app_context():
    # 检查物流公司用户
    logistics_users = User.query.join(Tenant).filter(Tenant.type == 'LOGISTICS').all()
    print('=== 物流公司用户列表 ===')
    for user in logistics_users:
        print(f'用户名: {user.username}')
        print(f'角色: {user.role}')
        print(f'租户: {user.tenant.name} (ID: {user.tenant_id})')
        print(f'租户类型: {user.tenant.type}')
        print('---')
    
    # 检查当前登录的用户
    problem_user = User.query.filter_by(username='wt_test1').first()
    if problem_user:
        print('=== 当前登录用户信息 ===')
        print(f'用户名: {problem_user.username}')
        print(f'角色: {problem_user.role}')
        print(f'租户: {problem_user.tenant.name if problem_user.tenant else "无"}')
        print(f'租户类型: {problem_user.tenant.type if problem_user.tenant else "无"}')
    else:
        print('用户 wt_test1 不存在')
        
    # 列出正确的物流登录凭据
    print('\n=== 物流公司登录凭据 ===')
    logistics_tenants = Tenant.query.filter_by(type='LOGISTICS').all()
    for tenant in logistics_tenants:
        user = User.query.filter_by(tenant_id=tenant.id).first()
        if user:
            print(f'{tenant.name}: 用户名={user.username}, 密码=sf123456')
