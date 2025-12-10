#!/usr/bin/env python3
"""
为供应商创建库存数据
为所有供应商针对 30 种药品随机生成库存记录
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# 确保可以导入项目模块
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import Tenant, Drug, InventoryItem

def generate_batch_number():
    """生成批次号"""
    date_str = datetime.now().strftime('%Y%m%d')
    random_num = random.randint(1000, 9999)
    return f"BN-{date_str}-{random_num}"

def create_supplier_inventory():
    """为供应商创建库存数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("为供应商创建库存数据")
        print("=" * 80)
        
        # 获取所有供应商
        suppliers = Tenant.query.filter_by(type='SUPPLIER').order_by(Tenant.id).all()
        print(f"\n找到 {len(suppliers)} 个供应商")
        
        # 获取所有药品
        drugs = Drug.query.all()
        print(f"找到 {len(drugs)} 种药品")
        
        if len(drugs) == 0:
            print("\n❌ 错误: 数据库中没有药品数据")
            return False
        
        # 检查供应商现有库存
        existing_supplier_inventory = InventoryItem.query.join(Tenant).filter(
            Tenant.type == 'SUPPLIER'
        ).count()
        
        print(f"供应商现有库存记录: {existing_supplier_inventory} 条")
        
        added_count = 0
        
        print("\n开始生成供应商库存...")
        print("-" * 80)
        
        for supplier in suppliers:
            print(f"\n供应商: {supplier.name} (ID: {supplier.id})")
            
            # 为每个供应商随机选择 15-25 种药品
            num_drugs = random.randint(15, 25)
            selected_drugs = random.sample(drugs, min(num_drugs, len(drugs)))
            
            for drug in selected_drugs:
                # 生成随机库存数据
                production_date = datetime.now() - timedelta(days=random.randint(30, 180))
                expiry_date = production_date + timedelta(days=random.randint(540, 1095))  # 18-36个月
                quantity = random.randint(1000, 10000)
                unit_price = round(random.uniform(5.0, 200.0), 2)
                
                # 创建库存记录
                inventory_item = InventoryItem(
                    tenant_id=supplier.id,
                    drug_id=drug.id,
                    batch_number=generate_batch_number(),
                    production_date=production_date.date(),
                    expiry_date=expiry_date.date(),
                    quantity=quantity,
                    unit_price=unit_price,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(inventory_item)
                added_count += 1
            
            print(f"  添加 {len(selected_drugs)} 种药品的库存")
            
            # 每个供应商提交一次
            db.session.commit()
        
        print("\n" + "=" * 80)
        print("库存创建完成:")
        print(f"  供应商数量: {len(suppliers)} 个")
        print(f"  新增库存: {added_count} 条")
        print(f"  平均每个供应商: {added_count // len(suppliers) if len(suppliers) > 0 else 0} 条")
        print("=" * 80)
        
        # 统计最终结果
        total_inventory = InventoryItem.query.count()
        supplier_inventory = InventoryItem.query.join(Tenant).filter(
            Tenant.type == 'SUPPLIER'
        ).count()
        pharmacy_inventory = InventoryItem.query.join(Tenant).filter(
            Tenant.type == 'PHARMACY'
        ).count()
        
        print("\n📊 库存统计:")
        print(f"  供应商库存: {supplier_inventory} 条")
        print(f"  药店库存: {pharmacy_inventory} 条")
        print(f"  总库存: {total_inventory} 条")
        print("=" * 80)
        
        print("\n✅ 成功为所有供应商创建库存数据")
        
        return True

if __name__ == '__main__':
    try:
        success = create_supplier_inventory()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
