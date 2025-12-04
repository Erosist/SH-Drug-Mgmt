#!/usr/bin/env python3
"""
为开发环境创建物流租户/用户并生成示例订单，分配给该物流公司。
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Ensure backend package imports work
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import Tenant, User, SupplyInfo, Order, OrderItem
from models import Drug
from datetime import date


def ensure_logistics_tenant_and_user():
    """确保目标租户与用户存在，返回 (tenant, user)."""
    # Provided data
    tenant_data = {
        'name': 'Logistics Co',
        'type': 'LOGISTICS',
        'unified_social_credit_code': 'LOGISTICS-DEV-0001',
        'legal_representative': 'Logistics Co',
        'contact_person': 'Logistics Co',
        'contact_phone': '00000000000',
        'contact_email': 'logistics@example.com',
        'address': '开发环境地址',
        'business_scope': '物流配送',
        'is_active': True
    }

    user_data = {
        'username': 'logistics_dev',
        'email': 'logistics@example.com',
        'phone': None,
        'real_name': None,
        'company_name': 'Logistics Co',
        'role': 'logistics',
        'is_authenticated': False,
        'is_active': True
    }

    tenant = Tenant.query.filter_by(unified_social_credit_code=tenant_data['unified_social_credit_code']).first()
    if not tenant:
        tenant = Tenant(**tenant_data)
        db.session.add(tenant)
        db.session.flush()
        print(f"Created tenant: {tenant.name} (id={tenant.id})")
    else:
        print(f"Tenant exists: {tenant.name} (id={tenant.id})")

    user = User.query.filter_by(username=user_data['username']).first()
    if not user:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            phone=user_data['phone'],
            real_name=user_data['real_name'],
            company_name=user_data['company_name'],
            role=user_data['role'],
            tenant_id=tenant.id,
            is_authenticated=user_data['is_authenticated'],
            is_active=user_data['is_active']
        )
        # set a default password for dev usage
        user.set_password('devpass')
        db.session.add(user)
        db.session.flush()
        print(f"Created user: {user.username} (id={user.id})")
    else:
        # update tenant association if needed
        updated = False
        if user.tenant_id != tenant.id:
            user.tenant_id = tenant.id
            updated = True
        if user.role != 'logistics':
            user.role = 'logistics'
            updated = True
        if updated:
            db.session.add(user)
            db.session.flush()
            print(f"Updated user {user.username} to tenant_id={tenant.id} role=logistics")
        else:
            print(f"User exists: {user.username} (id={user.id})")

    return tenant, user


def ensure_supplier_tenant_and_user():
    """确保存在一个用于测试的供应商租户与用户，返回 (tenant, user)。"""
    supplier_tenant_data = {
        'name': 'Dev Supplier',
        'type': 'SUPPLIER',
        'unified_social_credit_code': 'SUPPLIER-DEV-0001',
        'legal_representative': 'Dev Supplier',
        'contact_person': 'Dev Supplier',
        'contact_phone': '00000000001',
        'contact_email': 'supplier@example.com',
        'address': '开发环境供应商地址',
        'business_scope': '药品供应',
        'is_active': True
    }

    supplier_user_data = {
        'username': 'supplier_dev',
        'email': 'supplier@example.com',
        'role': 'supplier',
        'company_name': 'Dev Supplier',
        'is_authenticated': False,
        'is_active': True
    }

    tenant = Tenant.query.filter_by(unified_social_credit_code=supplier_tenant_data['unified_social_credit_code']).first()
    if not tenant:
        tenant = Tenant(**supplier_tenant_data)
        db.session.add(tenant)
        db.session.flush()
        print(f"Created supplier tenant: {tenant.name} (id={tenant.id})")
    else:
        print(f"Supplier tenant exists: {tenant.name} (id={tenant.id})")

    user = User.query.filter((User.username == supplier_user_data['username']) | (User.email == supplier_user_data['email'])).first()
    if not user:
        user = User(
            username=supplier_user_data['username'],
            email=supplier_user_data['email'],
            role=supplier_user_data['role'],
            tenant_id=tenant.id,
            company_name=supplier_user_data['company_name'],
            is_authenticated=supplier_user_data['is_authenticated'],
            is_active=supplier_user_data['is_active']
        )
        user.set_password('devpass')
        db.session.add(user)
        db.session.flush()
        print(f"Created supplier user: {user.username} (id={user.id})")
    else:
        updated = False
        if user.tenant_id != tenant.id:
            user.tenant_id = tenant.id
            updated = True
        if user.role != 'supplier':
            user.role = 'supplier'
            updated = True
        if updated:
            db.session.add(user)
            db.session.flush()
            print(f"Updated supplier user {user.username} to tenant_id={tenant.id} role=supplier")
        else:
            print(f"Supplier user exists: {user.username} (id={user.id})")

    return tenant, user


def create_orders_for_logistics(logistics_tenant, count=3):
    """为物流公司创建若干示例订单，使用系统中存在的药店与供应信息作为买卖双方。"""
    # 找到可用的药店买家
    pharmacy_supply = SupplyInfo.query.filter_by(status='ACTIVE').all()
    if not pharmacy_supply:
        print("没有可用的 SupplyInfo，请先运行 init_db 或确保有供应数据。")
        return []

    # 找到一个药店用户作为下单方
    from models import User as UserModel, Tenant as TenantModel
    pharmacy_user = UserModel.query.filter_by(role='pharmacy', is_authenticated=True).first()
    if not pharmacy_user:
        # 如果没有已认证药店用户，尝试使用任何药店租户创建临时用户
        pharmacy_tenant = TenantModel.query.filter_by(type='PHARMACY').first()
        if not pharmacy_tenant:
            print('未找到 PHARMACY 租户，无法创建订单')
            return []
        pharmacy_user = UserModel(
            username=f'pharmacy_auto_{random.randint(1000,9999)}',
            email=f'pharmacy_auto_{random.randint(1000,9999)}@example.com',
            role='pharmacy',
            tenant_id=pharmacy_tenant.id,
            is_authenticated=True,
            is_active=True
        )
        pharmacy_user.set_password('devpass')
        db.session.add(pharmacy_user)
        db.session.flush()
        print(f'Created fallback pharmacy user: {pharmacy_user.username} (id={pharmacy_user.id})')

    created_orders = []
    now = datetime.utcnow()
    for i in range(count):
        supply = random.choice(pharmacy_supply)
        # create order
        order = Order(
            buyer_tenant_id=pharmacy_user.tenant_id,
            supplier_tenant_id=supply.tenant_id,
            supply_info_id=supply.id,
            expected_delivery_date=(now + timedelta(days=3+i)).date(),
            notes='开发环境分配给物流公司的测试订单',
            status=random.choice(['SHIPPED', 'IN_TRANSIT', 'DELIVERED']),
            logistics_tenant_id=logistics_tenant.id,
            tracking_number=f'TRK{random.randint(1000000,9999999)}',
            shipped_at=now - timedelta(hours=2+i),
            created_by=pharmacy_user.id,
            created_at=now - timedelta(days=i),
            updated_at=now - timedelta(days=i)
        )

        # create an order item
        item = OrderItem(
            drug_id=supply.drug_id,
            unit_price=supply.unit_price,
            quantity= random.choice([10, 50, 100])
        )
        order.items.append(item)
        db.session.add(order)
        db.session.flush()
        created_orders.append(order)
        print(f'Created order {order.order_number} -> logistics_tenant_id={order.logistics_tenant_id} tracking={order.tracking_number}')

    db.session.commit()
    return created_orders


def ensure_supplier_has_supply(supplier_tenant):
    """若供应商没有任何 SupplyInfo，则创建一个示例 Drug 与 SupplyInfo 以供测试"""
    # 检查该供应商是否已有 active supply
    existing = SupplyInfo.query.filter_by(tenant_id=supplier_tenant.id, status='ACTIVE').first()
    if existing:
        print(f"Supplier tenant {supplier_tenant.name} already has supply info (id={existing.id})")
        return existing

    # 尝试找到任意已有 drug
    drug = Drug.query.first()
    if not drug:
        # 创建示例药品
        drug = Drug(
            generic_name='示例药品A',
            brand_name='示例牌',
            approval_number=f'DEV-{random.randint(10000,99999)}',
            dosage_form='胶囊',
            specification='10mg',
            manufacturer='开发环境厂家',
            category='通用',
            prescription_type='非处方'
        )
        db.session.add(drug)
        db.session.flush()
        print(f"Created sample drug: {drug.generic_name} (id={drug.id})")

    # 创建 SupplyInfo
    valid_until = date.today() + timedelta(days=365)
    supply = SupplyInfo(
        tenant_id=supplier_tenant.id,
        drug_id=drug.id,
        available_quantity=1000,
        unit_price=12.50,
        valid_until=valid_until,
        min_order_quantity=10,
        description='开发环境示例供应信息',
        status='ACTIVE'
    )
    db.session.add(supply)
    db.session.commit()
    print(f"Created SupplyInfo id={supply.id} for supplier {supplier_tenant.name}")
    return supply


def main():
    app = create_app()
    with app.app_context():
        tenant, user = ensure_logistics_tenant_and_user()
        # Ensure there is at least one supplier tenant/user available for orders
        supplier_tenant, supplier_user = ensure_supplier_tenant_and_user()
        # 确保供应商有供应信息可用于生成订单
        ensure_supplier_has_supply(supplier_tenant)

        orders = create_orders_for_logistics(tenant, count=3)
        print('\nSummary:')
        print(f'Logistics tenant id: {tenant.id}, user id: {user.id}')
        print(f'Created {len(orders)} orders assigned to logistics tenant {tenant.name}')


if __name__ == '__main__':
    main()
