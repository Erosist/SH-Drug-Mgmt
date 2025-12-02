import csv
import io
from datetime import datetime, timedelta

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func, or_

from extensions import db
from audit import record_admin_action
from auth import (
    get_authenticated_user,
    normalize_email,
    normalize_phone,
    validate_password_strength,
    ALLOWED_ROLES,
)
from models import (
    User,
    EnterpriseCertification,
    InventoryItem,
    Order,
    SupplyInfo,
    Tenant,
    to_iso,
    AdminAuditLog,
)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _require_admin(user: User):
    return user and user.role == 'admin'


def _parse_bool(value, default=None):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'y', 'on'}
    return bool(value)


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _paginate(query):
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        per_page = 10
    page = max(page, 1)
    per_page = max(min(per_page, 100), 1)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination


def _serialize_certification(cert: EnterpriseCertification, brief: bool = True):
    if not cert:
        return None

    if brief:
        return {
            'status': cert.status,
            'role': cert.role,
            'submitted_at': to_iso(cert.submitted_at),
            'reviewed_at': to_iso(cert.reviewed_at),
            'attempt_count': cert.attempt_count,
            'reject_reason': cert.reject_reason,
        }
    return cert.to_dict()


def _build_user_payload(user: User, cert: EnterpriseCertification = None, include_relations: bool = False, brief_cert: bool = True):
    data = user.to_dict(include_relations=include_relations)
    data['certification'] = _serialize_certification(cert, brief=brief_cert)
    return data


USER_EXPORT_FIELDS = [
    'id', 'username', 'email', 'phone', 'real_name', 'company_name',
    'role', 'tenant_id', 'is_authenticated', 'is_active', 'created_at', 'updated_at'
]


def _build_export_row(user: User):
    payload = user.to_dict()
    return {field: payload.get(field) for field in USER_EXPORT_FIELDS}


def _get_cert_map(user_ids):
    if not user_ids:
        return {}
    certs = EnterpriseCertification.query.filter(
        EnterpriseCertification.user_id.in_(user_ids)
    ).all()
    return {c.user_id: c for c in certs}


@bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可操作'}), 403

    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email = normalize_email(data.get('email'))
    password = data.get('password') or ''
    phone = normalize_phone(data.get('phone'))
    role = (data.get('role') or 'unauth').lower()

    if not username or not email or not password:
        return jsonify({'msg': 'username、email、password 为必填项'}), 400

    if role not in ALLOWED_ROLES:
        return jsonify({'msg': f'角色必须在 {", ".join(sorted(ALLOWED_ROLES))} 中选择'}), 400

    duplicate_filters = [User.username == username, User.email == email]
    if phone:
        duplicate_filters.append(User.phone == phone)

    if User.query.filter(or_(*duplicate_filters)).first():
        return jsonify({'msg': '用户名、邮箱或手机号已存在'}), 400

    password_errors = validate_password_strength(password)
    if password_errors:
        return jsonify({'msg': '密码不符合安全策略', 'errors': password_errors}), 400

    tenant_id = data.get('tenant_id')
    tenant = None
    if tenant_id is not None:
        try:
            tenant_id = int(tenant_id)
        except (TypeError, ValueError):
            return jsonify({'msg': 'tenant_id 必须为整数'}), 400
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'msg': 'tenant_id 无效'}), 400

    user = User(
        username=username,
        email=email,
        phone=phone or None,
        real_name=(data.get('real_name') or '').strip() or None,
        company_name=(data.get('company_name') or '').strip() or None,
        role=role,
        tenant_id=tenant_id if tenant else None,
        is_authenticated=_parse_bool(data.get('is_authenticated'), role != 'unauth'),
        is_active=_parse_bool(data.get('is_active'), True),
    )
    user.set_password(password)

    db.session.add(user)
    db.session.flush()

    record_admin_action(
        admin,
        'create_user',
        target_user_id=user.id,
        resource_type='user',
        resource_id=user.id,
        details={'username': user.username, 'role': user.role, 'tenant_id': user.tenant_id},
    )

    db.session.commit()

    return jsonify({'msg': '用户创建成功', 'user': user.to_dict()}), 201


@bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可访问'}), 403

    keyword = (request.args.get('keyword') or '').strip()
    role = (request.args.get('role') or '').strip()
    status = (request.args.get('status') or '').strip().lower()

    query = User.query
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(or_(
            User.username.ilike(like),
            User.real_name.ilike(like),
            User.company_name.ilike(like),
        ))
    if role:
        query = query.filter(User.role == role)
    if status in {'enabled', 'disabled'}:
        query = query.filter(User.is_active == (status == 'enabled'))

    query = query.order_by(User.id.desc())
    pagination = _paginate(query)

    user_ids = [u.id for u in pagination.items]
    cert_map = _get_cert_map(user_ids)

    record_admin_action(
        admin,
        'list_users',
        details={
            'keyword': keyword,
            'role': role,
            'status': status,
            'page': pagination.page,
            'per_page': pagination.per_page,
        },
        commit=True,
    )

    return jsonify({
        'items': [_build_user_payload(u, cert_map.get(u.id), brief_cert=True) for u in pagination.items],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
    })


@bp.route('/users/export', methods=['GET'])
@jwt_required()
def export_users():
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可访问'}), 403

    export_format = (request.args.get('format') or 'csv').strip().lower()
    users = User.query.order_by(User.id.asc()).all()
    rows = [_build_export_row(u) for u in users]

    record_admin_action(
        admin,
        'export_users',
        details={'format': export_format, 'count': len(rows)},
        commit=True,
    )

    if export_format == 'json':
        return jsonify({'items': rows, 'total': len(rows)})

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=USER_EXPORT_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)

    filename = f"users-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    return Response(
        buffer.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )


@bp.route('/users/<int:user_id>/status', methods=['POST'])
@jwt_required()
def update_user_status(user_id):
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可操作'}), 403

    if admin.id == user_id:
        return jsonify({'msg': '无法修改自己的状态'}), 400

    data = request.get_json() or {}
    action = (data.get('action') or '').lower()
    if action not in {'enable', 'disable'}:
        return jsonify({'msg': 'action must be enable or disable'}), 400

    user = User.query.get_or_404(user_id)
    user.is_active = action == 'enable'
    user.updated_at = datetime.utcnow()

    audit_action = 'enable_user' if user.is_active else 'disable_user'
    record_admin_action(
        admin,
        audit_action,
        target_user_id=user.id,
        resource_type='user',
        resource_id=user.id,
        details={'action': action, 'is_active': user.is_active},
    )

    db.session.commit()

    return jsonify({'msg': '状态已更新', 'user': user.to_dict()})


@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_detail(user_id):
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可访问'}), 403

    user = User.query.get_or_404(user_id)
    cert = EnterpriseCertification.query.filter_by(user_id=user.id).first()

    record_admin_action(
        admin,
        'get_user_detail',
        target_user_id=user.id,
        resource_type='user',
        resource_id=user.id,
        commit=True,
    )

    return jsonify({'user': _build_user_payload(user, cert, include_relations=True, brief_cert=False)})


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可操作'}), 403

    if user_id == admin.id:
        return jsonify({'msg': '不能删除当前登录的管理员'}), 400

    user = User.query.get_or_404(user_id)

    related_order = Order.query.filter(
        or_(
            Order.created_by == user.id,
            Order.confirmed_by == user.id,
            Order.received_confirmed_by == user.id,
            Order.cancelled_by == user.id,
        )
    ).first()
    if related_order:
        return jsonify({'msg': '该用户存在关联订单，无法删除，请先禁用账户'}), 400

    cert_exists = EnterpriseCertification.query.filter_by(user_id=user.id).first()
    if cert_exists:
        return jsonify({'msg': '该用户有进行中的企业认证，无法删除'}), 400

    db.session.delete(user)
    record_admin_action(
        admin,
        'delete_user',
        target_user_id=user.id,
        resource_type='user',
        resource_id=user.id,
        details={'username': user.username, 'role': user.role},
    )
    db.session.commit()

    return jsonify({'msg': '用户已删除'})


@bp.route('/users/<int:user_id>/role', methods=['POST'])
@jwt_required()
def update_user_role(user_id):
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可操作'}), 403

    if user_id == admin.id:
        return jsonify({'msg': '无法通过此接口修改自身角色'}), 400

    data = request.get_json() or {}
    target_role = (data.get('role') or '').lower()
    if target_role not in ALLOWED_ROLES:
        return jsonify({'msg': f'role 必须在 {", ".join(sorted(ALLOWED_ROLES))} 范围内'}), 400

    user = User.query.get_or_404(user_id)
    user.role = target_role
    if 'mark_authenticated' in data:
        user.is_authenticated = bool(data.get('mark_authenticated'))
    user.updated_at = datetime.utcnow()
    record_admin_action(
        admin,
        'update_user_role',
        target_user_id=user.id,
        resource_type='user',
        resource_id=user.id,
        details={'new_role': user.role, 'mark_authenticated': user.is_authenticated},
    )
    db.session.commit()

    cert = EnterpriseCertification.query.filter_by(user_id=user.id).first()
    return jsonify({'msg': '角色已更新', 'user': _build_user_payload(user, cert, brief_cert=False)})


@bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def list_audit_logs():
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可访问'}), 403

    query = AdminAuditLog.query

    admin_id = request.args.get('admin_id')
    action = (request.args.get('action') or '').strip()
    target_user_id = request.args.get('target_user_id')
    start = _parse_datetime(request.args.get('start'))
    end = _parse_datetime(request.args.get('end'))

    if admin_id:
        try:
            query = query.filter(AdminAuditLog.admin_id == int(admin_id))
        except (TypeError, ValueError):
            return jsonify({'msg': 'admin_id 必须为整数'}), 400
    if target_user_id:
        try:
            query = query.filter(AdminAuditLog.target_user_id == int(target_user_id))
        except (TypeError, ValueError):
            return jsonify({'msg': 'target_user_id 必须为整数'}), 400
    if action:
        query = query.filter(AdminAuditLog.action == action)
    if start:
        query = query.filter(AdminAuditLog.created_at >= start)
    if end:
        query = query.filter(AdminAuditLog.created_at <= end)

    query = query.order_by(AdminAuditLog.created_at.desc())
    pagination = _paginate(query)

    record_admin_action(
        admin,
        'list_audit_logs',
        details={
            'admin_id': admin_id,
            'action': action,
            'target_user_id': target_user_id,
            'page': pagination.page,
        },
        commit=True,
    )

    return jsonify({
        'items': [log.to_dict(include_users=True) for log in pagination.items],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
    })


@bp.route('/system/status', methods=['GET'])
@jwt_required()
def system_status():
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'msg': '仅系统管理员可访问'}), 403

    now = datetime.utcnow()
    today = now.date()
    near_expiry_threshold = today + timedelta(days=30)

    user_stats = {
        'total': db.session.query(func.count(User.id)).scalar() or 0,
        'active': db.session.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0,
        'disabled': db.session.query(func.count(User.id)).filter(User.is_active.is_(False)).scalar() or 0,
        'new_last_7_days': db.session.query(func.count(User.id)).filter(User.created_at >= now - timedelta(days=7)).scalar() or 0,
    }

    cert_stats = {
        'pending': db.session.query(func.count(EnterpriseCertification.id)).filter(EnterpriseCertification.status == 'pending').scalar() or 0,
        'approved': db.session.query(func.count(EnterpriseCertification.id)).filter(EnterpriseCertification.status == 'approved').scalar() or 0,
        'rejected': db.session.query(func.count(EnterpriseCertification.id)).filter(EnterpriseCertification.status == 'rejected').scalar() or 0,
    }

    order_counts = dict(
        db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    )
    order_stats = {
        'total': sum(order_counts.values()),
        'by_status': order_counts,
    }

    inventory_stats = {
        'total_items': db.session.query(func.count(InventoryItem.id)).scalar() or 0,
        'low_stock': db.session.query(func.count(InventoryItem.id)).filter(InventoryItem.quantity < 10).scalar() or 0,
        'near_expiry': db.session.query(func.count(InventoryItem.id)).filter(InventoryItem.expiry_date <= near_expiry_threshold).scalar() or 0,
        'expired': db.session.query(func.count(InventoryItem.id)).filter(InventoryItem.expiry_date < today).scalar() or 0,
    }

    supply_stats = {
        'active_supplies': db.session.query(func.count(SupplyInfo.id)).filter(SupplyInfo.status == 'ACTIVE').scalar() or 0,
        'inactive_supplies': db.session.query(func.count(SupplyInfo.id)).filter(SupplyInfo.status != 'ACTIVE').scalar() or 0,
    }

    payload = {
        'generated_at': now.isoformat(),
        'users': user_stats,
        'certifications': cert_stats,
        'orders': order_stats,
        'inventory': inventory_stats,
        'supply': supply_stats,
    }

    record_admin_action(
        admin,
        'system_status',
        details={'snapshot_time': payload['generated_at']},
        commit=True,
    )

    return jsonify(payload)
