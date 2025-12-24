"""
监管用户相关功能模块
提供监管用户查看所有企业库存和订单的API
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Tenant, SupplyInfo, Drug, Order, OrderItem, User, InventoryItem
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('regulator', __name__, url_prefix='/api/regulator')


@bp.route('/enterprises', methods=['GET'])
@jwt_required()
def get_all_enterprises():
    """获取所有企业列表"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user or current_user.role != 'regulator':
        return jsonify({'error': '权限不足，仅监管用户可访问'}), 403
    
    try:
        # 获取查询参数
        tenant_type = request.args.get('type')  # 企业类型过滤
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = Tenant.query
        
        if tenant_type:
            query = query.filter_by(type=tenant_type)
        
        # 分页
        pagination = query.order_by(Tenant.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        enterprises = [{
            **tenant.to_dict(),
            'user_count': User.query.filter_by(tenant_id=tenant.id).count(),
            'supply_count': SupplyInfo.query.filter_by(tenant_id=tenant.id).count(),
            'order_count_as_buyer': Order.query.filter_by(buyer_tenant_id=tenant.id).count(),
            'order_count_as_supplier': Order.query.filter_by(supplier_tenant_id=tenant.id).count(),
        } for tenant in pagination.items]
        
        return jsonify({
            'enterprises': enterprises,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inventory/overview', methods=['GET'])
@jwt_required()
def get_inventory_overview():
    """获取所有企业的库存概览"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user or current_user.role != 'regulator':
        return jsonify({'error': '权限不足，仅监管用户可访问'}), 403
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        tenant_id = request.args.get('tenant_id', type=int)
        drug_name = request.args.get('drug_name')
        
        # 查询供应信息（包含库存）
        query = db.session.query(
            SupplyInfo,
            Drug,
            Tenant
        ).join(
            Drug, SupplyInfo.drug_id == Drug.id
        ).join(
            Tenant, SupplyInfo.tenant_id == Tenant.id
        )
        
        # 应用过滤条件
        if tenant_id:
            query = query.filter(SupplyInfo.tenant_id == tenant_id)
        
        if drug_name:
            query = query.filter(
                db.or_(
                    Drug.generic_name.like(f'%{drug_name}%'),
                    Drug.brand_name.like(f'%{drug_name}%')
                )
            )
        
        # 分页
        pagination = query.order_by(SupplyInfo.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        inventory_list = []
        for supply_info, drug, tenant in pagination.items:
            inventory_list.append({
                'id': supply_info.id,
                'tenant': {
                    'id': tenant.id,
                    'name': tenant.name,
                    'type': tenant.type,
                    'address': tenant.address
                },
                'drug': {
                    'id': drug.id,
                    'generic_name': drug.generic_name,
                    'brand_name': drug.brand_name,
                    'approval_number': drug.approval_number,
                    'specification': drug.specification,
                    'manufacturer': drug.manufacturer
                },
                'available_quantity': supply_info.available_quantity,
                'unit_price': float(supply_info.unit_price),
                'valid_until': supply_info.valid_until.isoformat() if supply_info.valid_until else None,
                'status': supply_info.status,
                'updated_at': supply_info.updated_at.isoformat() if supply_info.updated_at else None
            })
        
        # 统计信息
        total_suppliers = db.session.query(func.count(func.distinct(SupplyInfo.tenant_id))).scalar()
        total_drugs = db.session.query(func.count(func.distinct(SupplyInfo.drug_id))).scalar()
        total_supply_records = db.session.query(func.count(SupplyInfo.id)).scalar()
        
        return jsonify({
            'inventory': inventory_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'statistics': {
                'total_suppliers': total_suppliers,
                'total_drugs': total_drugs,
                'total_supply_records': total_supply_records
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/orders/overview', methods=['GET'])
@jwt_required()
def get_orders_overview():
    """获取所有订单概览"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user or current_user.role != 'regulator':
        return jsonify({'error': '权限不足，仅监管用户可访问'}), 403
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')
        buyer_id = request.args.get('buyer_id', type=int)
        supplier_id = request.args.get('supplier_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = db.session.query(
            Order,
            Tenant.label('buyer'),
            Tenant.label('supplier')
        ).join(
            Tenant, Order.buyer_tenant_id == Tenant.id, isouter=False
        ).join(
            Tenant, Order.supplier_tenant_id == Tenant.id, isouter=False
        )
        
        # 应用过滤
        if status:
            query = query.filter(Order.status == status)
        if buyer_id:
            query = query.filter(Order.buyer_tenant_id == buyer_id)
        if supplier_id:
            query = query.filter(Order.supplier_tenant_id == supplier_id)
        if start_date:
            query = query.filter(Order.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Order.created_at <= datetime.fromisoformat(end_date))
        
        # 分页
        pagination = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        orders_list = []
        for order in pagination.items:
            # 获取订单关联的企业信息
            buyer_tenant = Tenant.query.get(order.buyer_tenant_id)
            supplier_tenant = Tenant.query.get(order.supplier_tenant_id)
            
            # 获取订单项
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            total_amount = sum(float(item.unit_price) * item.quantity for item in order_items)
            total_quantity = sum(item.quantity for item in order_items)
            
            orders_list.append({
                'id': order.id,
                'order_number': order.order_number,
                'buyer': {
                    'id': buyer_tenant.id,
                    'name': buyer_tenant.name,
                    'type': buyer_tenant.type
                } if buyer_tenant else None,
                'supplier': {
                    'id': supplier_tenant.id,
                    'name': supplier_tenant.name,
                    'type': supplier_tenant.type
                } if supplier_tenant else None,
                'status': order.status,
                'total_amount': total_amount,
                'total_quantity': total_quantity,
                'items_count': len(order_items),
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None
            })
        
        # 统计信息
        status_stats = db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()
        
        status_distribution = {status: count for status, count in status_stats}
        
        # 最近7天订单趋势
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_orders = db.session.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('count')
        ).filter(
            Order.created_at >= seven_days_ago
        ).group_by(
            func.date(Order.created_at)
        ).all()
        
        daily_trend = [{'date': str(date), 'count': count} for date, count in recent_orders]
        
        return jsonify({
            'orders': orders_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'statistics': {
                'status_distribution': status_distribution,
                'daily_trend': daily_trend
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """获取订单详情"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user or current_user.role != 'regulator':
        return jsonify({'error': '权限不足，仅监管用户可访问'}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        buyer_tenant = Tenant.query.get(order.buyer_tenant_id)
        supplier_tenant = Tenant.query.get(order.supplier_tenant_id)
        
        # 获取订单项详情
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        items_detail = []
        
        for item in order_items:
            drug = Drug.query.get(item.drug_id)
            items_detail.append({
                'id': item.id,
                'drug': drug.to_dict() if drug else None,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': float(item.unit_price) * item.quantity
            })
        
        total_amount = sum(float(item.unit_price) * item.quantity for item in order_items)
        
        return jsonify({
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'buyer': buyer_tenant.to_dict() if buyer_tenant else None,
                'supplier': supplier_tenant.to_dict() if supplier_tenant else None,
                'status': order.status,
                'total_amount': total_amount,
                'items': items_detail,
                'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
                'tracking_number': order.tracking_number,
                'notes': order.notes,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
                'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
                'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
                'received_at': order.received_at.isoformat() if order.received_at else None,
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_statistics():
    """获取监管仪表盘统计数据"""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if not current_user or current_user.role != 'regulator':
        return jsonify({'error': '权限不足，仅监管用户可访问'}), 403
    
    try:
        # 企业统计
        total_enterprises = Tenant.query.count()
        enterprises_by_type = db.session.query(
            Tenant.type,
            func.count(Tenant.id)
        ).group_by(Tenant.type).all()
        
        enterprise_stats = {
            'total': total_enterprises,
            'by_type': {tenant_type: count for tenant_type, count in enterprises_by_type}
        }
        
        # 订单统计
        total_orders = Order.query.count()
        orders_by_status = db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()
        
        # 今日订单
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders = Order.query.filter(Order.created_at >= today_start).count()
        
        order_stats = {
            'total': total_orders,
            'today': today_orders,
            'by_status': {status: count for status, count in orders_by_status}
        }
        
        # 库存统计
        total_supply_records = SupplyInfo.query.count()
        active_supply = SupplyInfo.query.filter_by(status='ACTIVE').count()
        
        # 低库存预警（库存数量小于10）
        low_stock_count = SupplyInfo.query.filter(
            SupplyInfo.available_quantity < 10,
            SupplyInfo.status == 'ACTIVE'
        ).count()
        
        inventory_stats = {
            'total_records': total_supply_records,
            'active_supply': active_supply,
            'low_stock_alerts': low_stock_count
        }
        
        # 用户统计
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        authenticated_users = User.query.filter_by(is_authenticated=True).count()
        
        user_stats = {
            'total': total_users,
            'active': active_users,
            'authenticated': authenticated_users
        }
        
        return jsonify({
            'enterprises': enterprise_stats,
            'orders': order_stats,
            'inventory': inventory_stats,
            'users': user_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
