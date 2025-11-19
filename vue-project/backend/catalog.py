from flask import Blueprint, jsonify, request
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload

from models import Drug, InventoryItem, Tenant
from extensions import db
from models import Drug, InventoryItem, TenantPharmacy

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
    tenant = TenantPharmacy.query.get_or_404(tenant_id)
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
