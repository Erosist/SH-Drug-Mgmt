#!/usr/bin/env python3
"""
验证GPS位置信息在数据库中的存储
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from models import CirculationRecord, User, Order
from app import app

def check_circulation_records():
    """检查流通记录中的GPS信息存储"""
    with app.app_context():
        print("=== 检查流通记录中的GPS位置信息 ===")
        
        # 查询最近的流通记录
        records = CirculationRecord.query.order_by(
            CirculationRecord.created_at.desc()
        ).limit(10).all()
        
        if not records:
            print("没有找到流通记录")
            return
            
        print(f"找到 {len(records)} 条最新的流通记录:")
        print()
        
        for i, record in enumerate(records, 1):
            print(f"记录 {i}:")
            print(f"  ID: {record.id}")
            print(f"  运单号: {record.tracking_number}")
            print(f"  运输状态: {record.transport_status}")
            print(f"  纬度: {record.latitude}")
            print(f"  经度: {record.longitude}")
            print(f"  位置描述: {record.current_location}")
            print(f"  时间戳: {record.timestamp}")
            print(f"  创建时间: {record.created_at}")
            print(f"  备注: {record.remarks}")
            
            # 检查GPS坐标是否有效
            if record.latitude is not None and record.longitude is not None:
                lat_valid = -90 <= record.latitude <= 90
                lng_valid = -180 <= record.longitude <= 180
                print(f"  GPS坐标有效性: 纬度{'有效' if lat_valid else '无效'}, 经度{'有效' if lng_valid else '无效'}")
            else:
                print(f"  GPS坐标状态: 缺失")
            print("-" * 50)

def verify_database_schema():
    """验证数据库表结构"""
    with app.app_context():
        print("=== 验证数据库表结构 ===")
        
        # 检查CirculationRecord表结构
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('circulation_records')
        
        print("circulation_records表的列:")
        gps_columns = []
        for col in columns:
            if col['name'] in ['latitude', 'longitude', 'current_location']:
                gps_columns.append(col)
                print(f"  {col['name']}: {col['type']}, nullable={col['nullable']}")
        
        if len(gps_columns) >= 2:
            print("✅ GPS相关字段存在")
        else:
            print("❌ GPS相关字段缺失")
        
        print()

def check_recent_orders():
    """检查最近的订单运单号"""
    with app.app_context():
        print("=== 检查最近的订单运单号 ===")
        
        orders = Order.query.filter(
            Order.tracking_number.isnot(None)
        ).order_by(Order.created_at.desc()).limit(5).all()
        
        if orders:
            print("可用于测试的运单号:")
            for order in orders:
                print(f"  {order.tracking_number} (订单ID: {order.id})")
        else:
            print("没有找到有运单号的订单")
        print()

if __name__ == "__main__":
    print("GPS位置信息数据库验证")
    print("=" * 60)
    
    try:
        verify_database_schema()
        check_recent_orders()
        check_circulation_records()
        
        print()
        print("验证完成！")
        print()
        print("注意事项：")
        print("1. 确保数据库包含latitude和longitude字段")
        print("2. 新的流通记录应该包含有效的GPS坐标")
        print("3. GPS坐标应该在合理的范围内（纬度-90到90，经度-180到180）")
        
    except Exception as e:
        print(f"验证过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
