from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, desc, asc
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

from extensions import db
from models import User, Order, OrderItem, SupplyInfo, Drug, Tenant, InventoryItem, InventoryTransaction
from supply_utils import update_supply_info_quantity

bp = Blueprint('orders', __name__, url_prefix='/api/orders')


def get_authenticated_user():
    """获取当前认证用户"""
    identity = get_jwt_identity()
    if not identity:
        return None
    try:
        # Flask-JWT-Extended 返回的 identity 可能是字符串或整数
        user_id = int(identity)
    except (TypeError, ValueError):
        # 如果转换失败，记录错误并返回 None
        current_app.logger.error(f'无法解析 JWT identity: {identity}, type: {type(identity)}')
        return None
    
    user = User.query.get(user_id)
    if not user:
        current_app.logger.error(f'用户ID {user_id} 不存在')
        return None
        
    current_app.logger.info(f'成功获取用户: ID={user.id}, 用户名={user.username}, 角色={user.role}')
    return user


def require_buyer_role(f):
    """装饰器：要求具备下单权限的角色"""
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            return jsonify({'msg': '用户未登录'}), 401
        if user.role not in ['pharmacy', 'supplier', 'admin']:
            return jsonify({'msg': '权限不足，需要药店或供应商角色'}), 403
        return f(user, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def require_supplier_role(f):
    """装饰器：要求供应商角色"""
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            return jsonify({'msg': '用户未登录'}), 401
        if user.role not in ['supplier', 'admin']:
            return jsonify({'msg': '权限不足，需要供应商角色'}), 403
        return f(user, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def can_access_order(user, order):
    """检查用户是否有权限访问订单"""
    if user.role == 'admin':
        return True
    
    # 药店用户只能访问自己的采购订单
    if user.role == 'pharmacy' and order.buyer_tenant_id == user.tenant_id:
        return True
    
    # 供应商用户只能访问自己的供应订单
    if user.role == 'supplier' and order.supplier_tenant_id == user.tenant_id:
        return True
    
    # 物流用户只能访问分配给自己的订单
    if user.role == 'logistics' and order.logistics_tenant_id == user.tenant_id:
        return True
    
    return False


def _coerce_to_date(value):
    """将 datetime/date/None 转换为 date 对象"""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.utcnow().date()


def _sync_inventory_for_receipt(order, current_user):
    """收货后自动将订单明细同步到买方库存"""
    if not order.buyer_tenant_id:
        raise ValueError('订单缺少买方企业，无法同步库存')

    if not order.items:
        current_app.logger.info(f'订单 {order.id} 无明细，跳过库存同步')
        return

    base_date = _coerce_to_date(order.delivered_at or order.shipped_at or order.confirmed_at or order.created_at)
    default_expiry = base_date + timedelta(days=365)
    order_identifier = order.order_number or f'ORDER-{order.id}'

    for item in order.items:
        if not item.quantity or item.quantity <= 0:
            current_app.logger.warning(f'订单 {order.id} 明细 {item.id} 数量异常，跳过自动入库')
            continue

        batch_number = item.batch_number or f'AUTO-{order_identifier}-{item.id}'
        inventory_item = InventoryItem.query.filter_by(
            tenant_id=order.buyer_tenant_id,
            drug_id=item.drug_id,
            batch_number=batch_number
        ).first()

        incoming_qty = int(item.quantity)
        incoming_price = float(item.unit_price or 0)

        if inventory_item:
            total_quantity = inventory_item.quantity + incoming_qty
            if total_quantity <= 0:
                raise ValueError('库存数量即将变为负数，终止自动入库')

            current_total_value = (inventory_item.unit_price or 0) * inventory_item.quantity
            new_total_value = current_total_value + incoming_price * incoming_qty
            inventory_item.quantity = total_quantity
            if total_quantity > 0:
                inventory_item.unit_price = round(new_total_value / total_quantity, 2)
            inventory_item.updated_at = datetime.utcnow()
        else:
            inventory_item = InventoryItem(
                tenant_id=order.buyer_tenant_id,
                drug_id=item.drug_id,
                batch_number=batch_number,
                production_date=base_date,
                expiry_date=default_expiry,
                quantity=incoming_qty,
                unit_price=incoming_price
            )
            db.session.add(inventory_item)
            db.session.flush()  # 获取ID供流水使用

        transaction = InventoryTransaction(
            inventory_item_id=inventory_item.id,
            transaction_type='IN',
            quantity_delta=incoming_qty,
            source_tenant_id=order.supplier_tenant_id,
            related_order_id=order.id,
            notes=f'订单 {order_identifier} 收货自动入库',
            created_by=current_user.id
        )
        db.session.add(transaction)


def _deduct_inventory_for_shipment(order, current_user):
    """发货时从供应商库存扣减相应药品"""
    if not order.supplier_tenant_id:
        raise ValueError('订单缺少供应商企业，无法扣减库存')

    if not order.items:
        current_app.logger.info(f'订单 {order.id} 无明细，跳过库存扣减')
        return

    order_identifier = order.order_number or f'ORDER-{order.id}'

    for item in order.items:
        required_qty = int(item.quantity or 0)
        if required_qty <= 0:
            continue

        query = InventoryItem.query.filter_by(
            tenant_id=order.supplier_tenant_id,
            drug_id=item.drug_id
        ).filter(InventoryItem.quantity > 0)

        if item.batch_number:
            query = query.filter(InventoryItem.batch_number == item.batch_number)

        inventory_entries = query.order_by(
            asc(InventoryItem.expiry_date),
            asc(InventoryItem.id)
        ).all()

        if not inventory_entries:
            if item.batch_number:
                raise ValueError(f'库存中未找到批次 {item.batch_number} 的药品，无法发货')
            raise ValueError('库存中没有可用的药品，无法发货')

        remaining = required_qty

        for inventory_item in inventory_entries:
            if remaining <= 0:
                break
            available = inventory_item.quantity or 0
            if available <= 0:
                continue

            deduction = min(available, remaining)
            inventory_item.quantity -= deduction
            inventory_item.updated_at = datetime.utcnow()

            transaction = InventoryTransaction(
                inventory_item_id=inventory_item.id,
                transaction_type='OUT',
                quantity_delta=-deduction,
                source_tenant_id=order.buyer_tenant_id,
                related_order_id=order.id,
                notes=f'订单 {order_identifier} 发货扣减库存',
                created_by=current_user.id
            )
            db.session.add(transaction)

            remaining -= deduction

        if remaining > 0:
            raise ValueError('库存不足，无法完成此次发货')


@bp.route('', methods=['POST'])
@jwt_required()
@require_buyer_role
def create_order(current_user):
    """
    创建订单（下单）
    
    请求体参数:
    - supply_info_id: 供应信息ID
    - quantity: 订购数量

    - expected_delivery_date: 期望交付日期 (可选，YYYY-MM-DD格式)
    - notes: 备注 (可选)
    """
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        required_fields = ['supply_info_id', 'quantity']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'msg': '缺少必填字段',
                'missing_fields': missing_fields
            }), 400
        
        supply_info_id = data.get('supply_info_id')
        quantity = data.get('quantity')
        expected_delivery_date_str = data.get('expected_delivery_date')
        notes = data.get('notes', '')
        
        # 验证数据类型
        try:
            supply_info_id = int(supply_info_id)
            quantity = int(quantity)
            expected_delivery_date = None
            if expected_delivery_date_str:
                expected_delivery_date = datetime.strptime(expected_delivery_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError) as e:
            return jsonify({'msg': '数据格式错误', 'error': str(e)}), 400
        
        # 业务逻辑验证
        if quantity <= 0:
            return jsonify({'msg': '订购数量必须大于0'}), 400
        
        # 验证供应信息是否存在且有效
        supply_info = SupplyInfo.query.get(supply_info_id)
        if not supply_info:
            return jsonify({'msg': '供应信息不存在'}), 404
        
        if supply_info.status != 'ACTIVE':
            return jsonify({'msg': '供应信息已下架，无法下单'}), 400
        
        if supply_info.valid_until <= date.today():
            return jsonify({'msg': '供应信息已过期，无法下单'}), 400
        
        # 检查库存是否充足
        if quantity > supply_info.available_quantity:
            return jsonify({
                'msg': '库存不足',
                'available_quantity': supply_info.available_quantity,
                'requested_quantity': quantity
            }), 400
        
        # 检查是否满足最小起订量
        if quantity < supply_info.min_order_quantity:
            return jsonify({
                'msg': f'订购数量不满足最小起订量要求',
                'min_order_quantity': supply_info.min_order_quantity,
                'requested_quantity': quantity
            }), 400
        
        # 检查用户是否有关联的企业
        if not current_user.tenant_id:
            return jsonify({'msg': '用户未关联企业，无法下单'}), 400
        
        # 不能向自己的企业下单
        if current_user.tenant_id == supply_info.tenant_id:
            return jsonify({'msg': '不能向自己的企业下单'}), 400
        
        # 创建订单
        order = Order(
            buyer_tenant_id=current_user.tenant_id,
            supplier_tenant_id=supply_info.tenant_id,
            supply_info_id=supply_info_id,  # 关联供应信息ID
            expected_delivery_date=expected_delivery_date,
            notes=notes,
            status='PENDING',
            created_by=current_user.id
        )
        
        # 创建订单明细
        order_item = OrderItem(
            drug_id=supply_info.drug_id,
            unit_price=supply_info.unit_price,
            quantity=quantity
        )
        
        order.items.append(order_item)
        
        db.session.add(order)
        db.session.flush()  # 获取订单ID
        
        # 更新供应信息的可用数量（预占库存）
        updated_supply_info = update_supply_info_quantity(
            supply_info.tenant_id, 
            supply_info.drug_id, 
            -quantity,
            f"订单{order.order_number}创建，预占库存"
        )
        
        if not updated_supply_info:
            db.session.rollback()
            return jsonify({'msg': '供应信息数量不足，无法创建订单'}), 400
        
        db.session.commit()
        
        return jsonify({
            'msg': '订单创建成功',
            'data': order.to_dict(include_relations=True)
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'msg': '数据库约束错误', 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'创建订单失败: {str(e)}')
        return jsonify({'msg': '创建订单失败', 'error': str(e)}), 500


@bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """
    获取订单列表
    
    查询参数:
    - page: 页码 (默认1)
    - per_page: 每页数量 (默认20, 最大100)
    - status: 订单状态筛选
    - role_filter: 角色筛选 (my_purchases: 我的采购, my_sales: 我的销售)
    - order_number: 订单号搜索
    - drug_name: 药品名称搜索
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        # 物流用户不通过此通用接口获取订单，请使用 /api/logistics/orders
        if current_user.role == 'logistics':
            return jsonify({'msg': '权限不足：物流用户请使用物流专用订单接口'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status', '').strip()
        role_filter = request.args.get('role_filter', '').strip()
        order_number = request.args.get('order_number', '').strip()
        drug_name = request.args.get('drug_name', '').strip()
        
        # 构建查询
        query = db.session.query(Order)
        
        # 权限控制
        current_app.logger.info(f'get_orders - 用户权限检查: 用户ID={current_user.id}, 角色={current_user.role}, 租户ID={current_user.tenant_id}')
        
        if current_user.role == 'pharmacy':
            # 药店用户只能看到自己的采购订单
            query = query.filter(Order.buyer_tenant_id == current_user.tenant_id)
            current_app.logger.info(f'get_orders - 药店用户过滤: buyer_tenant_id={current_user.tenant_id}')
        elif current_user.role == 'supplier':
            # 供应商用户只能看到自己的供应订单
            query = query.filter(Order.supplier_tenant_id == current_user.tenant_id)
            current_app.logger.info(f'get_orders - 供应商用户过滤: supplier_tenant_id={current_user.tenant_id}')
        elif current_user.role == 'logistics':
            # 物流用户不允许通过此接口查看订单（有专用接口 /api/logistics/orders）
            return jsonify({'msg': '权限不足：物流用户不可通过此接口查看订单'}), 403
        elif current_user.role == 'admin':
            # 管理员可以看到所有订单
            current_app.logger.info('get_orders - 管理员用户，无过滤')
            pass
        else:
            current_app.logger.warning(f'get_orders - 权限不足: 角色={current_user.role}')
            return jsonify({'msg': '权限不足'}), 403
        
        # 角色筛选 - 注意：pharmacy用户已经在上面过滤了buyer_tenant_id，这里的my_purchases实际上是多余的
        # 但为了兼容前端的调用，保持这个逻辑，只是不重复过滤
        if role_filter == 'my_purchases' and current_user.role == 'supplier':
            # 供应商想看作为买方的订单（这种情况很少见，但逻辑上支持）
            query = query.filter(Order.buyer_tenant_id == current_user.tenant_id)
        elif role_filter == 'my_sales' and current_user.role == 'pharmacy':
            # 药店想看作为供应商的订单（这种情况很少见，但逻辑上支持）
            query = query.filter(Order.supplier_tenant_id == current_user.tenant_id)
        # 对于pharmacy用户请求my_purchases，由于上面已经过滤了buyer_tenant_id，无需重复处理
        # 对于supplier用户请求my_sales，由于上面已经过滤了supplier_tenant_id，无需重复处理
        
        # 状态筛选
        valid_statuses = [
            'PENDING', 'CONFIRMED', 'SHIPPED', 'IN_TRANSIT', 'DELIVERED', 
            'COMPLETED', 'CANCELLED_BY_PHARMACY', 'CANCELLED_BY_SUPPLIER', 'EXPIRED_CANCELLED'
        ]
        if status and status in valid_statuses:
            query = query.filter(Order.status == status)
        
        # 订单号搜索
        if order_number:
            query = query.filter(Order.order_number.ilike(f'%{order_number}%'))
        
        # 药品名称搜索
        if drug_name:
            query = query.join(OrderItem).join(Drug).filter(
                or_(
                    Drug.generic_name.ilike(f'%{drug_name}%'),
                    Drug.brand_name.ilike(f'%{drug_name}%')
                )
            )
        
        # 排序
        query = query.order_by(desc(Order.created_at))
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 格式化数据
        orders_list = [order.to_dict(include_relations=True) for order in pagination.items]
        
        return jsonify({
            'msg': '获取订单列表成功',
            'data': {
                'items': orders_list,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'获取订单列表失败: {str(e)}')
        return jsonify({'msg': '获取订单列表失败', 'error': str(e)}), 500


@bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """获取订单详情"""
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'msg': '订单不存在'}), 404
        
        # 权限检查
        if not can_access_order(current_user, order):
            return jsonify({'msg': '无权限访问此订单'}), 403
        
        return jsonify({
            'msg': '获取订单详情成功',
            'data': order.to_dict(include_relations=True)
        })
        
    except Exception as e:
        current_app.logger.error(f'获取订单详情失败: {str(e)}')
        return jsonify({'msg': '获取订单详情失败', 'error': str(e)}), 500


@bp.route('/<int:order_id>/confirm', methods=['POST'])
@jwt_required()
@require_supplier_role
def confirm_order(current_user, order_id):
    """
    供应商确认订单
    
    请求体参数:
    - action: 'accept' 或 'reject'
    - reason: 拒绝原因 (当action为reject时必填)
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'msg': '订单不存在'}), 404
        
        # 权限检查：只能确认自己企业的供应订单
        if order.supplier_tenant_id != current_user.tenant_id:
            return jsonify({'msg': '无权限确认此订单'}), 403
        
        # 状态检查：只有PENDING状态的订单可以确认
        if order.status != 'PENDING':
            return jsonify({'msg': f'订单状态为 {order.status}，无法确认'}), 400
        
        data = request.get_json() or {}
        action = data.get('action', '').strip().lower()
        reason = data.get('reason', '').strip()
        
        if action not in ['accept', 'reject']:
            return jsonify({'msg': 'action 必须是 accept 或 reject'}), 400
        
        if action == 'accept':
            # 接受订单
            order.status = 'CONFIRMED'
            order.confirmed_by = current_user.id
            order.confirmed_at = datetime.utcnow()
            
            message = '订单确认成功'
            
        else:  # reject
            if not reason:
                return jsonify({'msg': '拒绝订单时必须提供原因'}), 400
            
            # 拒绝订单
            order.status = 'CANCELLED_BY_SUPPLIER'
            order.cancelled_by = current_user.id
            order.cancelled_at = datetime.utcnow()
            order.cancel_reason = reason
            
            # 恢复供应信息的可用数量
            for item in order.items:
                update_supply_info_quantity(
                    order.supplier_tenant_id,
                    item.drug_id, 
                    item.quantity,
                    f"订单{order.order_number}被供应商拒绝，恢复库存"
                )
            
            message = '订单已拒绝'
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'msg': message,
            'data': order.to_dict(include_relations=True)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'确认订单失败: {str(e)}')
        return jsonify({'msg': '确认订单失败', 'error': str(e)}), 500


@bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
@require_buyer_role
def cancel_order(current_user, order_id):
    """
    药店取消订单
    
    请求体参数:
    - reason: 取消原因 (可选)
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'msg': '订单不存在'}), 404
        
        # 权限检查：只能取消自己的采购订单
        if order.buyer_tenant_id != current_user.tenant_id:
            return jsonify({'msg': '无权限取消此订单'}), 403
        
        # 状态检查：只有PENDING状态的订单可以取消
        if order.status != 'PENDING':
            return jsonify({'msg': f'订单状态为 {order.status}，无法取消'}), 400
        
        data = request.get_json() or {}
        reason = data.get('reason', '').strip()
        
        # 取消订单
        order.status = 'CANCELLED_BY_PHARMACY'
        order.cancelled_by = current_user.id
        order.cancelled_at = datetime.utcnow()
        order.cancel_reason = reason if reason else '用户主动取消'
        order.updated_at = datetime.utcnow()
        
        # 恢复供应信息的可用数量
        for item in order.items:
            update_supply_info_quantity(
                order.supplier_tenant_id,
                item.drug_id, 
                item.quantity,
                f"订单{order.order_number}取消，恢复库存"
            )
        
        db.session.commit()
        
        return jsonify({
            'msg': '订单取消成功',
            'data': order.to_dict(include_relations=True)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'取消订单失败: {str(e)}')
        return jsonify({'msg': '取消订单失败', 'error': str(e)}), 500


@bp.route('/<int:order_id>/ship', methods=['POST'])
@jwt_required()
@require_supplier_role
def ship_order(current_user, order_id):
    """
    供应商发货
    
    请求体参数:
    - tracking_number: 运单号 (可选)
    - logistics_tenant_id: 物流公司ID (可选)
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'msg': '订单不存在'}), 404
        
        # 权限检查
        if order.supplier_tenant_id != current_user.tenant_id:
            return jsonify({'msg': '无权限操作此订单'}), 403
        
        # 状态检查：只有CONFIRMED状态的订单可以发货
        if order.status != 'CONFIRMED':
            return jsonify({'msg': f'订单状态为 {order.status}，无法发货'}), 400
        
        data = request.get_json() or {}
        tracking_number = data.get('tracking_number', '').strip()
        logistics_tenant_id = data.get('logistics_tenant_id')
        
        # 验证物流公司
        if logistics_tenant_id:
            try:
                logistics_tenant_id = int(logistics_tenant_id)
                logistics_tenant = Tenant.query.get(logistics_tenant_id)
                if not logistics_tenant or logistics_tenant.type != 'LOGISTICS':
                    return jsonify({'msg': '无效的物流公司'}), 400
            except (ValueError, TypeError):
                return jsonify({'msg': '物流公司ID格式错误'}), 400
        
        _deduct_inventory_for_shipment(order, current_user)

        # 更新订单状态
        order.status = 'SHIPPED'
        order.tracking_number = tracking_number
        order.logistics_tenant_id = logistics_tenant_id
        order.shipped_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'msg': '发货成功',
            'data': order.to_dict(include_relations=True)
        })
        
    except ValueError as inventory_error:
        db.session.rollback()
        return jsonify({'msg': str(inventory_error)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'发货失败: {str(e)}')
        return jsonify({'msg': '发货失败', 'error': str(e)}), 500


@bp.route('/<int:order_id>/receive', methods=['POST'])
@jwt_required()
@require_buyer_role
def receive_order(current_user, order_id):
    """
    药店确认收货
    
    请求体参数:
    - notes: 收货备注 (可选)
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'msg': '订单不存在'}), 404
        
        # 权限检查
        if order.buyer_tenant_id != current_user.tenant_id:
            return jsonify({'msg': '无权限操作此订单'}), 403
        
        # 状态检查：只有DELIVERED状态的订单可以确认收货
        if order.status != 'DELIVERED':
            return jsonify({'msg': f'订单状态为 {order.status}，无法确认收货'}), 400
        
        data = request.get_json() or {}
        notes = data.get('notes', '').strip()
        
        # 更新订单状态
        order.status = 'COMPLETED'
        order.received_confirmed_by = current_user.id
        order.received_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        
        if notes:
            order.notes = (order.notes or '') + f'\n收货备注: {notes}'
        
        _sync_inventory_for_receipt(order, current_user)
        
        db.session.commit()
        
        return jsonify({
            'msg': '确认收货成功，订单已完成',
            'data': order.to_dict(include_relations=True)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'确认收货失败: {str(e)}')
        return jsonify({'msg': '确认收货失败', 'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_order_stats():
    """获取订单统计信息"""
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        if not current_user.tenant_id:
            return jsonify({'msg': '用户未关联企业'}), 400

        # 禁止物流用户访问订单统计（有专用物流接口）
        if current_user.role == 'logistics':
            return jsonify({'msg': '权限不足：物流用户无法访问订单统计'}), 403

        # 根据角色统计不同的数据
        current_app.logger.info(f'get_order_stats - 用户权限检查: 用户ID={current_user.id}, 角色={current_user.role}, 租户ID={current_user.tenant_id}')

        if current_user.role == 'pharmacy':
            # 药店统计采购订单
            query = Order.query.filter_by(buyer_tenant_id=current_user.tenant_id)
            current_app.logger.info(f'get_order_stats - 药店统计: buyer_tenant_id={current_user.tenant_id}')
        elif current_user.role == 'supplier':
            # 供应商统计供应订单
            query = Order.query.filter_by(supplier_tenant_id=current_user.tenant_id)
            current_app.logger.info(f'get_order_stats - 供应商统计: supplier_tenant_id={current_user.tenant_id}')
        elif current_user.role == 'logistics':
            # 物流公司统计分配给自己的订单，且只统计物流相关状态
            query = Order.query.filter(
                Order.logistics_tenant_id == current_user.tenant_id,
                Order.status.in_(['SHIPPED', 'IN_TRANSIT', 'DELIVERED'])
            )
            current_app.logger.info(f'get_order_stats - 物流统计: logistics_tenant_id={current_user.tenant_id}')
        else:
            current_app.logger.warning(f'get_order_stats - 权限不足: 角色={current_user.role}')
            return jsonify({'msg': '权限不足'}), 403
        
        # 统计各状态订单数量
        stats = {
            'total': query.count(),
            'pending': query.filter_by(status='PENDING').count(),
            'confirmed': query.filter_by(status='CONFIRMED').count(),
            'shipped': query.filter_by(status='SHIPPED').count(),
            'in_transit': query.filter_by(status='IN_TRANSIT').count(),
            'delivered': query.filter_by(status='DELIVERED').count(),
            'completed': query.filter_by(status='COMPLETED').count(),
            'cancelled': query.filter(
                Order.status.in_(['CANCELLED_BY_PHARMACY', 'CANCELLED_BY_SUPPLIER', 'EXPIRED_CANCELLED'])
            ).count()
        }
        
        # 计算本月订单数量
        from datetime import datetime
        this_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stats['this_month'] = query.filter(Order.created_at >= this_month_start).count()
        
        return jsonify({
            'msg': '获取订单统计成功',
            'data': stats
        })
        
    except Exception as e:
        current_app.logger.error(f'获取订单统计失败: {str(e)}')
        return jsonify({'msg': '获取订单统计失败', 'error': str(e)}), 500


@bp.route('/status/<int:order_id>', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    """
    更新订单状态
    用于物流公司更新配送状态
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'msg': '订单不存在'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'msg': '状态参数缺失'}), 400
        
        # 验证状态转换的合法性
        valid_transitions = {
            'SHIPPED': ['IN_TRANSIT'],
            'IN_TRANSIT': ['DELIVERED'],
            'DELIVERED': ['COMPLETED']
        }
        
        # 如果订单已经是目标状态，直接返回成功（幂等操作）
        if order.status == new_status:
            return jsonify({
                'success': True,
                'message': f'订单状态已经是 {new_status}',
                'data': {
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'old_status': order.status,
                    'new_status': new_status
                }
            })
        
        if order.status not in valid_transitions:
            return jsonify({'success': False, 'message': f'当前状态 {order.status} 不允许更新'}), 400
        
        if new_status not in valid_transitions[order.status]:
            return jsonify({'success': False, 'message': f'无效的状态转换: {order.status} -> {new_status}'}), 400
        
        # 权限检查：只有物流公司和管理员可以更新配送状态
        if current_user.role == 'logistics':
            # 物流公司只能更新分配给自己的订单，或者未分配物流公司的订单
            if order.logistics_tenant_id is not None and order.logistics_tenant_id != current_user.tenant_id:
                return jsonify({'success': False, 'message': '权限不足，只能更新分配给本公司的订单'}), 403
            # 如果订单还没有分配物流公司，则将当前物流公司分配给该订单
            if order.logistics_tenant_id is None:
                order.logistics_tenant_id = current_user.tenant_id
        elif current_user.role != 'admin':
            return jsonify({'success': False, 'message': '权限不足，需要物流公司或管理员角色'}), 403
        
        # 更新订单状态
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(
            f'用户 {current_user.username} 将订单 {order_id} 状态从 {old_status} 更新为 {new_status}'
        )
        
        return jsonify({
            'success': True,
            'message': f'订单状态已更新为 {new_status}',
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': new_status
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新订单状态失败: {str(e)}')
        return jsonify({'success': False, 'message': '更新订单状态失败', 'error': str(e)}), 500


# 物流相关路由
from flask import Blueprint as FlaskBlueprint
logistics_bp = FlaskBlueprint('logistics', __name__, url_prefix='/api/logistics')

@logistics_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_logistics_companies():
    """
    获取物流公司列表
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        
        # 查询所有物流公司
        logistics_companies = Tenant.query.filter_by(type='LOGISTICS').all()
        
        companies_data = []
        for company in logistics_companies:
            companies_data.append({
                'id': company.id,
                'name': company.name,
                'type': company.type,
                'created_at': company.created_at.isoformat() if company.created_at else None
            })
        
        return jsonify({
            'success': True,
            'message': '获取物流公司列表成功',
            'data': companies_data
        })
        
    except Exception as e:
        current_app.logger.error(f'获取物流公司列表失败: {str(e)}')
        return jsonify({'success': False, 'message': '获取物流公司列表失败', 'error': str(e)}), 500


@logistics_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_logistics_orders():
    """
    获取物流公司的订单列表
    物流公司只能看到分配给自己的订单，且状态为 SHIPPED, IN_TRANSIT, DELIVERED
    支持筛选参数：
    - order_no: 订单号（模糊查询）
    - tracking_number: 运单号（模糊查询）
    - status: 订单状态（精确匹配）
    - start_date: 开始日期（按更新时间过滤）
    - end_date: 结束日期（按更新时间过滤）
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        
        if current_user.role not in ['logistics', 'admin']:
            return jsonify({'msg': '权限不足，需要物流公司或管理员角色'}), 403
        
        # 构建查询
        query = db.session.query(Order)
        
        # 如果是物流公司用户，只显示分配给该公司的订单
        if current_user.role == 'logistics':
            query = query.filter(Order.logistics_tenant_id == current_user.tenant_id)
        
        # 只显示物流相关的订单状态
        query = query.filter(Order.status.in_(['SHIPPED', 'IN_TRANSIT', 'DELIVERED']))
        
        # 获取筛选参数
        order_no = request.args.get('order_no', '').strip()
        tracking_number = request.args.get('tracking_number', '').strip()
        status = request.args.get('status', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        
        # 应用筛选条件
        if order_no:
            query = query.filter(Order.order_number.like(f'%{order_no}%'))
        
        if tracking_number:
            query = query.filter(Order.tracking_number.like(f'%{tracking_number}%'))
        
        if status:
            query = query.filter(Order.status == status)
        
        if start_date:
            try:
                from datetime import datetime
                # 处理 ISO 格式日期字符串
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Order.updated_at >= start)
            except Exception as e:
                current_app.logger.warning(f'解析开始日期失败: {e}')
        
        if end_date:
            try:
                from datetime import datetime
                # 处理 ISO 格式日期字符串
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Order.updated_at <= end)
            except Exception as e:
                current_app.logger.warning(f'解析结束日期失败: {e}')
        
        # 按更新时间倒序排列
        query = query.order_by(desc(Order.updated_at))
        
        orders = query.all()
        
        orders_data = []
        for order in orders:
            # 获取药房信息（买方租户）
            pharmacy = Tenant.query.get(order.buyer_tenant_id)
            pharmacy_name = pharmacy.name if pharmacy else 'Unknown'
            pharmacy_address = pharmacy.address if pharmacy else None
            
            # 获取供应商名称
            supplier = Tenant.query.get(order.supplier_tenant_id)
            supplier_name = supplier.name if supplier else 'Unknown'
            
            # 收集批号（从订单明细中获取第一个批号）
            batch_numbers = []
            drug_names = []
            total_quantity = 0
            
            for item in order.items:
                if item.batch_number:
                    batch_numbers.append(item.batch_number)
                
                drug = Drug.query.get(item.drug_id)
                if drug:
                    drug_names.append(f"{drug.generic_name or drug.brand_name}")
                
                total_quantity += item.quantity
            
            drug_name = ', '.join(drug_names) if drug_names else 'Unknown'
            batch_number = batch_numbers[0] if batch_numbers else None
            
            # 获取物流公司名称
            logistics_company_name = None
            if order.logistics_tenant_id:
                logistics_company = Tenant.query.get(order.logistics_tenant_id)
                if logistics_company:
                    logistics_company_name = logistics_company.name
            
            # 返回前端需要的字段格式
            orders_data.append({
                'id': order.id,
                'order_no': order.order_number,  # 前端使用 order_no
                'tracking_number': order.tracking_number,  # 运单号
                'batch_number': batch_number,  # 批号
                'status': order.status,
                'address': pharmacy_address,  # 收货地址（药房地址）
                'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                # 额外的字段（可选）
                'pharmacy_name': pharmacy_name,
                'supplier_name': supplier_name,
                'drug_name': drug_name,
                'quantity': total_quantity,
                'total_amount': str(order.total_amount),
                'logistics_company_name': logistics_company_name,
                'created_at': order.created_at.isoformat() if order.created_at else None
            })
        
        return jsonify({
            'success': True,
            'message': '获取物流订单列表成功',
            'data': orders_data,
            'total': len(orders_data)
        })
        
    except Exception as e:
        current_app.logger.error(f'获取物流订单列表失败: {str(e)}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': '获取物流订单列表失败',
            'error': str(e)
        }), 500


def register_logistics_blueprint(app):
    """注册物流蓝图"""
    app.register_blueprint(logistics_bp)
