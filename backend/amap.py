"""
高德地图 API 集成模块
功能：地理编码、距离计算、就近供应商推荐
"""
import requests
import math
from typing import Dict, List, Tuple, Optional
from flask import current_app


class AmapService:
    """高德地图服务类"""
    
    # 高德地图 API 端点
    GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
    DISTANCE_URL = "https://restapi.amap.com/v3/distance"
    
    @staticmethod
    def get_api_key() -> str:
        """获取高德地图 REST API Key"""
        return current_app.config.get('AMAP_REST_KEY')
    
    @staticmethod
    def geocode_address(address: str, city: Optional[str] = None) -> Optional[Dict]:
        """
        地理编码：将地址转换为经纬度坐标
        
        Args:
            address: 地址字符串
            city: 城市名称（可选，用于提高准确性）
            
        Returns:
            包含经纬度信息的字典，格式：
            {
                'longitude': 116.397128,
                'latitude': 39.916527,
                'formatted_address': '北京市东城区...',
                'province': '北京市',
                'city': '北京市',
                'district': '东城区'
            }
            如果查询失败返回 None
        """
        try:
            params = {
                'key': AmapService.get_api_key(),
                'address': address,
                'output': 'json'
            }
            
            if city:
                params['city'] = city
            
            response = requests.get(AmapService.GEOCODE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1' and data.get('count') != '0':
                geocode = data['geocodes'][0]
                location = geocode['location'].split(',')
                
                return {
                    'longitude': float(location[0]),
                    'latitude': float(location[1]),
                    'formatted_address': geocode.get('formatted_address', ''),
                    'province': geocode.get('province', ''),
                    'city': geocode.get('city', ''),
                    'district': geocode.get('district', ''),
                    'adcode': geocode.get('adcode', '')
                }
            else:
                print(f"地理编码失败: {data.get('info', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"地理编码异常: {str(e)}")
            return None
    
    @staticmethod
    def calculate_distance_haversine(lon1: float, lat1: float, 
                                     lon2: float, lat2: float) -> float:
        """
        使用 Haversine 公式计算两点之间的直线距离（单位：米）
        适用于快速本地计算，不依赖 API 调用
        
        Args:
            lon1, lat1: 第一个点的经度和纬度
            lon2, lat2: 第二个点的经度和纬度
            
        Returns:
            距离（米）
        """
        # 地球平均半径（米）
        R = 6371000
        
        # 转换为弧度
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine 公式
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        distance = R * c
        return round(distance, 2)
    
    @staticmethod
    def calculate_distance_api(origin: Tuple[float, float], 
                               destination: Tuple[float, float],
                               distance_type: int = 1) -> Optional[float]:
        """
        使用高德地图 API 计算两点之间的距离（支持驾车距离）
        
        Args:
            origin: 起点坐标 (longitude, latitude)
            destination: 终点坐标 (longitude, latitude)
            distance_type: 距离类型
                          0 - 直线距离
                          1 - 驾车导航距离（考虑道路）
                          3 - 步行规划距离
                          
        Returns:
            距离（米），失败返回 None
        """
        try:
            origin_str = f"{origin[0]},{origin[1]}"
            destination_str = f"{destination[0]},{destination[1]}"
            
            params = {
                'key': AmapService.get_api_key(),
                'origins': origin_str,
                'destination': destination_str,
                'type': distance_type,
                'output': 'json'
            }
            
            response = requests.get(AmapService.DISTANCE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1' and data.get('results'):
                distance = float(data['results'][0]['distance'])
                return round(distance, 2)
            else:
                print(f"距离计算失败: {data.get('info', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"距离计算异常: {str(e)}")
            return None
    
    @staticmethod
    def format_distance(distance: float) -> str:
        """
        格式化距离显示
        
        Args:
            distance: 距离（米）
            
        Returns:
            格式化后的距离字符串，如 "1.5km" 或 "500m"
        """
        if distance >= 1000:
            return f"{distance / 1000:.1f}km"
        else:
            return f"{int(distance)}m"


def find_nearby_suppliers(pharmacy_location: Tuple[float, float],
                          suppliers: List[Dict],
                          max_distance: Optional[float] = None,
                          limit: int = 10,
                          use_api: bool = False) -> List[Dict]:
    """
    查找就近的供应商并按距离排序
    
    Args:
        pharmacy_location: 药店位置 (longitude, latitude)
        suppliers: 供应商列表，每个供应商需包含 'longitude', 'latitude' 字段
        max_distance: 最大搜索半径（米），None 表示不限制
        limit: 返回结果数量限制
        use_api: 是否使用高德 API 计算距离（考虑道路），False 则使用直线距离
        
    Returns:
        按距离排序的供应商列表，每个供应商新增 'distance' 和 'distance_text' 字段
    """
    results = []
    
    for supplier in suppliers:
        # 检查供应商是否有坐标信息
        if not supplier.get('longitude') or not supplier.get('latitude'):
            continue
        
        supplier_location = (supplier['longitude'], supplier['latitude'])
        
        # 计算距离
        if use_api:
            distance = AmapService.calculate_distance_api(
                pharmacy_location, 
                supplier_location,
                distance_type=1  # 驾车距离
            )
        else:
            distance = AmapService.calculate_distance_haversine(
                pharmacy_location[0], pharmacy_location[1],
                supplier_location[0], supplier_location[1]
            )
        
        if distance is None:
            continue
        
        # 如果设置了最大距离，过滤超出范围的供应商
        if max_distance and distance > max_distance:
            continue
        
        # 添加距离信息
        supplier_with_distance = supplier.copy()
        supplier_with_distance['distance'] = distance
        supplier_with_distance['distance_text'] = AmapService.format_distance(distance)
        
        results.append(supplier_with_distance)
    
    # 按距离升序排序
    results.sort(key=lambda x: x['distance'])
    
    # 限制返回数量
    return results[:limit]


def get_current_location_by_ip() -> Optional[Dict]:
    """
    通过 IP 地址获取当前位置（粗略定位）
    注意：这个功能需要高德 Web 服务 API，且准确度较低
    建议前端使用浏览器的 Geolocation API 获取更精确的位置
    
    Returns:
        包含经纬度的字典，失败返回 None
    """
    try:
        url = "https://restapi.amap.com/v3/ip"
        params = {
            'key': AmapService.get_api_key(),
            'output': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == '1' and data.get('rectangle'):
            # 取矩形中心点作为大致位置
            rectangle = data['rectangle'].split(';')
            if len(rectangle) == 2:
                point1 = rectangle[0].split(',')
                point2 = rectangle[1].split(',')
                
                lon = (float(point1[0]) + float(point2[0])) / 2
                lat = (float(point1[1]) + float(point2[1])) / 2
                
                return {
                    'longitude': lon,
                    'latitude': lat,
                    'city': data.get('city', ''),
                    'province': data.get('province', '')
                }
        
        return None
        
    except Exception as e:
        print(f"IP定位异常: {str(e)}")
        return None
