#!/usr/bin/env python3
"""
测试订单状态和确认收货功能
"""
import sys
sys.path.append('backend')

from app import create_app, db
from models import User, Order, OrderItem, Drug, Tenant
from config import Config
from datetime import datetime

def test_order_statuses_and_receipt():
    """测试订单状态和确认收货"""
    print("=== 测试订单状态和确认收货功能 ===")
    
    app = create_app(Config)
    with app.app_context():
        # 1. 查看当前所有订单的状态分布
        print("\n1. 当前订单状态分布:")
        orders = Order.query.all()
        status_count = {}
        for order in orders:
            status = order.status
            status_count[status] = status_count.get(status, 0) + 1
            
        for status, count in status_count.items():
            print(f"   {status}: {count} 条")
        
        print(f"\n总订单数: {len(orders)}")
        
        # 2. 查看具体的订单详情（特别是药店用户的订单）
        print("\n2. 药店用户订单详情:")
        pharmacy_users = User.query.filter_by(role='pharmacy').all()
        for user in pharmacy_users[:3]:  # 只看前3个药店用户
            if user.tenant_id:
                user_orders = Order.query.filter_by(buyer_tenant_id=user.tenant_id).all()
                print(f"\n   用户 {user.username} (租户ID: {user.tenant_id}):")
                for order in user_orders[:5]:  # 只显示前5个订单
                    print(f"     - 订单ID: {order.id}, 状态: {order.status}, 创建时间: {order.created_at}")
        
        # 3. 检查是否有DELIVERED状态的订单
        print("\n3. DELIVERED状态的订单:")
        delivered_orders = Order.query.filter_by(status='DELIVERED').all()
        if delivered_orders:
            for order in delivered_orders:
                print(f"   - 订单ID: {order.id}, 订单号: {order.order_number}")
                print(f"     买方: {order.buyer_tenant_id}, 卖方: {order.supplier_tenant_id}")
        else:
            print("   没有DELIVERED状态的订单")
        
        # 4. 检查取消订单的情况
        print("\n4. 各种取消状态的订单:")
        cancelled_statuses = ['CANCELLED_BY_PHARMACY', 'CANCELLED_BY_SUPPLIER', 'EXPIRED_CANCELLED']
        for status in cancelled_statuses:
            cancelled_orders = Order.query.filter_by(status=status).all()
            print(f"   {status}: {len(cancelled_orders)} 条")
            for order in cancelled_orders[:2]:  # 只显示前2个
                print(f"     - 订单ID: {order.id}, 买方: {order.buyer_tenant_id}")
        
        # 5. 模拟创建一个DELIVERED状态的订单用于测试
        print("\n5. 创建测试用的DELIVERED订单:")
        
        # 找一个SHIPPED状态的订单
        shipped_order = Order.query.filter_by(status='SHIPPED').first()
        if shipped_order:
            print(f"   找到SHIPPED订单: {shipped_order.id}")
            print(f"   将其状态更新为DELIVERED用于测试...")
            
            # 更新状态
            shipped_order.status = 'DELIVERED'
            shipped_order.delivered_at = datetime.utcnow()
            shipped_order.updated_at = datetime.utcnow()
            
            db.session.commit()
            print(f"   ✓ 订单 {shipped_order.id} 已更新为DELIVERED状态")
        else:
            print("   没有找到SHIPPED状态的订单可以更新")

if __name__ == "__main__":
    test_order_statuses_and_receipt()
