from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, func
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User, SupplyInfo, Drug, Tenant, InventoryItem

bp = Blueprint('supply', __name__, url_prefix='/api/supply')

def get_authenticated_user():
    """获取当前认证用户"""
    identity = get_jwt_identity()
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return User.query.get(user_id)

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


def _get_available_inventory_quantity(tenant_id: int, drug_id: int) -> int:
    """计算指定企业针对给定药品的可用库存总量"""
    if not tenant_id or not drug_id:
        return 0
    total = (
        db.session.query(func.sum(InventoryItem.quantity))
        .filter(
            InventoryItem.tenant_id == tenant_id,
            InventoryItem.drug_id == drug_id,
            InventoryItem.quantity > 0
        )
        .scalar()
    )
    return int(total or 0)

@bp.route('/info', methods=['POST'])
@jwt_required()
@require_supplier_role
def create_supply_info(current_user):
    """
    发布供应信息
    
    请求体参数:
    - drug_id: 药品ID
    - available_quantity: 可供应数量
    - unit_price: 单价
    - valid_until: 有效期至 (YYYY-MM-DD)
    - min_order_quantity: 最小起订量 (可选，默认1)
    - description: 备注说明 (可选)
    """
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        required_fields = ['drug_id', 'available_quantity', 'unit_price', 'valid_until']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'msg': '缺少必填字段',
                'missing_fields': missing_fields
            }), 400
        
        drug_id = data.get('drug_id')
        available_quantity = data.get('available_quantity')
        unit_price = data.get('unit_price')
        valid_until_str = data.get('valid_until')
        min_order_quantity = data.get('min_order_quantity', 1)
        description = data.get('description', '')
        
        # 验证数据类型和范围
        try:
            drug_id = int(drug_id)
            available_quantity = int(available_quantity)
            unit_price = float(unit_price)
            min_order_quantity = int(min_order_quantity)
            valid_until = datetime.strptime(valid_until_str, '%Y-%m-%d').date()
        except (ValueError, TypeError) as e:
            return jsonify({'msg': '数据格式错误', 'error': str(e)}), 400
        
        # 业务逻辑验证
        if available_quantity <= 0:
            return jsonify({'msg': '可供应数量必须大于0'}), 400
        if unit_price <= 0:
            return jsonify({'msg': '单价必须大于0'}), 400
        if min_order_quantity <= 0:
            return jsonify({'msg': '最小起订量必须大于0'}), 400
        if valid_until <= date.today():
            return jsonify({'msg': '有效期必须晚于今天'}), 400
        
        # 验证药品是否存在
        drug = Drug.query.get(drug_id)
        if not drug:
            return jsonify({'msg': '药品不存在'}), 400
        
        # 检查用户是否有关联的企业
        if not current_user.tenant_id:
            return jsonify({'msg': '用户未关联企业，无法发布供应信息'}), 400

        available_stock = _get_available_inventory_quantity(current_user.tenant_id, drug_id)
        if available_stock <= 0:
            return jsonify({'msg': '当前库存中没有该药品，无法发布供应信息'}), 400
        if available_quantity > available_stock:
            return jsonify({
                'msg': f'可供应数量不能超过当前库存({available_stock})',
                'available_stock': available_stock
            }), 400
        
        # 创建供应信息
        supply_info = SupplyInfo(
            tenant_id=current_user.tenant_id,
            drug_id=drug_id,
            available_quantity=available_quantity,
            unit_price=unit_price,
            valid_until=valid_until,
            min_order_quantity=min_order_quantity,
            description=description,
            status='ACTIVE'
        )
        
        db.session.add(supply_info)
        db.session.commit()
        
        return jsonify({
            'msg': '供应信息发布成功',
            'data': supply_info.to_dict(include_relations=True)
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'msg': '数据库约束错误', 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'创建供应信息失败: {str(e)}')
        return jsonify({'msg': '创建供应信息失败', 'error': str(e)}), 500


@bp.route('/info', methods=['GET'])
@jwt_required()
def get_supply_info_list():
    """
    获取供应信息列表
    
    查询参数:
    - page: 页码 (默认1)
    - per_page: 每页数量 (默认20, 最大100)
    - drug_name: 药品名称搜索
    - supplier_name: 供应商名称搜索
    - status: 状态筛选 (ACTIVE/INACTIVE/EXPIRED)
    - only_mine: 只显示我的供应信息 (仅对供应商用户)
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        # 物流用户禁止访问供应信息列表
        if current_user.role == 'logistics':
            return jsonify({'msg': '权限不足：物流用户无法查看供应信息'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        drug_name = request.args.get('drug_name', '').strip()
        supplier_name = request.args.get('supplier_name', '').strip()
        status = request.args.get('status', '').strip()
        only_mine = request.args.get('only_mine', '').lower() == 'true'
        
        # 构建查询
        query = db.session.query(SupplyInfo).join(Drug).join(Tenant)
        
        # 状态筛选
        if status and status in ['ACTIVE', 'INACTIVE', 'EXPIRED']:
            query = query.filter(SupplyInfo.status == status)
        else:
            # 默认只显示ACTIVE状态且未过期的
            query = query.filter(
                and_(
                    SupplyInfo.status == 'ACTIVE',
                    SupplyInfo.valid_until > date.today()
                )
            )
        
        # 药品名称搜索
        if drug_name:
            query = query.filter(
                or_(
                    Drug.generic_name.ilike(f'%{drug_name}%'),
                    Drug.brand_name.ilike(f'%{drug_name}%')
                )
            )
        
        # 供应商名称搜索
        if supplier_name:
            query = query.filter(Tenant.name.ilike(f'%{supplier_name}%'))
        
        # 只显示我的供应信息
        if only_mine and current_user.role == 'supplier' and current_user.tenant_id:
            query = query.filter(SupplyInfo.tenant_id == current_user.tenant_id)
        
        # 排序
        query = query.order_by(SupplyInfo.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 格式化数据
        supply_list = [item.to_dict(include_relations=True) for item in pagination.items]
        
        return jsonify({
            'msg': '获取供应信息列表成功',
            'data': {
                'items': supply_list,
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
        current_app.logger.error(f'获取供应信息列表失败: {str(e)}')
        return jsonify({'msg': '获取供应信息列表失败', 'error': str(e)}), 500


@bp.route('/info/<int:supply_id>', methods=['GET'])
@jwt_required()
def get_supply_info_detail(supply_id):
    """获取供应信息详情"""
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        # 物流用户禁止查看供应信息详情
        if current_user.role == 'logistics':
            return jsonify({'msg': '权限不足：物流用户无法查看供应信息详情'}), 403
        
        supply_info = SupplyInfo.query.get(supply_id)
        if not supply_info:
            return jsonify({'msg': '供应信息不存在'}), 404
        
        return jsonify({
            'msg': '获取供应信息详情成功',
            'data': supply_info.to_dict(include_relations=True)
        })
        
    except Exception as e:
        current_app.logger.error(f'获取供应信息详情失败: {str(e)}')
        return jsonify({'msg': '获取供应信息详情失败', 'error': str(e)}), 500


@bp.route('/info/<int:supply_id>', methods=['PUT'])
@jwt_required()
@require_supplier_role
def update_supply_info(current_user, supply_id):
    """
    更新供应信息
    
    只能更新自己企业的供应信息
    """
    try:
        supply_info = SupplyInfo.query.get(supply_id)
        if not supply_info:
            return jsonify({'msg': '供应信息不存在'}), 404
        
        # 权限检查：只能更新自己企业的供应信息
        if supply_info.tenant_id != current_user.tenant_id:
            return jsonify({'msg': '无权限更新此供应信息'}), 403
        
        data = request.get_json() or {}
        
        # 可更新的字段
        updatable_fields = [
            'available_quantity', 'unit_price', 'valid_until', 
            'min_order_quantity', 'description', 'status'
        ]

        pending_updates = {}

        for field in updatable_fields:
            if field not in data:
                continue

            value = data[field]

            if field == 'valid_until' and value:
                try:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'msg': f'{field} 日期格式错误，应为 YYYY-MM-DD'}), 400

            if field in ['available_quantity', 'min_order_quantity'] and value is not None:
                if int(value) <= 0:
                    return jsonify({'msg': f'{field} 必须大于0'}), 400
                value = int(value)
            elif field == 'unit_price' and value is not None:
                if float(value) <= 0:
                    return jsonify({'msg': '单价必须大于0'}), 400
                value = float(value)
            elif field == 'status' and value not in ['ACTIVE', 'INACTIVE']:
                return jsonify({'msg': '状态只能是 ACTIVE 或 INACTIVE'}), 400

            pending_updates[field] = value

        if 'available_quantity' in pending_updates:
            available_stock = _get_available_inventory_quantity(current_user.tenant_id, supply_info.drug_id)
            if available_stock <= 0:
                return jsonify({'msg': '当前库存中没有该药品，无法设置供应数量'}), 400
            if pending_updates['available_quantity'] > available_stock:
                return jsonify({
                    'msg': f'可供应数量不能超过当前库存({available_stock})',
                    'available_stock': available_stock
                }), 400

        for field, value in pending_updates.items():
            setattr(supply_info, field, value)
        
        supply_info.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'msg': '供应信息更新成功',
            'data': supply_info.to_dict(include_relations=True)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新供应信息失败: {str(e)}')
        return jsonify({'msg': '更新供应信息失败', 'error': str(e)}), 500


@bp.route('/info/<int:supply_id>', methods=['DELETE'])
@jwt_required()
@require_supplier_role
def delete_supply_info(current_user, supply_id):
    """
    删除供应信息
    
    只能删除自己企业的供应信息
    """
    try:
        supply_info = SupplyInfo.query.get(supply_id)
        if not supply_info:
            return jsonify({'msg': '供应信息不存在'}), 404
        
        # 权限检查
        if supply_info.tenant_id != current_user.tenant_id:
            return jsonify({'msg': '无权限删除此供应信息'}), 403
        
        db.session.delete(supply_info)
        db.session.commit()
        
        return jsonify({'msg': '供应信息删除成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除供应信息失败: {str(e)}')
        return jsonify({'msg': '删除供应信息失败', 'error': str(e)}), 500


@bp.route('/drugs', methods=['GET'])
@jwt_required()
def get_drugs_list():
    """
    获取药品列表
    
    供发布供应信息时选择药品使用
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        # 物流用户禁止访问药品列表用于发布/编辑供应信息
        if current_user.role == 'logistics':
            return jsonify({'msg': '权限不足：物流用户无法查看药品列表'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        search = request.args.get('search', '').strip()
        
        query = Drug.query
        
        # 搜索功能
        if search:
            query = query.filter(
                or_(
                    Drug.generic_name.ilike(f'%{search}%'),
                    Drug.brand_name.ilike(f'%{search}%'),
                    Drug.approval_number.ilike(f'%{search}%')
                )
            )
        
        # 按通用名称排序
        query = query.order_by(Drug.generic_name)
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        drugs_list = [drug.to_dict() for drug in pagination.items]
        
        return jsonify({
            'msg': '获取药品列表成功',
            'data': {
                'items': drugs_list,
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
        current_app.logger.error(f'获取药品列表失败: {str(e)}')
        return jsonify({'msg': '获取药品列表失败', 'error': str(e)}), 500
