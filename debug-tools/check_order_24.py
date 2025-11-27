import sys
sys.path.append('.')
from app import create_app
from models import Order
from extensions import db

app = create_app()

with app.app_context():
    # 检查订单ID 24
    order = Order.query.get(24)
    if order:
        print(f'订单 {order.id} 存在:')
        print(f'  订单号: {order.order_number}')
        print(f'  状态: {order.status}')
        print(f'  物流公司ID: {order.logistics_tenant_id}')
        print(f'  买方租户ID: {order.buyer_tenant_id}')
        print(f'  供应商租户ID: {order.supplier_tenant_id}')
    else:
        print('订单ID 24 不存在')
        
    # 查看所有SHIPPED状态的订单
    shipped_orders = Order.query.filter_by(status='SHIPPED').all()
    print(f'\n找到 {len(shipped_orders)} 个SHIPPED状态的订单:')
    for order in shipped_orders:
        print(f'  订单ID: {order.id}, 订单号: {order.order_number}, 物流公司: {order.logistics_tenant_id}')
