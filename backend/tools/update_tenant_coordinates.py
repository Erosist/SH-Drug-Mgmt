#!/usr/bin/env python3
"""
更新 tenants 表的经纬度坐标
为所有供应商和药房添加地理位置信息
"""

import sys
import os
from pathlib import Path

# 确保可以导入项目模块
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import Tenant

# 黄浦区的供应商和药房的真实坐标（基于地址）
COORDINATES = {
    '上海医药集团股份有限公司': {
        'address': '黄浦区四牌楼路88号',
        'latitude': 31.2304,
        'longitude': 121.4737
    },
    '华润医药商业集团有限公司': {
        'address': '黄浦区中华路1359号康宁商厦1层3号商铺',
        'latitude': 31.2187,
        'longitude': 121.4888
    },
    '复星医药集团': {
        'address': '黄浦区人民路905号一层',
        'latitude': 31.2156,
        'longitude': 121.4890
    },
    '仁济医院药房': {
        'address': '黄浦区云南南路261号(大世界地铁站5号口步行160米)',
        'latitude': 31.2295,
        'longitude': 121.4756
    },
    '华山医院药房': {
        'address': '黄浦区百联房产云南南路大楼西门旁(大世界地铁站5号口步行160米)',
        'latitude': 31.2298,
        'longitude': 121.4760
    }
}

def update_coordinates():
    """更新租户坐标信息"""
    app = create_app()
    
    with app.app_context():
        updated_count = 0
        skipped_count = 0
        
        print("=" * 80)
        print("开始更新 tenants 表的经纬度坐标")
        print("=" * 80)
        
        # 获取所有租户
        tenants = Tenant.query.all()
        
        for tenant in tenants:
            if tenant.name in COORDINATES:
                coord_data = COORDINATES[tenant.name]
                
                # 更新地址和坐标
                tenant.address = coord_data['address']
                tenant.latitude = coord_data['latitude']
                tenant.longitude = coord_data['longitude']
                
                print(f"\n✅ 更新: {tenant.name}")
                print(f"   类型: {tenant.type}")
                print(f"   地址: {tenant.address}")
                print(f"   坐标: ({tenant.latitude}, {tenant.longitude})")
                
                updated_count += 1
            else:
                print(f"\n⚠️  跳过: {tenant.name} (没有坐标数据)")
                skipped_count += 1
        
        # 提交更改
        try:
            db.session.commit()
            print("\n" + "=" * 80)
            print(f"✅ 更新完成！")
            print(f"   已更新: {updated_count} 个租户")
            print(f"   已跳过: {skipped_count} 个租户")
            print("=" * 80)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 更新失败: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = update_coordinates()
    sys.exit(0 if success else 1)
