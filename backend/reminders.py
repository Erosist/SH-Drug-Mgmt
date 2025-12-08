"""
用药提醒模块 - CRUD接口
"""
from datetime import datetime, date
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import MedicationReminder, Drug, User
from extensions import db

bp = Blueprint('reminders', __name__, url_prefix='/api/reminders')


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_pagination_args():
    page = parse_int(request.args.get('page'), 1)
    per_page = parse_int(request.args.get('per_page'), 10)
    page = max(page or 1, 1)
    per_page = max(min(per_page or 10, 50), 1)
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


@bp.route('', methods=['GET'])
@jwt_required()
def list_reminders():
    """
    获取当前用户的用药提醒列表
    
    查询参数:
    - is_active: 筛选启用/禁用状态 (true/false)
    - page: 页码
    - per_page: 每页数量
    """
    user_id = get_jwt_identity()
    
    query = MedicationReminder.query.filter_by(user_id=user_id)
    
    # 筛选状态
    is_active = request.args.get('is_active', '').lower().strip()
    if is_active in {'true', 'false'}:
        query = query.filter(MedicationReminder.is_active == (is_active == 'true'))
    
    query = query.order_by(MedicationReminder.created_at.desc())
    
    result = paginate_query(query, lambda r: r.to_dict())
    result['success'] = True
    return jsonify(result)


@bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_reminders():
    """
    获取当前用户今日的用药提醒
    返回今日需要提醒的药品列表
    """
    user_id = get_jwt_identity()
    today = date.today()
    
    reminders = MedicationReminder.query.filter(
        MedicationReminder.user_id == user_id,
        MedicationReminder.is_active == True,
        MedicationReminder.start_date <= today,
        db.or_(
            MedicationReminder.end_date.is_(None),
            MedicationReminder.end_date >= today
        )
    ).order_by(MedicationReminder.drug_name.asc()).all()
    
    # 整理今日提醒数据
    items = []
    for r in reminders:
        for time_str in (r.remind_times or []):
            items.append({
                'id': r.id,
                'drug_name': r.drug_name,
                'dosage': r.dosage,
                'remind_time': time_str,
                'notes': r.notes
            })
    
    # 按时间排序
    items.sort(key=lambda x: x['remind_time'])
    
    return jsonify({
        'success': True,
        'date': today.isoformat(),
        'items': items,
        'total': len(items)
    })


@bp.route('/<int:reminder_id>', methods=['GET'])
@jwt_required()
def get_reminder(reminder_id):
    """获取单个用药提醒详情"""
    user_id = get_jwt_identity()
    
    reminder = MedicationReminder.query.filter_by(
        id=reminder_id,
        user_id=user_id
    ).first()
    
    if not reminder:
        return jsonify({
            'success': False,
            'msg': '提醒不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': reminder.to_dict()
    })


@bp.route('', methods=['POST'])
@jwt_required()
def create_reminder():
    """
    创建用药提醒
    
    请求体:
    {
        "drug_name": "阿莫西林",
        "drug_id": 1,  // 可选
        "dosage": "每次2粒",
        "frequency": "daily",
        "remind_times": ["08:00", "20:00"],
        "start_date": "2025-12-06",
        "end_date": "2025-12-31",  // 可选
        "notes": "饭后服用"  // 可选
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    # 验证必填字段
    required = ['drug_name', 'dosage', 'frequency', 'remind_times', 'start_date']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({
            'success': False,
            'msg': f'缺少必填字段: {", ".join(missing)}'
        }), 400
    
    # 验证 remind_times 格式
    remind_times = data.get('remind_times', [])
    if not isinstance(remind_times, list) or len(remind_times) == 0:
        return jsonify({
            'success': False,
            'msg': '提醒时间必须是非空数组'
        }), 400
    
    # 验证日期格式
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({
            'success': False,
            'msg': '开始日期格式错误，应为 YYYY-MM-DD'
        }), 400
    
    end_date = None
    if data.get('end_date'):
        try:
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'msg': '结束日期格式错误，应为 YYYY-MM-DD'
            }), 400
    
    # 验证 drug_id（如果提供）
    drug_id = data.get('drug_id')
    if drug_id:
        drug = Drug.query.get(drug_id)
        if not drug:
            return jsonify({
                'success': False,
                'msg': '关联的药品不存在'
            }), 400
    
    # 创建提醒
    reminder = MedicationReminder(
        user_id=user_id,
        drug_id=drug_id,
        drug_name=data['drug_name'],
        dosage=data['dosage'],
        frequency=data['frequency'],
        remind_times=remind_times,
        start_date=start_date,
        end_date=end_date,
        is_active=True,
        notes=data.get('notes')
    )
    
    db.session.add(reminder)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'msg': '创建成功',
        'data': reminder.to_dict()
    }), 201


@bp.route('/<int:reminder_id>', methods=['PUT'])
@jwt_required()
def update_reminder(reminder_id):
    """
    更新用药提醒
    
    可更新字段: drug_name, drug_id, dosage, frequency, remind_times, 
               start_date, end_date, is_active, notes
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    reminder = MedicationReminder.query.filter_by(
        id=reminder_id,
        user_id=user_id
    ).first()
    
    if not reminder:
        return jsonify({
            'success': False,
            'msg': '提醒不存在'
        }), 404
    
    # 更新字段
    if 'drug_name' in data:
        reminder.drug_name = data['drug_name']
    
    if 'drug_id' in data:
        if data['drug_id']:
            drug = Drug.query.get(data['drug_id'])
            if not drug:
                return jsonify({
                    'success': False,
                    'msg': '关联的药品不存在'
                }), 400
        reminder.drug_id = data['drug_id']
    
    if 'dosage' in data:
        reminder.dosage = data['dosage']
    
    if 'frequency' in data:
        reminder.frequency = data['frequency']
    
    if 'remind_times' in data:
        if not isinstance(data['remind_times'], list) or len(data['remind_times']) == 0:
            return jsonify({
                'success': False,
                'msg': '提醒时间必须是非空数组'
            }), 400
        reminder.remind_times = data['remind_times']
    
    if 'start_date' in data:
        try:
            reminder.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'msg': '开始日期格式错误'
            }), 400
    
    if 'end_date' in data:
        if data['end_date']:
            try:
                reminder.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'msg': '结束日期格式错误'
                }), 400
        else:
            reminder.end_date = None
    
    if 'is_active' in data:
        reminder.is_active = bool(data['is_active'])
    
    if 'notes' in data:
        reminder.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'msg': '更新成功',
        'data': reminder.to_dict()
    })


@bp.route('/<int:reminder_id>', methods=['DELETE'])
@jwt_required()
def delete_reminder(reminder_id):
    """删除用药提醒"""
    user_id = get_jwt_identity()
    
    reminder = MedicationReminder.query.filter_by(
        id=reminder_id,
        user_id=user_id
    ).first()
    
    if not reminder:
        return jsonify({
            'success': False,
            'msg': '提醒不存在'
        }), 404
    
    db.session.delete(reminder)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'msg': '删除成功'
    })


@bp.route('/<int:reminder_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_reminder(reminder_id):
    """切换提醒启用/禁用状态"""
    user_id = get_jwt_identity()
    
    reminder = MedicationReminder.query.filter_by(
        id=reminder_id,
        user_id=user_id
    ).first()
    
    if not reminder:
        return jsonify({
            'success': False,
            'msg': '提醒不存在'
        }), 404
    
    reminder.is_active = not reminder.is_active
    db.session.commit()
    
    status = '启用' if reminder.is_active else '禁用'
    return jsonify({
        'success': True,
        'msg': f'已{status}该提醒',
        'is_active': reminder.is_active
    })
