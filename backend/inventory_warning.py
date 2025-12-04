"""
库存预警模块
实现库存预警的API接口和业务逻辑
"""
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from extensions import db
from models import InventoryItem, User, Drug, Tenant, InventoryTransaction
from auth import get_authenticated_user

# 创建蓝图
bp = Blueprint('inventory_warning', __name__, url_prefix='/api/v1/inventory')

# 预警阈值常量
LOW_STOCK_THRESHOLD = 10  # 低库存阈值
EXPIRY_WARNING_DAYS = 30  # 近效期预警天数


def _get_current_inventory_user():
    """获取当前登录用户并做基础校验"""
    user = get_authenticated_user()
    if not user:
        abort(401, description='登录状态已失效')
    if user.role not in {'pharmacy', 'supplier', 'admin', 'regulator'}:
        abort(403, description='当前角色无权访问库存接口')
    return user


def _ensure_tenant_access(user: User, tenant_id: int):
    """校验用户是否有权访问指定企业"""
    if user.role in {'admin', 'regulator'}:
        return
    if not user.tenant_id:
        abort(403, description='当前账号尚未关联企业')
    if user.tenant_id != tenant_id:
        abort(403, description='无权访问其他企业库存')


def _require_manage_permission(user: User):
    if user.role not in {'pharmacy', 'supplier', 'admin'}:
        abort(403, description='仅药店/供应商/管理员可操作库存')
    if user.role != 'admin' and not user.tenant_id:
        abort(403, description='当前账号尚未完成企业认证')


def _parse_date(value, field_name: str):
    if not value:
        abort(400, description=f'{field_name} 为必填项')
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        abort(400, description=f'{field_name} 格式不正确，应为 YYYY-MM-DD')


def _serialize_item(item: InventoryItem):
    return item.to_dict(include_related=True)


@bp.route('/items', methods=['GET'])
@jwt_required()
def list_inventory_items():
    """列出当前企业或指定企业的库存批次"""
    user = _get_current_inventory_user()
    tenant_id = request.args.get('tenant_id', type=int)
    keyword = (request.args.get('keyword') or '').strip()
    page = max(request.args.get('page', type=int) or 1, 1)
    per_page = min(max(request.args.get('per_page', type=int) or 10, 1), 100)

    if user.role not in {'admin', 'regulator'}:
        tenant_id = user.tenant_id
    elif tenant_id is None and user.tenant_id:
        tenant_id = user.tenant_id

    if not tenant_id:
        abort(400, description='tenant_id 缺失，无法查询库存')

    _ensure_tenant_access(user, tenant_id)

    query = InventoryItem.query.filter(InventoryItem.tenant_id == tenant_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.join(InventoryItem.drug).filter(
            or_(
                InventoryItem.batch_number.ilike(like),
                Drug.generic_name.ilike(like),
                Drug.brand_name.ilike(like)
            )
        )
    query = query.order_by(InventoryItem.updated_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [_serialize_item(item) for item in pagination.items],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total
    })


@bp.route('/items/<int:item_id>', methods=['GET'])
@jwt_required()
def retrieve_inventory_item(item_id):
    user = _get_current_inventory_user()
    item = InventoryItem.query.get_or_404(item_id)
    _ensure_tenant_access(user, item.tenant_id)
    return jsonify({'item': _serialize_item(item)})


@bp.route('/items', methods=['POST'])
@jwt_required()
def create_inventory_item():
    user = _get_current_inventory_user()
    _require_manage_permission(user)
    data = request.get_json() or {}

    tenant_id = data.get('tenant_id') if user.role == 'admin' else user.tenant_id
    if not tenant_id:
        abort(400, description='tenant_id 为必填项')
    try:
        tenant_id = int(tenant_id)
    except (TypeError, ValueError):
        abort(400, description='tenant_id 必须为整数')
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        abort(404, description='企业不存在')

    _ensure_tenant_access(user, tenant.id)

    try:
        drug_id = int(data.get('drug_id'))
    except (TypeError, ValueError):
        abort(400, description='drug_id 为必填项')

    drug = Drug.query.get(drug_id)
    if not drug:
        abort(404, description='药品不存在')

    batch_number = (data.get('batch_number') or '').strip()
    if not batch_number:
        abort(400, description='batch_number 为必填项')

    production_date = _parse_date(data.get('production_date'), 'production_date')
    expiry_date = _parse_date(data.get('expiry_date'), 'expiry_date')
    if expiry_date <= production_date:
        abort(400, description='有效期必须晚于生产日期')

    try:
        quantity = int(data.get('quantity'))
    except (TypeError, ValueError):
        abort(400, description='quantity 必须为整数')
    if quantity <= 0:
        abort(400, description='quantity 必须大于0')

    try:
        unit_price = float(data.get('unit_price'))
    except (TypeError, ValueError):
        abort(400, description='unit_price 必须为数字')
    if unit_price < 0:
        abort(400, description='unit_price 不能为负数')

    item = InventoryItem(
        tenant_id=tenant.id,
        drug_id=drug.id,
        batch_number=batch_number,
        production_date=production_date,
        expiry_date=expiry_date,
        quantity=quantity,
        unit_price=unit_price
    )
    db.session.add(item)
    db.session.flush()

    transaction = InventoryTransaction(
        inventory_item_id=item.id,
        transaction_type='IN',
        quantity_delta=quantity,
        created_by=user.id,
        source_tenant_id=None,
        notes=(data.get('notes') or '').strip() or None
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'item': _serialize_item(item)}), 201


@bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def adjust_inventory_item(item_id):
    user = _get_current_inventory_user()
    _require_manage_permission(user)
    item = InventoryItem.query.get_or_404(item_id)
    _ensure_tenant_access(user, item.tenant_id)
    data = request.get_json() or {}

    try:
        quantity_delta = int(data.get('quantity_delta'))
    except (TypeError, ValueError):
        abort(400, description='quantity_delta 必须为整数')
    if quantity_delta == 0:
        abort(400, description='quantity_delta 不能为0')

    new_quantity = item.quantity + quantity_delta
    if new_quantity < 0:
        abort(400, description='调整后库存不能为负数')

    if 'unit_price' in data and data.get('unit_price') is not None:
        try:
            unit_price = float(data.get('unit_price'))
        except (TypeError, ValueError):
            abort(400, description='unit_price 必须为数字')
        if unit_price < 0:
            abort(400, description='unit_price 不能为负数')
        item.unit_price = unit_price

    if 'expiry_date' in data and data.get('expiry_date'):
        expiry_date = _parse_date(data.get('expiry_date'), 'expiry_date')
        if expiry_date <= item.production_date:
            abort(400, description='有效期必须晚于生产日期')
        item.expiry_date = expiry_date

    item.quantity = new_quantity
    adjustment_type = 'IN' if quantity_delta > 0 else 'OUT'
    db.session.add(item)

    transaction = InventoryTransaction(
        inventory_item_id=item.id,
        transaction_type=adjustment_type,
        quantity_delta=quantity_delta,
        created_by=user.id,
        source_tenant_id=None,
        notes=(data.get('notes') or '').strip() or None
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'item': _serialize_item(item)})


@bp.route('/warnings', methods=['GET'])
@jwt_required()
def get_inventory_warnings():
    """
    获取库存预警列表
    
    Query Parameters:
        warning_type (str): 预警类型，可选值：low_stock, near_expiry, all (默认)
        page (int): 页码，默认1
        per_page (int): 每页数量，默认20
    
    Returns:
        200: 预警列表
        400: 参数错误
        403: 权限不足
    """
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 简单的角色验证
        allowed_roles = ['PHARMACY', 'SUPPLIER', 'ADMIN', 'pharmacy', 'supplier', 'admin']
        if current_user.role not in allowed_roles:
            return jsonify({
                'success': False,
                'message': '权限不足'
            }), 403
        
        # 获取查询参数
        warning_type = request.args.get('warning_type', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # 构建基础查询
        query = InventoryItem.query.join(Drug).filter(
            InventoryItem.tenant_id == current_user.tenant_id
        )
        
        # 计算近效期阈值
        expiry_threshold = datetime.now() + timedelta(days=EXPIRY_WARNING_DAYS)
        
        # 根据预警类型过滤
        if warning_type == 'low_stock':
            query = query.filter(InventoryItem.quantity < LOW_STOCK_THRESHOLD)
        elif warning_type == 'near_expiry':
            query = query.filter(InventoryItem.expiry_date <= expiry_threshold)
        elif warning_type == 'all':
            query = query.filter(
                or_(
                    InventoryItem.quantity < LOW_STOCK_THRESHOLD,
                    InventoryItem.expiry_date <= expiry_threshold
                )
            )
        else:
            return jsonify({
                'success': False,
                'message': '无效的预警类型参数'
            }), 400
        
        # 按紧急程度排序：先按即将过期，再按库存量
        query = query.order_by(
            InventoryItem.expiry_date.asc(),
            InventoryItem.quantity.asc()
        )
        
        # 执行分页查询
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 构建响应数据
        warnings = []
        for item in pagination.items:
            warning_info = item.to_dict(include_related=True)
            
            # 添加预警信息
            warning_info['warning_types'] = []
            
            if item.quantity < LOW_STOCK_THRESHOLD:
                warning_info['warning_types'].append({
                    'type': 'low_stock',
                    'message': f'库存不足，当前数量：{item.quantity}件',
                    'severity': 'warning' if item.quantity > 0 else 'critical'
                })
            
            days_to_expiry = (item.expiry_date - datetime.now().date()).days
            if days_to_expiry <= EXPIRY_WARNING_DAYS:
                if days_to_expiry <= 0:
                    severity = 'critical'
                    message = f'已过期 {abs(days_to_expiry)} 天'
                elif days_to_expiry <= 7:
                    severity = 'critical'
                    message = f'{days_to_expiry} 天后过期'
                else:
                    severity = 'warning'
                    message = f'{days_to_expiry} 天后过期'
                    
                warning_info['warning_types'].append({
                    'type': 'near_expiry',
                    'message': message,
                    'severity': severity,
                    'days_to_expiry': days_to_expiry
                })
            
            warnings.append(warning_info)
        
        return jsonify({
            'success': True,
            'message': '获取预警列表成功',
            'data': {
                'warnings': warnings,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
                'statistics': {
                    'total_warnings': pagination.total,
                    'low_stock_count': _count_low_stock(current_user.tenant_id),
                    'near_expiry_count': _count_near_expiry(current_user.tenant_id)
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '获取预警列表失败',
            'error': str(e)
        }), 500


@bp.route('/warning-summary', methods=['GET'])
@jwt_required()
def get_warning_summary():
    """
    获取预警统计摘要
    
    Returns:
        200: 预警统计信息
        403: 权限不足
    """
    try:
        # 获取当前用户
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 简单的角色验证
        allowed_roles = ['PHARMACY', 'SUPPLIER', 'ADMIN', 'pharmacy', 'supplier', 'admin']
        if current_user.role not in allowed_roles:
            return jsonify({
                'success': False,
                'message': '权限不足'
            }), 403
        
        tenant_id = current_user.tenant_id
        
        # 统计各类预警数量
        low_stock_count = _count_low_stock(tenant_id)
        near_expiry_count = _count_near_expiry(tenant_id)
        critical_count = _count_critical_warnings(tenant_id)
        
        # 获取最紧急的几个预警
        urgent_warnings = _get_urgent_warnings(tenant_id, limit=5)
        
        return jsonify({
            'success': True,
            'message': '获取预警摘要成功',
            'data': {
                'summary': {
                    'total_warnings': low_stock_count + near_expiry_count,
                    'low_stock_count': low_stock_count,
                    'near_expiry_count': near_expiry_count,
                    'critical_count': critical_count
                },
                'urgent_warnings': urgent_warnings,
                'thresholds': {
                    'low_stock_threshold': LOW_STOCK_THRESHOLD,
                    'expiry_warning_days': EXPIRY_WARNING_DAYS
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '获取预警摘要失败',
            'error': str(e)
        }), 500


def _count_low_stock(tenant_id):
    """统计低库存数量"""
    return InventoryItem.query.filter(
        and_(
            InventoryItem.tenant_id == tenant_id,
            InventoryItem.quantity < LOW_STOCK_THRESHOLD
        )
    ).count()


def _count_near_expiry(tenant_id):
    """统计近效期数量"""
    expiry_threshold = datetime.now() + timedelta(days=EXPIRY_WARNING_DAYS)
    return InventoryItem.query.filter(
        and_(
            InventoryItem.tenant_id == tenant_id,
            InventoryItem.expiry_date <= expiry_threshold
        )
    ).count()


def _count_critical_warnings(tenant_id):
    """统计严重预警数量（库存为0或已过期）"""
    now = datetime.now()
    return InventoryItem.query.filter(
        and_(
            InventoryItem.tenant_id == tenant_id,
            or_(
                InventoryItem.quantity == 0,
                InventoryItem.expiry_date <= now.date()
            )
        )
    ).count()


def _get_urgent_warnings(tenant_id, limit=5):
    """获取最紧急的预警"""
    now = datetime.now()
    expiry_threshold = now + timedelta(days=EXPIRY_WARNING_DAYS)
    
    # 查询紧急预警项目
    urgent_items = InventoryItem.query.join(Drug).filter(
        and_(
            InventoryItem.tenant_id == tenant_id,
            or_(
                InventoryItem.quantity < LOW_STOCK_THRESHOLD,
                InventoryItem.expiry_date <= expiry_threshold
            )
        )
    ).order_by(
        # 按紧急程度排序：已过期 > 即将过期 > 库存为0 > 低库存
        (InventoryItem.expiry_date <= now.date()).desc(),
        InventoryItem.expiry_date.asc(),
        (InventoryItem.quantity == 0).desc(),
        InventoryItem.quantity.asc()
    ).limit(limit).all()
    
    urgent_warnings = []
    for item in urgent_items:
        days_to_expiry = (item.expiry_date - now.date()).days
        
        # 确定预警级别和消息
        if days_to_expiry <= 0:
            severity = 'critical'
            message = f'{item.drug.generic_name} 已过期 {abs(days_to_expiry)} 天'
        elif item.quantity == 0:
            severity = 'critical'
            message = f'{item.drug.generic_name} 库存为零'
        elif days_to_expiry <= 7:
            severity = 'critical' 
            message = f'{item.drug.generic_name} {days_to_expiry} 天后过期'
        elif item.quantity < LOW_STOCK_THRESHOLD:
            severity = 'warning'
            message = f'{item.drug.generic_name} 库存不足，剩余 {item.quantity} 件'
        else:
            severity = 'warning'
            message = f'{item.drug.generic_name} {days_to_expiry} 天后过期'
        
        urgent_warnings.append({
            'id': item.id,
            'drug_name': item.drug.generic_name,
            'batch_number': item.batch_number,
            'quantity': item.quantity,
            'expiry_date': item.expiry_date.isoformat(),
            'days_to_expiry': days_to_expiry,
            'message': message,
            'severity': severity
        })
    
    return urgent_warnings


@bp.route('/scan-warnings', methods=['POST'])
@jwt_required()
def manual_scan_warnings():
    """
    手动触发预警扫描（仅管理员可用）
    
    Returns:
        200: 扫描完成
        403: 权限不足
    """
    try:
        # 执行预警扫描
        scan_result = scan_inventory_warnings()
        
        return jsonify({
            'success': True,
            'message': '预警扫描完成',
            'data': scan_result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '预警扫描失败',
            'error': str(e)
        }), 500


def scan_inventory_warnings():
    """
    执行库存预警扫描
    这个函数可以被定时任务调用
    
    Returns:
        dict: 扫描结果统计
    """
    try:
        now = datetime.now()
        expiry_threshold = now + timedelta(days=EXPIRY_WARNING_DAYS)
        
        # 查询所有需要预警的库存项
        warning_items = InventoryItem.query.filter(
            or_(
                InventoryItem.quantity < LOW_STOCK_THRESHOLD,
                InventoryItem.expiry_date <= expiry_threshold
            )
        ).all()
        
        # 按租户统计预警信息
        tenant_warnings = {}
        
        for item in warning_items:
            tenant_id = item.tenant_id
            if tenant_id not in tenant_warnings:
                tenant_warnings[tenant_id] = {
                    'low_stock': 0,
                    'near_expiry': 0,
                    'critical': 0,
                    'total': 0
                }
            
            # 统计预警类型
            if item.quantity < LOW_STOCK_THRESHOLD:
                tenant_warnings[tenant_id]['low_stock'] += 1
                if item.quantity == 0:
                    tenant_warnings[tenant_id]['critical'] += 1
            
            days_to_expiry = (item.expiry_date - now.date()).days
            if days_to_expiry <= EXPIRY_WARNING_DAYS:
                tenant_warnings[tenant_id]['near_expiry'] += 1
                if days_to_expiry <= 0:
                    tenant_warnings[tenant_id]['critical'] += 1
            
            tenant_warnings[tenant_id]['total'] += 1
        
        # 记录扫描结果到日志（这里简化处理）
        total_warnings = sum(tenant['total'] for tenant in tenant_warnings.values())
        
        return {
            'scan_time': now.isoformat(),
            'total_warnings': total_warnings,
            'affected_tenants': len(tenant_warnings),
            'tenant_statistics': tenant_warnings
        }
        
    except Exception as e:
        raise Exception(f"预警扫描失败: {str(e)}")
