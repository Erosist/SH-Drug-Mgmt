import sys
sys.path.append('.')
from app import create_app
from models import Order
from extensions import db

app = create_app()

with app.app_context():
    # 修复已有订单的logistics_tenant_id
    orders_to_fix = Order.query.filter(
        Order.status.in_(['SHIPPED', 'IN_TRANSIT', 'DELIVERED']),
        Order.logistics_tenant_id.is_(None)
    ).all()
    
    print(f'Found {len(orders_to_fix)} orders with logistics status but no logistics company assigned')
    
    # 假设sfexpress的tenant_id是19（从之前的调试信息得出）
    sfexpress_tenant_id = None
    
    # 查找sfexpress用户的tenant_id
    from models import User
    sfexpress_user = User.query.filter_by(username='sfexpress').first()
    if sfexpress_user:
        sfexpress_tenant_id = sfexpress_user.tenant_id
        print(f'Found sfexpress user with tenant_id: {sfexpress_tenant_id}')
    
    if sfexpress_tenant_id:
        for order in orders_to_fix:
            print(f'Fixing order {order.id} ({order.order_number}) - status: {order.status}')
            order.logistics_tenant_id = sfexpress_tenant_id
            
        db.session.commit()
        print(f'Fixed {len(orders_to_fix)} orders')
    else:
        print('No sfexpress user found')
