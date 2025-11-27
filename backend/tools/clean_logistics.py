#!/usr/bin/env python3
"""
删除现有物流公司并重新创建
"""
import sys
sys.path.append('backend')

from app import create_app, db
from models import User, Tenant
from config import Config

def clean_and_recreate_logistics():
    """删除现有物流公司并重新创建"""
    print("=== 清理并重新创建物流公司 ===")
    
    app = create_app(Config)
    with app.app_context():
        # 删除现有的物流用户和租户
        print("删除现有物流公司...")
        
        # 删除物流用户
        logistics_users = User.query.filter_by(role='logistics').all()
        for user in logistics_users:
            print(f"删除物流用户: {user.username}")
            db.session.delete(user)
        
        # 删除物流租户
        logistics_tenants = Tenant.query.filter_by(type='LOGISTICS').all()
        for tenant in logistics_tenants:
            print(f"删除物流租户: {tenant.name}")
            db.session.delete(tenant)
        
        db.session.commit()
        print("✓ 清理完成")

if __name__ == "__main__":
    clean_and_recreate_logistics()
