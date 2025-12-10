#!/usr/bin/env python3
"""
验证最新的流通记录GPS信息存储
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from models import CirculationRecord, User, Order
from app import app

def check_latest_circulation_records():
    """检查最新的流通记录中的GPS信息"""
    with app.app_context():
        print("=== 检查最新5条流通记录的GPS位置信息 ===")
        
        # 查询最近的5条流通记录
        records = CirculationRecord.query.order_by(
            CirculationRecord.created_at.desc()
        ).limit(5).all()
        
        if not records:
            print("没有找到流通记录")
            return
            
        print(f"找到 {len(records)} 条最新的流通记录:")
        print()
        
        has_valid_gps = 0
        missing_gps = 0
        
        for i, record in enumerate(records, 1):
            print(f"记录 {i} (ID: {record.id}):")
            print(f"  运单号: {record.tracking_number}")
            print(f"  运输状态: {record.transport_status}")
            print(f"  纬度: {record.latitude}")
            print(f"  经度: {record.longitude}")
            print(f"  创建时间: {record.created_at}")
            print(f"  时间戳: {record.timestamp}")
            
            # 检查GPS坐标是否有效
            if record.latitude is not None and record.longitude is not None:
                lat_valid = -90 <= record.latitude <= 90
                lng_valid = -180 <= record.longitude <= 180
                if lat_valid and lng_valid:
                    print(f"  ✅ GPS坐标有效")
                    has_valid_gps += 1
                else:
                    print(f"  ❌ GPS坐标超出有效范围")
            else:
                print(f"  ❌ GPS坐标缺失")
                missing_gps += 1
            print("-" * 50)
            
        print(f"\n总结:")
        print(f"  有效GPS记录: {has_valid_gps}")
        print(f"  缺失GPS记录: {missing_gps}")
        
        # 检查今天的记录
        from datetime import datetime, date
        today = date.today()
        today_records = CirculationRecord.query.filter(
            db.func.date(CirculationRecord.created_at) == today
        ).all()
        
        print(f"\n今天({today})的流通记录:")
        print(f"  总计: {len(today_records)} 条")
        
        today_with_gps = sum(1 for r in today_records if r.latitude is not None and r.longitude is not None)
        today_without_gps = len(today_records) - today_with_gps
        
        print(f"  包含GPS: {today_with_gps} 条")
        print(f"  缺失GPS: {today_without_gps} 条")
        
        if today_without_gps > 0:
            print(f"\n  提示: 发现今天有 {today_without_gps} 条记录没有GPS信息，")
            print(f"        这可能是修改要求GPS之前创建的记录。")

if __name__ == "__main__":
    print("最新流通记录GPS验证")
    print("=" * 60)
    
    try:
        check_latest_circulation_records()
        
        print()
        print("验证完成！")
        print()
        print("注意事项：")
        print("1. 新的流通记录应该包含有效的GPS坐标")
        print("2. 如果看到缺失GPS的记录，可能是修改之前创建的历史数据")
        print("3. 从现在开始，所有新记录都应该包含GPS坐标")
        
    except Exception as e:
        print(f"验证过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
