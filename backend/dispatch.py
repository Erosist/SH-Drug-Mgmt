"""
配送路径规划 API
为物流公司提供多目的地配送路径优化服务
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Tenant, Order
from amap import AmapService, optimize_delivery_route, search_address_suggestions
from extensions import db
from typing import List, Dict, Tuple, Optional

bp = Blueprint('dispatch', __name__, url_prefix='/api/dispatch')


def parse_location_input(location_input: str) -> Optional[Tuple[float, float]]:
    """
    解析位置输入（支持经纬度或地址）
    
    Args:
        location_input: 可以是 "经度,纬度" 或 地址字符串
        
    Returns:
        (longitude, latitude) 或 None
    """
    if not location_input or not isinstance(location_input, str):
        return None
    
    location_input = location_input.strip()
    
    # 尝试解析为经纬度
    if ',' in location_input:
        try:
            parts = location_input.split(',')
            if len(parts) == 2:
                lon = float(parts[0].strip())
                lat = float(parts[1].strip())
                # 简单验证经纬度范围
                if -180 <= lon <= 180 and -90 <= lat <= 90:
                    return (lon, lat)
        except ValueError:
            pass
    
    # 尝试地理编码
    geocode_result = AmapService.geocode_address(location_input)
    if geocode_result:
        return (geocode_result['longitude'], geocode_result['latitude'])
    
    return None


@bp.route('/optimize_route', methods=['POST'])
@jwt_required()
def optimize_route():
    """
    优化配送路径
    
    请求体:
    {
        "start": "121.48,31.23" 或 "上海市浦东新区张江高科",  // 起点（仓库）
        "destinations": [                                    // 目的地列表
            {
                "name": "药店 A",                             // 目的地名称
                "location": "121.50,31.22" 或 "上海市徐汇区xxx路"  // 位置
            },
            {
                "name": "药店 B",
                "location": "121.51,31.21"
            }
        ],
        "use_api": false,          // 是否使用高德 API 计算驾车距离（可选，默认 false）
        "algorithm": "greedy"      // 优化算法：greedy 或 dp（可选，默认 greedy）
    }
    
    返回:
    {
        "success": true,
        "start": {
            "longitude": 121.48,
            "latitude": 31.23
        },
        "route": [                 // 优化后的访问顺序
            {
                "name": "药店 A",
                "longitude": 121.50,
                "latitude": 31.22,
                "order": 1,                      // 访问顺序
                "distance_from_prev": 2534.5,    // 距离上一个点的距离（米）
                "distance_from_prev_text": "2.5km"
            },
            ...
        ],
        "total_distance": 12345.6,
        "total_distance_text": "12.3km"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'message': '用户未找到'}), 404
        
        # 验证用户角色（仅物流公司可使用）
        if user.role != 'logistics':
            return jsonify({
                'success': False, 
                'message': '仅物流公司用户可以使用配送路径规划功能'
            }), 403
        
        data = request.get_json()
        
        # 验证必需参数
        if not data or 'start' not in data or 'destinations' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必需参数：start（起点）和 destinations（目的地列表）'
            }), 400
        
        # 解析起点
        start_coords = parse_location_input(data['start'])
        if not start_coords:
            return jsonify({
                'success': False,
                'message': f'无法解析起点位置：{data["start"]}。请输入有效的经纬度（如 121.48,31.23）或地址'
            }), 400
        
        # 解析目的地
        destinations = data['destinations']
        if not isinstance(destinations, list) or len(destinations) == 0:
            return jsonify({
                'success': False,
                'message': '目的地列表不能为空'
            }), 400
        
        parsed_destinations = []
        for i, dest in enumerate(destinations):
            if not isinstance(dest, dict) or 'location' not in dest:
                return jsonify({
                    'success': False,
                    'message': f'目的地 {i+1} 格式错误，需要包含 location 字段'
                }), 400
            
            coords = parse_location_input(dest['location'])
            if not coords:
                return jsonify({
                    'success': False,
                    'message': f'无法解析目的地 {i+1} 的位置：{dest["location"]}'
                }), 400
            
            parsed_destinations.append({
                'name': dest.get('name', f'目的地 {i+1}'),
                'longitude': coords[0],
                'latitude': coords[1],
                'original_location': dest['location']
            })
        
        # 获取优化参数
        use_api = data.get('use_api', False)
        algorithm = data.get('algorithm', 'greedy')
        
        # 执行路径优化
        optimized_route = optimize_delivery_route(
            start_coords,
            parsed_destinations,
            use_api=use_api,
            algorithm=algorithm
        )
        
        # 计算总距离
        total_distance = sum(dest.get('distance_from_prev', 0) for dest in optimized_route)
        
        return jsonify({
            'success': True,
            'start': {
                'longitude': start_coords[0],
                'latitude': start_coords[1]
            },
            'route': optimized_route,
            'total_distance': round(total_distance, 2),
            'total_distance_text': AmapService.format_distance(total_distance),
            'algorithm': algorithm,
            'use_api': use_api
        }), 200
        
    except Exception as e:
        print(f"配送路径优化异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误：{str(e)}'
        }), 500


@bp.route('/orders_destinations', methods=['GET'])
@jwt_required()
def get_orders_destinations():
    """
    获取待配送订单的目的地列表（从订单数据中提取）
    
    查询参数:
        status: 订单状态筛选（可选，默认为 'pending' 和 'confirmed'）
        limit: 返回数量限制（可选，默认 20）
    
    返回:
    {
        "success": true,
        "destinations": [
            {
                "order_id": 123,
                "name": "某某药店",
                "address": "上海市xxx",
                "longitude": 121.50,
                "latitude": 31.22,
                "contact_phone": "021-12345678"
            },
            ...
        ]
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'message': '用户未找到'}), 404
        
        # 验证用户角色
        if user.role != 'logistics':
            return jsonify({
                'success': False,
                'message': '仅物流公司用户可以访问此接口'
            }), 403
        
        # 获取查询参数
        status_filter = request.args.get('status', 'pending,confirmed')
        limit = int(request.args.get('limit', 20))
        
        # 解析状态列表
        statuses = [s.strip() for s in status_filter.split(',')]
        
        # 查询订单（需要配送的订单）
        orders_query = Order.query.filter(
            Order.status.in_(statuses),
            Order.logistics_id == user.id  # 分配给当前物流公司
        ).limit(limit)
        
        destinations = []
        for order in orders_query:
            # 获取买方（药店）信息
            buyer = User.query.get(order.buyer_id)
            if not buyer:
                continue
            
            buyer_tenant = Tenant.query.filter_by(user_id=buyer.id).first()
            if not buyer_tenant:
                continue
            
            # 检查是否有坐标信息
            if buyer_tenant.longitude and buyer_tenant.latitude:
                destinations.append({
                    'order_id': order.id,
                    'name': buyer_tenant.name or buyer.username,
                    'address': buyer_tenant.address or '',
                    'longitude': float(buyer_tenant.longitude),
                    'latitude': float(buyer_tenant.latitude),
                    'contact_phone': buyer_tenant.contact_phone or '',
                    'order_created_at': order.created_at.isoformat() if order.created_at else None
                })
        
        return jsonify({
            'success': True,
            'destinations': destinations,
            'count': len(destinations)
        }), 200
        
    except Exception as e:
        print(f"获取订单目的地异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误：{str(e)}'
        }), 500


@bp.route('/geocode', methods=['POST'])
@jwt_required()
def geocode():
    """
    地理编码接口（地址转坐标）
    
    请求体:
    {
        "address": "上海市浦东新区张江高科",
        "city": "上海市"  // 可选
    }
    
    返回:
    {
        "success": true,
        "longitude": 121.6,
        "latitude": 31.2,
        "formatted_address": "上海市浦东新区...",
        "province": "上海市",
        "city": "上海市",
        "district": "浦东新区"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'message': '用户未找到'}), 404
        
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必需参数：address'
            }), 400
        
        address = data['address']
        city = data.get('city')
        
        result = AmapService.geocode_address(address, city)
        
        if result:
            return jsonify({
                'success': True,
                **result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'无法解析地址：{address}'
            }), 400
        
    except Exception as e:
        print(f"地理编码异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误：{str(e)}'
        }), 500


@bp.route('/search_address', methods=['POST'])
@jwt_required()
def search_address():
    """
    搜索地址建议（输入提示）
    用于前端输入框的自动补全功能
    """
    try:
        data = request.get_json()
        
        if not data or 'keyword' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必需参数：keyword'
            }), 400
        
        keyword = data['keyword'].strip()
        
        if not keyword or len(keyword) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            }), 200
        
        city = data.get('city', '上海')
        
        suggestions = search_address_suggestions(keyword, city)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        print(f"地址搜索异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误：{str(e)}'
        }), 500
