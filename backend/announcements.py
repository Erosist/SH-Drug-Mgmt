"""
公告与资讯管理接口
支持健康资讯(health_news)和紧急通知(urgent_notice)的增删改查
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import desc

from extensions import db
from auth import get_authenticated_user
from models import Announcement, User

bp = Blueprint('announcements', __name__, url_prefix='/api/announcements')


def _require_admin(user: User):
    """检查是否为管理员"""
    return user and user.role == 'admin'


def _paginate(query):
    """分页处理"""
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except (TypeError, ValueError):
        per_page = 10
    page = max(page, 1)
    per_page = max(min(per_page, 100), 1)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination


@bp.route('', methods=['GET'])
def list_announcements():
    """
    获取公告列表
    查询参数：
    - type: 类型筛选 (health_news, urgent_notice)
    - status: 状态筛选 (active, inactive)
    - page: 页码
    - per_page: 每页数量
    """
    try:
        ann_type = request.args.get('type', '').strip()
        status = request.args.get('status', '').strip()
        
        query = Announcement.query
        
        if ann_type:
            query = query.filter(Announcement.type == ann_type)
        if status:
            query = query.filter(Announcement.status == status)
        
        query = query.order_by(desc(Announcement.publish_date), desc(Announcement.id))
        pagination = _paginate(query)
        
        return jsonify({
            'success': True,
            'items': [ann.to_dict() for ann in pagination.items],
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        })
        
    except Exception as e:
        return jsonify({'success': False, 'msg': f'获取公告列表失败: {str(e)}'}), 500


@bp.route('/<int:ann_id>', methods=['GET'])
def get_announcement(ann_id):
    """获取单个公告详情"""
    try:
        announcement = Announcement.query.get_or_404(ann_id)
        return jsonify({
            'success': True,
            'data': announcement.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'msg': f'获取公告失败: {str(e)}'}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_announcement():
    """
    创建公告（仅管理员）
    请求体：
    - title: 标题（必填）
    - content: 内容（必填）
    - type: 类型（必填，health_news 或 urgent_notice）
    - level: 级别（可选，normal/important/urgent）
    - publish_date: 发布日期（可选，默认今天）
    - source: 来源（可选）
    - status: 状态（可选，默认 active）
    """
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'success': False, 'msg': '仅管理员可操作'}), 403
    
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()
        ann_type = (data.get('type') or '').strip()
        
        if not title:
            return jsonify({'success': False, 'msg': '标题不能为空'}), 400
        if not content:
            return jsonify({'success': False, 'msg': '内容不能为空'}), 400
        if ann_type not in ['health_news', 'urgent_notice']:
            return jsonify({'success': False, 'msg': '类型必须为 health_news 或 urgent_notice'}), 400
        
        # 解析发布日期
        publish_date_str = data.get('publish_date')
        if publish_date_str:
            try:
                publish_date = datetime.strptime(publish_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'msg': '发布日期格式错误，应为 YYYY-MM-DD'}), 400
        else:
            publish_date = datetime.utcnow().date()
        
        announcement = Announcement(
            title=title,
            content=content,
            type=ann_type,
            level=data.get('level', 'normal'),
            publish_date=publish_date,
            source=data.get('source', ''),
            status=data.get('status', 'active')
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'msg': '公告创建成功',
            'data': announcement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'msg': f'创建公告失败: {str(e)}'}), 500


@bp.route('/<int:ann_id>', methods=['PUT'])
@jwt_required()
def update_announcement(ann_id):
    """
    更新公告（仅管理员）
    """
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'success': False, 'msg': '仅管理员可操作'}), 403
    
    try:
        announcement = Announcement.query.get_or_404(ann_id)
        data = request.get_json() or {}
        
        # 更新字段
        if 'title' in data:
            title = (data['title'] or '').strip()
            if not title:
                return jsonify({'success': False, 'msg': '标题不能为空'}), 400
            announcement.title = title
        
        if 'content' in data:
            content = (data['content'] or '').strip()
            if not content:
                return jsonify({'success': False, 'msg': '内容不能为空'}), 400
            announcement.content = content
        
        if 'type' in data:
            ann_type = (data['type'] or '').strip()
            if ann_type not in ['health_news', 'urgent_notice']:
                return jsonify({'success': False, 'msg': '类型必须为 health_news 或 urgent_notice'}), 400
            announcement.type = ann_type
        
        if 'level' in data:
            announcement.level = data['level']
        
        if 'publish_date' in data:
            try:
                announcement.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'msg': '发布日期格式错误，应为 YYYY-MM-DD'}), 400
        
        if 'source' in data:
            announcement.source = data['source']
        
        if 'status' in data:
            announcement.status = data['status']
        
        announcement.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'msg': '公告更新成功',
            'data': announcement.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'msg': f'更新公告失败: {str(e)}'}), 500


@bp.route('/<int:ann_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(ann_id):
    """删除公告（仅管理员）"""
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'success': False, 'msg': '仅管理员可操作'}), 403
    
    try:
        announcement = Announcement.query.get_or_404(ann_id)
        db.session.delete(announcement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'msg': '公告删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'msg': f'删除公告失败: {str(e)}'}), 500


@bp.route('/<int:ann_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_announcement(ann_id):
    """切换公告状态（仅管理员）"""
    admin = get_authenticated_user()
    if not _require_admin(admin):
        return jsonify({'success': False, 'msg': '仅管理员可操作'}), 403
    
    try:
        announcement = Announcement.query.get_or_404(ann_id)
        announcement.status = 'inactive' if announcement.status == 'active' else 'active'
        announcement.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'msg': f'公告已{"停用" if announcement.status == "inactive" else "启用"}',
            'data': announcement.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'msg': f'操作失败: {str(e)}'}), 500
