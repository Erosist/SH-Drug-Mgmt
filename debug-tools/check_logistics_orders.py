#!/usr/bin/env python3
"""
检查物流订单数据
"""
import sys
sys.path.append('backend')

from app import create_app, db
from models import Order, Tenant, User
from config import Config

def check_logistics_orders():
    """检查物流订单数据"""
    print("=== 检查物流订单数据 ===")
    
    app = create_app(Config)
    with app.app_context():
        # 查看顺丰速运的ID和相关订单
        logistics_company = Tenant.query.filter_by(name='顺丰速运', type='LOGISTICS').first()
        if not logistics_company:
            print("❌ 找不到顺丰速运物流公司")
            return
        
        print(f"✓ 顺丰速运 ID: {logistics_company.id}")
        
        # 查看所有订单
        all_orders = Order.query.all()
        print(f"✓ 总订单数: {len(all_orders)}")
        
        # 查看分配给顺丰的订单
        logistics_orders = Order.query.filter_by(logistics_tenant_id=logistics_company.id).all()
        print(f"✓ 分配给顺丰的订单数: {len(logistics_orders)}")
        
        # 查看SHIPPED/IN_TRANSIT/DELIVERED状态的订单
        relevant_orders = Order.query.filter(
            Order.logistics_tenant_id == logistics_company.id,
            Order.status.in_(['SHIPPED', 'IN_TRANSIT', 'DELIVERED'])
        ).all()
        print(f"✓ 符合物流状态的订单数: {len(relevant_orders)}")
        
        # 查看所有订单的状态和物流分配
        print("\n=== 所有订单详情 ===")
        for order in all_orders:
            print(f"订单 {order.order_number}:")
            print(f"  状态: {order.status}")
            print(f"  物流公司ID: {order.logistics_tenant_id}")
            if order.logistics_tenant_id:
                logistics = Tenant.query.get(order.logistics_tenant_id)
                print(f"  物流公司: {logistics.name if logistics else '未知'}")
            print()

if __name__ == "__main__":
    check_logistics_orders()
