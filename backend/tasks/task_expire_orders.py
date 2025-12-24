"""
订单超时处理任务

处理24小时内未确认的订单，自动标记为超时取消
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import Order, SupplyInfo
from supply_utils import update_supply_info_quantity


def handle_expired_orders():
    """处理超时订单"""
    app = create_app()
    
    with app.app_context():
        # 查找24小时前创建且仍为PENDING状态的订单
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        expired_orders = Order.query.filter(
            Order.status == 'PENDING',
            Order.created_at <= cutoff_time
        ).all()
        
        if not expired_orders:
            print("没有找到超时订单")
            return
        
        for order in expired_orders:
            try:
                print(f"处理超时订单: {order.order_number}")
                
                # 更新订单状态
                order.status = 'EXPIRED_CANCELLED'
                order.cancelled_at = datetime.utcnow()
                order.cancel_reason = '供应商24小时内未确认，系统自动取消'
                order.updated_at = datetime.utcnow()
                
                # 恢复供应信息的可用数量
                for item in order.items:
                    update_supply_info_quantity(
                        order.supplier_tenant_id,
                        item.drug_id,
                        item.quantity,
                        f"订单{order.order_number}超时自动取消，恢复库存"
                    )
                
                db.session.commit()
                print(f"订单 {order.order_number} 已标记为超时取消")
                
            except Exception as e:
                db.session.rollback()
                print(f"处理订单 {order.order_number} 失败: {str(e)}")
        
        print(f"共处理 {len(expired_orders)} 个超时订单")


if __name__ == '__main__':
    handle_expired_orders()
