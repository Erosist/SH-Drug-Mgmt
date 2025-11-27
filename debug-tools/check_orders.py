import sys
sys.path.append('.')
from app import create_app
from models import Order
from extensions import db

app = create_app()

with app.app_context():
    # 查看订单的当前状态
    orders = Order.query.limit(5).all()
    if orders:
        for order in orders:
            print(f'Order ID: {order.id}')
            print(f'Order Number: {order.order_number}')
            print(f'Status: {order.status}')
            print(f'Buyer Tenant: {order.buyer_tenant_id}')
            print(f'Supplier Tenant: {order.supplier_tenant_id}')
            print(f'Logistics Tenant: {order.logistics_tenant_id}')
            print(f'Created At: {order.created_at}')
            print(f'Updated At: {order.updated_at}')
            print('---')
    else:
        print('No orders found')
