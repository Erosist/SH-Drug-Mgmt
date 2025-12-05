from datetime import date
from flask import Blueprint, jsonify, request
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload

from models import Drug, InventoryItem, Tenant, SupplyInfo
from extensions import db
from auth import get_authenticated_user
from flask import abort

bp = Blueprint('catalog', __name__, url_prefix='/api/catalog')


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_pagination_args():
    page = parse_int(request.args.get('page'), 1)
    per_page = parse_int(request.args.get('per_page'), 10)
    page = max(page or 1, 1)
    per_page = max(min(per_page or 10, 100), 1)
    return page, per_page


def paginate_query(query, serializer):
    page, per_page = get_pagination_args()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [serializer(item) for item in pagination.items],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
    }


@bp.route('/drugs', methods=['GET'])
def list_drugs():
    keyword = (request.args.get('keyword') or '').strip()
    category = (request.args.get('category') or '').strip()
    prescription = (request.args.get('prescription_type') or '').strip()

    query = Drug.query
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Drug.generic_name.ilike(like),
                Drug.brand_name.ilike(like),
                Drug.approval_number.ilike(like),
            )
        )
    if category:
        query = query.filter(Drug.category == category)
    if prescription:
        query = query.filter(Drug.prescription_type == prescription)

    query = query.order_by(Drug.id.asc())
    return jsonify(paginate_query(query, lambda d: d.to_dict()))


@bp.route('/drugs/search', methods=['GET'])
def search_drugs():
    """
    药品搜索接口
    支持按药品通用名、商品名、厂家进行模糊搜索
    
    查询参数:
    - q: 搜索关键词（必填）
    - page: 页码，默认1
    - per_page: 每页数量，默认10，最大50
    """
    keyword = (request.args.get('q') or '').strip()
    
    if not keyword:
        return jsonify({
            'success': False,
            'msg': '请输入搜索关键词',
            'items': [],
            'total': 0
        }), 400
    
    like = f"%{keyword}%"
    query = Drug.query.filter(
        or_(
            Drug.generic_name.ilike(like),
            Drug.brand_name.ilike(like),
            Drug.manufacturer.ilike(like),
        )
    ).order_by(Drug.generic_name.asc())
    
    result = paginate_query(query, lambda d: d.to_dict())
    result['success'] = True
    result['msg'] = f'找到 {result["total"]} 个药品'
    return jsonify(result)


@bp.route('/drugs/<int:drug_id>', methods=['GET'])
def get_drug_detail(drug_id):
    """
    获取药品详情
    
    返回完整的药品信息，包括：
    - 基本信息：通用名、商品名、规格、剂型等
    - 厂家信息：生产厂家、批准文号
    - 分类信息：药品分类、处方类型
    """
    drug = Drug.query.get(drug_id)
    
    if not drug:
        return jsonify({
            'success': False,
            'msg': '药品不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': drug.to_dict()
    })


@bp.route('/tenants', methods=['GET'])
def list_tenants():
    keyword = (request.args.get('keyword') or '').strip()
    type_filter = (request.args.get('type') or '').strip()
    active_raw = (request.args.get('is_active') or '').lower().strip()

    query = Tenant.query
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Tenant.name.ilike(like),
                Tenant.address.ilike(like),
                Tenant.unified_social_credit_code.ilike(like),
            )
        )
    if type_filter:
        query = query.filter(Tenant.type == type_filter.upper())
    if active_raw in {'true', 'false'}:
        query = query.filter(Tenant.is_active == (active_raw == 'true'))

    query = query.order_by(Tenant.id.asc())
    return jsonify(paginate_query(query, lambda t: t.to_dict()))


@bp.route('/tenants/<int:tenant_id>', methods=['GET'])
def tenant_detail(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    # 如果是已登录的药店/供应商用户，只允许访问与其关联的租户详情
    try:
        user = get_authenticated_user()
    except Exception:
        user = None
    # 物流用户无权查看企业详情（不应该访问库存/企业管理相关数据）
    if user and user.role == 'logistics':
        abort(403, description='物流用户无权访问此企业信息')

    if user and user.role in {'pharmacy', 'supplier'} and user.tenant_id and user.tenant_id != tenant_id:
        abort(403, description='无权访问此企业信息')
    total_batches, total_drugs, total_quantity, latest_update = db.session.query(
        func.count(InventoryItem.id),
        func.count(func.distinct(InventoryItem.drug_id)),
        func.coalesce(func.sum(InventoryItem.quantity), 0),
        func.max(InventoryItem.updated_at)
    ).filter(InventoryItem.tenant_id == tenant_id).first()

    return jsonify({
        'tenant': tenant.to_dict(),
        'stats': {
            'total_batches': total_batches or 0,
            'unique_drugs': total_drugs or 0,
            'total_quantity': int(total_quantity or 0),
            'latest_update': latest_update.isoformat() if latest_update else None
        }
    })


@bp.route('/inventory', methods=['GET'])
def list_inventory():
    keyword = (request.args.get('keyword') or '').strip()
    tenant_id = parse_int(request.args.get('tenant_id'), None)
    drug_id = parse_int(request.args.get('drug_id'), None)

    # 若为已登录的药店/供应商用户，强制限定 tenant_id 为其所属企业
    try:
        user = get_authenticated_user()
    except Exception:
        user = None
    # 禁止物流用户访问库存管理接口
    if user and user.role == 'logistics':
        abort(403, description='权限不足：物流用户无法查看库存管理')

    if user and user.role in {'pharmacy', 'supplier'}:
        if not user.tenant_id:
            abort(403, description='未关联企业，无法查看库存')
        if tenant_id and tenant_id != user.tenant_id:
            abort(403, description='无权查看其他企业库存')
        tenant_id = user.tenant_id

    query = InventoryItem.query.options(
        joinedload(InventoryItem.drug),
        joinedload(InventoryItem.tenant),
    )
    if keyword:
        like = f"%{keyword}%"
        query = query.join(InventoryItem.drug).join(InventoryItem.tenant).filter(
            or_(
                InventoryItem.batch_number.ilike(like),
                Drug.generic_name.ilike(like),
                Drug.brand_name.ilike(like),
                Tenant.name.ilike(like),
            )
        )
    if tenant_id:
        query = query.filter(InventoryItem.tenant_id == tenant_id)
    if drug_id:
        query = query.filter(InventoryItem.drug_id == drug_id)

    query = query.order_by(InventoryItem.id.desc())
    return jsonify(paginate_query(query, lambda item: item.to_dict(include_related=True)))


@bp.route('/price/compare', methods=['GET'])
def compare_drug_prices():
    """
    药品价格对比接口
    
    查询参数:
    - drug_name: 药品名称（必填）
    - sort: 排序方式（price_asc/price_desc），默认 price_asc
    
    返回指定药品在各药房/供应商的价格列表
    """
    drug_name = (request.args.get('drug_name') or '').strip()
    sort = (request.args.get('sort') or 'price_asc').strip()
    
    if not drug_name:
        return jsonify({
            'success': False,
            'msg': '请输入药品名称',
            'items': []
        }), 400
    
    # 先查找匹配的药品
    like = f"%{drug_name}%"
    drugs = Drug.query.filter(
        or_(
            Drug.generic_name.ilike(like),
            Drug.brand_name.ilike(like)
        )
    ).all()
    
    if not drugs:
        return jsonify({
            'success': True,
            'msg': '未找到匹配的药品',
            'items': [],
            'total': 0
        })
    
    drug_ids = [d.id for d in drugs]
    
    # 查询这些药品的有效供应信息
    query = db.session.query(SupplyInfo).options(
        joinedload(SupplyInfo.drug),
        joinedload(SupplyInfo.tenant)
    ).filter(
        SupplyInfo.drug_id.in_(drug_ids),
        SupplyInfo.status == 'ACTIVE',
        SupplyInfo.valid_until > date.today(),
        SupplyInfo.available_quantity > 0
    )
    
    # 排序
    if sort == 'price_desc':
        query = query.order_by(SupplyInfo.unit_price.desc())
    else:
        query = query.order_by(SupplyInfo.unit_price.asc())
    
    supply_list = query.all()
    
    # 格式化结果
    items = []
    for s in supply_list:
        items.append({
            'supply_id': s.id,
            'drug_id': s.drug_id,
            'drug_name': s.drug.generic_name if s.drug else '',
            'brand_name': s.drug.brand_name if s.drug else '',
            'specification': s.drug.specification if s.drug else '',
            'manufacturer': s.drug.manufacturer if s.drug else '',
            'supplier_id': s.tenant_id,
            'supplier_name': s.tenant.name if s.tenant else '',
            'supplier_type': s.tenant.type if s.tenant else '',
            'unit_price': float(s.unit_price) if s.unit_price else 0,
            'available_quantity': s.available_quantity,
            'min_order_quantity': s.min_order_quantity,
            'valid_until': s.valid_until.isoformat() if s.valid_until else None
        })
    
    return jsonify({
        'success': True,
        'msg': f'找到 {len(items)} 条价格信息',
        'items': items,
        'total': len(items)
    })
