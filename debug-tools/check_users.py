#!/usr/bin/env python3
"""
检查用户账号和密码
"""
import sys
sys.path.append('backend')

from app import create_app, db
from models import User, Tenant
from config import Config

def check_users():
    """检查用户账号"""
    print("=== 检查用户账号 ===")
    
    app = create_app(Config)
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"用户: {user.username}, 角色: {user.role}, 租户ID: {user.tenant_id}")
            
        print(f"\n尝试验证pharmacy_dev用户密码...")
        user = User.query.filter_by(username='pharmacy_dev').first()
        if user:
            print(f"用户存在: {user.username}")
            # 尝试不同的密码
            passwords = ['123456', 'password', 'pharmacy_dev', '123', '111111']
            for pwd in passwords:
                if user.check_password(pwd):
                    print(f"✓ 正确密码是: {pwd}")
                    break
                else:
                    print(f"✗ 密码 {pwd} 错误")
        else:
            print("pharmacy_dev用户不存在")
            
        print(f"\n尝试验证supplier_dev用户密码...")
        user = User.query.filter_by(username='supplier_dev').first()
        if user:
            print(f"用户存在: {user.username}")
            # 尝试不同的密码
            passwords = ['123456', 'password', 'supplier_dev', '123', '111111']
            for pwd in passwords:
                if user.check_password(pwd):
                    print(f"✓ 正确密码是: {pwd}")
                    break
                else:
                    print(f"✗ 密码 {pwd} 错误")
        else:
            print("supplier_dev用户不存在")

if __name__ == "__main__":
    check_users()
