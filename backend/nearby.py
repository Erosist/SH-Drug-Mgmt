"""
就近供应商推荐 API
提供基于地理位置的供应商查询和推荐功能
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Tenant, User
from amap import AmapService, find_nearby_suppliers
from extensions import db

bp = Blueprint('nearby', __name__, url_prefix='/api/nearby')


@bp.route('/suppliers', methods=['POST'])
@jwt_required()
def get_nearby_suppliers():
    """
    根据药品名称获取有库存的就近供应商列表
    
    请求体:
    {
        "drug_name": "阿莫西林",    // 药品名称（必需，支持模糊搜索）
        "longitude": 116.470697,  // 药店经度（必需，如果不提供 address）
        "latitude": 40.000565,    // 药店纬度（必需，如果不提供 address）
        "address": "北京市朝阳区望京SOHO",  // 或者提供地址（会自动转换为坐标）
        "city": "北京市",          // 城市名称（配合 address 使用，提高精度）
        "max_distance": 50000,    // 最大搜索半径（米），可选，默认不限制
        "limit": 10,              // 返回结果数量，可选，默认10
        "use_api": false          // 是否使用高德 API 计算驾车距离，可选，默认 false（直线距离）
    }
    
    返回:
    {
        "success": true,
        "drug_name": "阿莫西林",
        "pharmacy_location": {
            "longitude": 116.470697,
            "latitude": 40.000565
        },
        "suppliers": [
            {
                "id": 1,
                "name": "供应商名称",
                "address": "供应商地址",
                "contact_person": "联系人",
                "contact_phone": "联系电话",
                "longitude": 116.480697,
                "latitude": 40.010565,
                "distance": 1289.45,        // 距离（米）
                "distance_text": "1.3km",   // 格式化的距离
                "inventory": {              // 库存信息
                    "quantity": 100,
                    "unit_price": 25.50
                }
            },
            ...
        ],
        "total": 5,
        "filtered": 3  // 过滤后的数量
    }
    """
    try:
        data = request.get_json()
        
        # 检查是否提供药品名称
        if 'drug_name' not in data or not data['drug_name']:
            return jsonify({
                'success': False,
                'message': '请提供药品名称'
            }), 400
        
        drug_name = data['drug_name'].strip()
        
        # 获取药店位置
        pharmacy_location = None
        
        # 方式1：直接提供经纬度
        if 'longitude' in data and 'latitude' in data:
            try:
                longitude = float(data['longitude'])
                latitude = float(data['latitude'])
                pharmacy_location = (longitude, latitude)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '经纬度格式错误，必须是数字'
                }), 400
        
        # 方式2：提供地址，自动转换为坐标
        elif 'address' in data:
            address = data['address']
            city = data.get('city')
            
            geocode_result = AmapService.geocode_address(address, city)
            
            if not geocode_result:
                return jsonify({
                    'success': False,
                    'message': f'无法解析地址: {address}'
                }), 400
            
            pharmacy_location = (geocode_result['longitude'], geocode_result['latitude'])
        
        else:
            return jsonify({
                'success': False,
                'message': '请提供 longitude/latitude 或 address'
            }), 400
        
        # 获取查询参数
        max_distance = data.get('max_distance')  # 米
        limit = data.get('limit', 10)
        use_api = data.get('use_api', False)
        
        # 查找匹配的药品（支持模糊搜索：通用名或商品名）
        from models import Drug, SupplyInfo
        drugs = Drug.query.filter(
            db.or_(
                Drug.generic_name.like(f'%{drug_name}%'),
                Drug.brand_name.like(f'%{drug_name}%')
            )
        ).all()
        
        if not drugs:
            return jsonify({
                'success': False,
                'message': f'未找到药品: {drug_name}'
            }), 404
        
        drug_ids = [drug.id for drug in drugs]
        
        # 查询有这些药品库存的活跃供应商
        # 使用 SupplyInfo 表查找有库存的供应商
        supply_infos = SupplyInfo.query.filter(
            SupplyInfo.drug_id.in_(drug_ids),
            SupplyInfo.status == 'ACTIVE',
            SupplyInfo.available_quantity > 0
        ).all()
        
        if not supply_infos:
            return jsonify({
                'success': True,
                'drug_name': drug_name,
                'pharmacy_location': {
                    'longitude': pharmacy_location[0],
                    'latitude': pharmacy_location[1]
                },
                'suppliers': [],
                'total': 0,
                'filtered': 0,
                'params': {
                    'max_distance': max_distance,
                    'limit': limit,
                    'use_api': use_api
                },
                'message': f'没有供应商有 {drug_name} 的库存'
            })
        
        # 获取供应商租户信息，并附加库存信息
        tenant_ids = list(set([si.tenant_id for si in supply_infos]))
        tenants = Tenant.query.filter(
            Tenant.id.in_(tenant_ids),
            Tenant.type == 'SUPPLIER',
            Tenant.is_active == True,
            Tenant.longitude.isnot(None),  # 必须有坐标信息
            Tenant.latitude.isnot(None)
        ).all()
        
        # 构建供应商列表，包含库存信息
        suppliers = []
        for tenant in tenants:
            # 获取该供应商的库存信息（选择价格最低的）
            tenant_supplies = [si for si in supply_infos if si.tenant_id == tenant.id]
            if not tenant_supplies:
                continue
                
            # 按价格排序，选择最优的供应信息
            best_supply = min(tenant_supplies, key=lambda x: float(x.unit_price))
            
            supplier_dict = tenant.to_dict()
            supplier_dict['inventory'] = {
                'supply_id': best_supply.id,
                'drug_id': best_supply.drug_id,
                'quantity': best_supply.available_quantity,
                'unit_price': float(best_supply.unit_price),
                'min_order_quantity': best_supply.min_order_quantity,
                'valid_until': best_supply.valid_until.isoformat() if best_supply.valid_until else None
            }
            # 获取药品详细信息
            drug = Drug.query.get(best_supply.drug_id)
            if drug:
                supplier_dict['inventory']['drug_info'] = {
                    'generic_name': drug.generic_name,
                    'brand_name': drug.brand_name,
                    'specification': drug.specification,
                    'manufacturer': drug.manufacturer
                }
            
            suppliers.append(supplier_dict)
        
        if not suppliers:
            return jsonify({
                'success': True,
                'drug_name': drug_name,
                'pharmacy_location': {
                    'longitude': pharmacy_location[0],
                    'latitude': pharmacy_location[1]
                },
                'suppliers': [],
                'total': 0,
                'filtered': 0,
                'params': {
                    'max_distance': max_distance,
                    'limit': limit,
                    'use_api': use_api
                },
                'message': f'有 {drug_name} 库存的供应商未设置位置信息'
            })
        
        # 查找就近供应商
        nearby_suppliers = find_nearby_suppliers(
            pharmacy_location=pharmacy_location,
            suppliers=suppliers,
            max_distance=max_distance,
            limit=limit,
            use_api=use_api
        )
        
        return jsonify({
            'success': True,
            'drug_name': drug_name,
            'pharmacy_location': {
                'longitude': pharmacy_location[0],
                'latitude': pharmacy_location[1]
            },
            'suppliers': nearby_suppliers,
            'total': len(suppliers),
            'filtered': len(nearby_suppliers),
            'params': {
                'max_distance': max_distance,
                'limit': limit,
                'use_api': use_api
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500


@bp.route('/geocode', methods=['POST'])
@jwt_required()
def geocode():
    """
    地理编码：将地址转换为经纬度
    
    请求体:
    {
        "address": "北京市朝阳区望京SOHO",
        "city": "北京市"  // 可选，提高精度
    }
    
    返回:
    {
        "success": true,
        "result": {
            "longitude": 116.470697,
            "latitude": 40.000565,
            "formatted_address": "北京市朝阳区望京街道...",
            "province": "北京市",
            "city": "北京市",
            "district": "朝阳区",
            "adcode": "110105"
        }
    }
    """
    try:
        data = request.get_json()
        
        if 'address' not in data:
            return jsonify({
                'success': False,
                'message': '请提供 address'
            }), 400
        
        address = data['address']
        city = data.get('city')
        
        result = AmapService.geocode_address(address, city)
        
        if not result:
            return jsonify({
                'success': False,
                'message': f'无法解析地址: {address}'
            }), 400
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'地理编码失败: {str(e)}'
        }), 500


@bp.route('/distance', methods=['POST'])
@jwt_required()
def calculate_distance():
    """
    计算两点之间的距离
    
    请求体:
    {
        "origin": {
            "longitude": 116.397128,
            "latitude": 39.916527
        },
        "destination": {
            "longitude": 116.427281,
            "latitude": 39.903738
        },
        "use_api": false  // 可选，是否使用高德 API（驾车距离），默认 false（直线距离）
    }
    
    返回:
    {
        "success": true,
        "distance": 2823.45,           // 距离（米）
        "distance_text": "2.8km",      // 格式化的距离
        "method": "haversine"          // 计算方法：haversine 或 api
    }
    """
    try:
        data = request.get_json()
        
        # 验证必需字段
        if 'origin' not in data or 'destination' not in data:
            return jsonify({
                'success': False,
                'message': '请提供 origin 和 destination'
            }), 400
        
        origin = data['origin']
        destination = data['destination']
        
        if 'longitude' not in origin or 'latitude' not in origin:
            return jsonify({
                'success': False,
                'message': 'origin 必须包含 longitude 和 latitude'
            }), 400
        
        if 'longitude' not in destination or 'latitude' not in destination:
            return jsonify({
                'success': False,
                'message': 'destination 必须包含 longitude 和 latitude'
            }), 400
        
        use_api = data.get('use_api', False)
        
        # 计算距离
        if use_api:
            distance = AmapService.calculate_distance_api(
                (origin['longitude'], origin['latitude']),
                (destination['longitude'], destination['latitude']),
                distance_type=1
            )
            method = 'api'
        else:
            distance = AmapService.calculate_distance_haversine(
                origin['longitude'], origin['latitude'],
                destination['longitude'], destination['latitude']
            )
            method = 'haversine'
        
        if distance is None:
            return jsonify({
                'success': False,
                'message': '距离计算失败'
            }), 500
        
        return jsonify({
            'success': True,
            'distance': distance,
            'distance_text': AmapService.format_distance(distance),
            'method': method
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'距离计算失败: {str(e)}'
        }), 500


@bp.route('/my-location', methods=['GET'])
@jwt_required()
def get_my_location():
    """
    获取当前登录用户所属租户的位置信息
    
    返回:
    {
        "success": true,
        "tenant": {
            "id": 1,
            "name": "药店名称",
            "type": "PHARMACY",
            "address": "详细地址",
            "longitude": 116.470697,
            "latitude": 40.000565,
            "has_location": true  // 是否已设置坐标
        }
    }
    """
    try:
        current_user_id = get_jwt_identity()
        # JWT identity 是字符串，需要转换为整数
        try:
            user_id = int(current_user_id)
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'message': '无效的用户ID'
            }), 400
        
        user = User.query.get(user_id)
        
        if not user or not user.tenant_id:
            return jsonify({
                'success': False,
                'message': '用户未关联租户'
            }), 400
        
        tenant = Tenant.query.get(user.tenant_id)
        
        if not tenant:
            return jsonify({
                'success': False,
                'message': '租户不存在'
            }), 404
        
        tenant_dict = tenant.to_dict()
        tenant_dict['has_location'] = (tenant.longitude is not None and 
                                        tenant.latitude is not None)
        
        return jsonify({
            'success': True,
            'tenant': tenant_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500


@bp.route('/update-location', methods=['PUT'])
@jwt_required()
def update_my_location():
    """
    更新当前登录用户所属租户的位置信息
    
    请求体:
    {
        "longitude": 116.470697,
        "latitude": 40.000565
    }
    或
    {
        "address": "北京市朝阳区望京SOHO",
        "city": "北京市"  // 可选
    }
    
    返回:
    {
        "success": true,
        "tenant": {
            "id": 1,
            "name": "药店名称",
            "longitude": 116.470697,
            "latitude": 40.000565
        },
        "message": "位置更新成功"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        # JWT identity 是字符串，需要转换为整数
        try:
            user_id = int(current_user_id)
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'message': '无效的用户ID'
            }), 400
        
        user = User.query.get(user_id)
        
        if not user or not user.tenant_id:
            return jsonify({
                'success': False,
                'message': '用户未关联租户'
            }), 400
        
        tenant = Tenant.query.get(user.tenant_id)
        
        if not tenant:
            return jsonify({
                'success': False,
                'message': '租户不存在'
            }), 404
        
        data = request.get_json()
        
        # 方式1：直接提供经纬度
        if 'longitude' in data and 'latitude' in data:
            try:
                tenant.longitude = float(data['longitude'])
                tenant.latitude = float(data['latitude'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '经纬度格式错误，必须是数字'
                }), 400
        
        # 方式2：提供地址，自动转换为坐标
        elif 'address' in data:
            address = data['address']
            city = data.get('city')
            
            geocode_result = AmapService.geocode_address(address, city)
            
            if not geocode_result:
                return jsonify({
                    'success': False,
                    'message': f'无法解析地址: {address}'
                }), 400
            
            tenant.longitude = geocode_result['longitude']
            tenant.latitude = geocode_result['latitude']
        
        else:
            return jsonify({
                'success': False,
                'message': '请提供 longitude/latitude 或 address'
            }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tenant': {
                'id': tenant.id,
                'name': tenant.name,
                'longitude': tenant.longitude,
                'latitude': tenant.latitude
            },
            'message': '位置更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500
