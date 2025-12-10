#!/usr/bin/env python3
"""
检查库存数据的 tenant_id 分布
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import User, InventoryItem, Tenant
from sqlalchemy import func

app = create_app()

with app.app_context():
    # 检查 supplier_66
    user = User.query.filter_by(username='supplier_66').first()
    print(f"用户: {user.username}")
    print(f"Tenant ID: {user.tenant_id}")
    print(f"企业名称: {user.company_name}")
    
    tenant = Tenant.query.get(user.tenant_id)
    print(f"企业类型: {tenant.type}")
    
    inventory_count = InventoryItem.query.filter_by(tenant_id=user.tenant_id).count()
    print(f"该企业的库存数量: {inventory_count}")
    
    print("\n所有库存数据的 tenant_id 分布:")
    result = db.session.query(
        InventoryItem.tenant_id, 
        func.count(InventoryItem.id)
    ).group_by(InventoryItem.tenant_id).all()
    
    for tid, count in result[:15]:
        t = Tenant.query.get(tid)
        print(f"  Tenant {tid:2d} ({t.type:10s}): {count:4d} 条 - {t.name}")
    
    print(f"\n总库存记录: {InventoryItem.query.count()} 条")
