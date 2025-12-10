#!/usr/bin/env python3
"""
生成流通记录数据脚本

为药店和供应商之间的订单生成物流流通数据（circulation_records）。

用法：
  cd backend
  python tools/generate_circulation_data.py
"""
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# 确保项目根路径在 sys.path 中
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from app import create_app
    from extensions import db
    from models import Order, CirculationRecord, Tenant, User
except Exception as e:
    print('导入应用失败，请在 backend 目录下运行本脚本，且确保已安装依赖。错误：', e)
    raise


# 上海市区的GPS坐标范围（大致）
SHANGHAI_LAT_RANGE = (31.1, 31.4)
SHANGHAI_LNG_RANGE = (121.3, 121.7)

# 运输状态及其对应的位置描述模板
STATUS_LOCATIONS = {
    'SHIPPED': [
        '上海市浦东新区张江高科技园区仓库',
        '上海市徐汇区漕河泾开发区配送中心',
        '上海市闵行区莘庄工业园区物流仓库',
        '上海市杨浦区五角场物流站点',
        '上海市普陀区曹杨路配送站'
    ],
    'IN_TRANSIT': [
        '上海市中环路段',
        '上海市内环高架',
        '上海市延安路高架',
        '上海市南北高架',
        '上海市外环高速',
        '上海市浦东新区世纪大道',
        '上海市黄浦区南京路',
        '上海市静安区石门路'
    ],
    'DELIVERED': [
        '上海市徐汇区天钥桥路药店',
        '上海市浦东新区陆家嘴配送点',
        '上海市黄浦区人民广场药房',
        '上海市长宁区中山公园药店',
        '上海市杨浦区五角场医药超市',
        '上海市闵行区莘庄药店',
        '上海市宝山区共康路药房',
        '上海市普陀区真如药店'
    ]
}

# 备注模板
REMARKS_TEMPLATES = {
    'SHIPPED': [
        '货物已从仓库发出，准备装车',
        '药品已打包完成，等待配送',
        '订单已确认，开始配送',
        '货物已交接给物流司机',
        '包裹已出库，准备运输'
    ],
    'IN_TRANSIT': [
        '车辆行驶中，预计30分钟后到达',
        '正在配送途中，交通顺畅',
        '运输中，当前路况良好',
        '配送进行中，预计1小时内送达',
        '车辆正常行驶，即将到达目的地',
        None  # 有些记录可以没有备注
    ],
    'DELIVERED': [
        '货物已送达，签收完成',
        '药品已交付，收货人已验收',
        '订单完成配送，客户满意',
        '包裹已送达指定地点',
        '配送完成，药品完好无损'
    ]
}


def random_gps_in_shanghai():
    """生成上海市区范围内的随机GPS坐标"""
    lat = random.uniform(*SHANGHAI_LAT_RANGE)
    lng = random.uniform(*SHANGHAI_LNG_RANGE)
    return round(lat, 6), round(lng, 6)


def generate_circulation_for_order(order, logistics_user_id):
    """为指定订单生成完整的流通记录（待揽收 -> 运输中 -> 已送达）"""
    if not order.tracking_number:
        print(f"  ⚠️ 订单 {order.order_number} 没有运单号，跳过")
        return []
    
    # 检查是否已有流通记录
    existing = CirculationRecord.query.filter_by(tracking_number=order.tracking_number).first()
    if existing:
        print(f"  ⚠️ 运单号 {order.tracking_number} 已有流通记录，跳过")
        return []
    
    records = []
    
    # 基准时间：使用最近3天内的随机时间（确保数据在7天范围内）
    days_ago = random.randint(0, 3)  # 0-3天前
    base_time = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(1, 12))
    
    # 1. SHIPPED - 待揽收
    shipped_time = base_time + timedelta(minutes=random.randint(0, 30))
    shipped_lat, shipped_lng = random_gps_in_shanghai()
    shipped_record = CirculationRecord(
        tracking_number=order.tracking_number,
        order_id=order.id,
        batch_number=f"BATCH{random.randint(100000, 999999)}",
        transport_status='SHIPPED',
        reported_by=logistics_user_id,
        timestamp=shipped_time,
        current_location=random.choice(STATUS_LOCATIONS['SHIPPED']),
        latitude=shipped_lat,
        longitude=shipped_lng,
        remarks=random.choice(REMARKS_TEMPLATES['SHIPPED']),
        created_at=shipped_time
    )
    records.append(shipped_record)
    
    # 2. IN_TRANSIT - 运输中（2-4条记录）
    in_transit_count = random.randint(2, 4)
    for i in range(in_transit_count):
        transit_time = shipped_time + timedelta(minutes=random.randint(20, 60) * (i + 1))
        transit_lat, transit_lng = random_gps_in_shanghai()
        transit_record = CirculationRecord(
            tracking_number=order.tracking_number,
            order_id=order.id,
            batch_number=shipped_record.batch_number,
            transport_status='IN_TRANSIT',
            reported_by=logistics_user_id,
            timestamp=transit_time,
            current_location=random.choice(STATUS_LOCATIONS['IN_TRANSIT']),
            latitude=transit_lat,
            longitude=transit_lng,
            remarks=random.choice(REMARKS_TEMPLATES['IN_TRANSIT']),
            created_at=transit_time
        )
        records.append(transit_record)
    
    # 3. DELIVERED - 已送达
    delivered_time = transit_time + timedelta(minutes=random.randint(30, 90))
    delivered_lat, delivered_lng = random_gps_in_shanghai()
    delivered_record = CirculationRecord(
        tracking_number=order.tracking_number,
        order_id=order.id,
        batch_number=shipped_record.batch_number,
        transport_status='DELIVERED',
        reported_by=logistics_user_id,
        timestamp=delivered_time,
        current_location=random.choice(STATUS_LOCATIONS['DELIVERED']),
        latitude=delivered_lat,
        longitude=delivered_lng,
        remarks=random.choice(REMARKS_TEMPLATES['DELIVERED']),
        created_at=delivered_time
    )
    records.append(delivered_record)
    
    # 更新订单状态时间戳
    order.shipped_at = shipped_time
    order.delivered_at = delivered_time
    order.status = 'DELIVERED'
    
    return records


def main():
    app = create_app()
    with app.app_context():
        print('开始生成流通记录数据...\n')
        
        # 1. 获取物流公司的物流用户（用于上报流通数据）
        logistics_tenants = Tenant.query.filter_by(type='LOGISTICS').all()
        if not logistics_tenants:
            print('❌ 未找到物流公司租户，无法生成流通记录')
            return
        
        logistics_users = User.query.filter_by(role='logistics').all()
        if not logistics_users:
            print('❌ 未找到物流角色用户，无法生成流通记录')
            return
        
        # 使用第一个物流用户作为上报人
        logistics_user = logistics_users[0]
        print(f'✓ 使用物流用户: {logistics_user.username} (ID: {logistics_user.id})\n')
        
        # 2. 查询药店和供应商之间的订单（有运单号的订单）
        orders = Order.query.filter(
            Order.tracking_number.isnot(None),
            Order.status.in_(['PENDING', 'CONFIRMED', 'SHIPPED', 'IN_TRANSIT', 'DELIVERED'])
        ).limit(30).all()  # 限制生成30个订单的流通记录
        
        if not orders:
            print('❌ 未找到符合条件的订单（需要有运单号）')
            return
        
        print(f'找到 {len(orders)} 个订单，开始生成流通记录...\n')
        
        total_records = 0
        for idx, order in enumerate(orders, 1):
            print(f'[{idx}/{len(orders)}] 订单 {order.order_number} (运单号: {order.tracking_number})')
            
            records = generate_circulation_for_order(order, logistics_user.id)
            
            if records:
                for record in records:
                    db.session.add(record)
                total_records += len(records)
                print(f'  ✓ 生成 {len(records)} 条流通记录')
            
            # 每处理10个订单提交一次
            if idx % 10 == 0:
                db.session.commit()
                print(f'\n--- 已处理 {idx} 个订单，提交到数据库 ---\n')
        
        # 最终提交
        db.session.commit()
        
        print('\n' + '=' * 60)
        print(f'✓ 流通记录生成完成！')
        print(f'  总订单数: {len(orders)}')
        print(f'  生成流通记录数: {total_records}')
        print(f'  上报用户: {logistics_user.username}')
        print('=' * 60)
        
        # 显示统计信息
        shipped_count = CirculationRecord.query.filter_by(transport_status='SHIPPED').count()
        in_transit_count = CirculationRecord.query.filter_by(transport_status='IN_TRANSIT').count()
        delivered_count = CirculationRecord.query.filter_by(transport_status='DELIVERED').count()
        
        print('\n流通记录统计:')
        print(f'  待揽收 (SHIPPED): {shipped_count}')
        print(f'  运输中 (IN_TRANSIT): {in_transit_count}')
        print(f'  已送达 (DELIVERED): {delivered_count}')
        print(f'  总计: {shipped_count + in_transit_count + delivered_count}')


if __name__ == '__main__':
    main()
