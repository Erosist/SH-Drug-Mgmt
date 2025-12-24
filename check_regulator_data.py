"""
检查监管API和数据库数据
"""
import sys
sys.path.insert(0, 'backend')

from backend.app import create_app
from backend.extensions import db
from backend.models import Tenant, User, SupplyInfo, Order, Drug

app = create_app()

with app.app_context():
    print("=" * 60)
    print("数据库数据统计")
    print("=" * 60)
    
    # 统计企业
    total_tenants = Tenant.query.count()
    print(f"\n📊 企业总数: {total_tenants}")
    
    if total_tenants > 0:
        tenants_by_type = db.session.query(
            Tenant.type,
            db.func.count(Tenant.id)
        ).group_by(Tenant.type).all()
        
        print("企业类型分布:")
        for tenant_type, count in tenants_by_type:
            print(f"  - {tenant_type}: {count}")
        
        print("\n前5个企业:")
        for tenant in Tenant.query.limit(5).all():
            print(f"  - ID:{tenant.id} | {tenant.name} | {tenant.type}")
    
    # 统计用户
    total_users = User.query.count()
    print(f"\n👥 用户总数: {total_users}")
    
    if total_users > 0:
        users_by_role = db.session.query(
            User.role,
            db.func.count(User.id)
        ).group_by(User.role).all()
        
        print("用户角色分布:")
        for role, count in users_by_role:
            print(f"  - {role}: {count}")
        
        # 查找监管用户
        regulators = User.query.filter_by(role='regulator').all()
        print(f"\n监管用户列表 ({len(regulators)}):")
        for user in regulators:
            print(f"  - ID:{user.id} | {user.username} | {user.email}")
    
    # 统计库存
    total_supply = SupplyInfo.query.count()
    print(f"\n📦 库存记录总数: {total_supply}")
    
    # 统计订单
    total_orders = Order.query.count()
    print(f"\n📋 订单总数: {total_orders}")
    
    if total_orders > 0:
        orders_by_status = db.session.query(
            Order.status,
            db.func.count(Order.id)
        ).group_by(Order.status).all()
        
        print("订单状态分布:")
        for status, count in orders_by_status:
            print(f"  - {status}: {count}")
    
    # 统计药品
    total_drugs = Drug.query.count()
    print(f"\n💊 药品总数: {total_drugs}")
    
    print("\n" + "=" * 60)
