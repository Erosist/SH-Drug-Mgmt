#!/usr/bin/env python3
import jwt
import json

# 解析新的正确 token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDIzOTgyNCwianRpIjoiM2Y4OGE0ZjktYjRjNi00NjhjLWE1NTUtYWMxYTRiN2FmYWY2IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjE5IiwibmJmIjoxNzY0MjM5ODI0LCJjc3JmIjoiYTVlOGEwOWQtZDc4Yi00ODNhLWJlZjgtN2ZkMGY0ZDcwNzFiIiwiZXhwIjoxNzY0MjQ3MDI0fQ.c-3xOaQ6Ghn7fAF6Q4spW5c5oLp9oK9EvghHMsCMlSk'

try:
    # 不验证签名，只解码 payload
    decoded = jwt.decode(token, options={'verify_signature': False})
    print('新 Token 解析结果:')
    print(json.dumps(decoded, indent=2))
    print()
    
    user_id = decoded.get('sub')  # Flask-JWT-Extended 使用 'sub' 字段
    print(f'Token 中的用户ID: {user_id}')
    
except Exception as e:
    print(f'Token 解析失败: {e}')

# 检查数据库中用户ID=19的信息
print('\n=== 检查数据库中用户ID=19的信息 ===')
from app import create_app
from models import User, Tenant
from extensions import db

app = create_app()
with app.app_context():
    # 查找用户ID=19
    user_19 = User.query.get(19)
    if user_19:
        print(f'用户ID: {user_19.id}')
        print(f'用户名: {user_19.username}')
        print(f'角色: {user_19.role}')
        print(f'租户ID: {user_19.tenant_id}')
        print(f'租户名称: {user_19.tenant.name if user_19.tenant else "无"}')
        print(f'租户类型: {user_19.tenant.type if user_19.tenant else "无"}')
    else:
        print('用户ID=19不存在!')
