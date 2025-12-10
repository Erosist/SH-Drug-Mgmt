#!/usr/bin/env python3
"""
查询数据库中现有的 tenant IDs
"""

import sys
from pathlib import Path

# 确保可以导入项目模块
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import Tenant

def check_tenant_ids():
    """查询现有的 tenant IDs"""
    app = create_app()
    
    with app.app_context():
        tenants = Tenant.query.order_by(Tenant.id).all()
        
        print(f"\n数据库中现有 {len(tenants)} 条 tenant 记录:")
        print("=" * 80)
        
        for tenant in tenants:
            print(f"ID: {tenant.id:3d} | 类型: {tenant.type:10s} | 名称: {tenant.name}")
        
        print("=" * 80)
        if tenants:
            print(f"最小 ID: {tenants[0].id}")
            print(f"最大 ID: {tenants[-1].id}")

if __name__ == '__main__':
    check_tenant_ids()
