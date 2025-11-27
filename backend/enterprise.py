from datetime import datetime, timedelta
from pathlib import Path
import os

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from extensions import db
from models import EnterpriseCertification, EnterpriseReviewLog, User, Tenant, to_iso
from auth import get_authenticated_user

bp = Blueprint('enterprise', __name__, url_prefix='/api/enterprise')

UPLOAD_DIR_NAME = 'uploads'
ALLOWED_UPLOAD_EXTS = {'jpg', 'jpeg', 'png', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_RESUBMIT = 3
REVIEW_TARGET_DAYS = 3
SUPPORTED_ROLES = {'pharmacy', 'supplier', 'logistics'}
ROLE_TO_TENANT_TYPE = {
    'pharmacy': 'PHARMACY',
    'supplier': 'SUPPLIER',
    'logistics': 'LOGISTICS'
}

ROLE_REQUIREMENTS = {
    'pharmacy': {
        'label': '药店用户（PHARMACY）',
        'docs': ['药品经营许可证', '营业执照（可选上传）'],
        'note': '可上传执照与许可证，用于验证零售资质'
    },
    'supplier': {
        'label': '供应商用户（SUPPLIER）',
        'docs': ['药品生产/经营许可证（批发）', '营业执照（可选上传）'],
        'note': '侧重生产/批发资质，至少提供基础信息'
    },
    'logistics': {
        'label': '物流用户（LOGISTICS）',
        'docs': ['道路运输经营许可证', '营业执照（可选上传）'],
        'note': '上传冷链/运输证明可加速审核'
    }
}

BASE_REQUIRED_FIELDS = [
    'company_name',
    'unified_social_credit_code',
    'contact_person',
    'contact_phone',
    'contact_email',
    'registered_address',
    'business_scope',
]

COMMON_STANDARDS = [
    '营业执照真实有效、信息清晰',
    '在线填写的企业信息与证件信息一致',
]

ROLE_STANDARDS = {
    'pharmacy': ['具备有效的《药品经营许可证》（零售）'],
    'supplier': ['具备有效的《药品生产许可证》或《药品经营许可证》（批发）'],
    'logistics': ['具备有效的《道路运输经营许可证》'],
}

REJECT_REASONS = [
    {'code': 'license_blurry', 'label': '营业执照信息不清晰'},
    {'code': 'name_mismatch', 'label': '企业名称与证件不符'},
    {'code': 'missing_retail_license', 'label': '缺少药品经营许可证（零售）'},
    {'code': 'license_expired', 'label': '药品经营许可证已过期'},
    {'code': 'missing_transport_license', 'label': '缺少道路运输经营许可证'},
]


def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_UPLOAD_EXTS


def _save_files(user_id: int):
    saved = []
    upload_dir = Path(current_app.instance_path) / UPLOAD_DIR_NAME / 'enterprise' / f'user_{user_id}'
    upload_dir.mkdir(parents=True, exist_ok=True)

    for file in request.files.getlist('files'):
        if not file.filename:
            continue
        if not _allowed_file(file.filename):
            raise ValueError(f'仅支持 {", ".join(sorted(ALLOWED_UPLOAD_EXTS))} 格式')

        file.stream.seek(0, os.SEEK_END)
        size = file.stream.tell()
        file.stream.seek(0)
        if size > MAX_FILE_SIZE:
            raise ValueError('单个文件大小不能超过 5MB')

        safe_name = secure_filename(f'{int(datetime.utcnow().timestamp())}_{file.filename}')
        file_path = upload_dir / safe_name
        file.save(file_path)

        saved.append({
            'name': file.filename,
            'stored_name': safe_name,
            'size': size,
            'mimetype': file.mimetype,
            'path': str(file_path),
        })
    return saved


@bp.route('/requirements', methods=['GET'])
def get_requirements():
    return jsonify({
        'roles': ROLE_REQUIREMENTS,
        'upload_policy': {
            'allowed_ext': sorted(ALLOWED_UPLOAD_EXTS),
            'max_size_mb': MAX_FILE_SIZE // (1024 * 1024),
            'optional_for': sorted(SUPPORTED_ROLES),
            'message': '药店/供应商/物流可选择是否上传资质，基础信息必填'
        },
        'base_required_fields': BASE_REQUIRED_FIELDS,
        'review_sla_days': REVIEW_TARGET_DAYS,
        'standards': {
            'common': COMMON_STANDARDS,
            'roles': ROLE_STANDARDS,
        },
        'reject_reasons': REJECT_REASONS,
    })


@bp.route('/me', methods=['GET'])
@jwt_required()
def my_certification():
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': '用户不存在'}), 404

    record = EnterpriseCertification.query.filter_by(user_id=user.id).first()
    attempts_used = record.attempt_count if record else 0
    return jsonify({
        'application': record.to_dict() if record else None,
        'max_attempts': MAX_RESUBMIT,
        'attempts_left': max(MAX_RESUBMIT - attempts_used, 0)
    })


def _require_admin(user: User):
    if not user or user.role != 'admin':
        return False
    return True


@bp.route('/applications', methods=['GET'])
@jwt_required()
def list_applications():
    reviewer = get_authenticated_user()
    if not _require_admin(reviewer):
        return jsonify({'msg': '仅系统管理员可查看认证申请列表'}), 403

    status = (request.args.get('status') or 'pending').lower()
    role = (request.args.get('role') or '').lower()

    query = EnterpriseCertification.query
    if status:
        query = query.filter(EnterpriseCertification.status == status)
    if role:
        query = query.filter(EnterpriseCertification.role == role)

    query = query.order_by(EnterpriseCertification.submitted_at.desc())
    items = [{
        'id': c.id,
        'user_id': c.user_id,
        'role': c.role,
        'company_name': c.company_name,
        'status': c.status,
        'submitted_at': to_iso(c.submitted_at),
        'attempt_count': c.attempt_count,
        'reject_reason': c.reject_reason,
    } for c in query.all()]

    return jsonify({
        'items': items,
        'standards': {
            'common': COMMON_STANDARDS,
            'roles': ROLE_STANDARDS,
        },
        'reject_reasons': REJECT_REASONS,
    })


@bp.route('/applications/<int:cert_id>', methods=['GET'])
@jwt_required()
def application_detail(cert_id):
    reviewer = get_authenticated_user()
    if not _require_admin(reviewer):
        return jsonify({'msg': '仅系统管理员可查看认证详情'}), 403

    record = EnterpriseCertification.query.get_or_404(cert_id)
    data = record.to_dict()
    data['standards'] = {
        'common': COMMON_STANDARDS,
        'roles': ROLE_STANDARDS.get(record.role, []),
    }
    data['reject_reasons'] = REJECT_REASONS
    data['review_logs'] = [log.to_dict() for log in (record.review_logs or [])]
    return jsonify({'application': data})


@bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_certification():
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': '用户不存在'}), 404

    # 支持 JSON 与 multipart/form-data
    data = request.form or (request.get_json(silent=True) or {})
    role = (data.get('role') or user.role or '').lower()

    if role in {'regulator', 'admin'} or (user.role or '').lower() in {'regulator', 'admin'}:
        return jsonify({'msg': '监管/管理员账号由系统管理员直接配置，无需走认证流程'}), 400
    if role not in SUPPORTED_ROLES:
        return jsonify({'msg': '角色类型仅支持 pharmacy/supplier/logistics'}), 400

    missing = [field for field in BASE_REQUIRED_FIELDS if not (data.get(field) or '').strip()]
    if missing:
        return jsonify({'msg': f'缺少必填项：{", ".join(missing)}'}), 400

    record = EnterpriseCertification.query.filter_by(user_id=user.id).first()
    if record and record.status == 'rejected' and record.attempt_count >= MAX_RESUBMIT:
        return jsonify({'msg': '认证已被驳回且重提次数已达上限，请联系管理员人工处理'}), 400

    qualification_files = []
    try:
        uploaded_files = _save_files(user.id)
        if uploaded_files:
            qualification_files = uploaded_files
    except ValueError as exc:
        return jsonify({'msg': str(exc)}), 400

    if not qualification_files and record and record.qualification_files:
        qualification_files = record.qualification_files

    now = datetime.utcnow()
    if record:
        if record.status == 'approved':
            return jsonify({'msg': '已通过审核，如需修改请联系管理员'}), 400
        if record.status == 'rejected':
            record.attempt_count += 1
        record.role = role
        record.company_name = data.get('company_name').strip()
        record.unified_social_credit_code = data.get('unified_social_credit_code').strip()
        record.contact_person = data.get('contact_person').strip()
        record.contact_phone = data.get('contact_phone').strip()
        record.contact_email = data.get('contact_email').strip()
        record.registered_address = data.get('registered_address').strip()
        record.business_scope = data.get('business_scope').strip()
        record.qualification_files = qualification_files
        record.status = 'pending'
        record.reject_reason = None
        record.submitted_at = now
        record.reviewed_at = None
        record.updated_at = now
    else:
        record = EnterpriseCertification(
            user_id=user.id,
            role=role,
            company_name=data.get('company_name').strip(),
            unified_social_credit_code=data.get('unified_social_credit_code').strip(),
            contact_person=data.get('contact_person').strip(),
            contact_phone=data.get('contact_phone').strip(),
            contact_email=data.get('contact_email').strip(),
            registered_address=data.get('registered_address').strip(),
            business_scope=data.get('business_scope').strip(),
            qualification_files=qualification_files,
            status='pending',
            submitted_at=now,
        )
        db.session.add(record)

    db.session.commit()

    return jsonify({
        'msg': '认证申请已提交，预计 3 个工作日完成审核。提交 24 小时后会提醒管理员处理。',
        'application': record.to_dict(),
        'attempts_left': max(MAX_RESUBMIT - record.attempt_count, 0),
        'review_eta': (now + timedelta(days=REVIEW_TARGET_DAYS)).isoformat()
    }), 201


def _record_review_log(certification_id: int, reviewer_id: int, decision: str, reason_code: str, reason_text: str):
    log = EnterpriseReviewLog(
        certification_id=certification_id,
        reviewer_id=reviewer_id,
        decision=decision,
        reason_code=reason_code,
        reason_text=reason_text
    )
    db.session.add(log)


def _upsert_tenant_from_cert(record: EnterpriseCertification):
    tenant_type = ROLE_TO_TENANT_TYPE.get(record.role)
    if not tenant_type:
        return None

    tenant = Tenant.query.filter_by(unified_social_credit_code=record.unified_social_credit_code).first()
    now = datetime.utcnow()

    if tenant:
        tenant.name = record.company_name
        tenant.type = tenant_type
        tenant.contact_person = record.contact_person
        tenant.contact_phone = record.contact_phone
        tenant.contact_email = record.contact_email
        tenant.address = record.registered_address
        tenant.business_scope = record.business_scope
        tenant.legal_representative = record.contact_person or tenant.legal_representative
        tenant.updated_at = now
    else:
        tenant = Tenant(
            name=record.company_name,
            type=tenant_type,
            unified_social_credit_code=record.unified_social_credit_code,
            legal_representative=record.contact_person or record.company_name,
            contact_person=record.contact_person,
            contact_phone=record.contact_phone,
            contact_email=record.contact_email,
            address=record.registered_address,
            business_scope=record.business_scope,
            is_active=True,
        )
        db.session.add(tenant)
        db.session.flush()

    return tenant


@bp.route('/review/<int:cert_id>', methods=['POST'])
@jwt_required()
def review_certification(cert_id):
    reviewer = get_authenticated_user()
    if not _require_admin(reviewer):
        return jsonify({'msg': '仅系统管理员可执行审核操作'}), 403

    record = EnterpriseCertification.query.get(cert_id)
    if not record:
        return jsonify({'msg': '未找到认证申请'}), 404

    data = request.get_json() or {}
    decision = (data.get('decision') or '').lower()
    reason_code = (data.get('reason_code') or '').strip()
    remark = (data.get('remark') or '').strip()

    if decision not in {'approved', 'rejected'}:
        return jsonify({'msg': 'decision 必须为 approved 或 rejected'}), 400

    if decision == 'rejected' and reason_code and reason_code not in {r['code'] for r in REJECT_REASONS}:
        return jsonify({'msg': '无效的驳回原因编码'}), 400
    if decision == 'rejected' and not reason_code:
        return jsonify({'msg': '驳回必须选择标准化原因'}), 400

    label_map = {r['code']: r['label'] for r in REJECT_REASONS}
    reject_reason = None
    if decision == 'rejected':
        base_reason = label_map.get(reason_code, '资料不符合要求')
        reject_reason = f'{base_reason}' + (f'；备注：{remark}' if remark else '')

    record.status = 'approved' if decision == 'approved' else 'rejected'
    record.reject_reason = reject_reason
    record.reviewed_at = datetime.utcnow()
    record.updated_at = datetime.utcnow()
    record.reviewer_id = reviewer.id

    if decision == 'approved':
        target_role = record.role if record.role in SUPPORTED_ROLES else 'unauth'
        user = User.query.get(record.user_id)
        if user and user.role != target_role:
            user.role = target_role
        if user:
            tenant = _upsert_tenant_from_cert(record)
            if tenant:
                user.tenant_id = tenant.id
            user.company_name = record.company_name
            user.is_authenticated = True
            user.updated_at = datetime.utcnow()

    _record_review_log(record.id, reviewer.id, decision, reason_code if decision == 'rejected' else None, reject_reason)
    db.session.commit()

    return jsonify({'msg': '审核结果已记录', 'application': record.to_dict()})
