from datetime import datetime, timedelta
import secrets
import string

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from extensions import db
from models import User, PasswordResetCode

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

ALLOWED_ROLES = {'pharmacy', 'supplier', 'logistics', 'regulator', 'admin', 'unauth'}
RESET_CODE_TTL_MINUTES = 10
CONTACT_CHANNELS = {'email', 'phone'}


def normalize_email(email: str) -> str:
    return (email or '').strip().lower()


def normalize_phone(phone: str) -> str:
    digits = ''.join(ch for ch in (phone or '') if ch.isdigit())
    return digits


def validate_password_strength(password: str):
    password = password or ''
    errors = []
    if len(password) < 8:
        errors.append('密码长度至少8位')
    if not any(ch.islower() for ch in password):
        errors.append('至少包含一个小写字母')
    if not any(ch.isupper() for ch in password):
        errors.append('至少包含一个大写字母')
    if not any(ch.isdigit() for ch in password):
        errors.append('至少包含一个数字')
    return errors


def find_user_by_identifier(identifier: str):
    if not identifier:
        return None
    ident = identifier.strip()
    return User.query.filter(
        or_(
            User.username == ident,
            User.email == normalize_email(ident),
            User.phone == normalize_phone(ident)
        )
    ).first()


def generate_numeric_code(length: int = 6) -> str:
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))


def get_authenticated_user():
    identity = get_jwt_identity()
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return User.query.get(user_id)


def ensure_admin(user: User):
    return user and user.role == 'admin'

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email_raw = data.get('email') or ''
    email = normalize_email(email_raw)
    phone_raw = data.get('phone') or ''
    phone = normalize_phone(phone_raw)
    password = data.get('password')
    role = 'unauth'

    if not username or not email or not password:
        return jsonify({'msg': '用户名、邮箱和密码均为必填项'}), 400

    if phone and (len(phone) < 6 or len(phone) > 20):
        return jsonify({'msg': '手机号格式不正确'}), 400

    password_errors = validate_password_strength(password)
    if password_errors:
        return jsonify({'msg': '密码不符合安全策略', 'errors': password_errors}), 400

    duplicate_filters = [User.username == username, User.email == email]
    if phone:
        duplicate_filters.append(User.phone == phone)

    if User.query.filter(or_(*duplicate_filters)).first():
        return jsonify({'msg': '用户名、邮箱或手机号已存在'}), 400

    user = User(username=username, email=email, phone=phone or None, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'user created', 'user': user.to_dict()}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    identifier = data.get('username')
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'msg': 'username and password are required'}), 400

    user = find_user_by_identifier(identifier)
    if not user or not user.check_password(password):
        return jsonify({'msg': 'bad username or password'}), 401
    if not user.is_active:
        return jsonify({'msg': '账户已被禁用'}), 403

    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token, 
        'user': user.to_dict(include_relations=True)
    })

@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': 'user not found'}), 404
    return jsonify({'user': user.to_dict()})


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': 'user not found'}), 404

    data = request.get_json() or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'msg': 'old_password and new_password are required'}), 400

    if not user.check_password(old_password):
        return jsonify({'msg': '旧密码验证失败'}), 400

    if old_password == new_password:
        return jsonify({'msg': '新密码不能与旧密码相同'}), 400

    password_errors = validate_password_strength(new_password)
    if password_errors:
        return jsonify({'msg': '新密码不符合安全策略', 'errors': password_errors}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'msg': '密码修改成功，请重新登录'}), 200


@bp.route('/request-reset-code', methods=['POST'])
def request_reset_code():
    data = request.get_json() or {}
    identifier = data.get('identifier')
    channel = (data.get('channel') or '').lower()
    contact_value_raw = data.get('contact') or ''

    if not identifier or not channel or not contact_value_raw:
        return jsonify({'msg': 'identifier, channel, contact are required'}), 400

    if channel not in CONTACT_CHANNELS:
        return jsonify({'msg': 'channel must be email or phone'}), 400

    user = find_user_by_identifier(identifier)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404

    if channel == 'email':
        expected = normalize_email(user.email)
        provided = normalize_email(contact_value_raw)
    else:
        expected = normalize_phone(user.phone or '')
        provided = normalize_phone(contact_value_raw)

    if not expected:
        return jsonify({'msg': f'当前账户未绑定{channel}，无法使用该方式找回密码'}), 400

    if expected != provided:
        return jsonify({'msg': '绑定信息与账户不匹配'}), 400

    code_plain = generate_numeric_code()
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_CODE_TTL_MINUTES)
    reset_code = PasswordResetCode(
        user_id=user.id,
        channel=channel,
        contact_value=expected,
        code_hash=generate_password_hash(code_plain),
        expires_at=expires_at
    )
    db.session.add(reset_code)
    db.session.commit()

    current_app.logger.info(
        'Reset code generated for user %s via %s (expires %s)',
        user.username,
        channel,
        expires_at.isoformat()
    )

    response = {
        'msg': '验证码已发送',
        'expires_in': RESET_CODE_TTL_MINUTES * 60
    }

    if current_app.config.get('DEBUG'):
        response['debug_code'] = code_plain

    return jsonify(response), 200


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    identifier = data.get('identifier')
    channel = (data.get('channel') or '').lower()
    contact_value_raw = data.get('contact') or ''
    code = data.get('code')
    new_password = data.get('new_password')

    if not all([identifier, channel, contact_value_raw, code, new_password]):
        return jsonify({'msg': 'identifier, channel, contact, code, new_password are required'}), 400

    if channel not in CONTACT_CHANNELS:
        return jsonify({'msg': 'channel must be email or phone'}), 400

    user = find_user_by_identifier(identifier)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404

    expected = normalize_email(user.email) if channel == 'email' else normalize_phone(user.phone or '')
    provided = normalize_email(contact_value_raw) if channel == 'email' else normalize_phone(contact_value_raw)

    if not expected:
        return jsonify({'msg': f'当前账户未绑定{channel}，无法使用该方式找回密码'}), 400

    if expected != provided:
        return jsonify({'msg': '绑定信息与账户不匹配'}), 400

    password_errors = validate_password_strength(new_password)
    if password_errors:
        return jsonify({'msg': '新密码不符合安全策略', 'errors': password_errors}), 400

    reset_code = PasswordResetCode.query.filter_by(
        user_id=user.id,
        channel=channel,
        used=False
    ).order_by(PasswordResetCode.created_at.desc()).first()

    if (not reset_code) or reset_code.contact_value != expected:
        return jsonify({'msg': '验证码无效，请重新获取'}), 400

    if reset_code.expires_at < datetime.utcnow():
        reset_code.used = True
        db.session.commit()
        return jsonify({'msg': '验证码已过期，请重新获取'}), 400

    if not reset_code.verify_code(code):
        return jsonify({'msg': '验证码错误'}), 400

    reset_code.used = True
    user.set_password(new_password)
    db.session.commit()

    return jsonify({'msg': '密码已重置，请使用新密码登录'}), 200


@bp.route('/admin/reset-user-password', methods=['POST'])
@jwt_required()
def admin_reset_user_password():
    admin_user = get_authenticated_user()
    if not ensure_admin(admin_user):
        return jsonify({'msg': '仅管理员可执行此操作'}), 403

    data = request.get_json() or {}
    user_id = data.get('user_id')
    identifier = data.get('identifier')
    new_password = data.get('new_password')

    if not new_password or not (user_id or identifier):
        return jsonify({'msg': 'user_id/identifier 与 new_password 为必填项'}), 400

    target_user = None
    if user_id is not None:
        try:
            target_user = User.query.get(int(user_id))
        except (TypeError, ValueError):
            return jsonify({'msg': 'user_id 必须为整数'}), 400

    if not target_user and identifier:
        target_user = find_user_by_identifier(identifier)

    if not target_user:
        return jsonify({'msg': '目标用户不存在'}), 404

    if target_user.id == admin_user.id:
        return jsonify({'msg': '无法通过此接口重置自身密码'}), 400

    password_errors = validate_password_strength(new_password)
    if password_errors:
        return jsonify({'msg': '新密码不符合安全策略', 'errors': password_errors}), 400

    target_user.set_password(new_password)
    target_user.updated_at = datetime.utcnow()
    db.session.commit()

    current_app.logger.info(
        'Admin %s reset password for user %s',
        admin_user.username,
        target_user.username
    )

    return jsonify({'msg': '用户密码已由管理员重置'}), 200
