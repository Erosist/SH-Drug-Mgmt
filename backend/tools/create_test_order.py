#!/usr/bin/env python3
"""
创建一个测试订单并分配给物流公司
"""
import sys
sys.path.append('backend')

from app import create_app, db
from models import Order, Tenant, User, SupplyInfo, Drug, OrderItem
from datetime import datetime, date
from decimal import Decimal
import random
from config import Config

def create_test_order():
    """创建测试订单"""
    print("=== 创建测试订单 ===")
    
    app = create_app(Config)
    with app.app_context():
        # 获取药房和供应商
        pharmacy = Tenant.query.filter_by(type='PHARMACY').first()
        supplier = Tenant.query.filter_by(type='SUPPLIER').first()
        logistics = Tenant.query.filter_by(name='顺丰速运').first()
        
        if not pharmacy or not supplier or not logistics:
            print("❌ 找不到必要的租户数据")
            return
        
        print(f"药房: {pharmacy.name} (ID: {pharmacy.id})")
        print(f"供应商: {supplier.name} (ID: {supplier.id})")
        print(f"物流: {logistics.name} (ID: {logistics.id})")
        
        # 获取供应信息
        supply = SupplyInfo.query.filter_by(tenant_id=supplier.id).first()
        if not supply:
            print("❌ 找不到供应信息")
            return
        
        print(f"供应信息: {supply.id}")
        
        # 获取药房用户和供应商用户
        pharmacy_user = User.query.filter_by(tenant_id=pharmacy.id).first()
        supplier_user = User.query.filter_by(tenant_id=supplier.id).first()
        
        if not pharmacy_user or not supplier_user:
            print("❌ 找不到用户")
            return
        
        # 创建订单
        order = Order(
            buyer_tenant_id=pharmacy.id,
            supplier_tenant_id=supplier.id,
            created_by=pharmacy_user.id,
            status='CONFIRMED',  # 直接创建为已确认状态
            notes='测试物流订单'
        )
        
        db.session.add(order)
        db.session.flush()  # 获取order ID
        
        # 创建订单明细
        order_item = OrderItem(
            order_id=order.id,
            drug_id=supply.drug_id,
            unit_price=supply.unit_price,
            quantity=10
        )
        
        db.session.add(order_item)
        
        # 立即发货并分配给顺丰
        order.status = 'SHIPPED'
        order.logistics_tenant_id = logistics.id
        order.tracking_number = f'SF{random.randint(100000000000, 999999999999)}'
        order.shipped_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"✓ 创建订单: {order.order_number}")
        print(f"✓ 状态: {order.status}")
        print(f"✓ 物流公司ID: {order.logistics_tenant_id}")
        print(f"✓ 运单号: {order.tracking_number}")
        
        # 验证查询
        logistics_orders = Order.query.filter(
            Order.logistics_tenant_id == logistics.id,
            Order.status.in_(['SHIPPED', 'IN_TRANSIT', 'DELIVERED'])
        ).all()
        
        print(f"✓ 物流订单查询结果: {len(logistics_orders)} 个订单")
        for order in logistics_orders:
            print(f"  - {order.order_number} ({order.status})")

if __name__ == "__main__":
    create_test_order()
