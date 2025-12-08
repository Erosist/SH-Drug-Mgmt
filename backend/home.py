"""
主页相关接口
提供平台统计、健康资讯、公告通知等功能
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Drug, SupplyInfo, Order, Tenant, Announcement
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from auth import get_authenticated_user

bp = Blueprint('home', __name__, url_prefix='/api/home')


@bp.route('/stats', methods=['GET'])
def get_platform_stats():
    """
    获取平台统计数据
    返回：
    - 注册企业数量
    - 药品种类数量
    - 供应信息数量
    - 订单总数
    - 今日新增订单数
    """
    try:
        # 注册企业数量（排除管理员和未认证用户）
        # 代码库中 Tenant 模型使用 is_active 字段而不是 status
        total_tenants = Tenant.query.filter(
            Tenant.is_active == True
        ).count()
        
        # 药品种类数量
        total_drugs = Drug.query.count()
        
        # 供应信息数量（仅统计ACTIVE状态）
        total_supplies = SupplyInfo.query.filter(
            SupplyInfo.status == 'ACTIVE'
        ).count()
        
        # 订单总数
        total_orders = Order.query.count()
        
        # 今日新增订单数
        today = datetime.utcnow().date()
        today_orders = Order.query.filter(
            func.date(Order.created_at) == today
        ).count()
        
        # 本月订单数
        first_day_of_month = today.replace(day=1)
        month_orders = Order.query.filter(
            Order.created_at >= first_day_of_month
        ).count()
        
        return jsonify({
            'msg': '获取平台统计成功',
            'data': {
                'total_tenants': total_tenants,
                'total_drugs': total_drugs,
                'total_supplies': total_supplies,
                'total_orders': total_orders,
                'today_orders': today_orders,
                'month_orders': month_orders
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'获取平台统计失败: {str(e)}')
        return jsonify({'msg': '获取平台统计失败', 'error': str(e)}), 500


@bp.route('/health-news', methods=['GET'])
def get_health_news():
    """
    获取健康资讯列表
    查询参数：
    - limit: 返回条数，默认10条
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        # 从数据库查询健康资讯
        news_list = Announcement.query.filter(
            Announcement.type == 'health_news',
            Announcement.status == 'active'
        ).order_by(desc(Announcement.publish_date)).limit(limit).all()
        
        return jsonify({
            'msg': '获取健康资讯成功',
            'data': [news.to_dict() for news in news_list]
        })
        
    except Exception as e:
        current_app.logger.error(f'获取健康资讯失败: {str(e)}')
        return jsonify({'msg': '获取健康资讯失败', 'error': str(e)}), 500


@bp.route('/urgent-notices', methods=['GET'])
def get_urgent_notices():
    """
    获取紧急通知列表
    查询参数：
    - limit: 返回条数，默认5条
    """
    try:
        limit = int(request.args.get('limit', 5))
        
        # 从数据库查询紧急通知
        notices = Announcement.query.filter(
            Announcement.type == 'urgent_notice',
            Announcement.status == 'active'
        ).order_by(desc(Announcement.publish_date)).limit(limit).all()
        
        return jsonify({
            'msg': '获取紧急通知成功',
            'data': [notice.to_dict() for notice in notices]
        })
        
    except Exception as e:
        current_app.logger.error(f'获取紧急通知失败: {str(e)}')
        return jsonify({'msg': '获取紧急通知失败', 'error': str(e)}), 500


@bp.route('/user-stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    获取当前用户的个性化统计数据
    根据用户角色返回不同的统计信息：
    - 供应商：我的供应信息数、我的订单数
    - 药店：我的订单数、我的库存预警数
    - 物流：我的配送任务数
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        
        stats = {}
        
        if current_user.role == 'supplier':
            # 供应商统计
            my_supplies = SupplyInfo.query.filter(
                SupplyInfo.tenant_id == current_user.tenant_id
            ).count()
            
            my_orders = Order.query.filter(
                Order.supplier_tenant_id == current_user.tenant_id
            ).count()
            
            pending_orders = Order.query.filter(
                Order.supplier_tenant_id == current_user.tenant_id,
                Order.status == 'PENDING'
            ).count()
            
            stats = {
                'my_supplies': my_supplies,
                'my_orders': my_orders,
                'pending_orders': pending_orders
            }
            
        elif current_user.role == 'pharmacy':
            # 药店统计
            my_orders = Order.query.filter(
                Order.buyer_tenant_id == current_user.tenant_id
            ).count()
            
            pending_orders = Order.query.filter(
                Order.buyer_tenant_id == current_user.tenant_id,
                Order.status == 'PENDING'
            ).count()
            
            stats = {
                'my_orders': my_orders,
                'pending_orders': pending_orders
            }
        
        return jsonify({
            'msg': '获取用户统计成功',
            'data': stats
        })
        
    except Exception as e:
        current_app.logger.error(f'获取用户统计失败: {str(e)}')
        return jsonify({'msg': '获取用户统计失败', 'error': str(e)}), 500


@bp.route('/recent-activities', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """
    获取最近活动记录
    查询参数：
    - limit: 返回条数，默认10条
    """
    try:
        current_user = get_authenticated_user()
        if not current_user:
            return jsonify({'msg': '用户未登录'}), 401
        
        limit = int(request.args.get('limit', 10))
        
        activities = []
        
        if current_user.role == 'supplier':
            # 供应商：最近的订单
            recent_orders = Order.query.filter(
                Order.supplier_tenant_id == current_user.tenant_id
            ).order_by(desc(Order.created_at)).limit(limit).all()
            
            for order in recent_orders:
                activities.append({
                    'type': 'order',
                    'id': order.id,
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'description': f'收到新订单 #{order.id}'
                })
                
        elif current_user.role == 'pharmacy':
            # 药店：最近的订单
            recent_orders = Order.query.filter(
                Order.buyer_tenant_id == current_user.tenant_id
            ).order_by(desc(Order.created_at)).limit(limit).all()
            
            for order in recent_orders:
                activities.append({
                    'type': 'order',
                    'id': order.id,
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'description': f'创建订单 #{order.id}'
                })
        
        return jsonify({
            'msg': '获取最近活动成功',
            'data': activities
        })
        
    except Exception as e:
        current_app.logger.error(f'获取最近活动失败: {str(e)}')
        return jsonify({'msg': '获取最近活动失败', 'error': str(e)}), 500
