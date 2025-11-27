#!/usr/bin/env python3
import jwt
import json

# 解析 localStorage 中的 token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6Ind0X3Rlc3QxIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NjM2NDA4MDh9.KDO8TlZGXcQvbR2jp6TATHTbCg6W5mCBcpKgh1JsOAc'

try:
    # 不验证签名，只解码 payload
    decoded = jwt.decode(token, options={'verify_signature': False})
    print('Token 解析结果:')
    print(json.dumps(decoded, indent=2))
    print()
    
    # 检查用户信息
    user_id = decoded.get('user_id')
    print(f'Token 中的用户ID: {user_id}')
    print(f'Token 中的用户名: {decoded.get("username")}')
    print(f'Token 中的角色: {decoded.get("role")}')
    
except Exception as e:
    print(f'Token 解析失败: {e}')

# 再检查一下正确的物流用户
print('\n=== 数据库中的物流用户 ===')
from app import create_app
from models import User, Tenant
from extensions import db

app = create_app()
with app.app_context():
    # 查找 sfexpress 用户
    sfexpress_user = User.query.filter_by(username='sfexpress').first()
    if sfexpress_user:
        print(f'sfexpress 用户ID: {sfexpress_user.id}')
        print(f'sfexpress 角色: {sfexpress_user.role}')
        print(f'sfexpress 租户: {sfexpress_user.tenant.name}')
    else:
        print('sfexpress 用户不存在!')
        
    # 查找 user_id=4 的用户
    user_4 = User.query.get(4)
    if user_4:
        print(f'\nuser_id=4 的用户信息:')
        print(f'用户名: {user_4.username}')
        print(f'角色: {user_4.role}')
        print(f'租户: {user_4.tenant.name if user_4.tenant else "无"}')
