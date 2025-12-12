from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_

from extensions import db
from models import (
    InventoryItem, InventoryTransaction, Tenant, User, Order, OrderItem,
    CirculationRecord, Drug
)

bp = Blueprint('circulation', __name__, url_prefix='/api/circulation')

# 允许的角色
ALLOWED_ROLES = {'logistics'}

# 运输状态枚举
TRANSPORT_STATUSES = {'SHIPPED', 'IN_TRANSIT', 'DELIVERED'}

# 状态流转规则：SHIPPED -> IN_TRANSIT -> DELIVERED (正向流转)
STATUS_TRANSITION_MAP = {
    'SHIPPED': {'IN_TRANSIT'},
    'IN_TRANSIT': {'DELIVERED'},
    'DELIVERED': set()  # DELIVERED 不可逆
}

# 订单状态映射
ORDER_STATUS_MAP = {
    'SHIPPED': 'SHIPPED',
    'IN_TRANSIT': 'IN_TRANSIT',
    'DELIVERED': 'DELIVERED'
}


def get_authenticated_user():
    """获取当前认证用户"""
    identity = get_jwt_identity()
    if not identity:
        return None
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return User.query.get(user_id)


def validate_transport_status_transition(current_status: str, new_status: str) -> tuple[bool, str]:
    """
    验证状态流转是否合法
    返回: (是否合法, 错误消息)
    """
    if current_status is None:
        # 首次上报，允许直接设置为 SHIPPED
        if new_status == 'SHIPPED':
            return True, ''
        else:
            return False, f'首次上报状态必须为 SHIPPED'
    
    if current_status == new_status:
        # 相同状态，IN_TRANSIT 允许重复上报以更新位置信息
        if new_status == 'IN_TRANSIT':
            return True, ''
        else:
            return False, f'状态 {new_status} 不允许重复上报'
    
    allowed_next_statuses = STATUS_TRANSITION_MAP.get(current_status, set())
    if new_status not in allowed_next_statuses:
        return False, f'状态流转非法：不能从 {current_status} 转换到 {new_status}'
    
    return True, ''


def sync_order_status(order: Order, transport_status: str):
    """
    同步更新订单状态
    """
    new_order_status = ORDER_STATUS_MAP.get(transport_status)
    if new_order_status and order.status != new_order_status:
        old_status = order.status
        order.status = new_order_status
        order.updated_at = datetime.utcnow()
        
        # 更新订单相关时间戳
        if transport_status == 'SHIPPED' and not order.shipped_at:
            order.shipped_at = datetime.utcnow()
        elif transport_status == 'DELIVERED' and not order.delivered_at:
            order.delivered_at = datetime.utcnow()
        
        current_app.logger.info(
            'Order status synced: order_id=%s, old_status=%s, new_status=%s',
            order.id, old_status, new_order_status
        )

TIME_RANGE_DAYS = {
    '7d': 7,
    '30d': 30,
    '90d': 90,
}


def _extract_region(address: str) -> str:
    """Try to normalize address string into a district/region label."""
    if not address:
        return '其他'
    for marker in ('区', '县', '市'):
        idx = address.find(marker)
        if idx != -1:
            return address[: idx + 1]
    return address[:4] if len(address) >= 2 else '其他'


def _available_regions():
    rows = db.session.query(Tenant.address).filter(Tenant.address.isnot(None)).all()
    regions = {_extract_region(addr) for (addr,) in rows if addr}
    if '其他' in regions:
        regions.remove('其他')
    return sorted(regions)


@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def circulation_dashboard():
    """
    监管分析看板数据
    GET /api/circulation/dashboard?range=7d&region=all
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    if user.role != 'regulator':
        return jsonify({'msg': '权限不足：仅监管用户可访问看板数据'}), 403
    
    range_key = request.args.get('range', '7d')
    region_filter = request.args.get('region', 'all').strip()
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # 解析时间范围
    if start_date_str and end_date_str:
        try:
            start_time = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            if start_time.tzinfo:
                start_time = start_time.replace(tzinfo=None) - (start_time.utcoffset() or timedelta(0))
            if end_time.tzinfo:
                end_time = end_time.replace(tzinfo=None) - (end_time.utcoffset() or timedelta(0))
        except Exception:
            days = TIME_RANGE_DAYS.get(range_key, 7)
            start_time = datetime.utcnow() - timedelta(days=days)
            end_time = datetime.utcnow()
    else:
        days = TIME_RANGE_DAYS.get(range_key, 7)
        start_time = datetime.utcnow() - timedelta(days=days)
        end_time = datetime.utcnow()

    inventory_query = db.session.query(func.coalesce(func.sum(InventoryItem.quantity), 0)).join(
        Tenant, InventoryItem.tenant_id == Tenant.id
    )
    if region_filter:
        inventory_query = inventory_query.filter(Tenant.address.contains(region_filter))
    total_inventory = int(inventory_query.scalar() or 0)

    # 查询流通记录
    records_query = CirculationRecord.query.filter(
        CirculationRecord.timestamp >= start_time,
        CirculationRecord.timestamp <= end_time
    )
    
    if region_filter and region_filter != 'all':
        # 通过订单关联的租户地址筛选
        records_query = records_query.join(Order).join(
            Tenant, Order.buyer_tenant_id == Tenant.id
        ).filter(Tenant.address.ilike(f'%{region_filter}%'))
    
    records = records_query.all()
    
    # 指标计算
    # 总库存量
    inventory_query = db.session.query(func.coalesce(func.sum(InventoryItem.quantity), 0))
    if region_filter and region_filter != 'all':
        inventory_query = inventory_query.join(Tenant).filter(
            Tenant.address.ilike(f'%{region_filter}%')
        )
    total_inventory = int(inventory_query.scalar() or 0)
    
    # 在途药品数量
    in_transit_count = sum(1 for r in records if r.transport_status == 'IN_TRANSIT')
    
    # 异常上报数量（通过备注中的关键词判断）
    abnormal_keywords = ['异常', '延迟', '告警', '超时']
    abnormal_count = 0
    for record in records:
        if record.remarks:
            if any(keyword in record.remarks for keyword in abnormal_keywords):
                abnormal_count += 1
    
    # 区域流向统计
    region_flow = defaultdict(int)
    for record in records:
        if record.current_location:
            region_name = _extract_region(record.current_location)
            region_flow[region_name] += 1
        elif record.order and record.order.buyer_tenant:
            region_name = _extract_region(record.order.buyer_tenant.address or '')
            region_flow[region_name] += 1
    
    region_flow_list = [
        {'region': region, 'count': count}
        for region, count in sorted(region_flow.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # 时间序列趋势（按状态统计）
    trend_map = defaultdict(lambda: {'shipped': 0, 'in_transit': 0, 'delivered': 0})
    for record in records:
        day_key = record.timestamp.strftime('%Y-%m-%d') if record.timestamp else '未知'
        status = record.transport_status
        if status == 'SHIPPED':
            trend_map[day_key]['shipped'] += 1
        elif status == 'IN_TRANSIT':
            trend_map[day_key]['in_transit'] += 1
        elif status == 'DELIVERED':
            trend_map[day_key]['delivered'] += 1
    
    trend_list = [
        {
            'date': date,
            'shipped': values['shipped'],
            'in_transit': values['in_transit'],
            'delivered': values['delivered']
        }
        for date, values in sorted(trend_map.items())
    ]
    
    # 地图数据
    map_data = [
        {'name': region, 'value': count}
        for region, count in region_flow.items()
    ]
    
    last_activity = datetime.utcnow()
    if records:
        last_activity = max(r.timestamp for r in records)

    return jsonify({
        'filters': {
            'range': range_key,
            'region': region_filter,
            'start_time': start_time.isoformat() if start_time else None,
            'end_time': end_time.isoformat() if end_time else None
        },
        'metrics': {
            'total_inventory': total_inventory,
            'in_transit': in_transit_count,
            'abnormal_reports': abnormal_count,
            'regions': len(region_flow_list)
        },
        'trend': trend_list,
        'region_flow': region_flow_list,
        'map': map_data,
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }), 200


@bp.route('/report', methods=['POST'])
@jwt_required()
def report_circulation():
    """
    流通数据上报
    POST /api/circulation/report
    
    请求体:
    {
        "tracking_number": "运单号",  # 必填
        "transport_status": "SHIPPED|IN_TRANSIT|DELIVERED",  # 必填
        "timestamp": "2025-01-01T12:00:00",  # 必填，ISO格式
        "current_location": "当前位置文字描述",  # 可选
        "latitude": 39.9042,  # 必填，GPS纬度
        "longitude": 116.4074,  # 必填，GPS经度
        "remarks": "备注信息"  # 可选
    }
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': '用户未找到'}), 404
    
    # 权限检查：只有物流公司可以上报
    if user.role not in ALLOWED_ROLES:
        return jsonify({'msg': '权限不足：只有物流公司可以上报流通数据'}), 403
    
    data = request.get_json() or {}
    tracking_number = (data.get('tracking_number') or '').strip()
    transport_status = (data.get('transport_status') or '').strip().upper()
    timestamp_str = data.get('timestamp')
    current_location = data.get('current_location')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    remarks = data.get('remarks')
    
    # 必填字段验证
    if not tracking_number:
        return jsonify({'msg': '运单号不能为空'}), 400
    
    if transport_status not in TRANSPORT_STATUSES:
        return jsonify({
            'msg': f'运输状态无效，必须是以下之一: {", ".join(sorted(TRANSPORT_STATUSES))}'
        }), 400
    
    # 时间戳验证和解析
    try:
        if timestamp_str:
            timestamp_str_clean = timestamp_str.replace('Z', '+00:00')
            if '+' in timestamp_str_clean or timestamp_str_clean.endswith('+00:00'):
                timestamp = datetime.fromisoformat(timestamp_str_clean)
            else:
                timestamp = datetime.fromisoformat(timestamp_str_clean)
            if timestamp.tzinfo:
                timestamp = timestamp.replace(tzinfo=None) - (timestamp.utcoffset() or timedelta(0))
        else:
            timestamp = datetime.utcnow()
    except (ValueError, AttributeError, TypeError) as e:
        current_app.logger.error(f'Timestamp parsing error: {str(e)}, input: {timestamp_str}')
        return jsonify({'msg': '时间戳格式无效，请使用ISO格式（如: 2025-01-01T12:00:00）'}), 400

    # GPS坐标验证 - 必须提供
    if latitude is None or longitude is None:
        return jsonify({'msg': 'GPS坐标是必填项，请先使用GPS定位'}), 400
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        # 验证坐标范围的合理性
        if not (-90 <= latitude <= 90):
            return jsonify({'msg': '纬度必须在-90到90之间'}), 400
        if not (-180 <= longitude <= 180):
            return jsonify({'msg': '经度必须在-180到180之间'}), 400
    except (ValueError, TypeError):
        return jsonify({'msg': 'GPS坐标格式无效，必须为数字'}), 400
    
    # 查找关联的订单（通过运单号）
    order = Order.query.filter_by(tracking_number=tracking_number).first()
    if not order:
        return jsonify({'msg': f'未找到运单号 {tracking_number} 对应的订单'}), 404
    
    # 查找当前运单的最新状态
    latest_record = CirculationRecord.query.filter_by(
        tracking_number=tracking_number
    ).order_by(CirculationRecord.timestamp.desc()).first()
    
    current_status = latest_record.transport_status if latest_record else None
    
    # 验证状态流转
    is_valid, error_msg = validate_transport_status_transition(current_status, transport_status)
    if not is_valid:
        return jsonify({'msg': error_msg}), 400
    
    try:
        # 从订单明细中获取批号（如果有）
        batch_number = None
        if order.items:
            # 取第一个订单项的批号
            first_item = order.items[0]
            if first_item.batch_number:
                batch_number = first_item.batch_number
            # 如果没有批号，尝试从库存项中查找
            elif first_item.drug_id:
                inventory_item = InventoryItem.query.filter_by(
                    drug_id=first_item.drug_id,
                    tenant_id=order.supplier_tenant_id
                ).first()
                if inventory_item:
                    batch_number = inventory_item.batch_number
        
        # 创建流通记录
        record = CirculationRecord(
            tracking_number=tracking_number,
            order_id=order.id,
            batch_number=batch_number,
            transport_status=transport_status,
            reported_by=user.id,
            timestamp=timestamp,
            current_location=current_location,
            latitude=float(latitude) if latitude is not None else None,
            longitude=float(longitude) if longitude is not None else None,
            remarks=remarks
        )
        
        db.session.add(record)
        
        # 同步更新订单状态
        sync_order_status(order, transport_status)
        
        db.session.commit()
        
        return jsonify({
            'msg': '状态更新成功',
            'record': record.to_dict(),
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Failed to create circulation record: {str(e)}')
        return jsonify({'msg': '服务器错误，请稍后重试'}), 500


@bp.route('/records/<tracking_number>', methods=['GET'])
@jwt_required()
def get_circulation_records(tracking_number: str):
    """
    获取指定运单号的流通记录列表
    GET /api/circulation/records/<tracking_number>
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': '用户未找到'}), 404
    
    # 权限检查
    if user.role not in ALLOWED_ROLES and user.role != 'regulator':
        return jsonify({'msg': '权限不足'}), 403
    
    records = CirculationRecord.query.filter_by(
        tracking_number=tracking_number
    ).order_by(CirculationRecord.timestamp.desc()).all()
    
    if not records:
        return jsonify({'msg': f'未找到运单号 {tracking_number} 的流通记录'}), 404

    # 仅允许监管用户或与订单相关的当事方查看记录
    if user.role != 'regulator':
        related = False
        for r in records:
            if r.order and (user.tenant_id == r.order.buyer_tenant_id or user.tenant_id == r.order.supplier_tenant_id):
                related = True
                break
        if not related:
            return jsonify({'msg': '权限不足：您不是该订单的相关方'}), 403
    
    return jsonify({
        'tracking_number': tracking_number,
        'records': [r.to_dict() for r in records]
    }), 200


@bp.route('/trace', methods=['GET'])
@jwt_required()
def trace_drug():
    """
    药品全生命周期追溯
    GET /api/circulation/trace?tracking_number=<运单号>&start_date=<开始日期>&end_date=<结束日期>
    
    查询参数:
    - tracking_number: 运单号（必填）
    - start_date: 开始日期（可选，ISO格式）
    - end_date: 结束日期（可选，ISO格式）
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({'msg': '用户未找到'}), 404
    
    # 权限检查：只有监管用户才能查询追溯
    if user.role != 'regulator':
        return jsonify({'msg': '权限不足：只有监管用户才能查询药品追溯'}), 403
    
    tracking_number = request.args.get('tracking_number', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    
    # 必填字段验证
    if not tracking_number:
        return jsonify({'msg': '运单号不能为空'}), 400
    
    try:
        # 解析时间范围（可选）
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            if start_date.tzinfo:
                start_date = start_date.replace(tzinfo=None) - (start_date.utcoffset() or timedelta(0))
        
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            if end_date.tzinfo:
                end_date = end_date.replace(tzinfo=None) - (end_date.utcoffset() or timedelta(0))
            # 结束日期设置为当天的23:59:59
            end_date = end_date.replace(hour=23, minute=59, second=59)
    except (ValueError, AttributeError, TypeError) as e:
        current_app.logger.error(f'Date parsing error: {str(e)}')
        return jsonify({'msg': '日期格式无效，请使用ISO格式'}), 400
    
    try:
        # 1. 通过运单号查找订单
        order = Order.query.filter_by(tracking_number=tracking_number).first()
        if not order:
            return jsonify({'msg': f'未找到运单号为 {tracking_number} 的订单'}), 404
        
        # 2. 获取药品信息（从订单项中获取）
        drug = None
        batch_number = None
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        if order_items:
            # 从第一个订单项获取药品信息
            first_item = order_items[0]
            batch_number = first_item.batch_number
            if first_item.drug:
                drug = first_item.drug
        
        # 3. 查找该运单号的所有流通记录
        records_query = CirculationRecord.query.filter_by(tracking_number=tracking_number)
        
        # 应用时间范围筛选
        if start_date:
            records_query = records_query.filter(CirculationRecord.timestamp >= start_date)
        if end_date:
            records_query = records_query.filter(CirculationRecord.timestamp <= end_date)
        
        records = records_query.order_by(CirculationRecord.timestamp.asc()).all()
        
        if not records:
            return jsonify({'msg': '未查询到相关流通记录'}), 404
        
        # 5. 构建时间轴数据
        timeline = []
        for record in records:
            status_map = {
                'SHIPPED': '待揽收',    # 更新为与前端一致的状态文本
                'IN_TRANSIT': '运输中',
                'DELIVERED': '已送达'
            }
            
            timeline_item = {
                'id': record.id,
                'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                'status': record.transport_status,
                'status_text': status_map.get(record.transport_status, record.transport_status),
                'location': record.current_location,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'remarks': record.remarks,
                'tracking_number': record.tracking_number
            }
            
            if record.order:
                timeline_item['order'] = {
                    'order_number': record.order.order_number,
                    'buyer_tenant_id': record.order.buyer_tenant_id,
                    'supplier_tenant_id': record.order.supplier_tenant_id
                }
            
            timeline.append(timeline_item)
        
        # 6. 构建流向图数据（Sankey图）
        nodes = []
        links = []
        node_index_map = {}
        
        status_nodes = {
            'SHIPPED': '供应商仓库',
            'IN_TRANSIT': '运输途中',
            'DELIVERED': '药店'
        }
        
        # 添加起始节点（生产厂家）
        prev_node_idx = None
        if drug and drug.manufacturer:
            if drug.manufacturer not in node_index_map:
                nodes.append({
                    'name': drug.manufacturer,
                    'category': 'manufacturer'
                })
                node_index_map[drug.manufacturer] = len(nodes) - 1
                prev_node_idx = node_index_map[drug.manufacturer]
        
        # 添加状态节点和链接
        for record in records:
            status_node_name = status_nodes.get(record.transport_status, record.transport_status)
            
            if status_node_name not in node_index_map:
                nodes.append({
                    'name': status_node_name,
                    'category': record.transport_status.lower()
                })
                node_index_map[status_node_name] = len(nodes) - 1
            
            current_node_idx = node_index_map[status_node_name]
            
            # 创建链接（避免自循环，即 source != target）
            if prev_node_idx is not None and prev_node_idx != current_node_idx:
                link_exists = any(
                    link['source'] == prev_node_idx and link['target'] == current_node_idx
                    for link in links
                )
                if not link_exists:
                    links.append({
                        'source': prev_node_idx,
                        'target': current_node_idx,
                        'value': 1
                    })
            
            # 只有当节点不同时才更新 prev_node_idx，避免同状态跳过
            if prev_node_idx is None or prev_node_idx != current_node_idx:
                prev_node_idx = current_node_idx
        
        # 构建返回数据
        result = {
            'tracking_number': tracking_number,
            'batch_number': batch_number,
            'drug': drug.to_dict() if drug else None,
            'timeline': timeline,
            'sankey': {
                'nodes': nodes,
                'links': links
            },
            'summary': {
                'total_records': len(records),
                'total_orders': 1 if order else 0,
                'first_record_time': timeline[0]['timestamp'] if timeline else None,
                'last_record_time': timeline[-1]['timestamp'] if timeline else None
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f'Failed to trace drug: {str(e)}')
        return jsonify({'msg': '服务器错误，请稍后重试'}), 500
