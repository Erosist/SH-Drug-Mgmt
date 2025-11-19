from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from extensions import db
from auth import get_authenticated_user
from models import User, EnterpriseCertification, to_iso

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _require_regulator(user: User):
    return user and user.role == 'regulator'


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


@bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    admin = get_authenticated_user()
    if not _require_regulator(admin):
        return jsonify({'msg': '仅监管员可访问'}), 403

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
    cert_map = {}
    if user_ids:
      certs = EnterpriseCertification.query.filter(EnterpriseCertification.user_id.in_(user_ids)).all()
      cert_map = {c.user_id: c for c in certs}

    def build_payload(u: User):
        data = u.to_dict()
        cert = cert_map.get(u.id)
        if cert:
            data['certification'] = {
                'status': cert.status,
                'role': cert.role,
                'submitted_at': to_iso(cert.submitted_at),
                'reviewed_at': to_iso(cert.reviewed_at),
            }
        else:
            data['certification'] = None
        return data

    return jsonify({
        'items': [build_payload(u) for u in pagination.items],
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
    })


@bp.route('/users/<int:user_id>/status', methods=['POST'])
@jwt_required()
def update_user_status(user_id):
    admin = get_authenticated_user()
    if not _require_regulator(admin):
        return jsonify({'msg': '仅监管员可操作'}), 403

    data = request.get_json() or {}
    action = (data.get('action') or '').lower()
    if action not in {'enable', 'disable'}:
        return jsonify({'msg': 'action must be enable or disable'}), 400

    user = User.query.get_or_404(user_id)
    user.is_active = action == 'enable'
    user.updated_at = datetime.utcnow()

    # TODO: Add audit log persistence if needed
    db.session.commit()

    return jsonify({'msg': '状态已更新', 'user': user.to_dict()})
