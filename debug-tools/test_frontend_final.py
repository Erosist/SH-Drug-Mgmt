#!/usr/bin/env python3
"""
测试最终的前端数据显示 - B2B.vue 真实数据集成
"""
import sys
import os
sys.path.append('backend')

from app import create_app, db
from models import User, Order, OrderItem, Drug, SupplyInfo
from config import Config
import json

def test_frontend_data_sources():
    """测试前端数据源"""
    print("=== 测试前端数据源 ===")
    
    app = create_app(Config)
    with app.app_context():
        # 1. 测试供应商信息API数据
        print("\n1. 供应商信息数据:")
        supply_info_list = SupplyInfo.query.all()
        for info in supply_info_list:
            # 获取关联的租户和药品信息
            tenant = User.query.filter_by(tenant_id=info.tenant_id, role='supplier').first()
            drug = Drug.query.get(info.drug_id)
            
            supplier_name = tenant.username if tenant else f"租户{info.tenant_id}"
            drug_name = drug.brand_name if drug else f"药品{info.drug_id}"
            drug_spec = drug.specification if drug else "规格未知"
            
            print(f"   - ID: {info.id}, 供应商: {supplier_name}, 药品: {drug_name}")
            print(f"     价格: {info.unit_price}, 库存: {info.available_quantity}, 状态: {info.status}")
        
        # 2. 测试订单数据  
        print(f"\n2. 订单数据 (总计 {Order.query.count()} 条):")
        orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        for order in orders:
            print(f"   - 订单ID: {order.id}, 订单号: {order.order_number}, 状态: {order.status}")
            print(f"     创建时间: {order.created_at}")
            print(f"     买方租户: {order.buyer_tenant_id}, 卖方租户: {order.supplier_tenant_id}")
            total_amount = sum([float(item.unit_price) * item.quantity for item in order.items])
            print(f"     总金额: {total_amount}")
            for item in order.items:
                drug = Drug.query.get(item.drug_id)
                drug_name = drug.brand_name if drug else f"药品{item.drug_id}"
                print(f"     └─ {drug_name} x{item.quantity} @ {item.unit_price}")
        
        # 3. 模拟B2B.vue中loadRecentRecords的数据处理
        print(f"\n3. B2B.vue数据处理模拟:")
        print("   供应商信息转换为发布记录:")
        for info in supply_info_list[:3]:
            tenant = User.query.filter_by(tenant_id=info.tenant_id, role='supplier').first()
            drug = Drug.query.get(info.drug_id)
            
            record = {
                'id': info.id,
                'company': tenant.username if tenant else f"租户{info.tenant_id}",
                'drug': drug.brand_name if drug else f"药品{info.drug_id}",
                'spec': drug.specification if drug else "规格未知",
                'quantity': info.available_quantity,
                'price': info.unit_price,
                'date': info.created_at.strftime('%Y-%m-%d %H:%M') if info.created_at else '未知时间',
                'status': '可供应' if info.status == 'ACTIVE' else '已下架'
            }
            print(f"     {record}")
        
        # 4. 检查用户和权限
        print(f"\n4. 用户和权限检查:")
        users = User.query.all()
        for user in users:
            print(f"   - 用户: {user.username} ({user.role})")
            if user.role == 'supplier':
                supplier_info = SupplyInfo.query.filter_by(tenant_id=user.tenant_id).first()
                if supplier_info:
                    drug = Drug.query.get(supplier_info.drug_id)
                    drug_name = drug.brand_name if drug else f"药品{supplier_info.drug_id}"
                    print(f"     └─ 有供应商信息: {drug_name}")
                else:
                    print(f"     └─ 无供应商信息")
        
        print(f"\n5. 前端数据总结:")
        print(f"   - 供应商信息: {len(supply_info_list)} 条")
        print(f"   - 订单记录: {Order.query.count()} 条")
        print(f"   - 注册用户: {User.query.count()} 人")
        print(f"   - 药品目录: {Drug.query.count()} 种")

if __name__ == "__main__":
    test_frontend_data_sources()
