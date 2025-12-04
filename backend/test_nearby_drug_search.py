"""
测试基于药品名称的就近供应商搜索功能
"""
import sys
from app import create_app
from models import db, Tenant, Drug, SupplyInfo
from datetime import date, timedelta

def test_nearby_drug_search():
    """测试药品搜索功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("测试基于药品名称的就近供应商搜索")
        print("=" * 60)
        
        # 1. 检查数据库中的药品
        print("\n1. 检查药品数据:")
        drugs = Drug.query.all()
        print(f"   总共有 {len(drugs)} 个药品")
        
        if drugs:
            print("\n   前5个药品:")
            for drug in drugs[:5]:
                print(f"   - ID: {drug.id}, 通用名: {drug.generic_name}, 商品名: {drug.brand_name}")
        
        # 2. 检查供应商及其坐标信息
        print("\n2. 检查供应商及坐标信息:")
        suppliers = Tenant.query.filter_by(type='SUPPLIER', is_active=True).all()
        print(f"   总共有 {len(suppliers)} 个活跃供应商")
        
        suppliers_with_coords = [s for s in suppliers if s.longitude and s.latitude]
        suppliers_without_coords = [s for s in suppliers if not s.longitude or not s.latitude]
        
        print(f"   有坐标的供应商: {len(suppliers_with_coords)}")
        print(f"   无坐标的供应商: {len(suppliers_without_coords)}")
        
        if suppliers_with_coords:
            print("\n   有坐标的供应商示例:")
            for supplier in suppliers_with_coords[:3]:
                print(f"   - {supplier.name}")
                print(f"     坐标: ({supplier.longitude}, {supplier.latitude})")
                print(f"     地址: {supplier.address}")
        
        if suppliers_without_coords:
            print("\n   ⚠️ 无坐标的供应商:")
            for supplier in suppliers_without_coords[:5]:
                print(f"   - {supplier.name}")
                print(f"     地址: {supplier.address}")
        
        # 3. 检查供应信息（库存）
        print("\n3. 检查供应信息:")
        supply_infos = SupplyInfo.query.filter_by(status='ACTIVE').all()
        print(f"   总共有 {len(supply_infos)} 条活跃的供应信息")
        
        if supply_infos:
            print("\n   供应信息示例:")
            for supply in supply_infos[:5]:
                drug = Drug.query.get(supply.drug_id)
                tenant = Tenant.query.get(supply.tenant_id)
                print(f"   - 供应商: {tenant.name if tenant else 'Unknown'}")
                print(f"     药品: {drug.generic_name if drug else 'Unknown'} (ID: {supply.drug_id})")
                print(f"     库存: {supply.available_quantity}, 价格: ¥{supply.unit_price}")
        
        # 4. 分析哪些药品有库存，哪些供应商有坐标
        print("\n4. 分析有库存且供应商有坐标的药品:")
        
        # 获取有库存的供应信息
        active_supplies = SupplyInfo.query.filter(
            SupplyInfo.status == 'ACTIVE',
            SupplyInfo.available_quantity > 0
        ).all()
        
        # 按药品分组
        drug_supplier_map = {}
        for supply in active_supplies:
            drug_id = supply.drug_id
            tenant = Tenant.query.get(supply.tenant_id)
            
            if not tenant or not tenant.is_active:
                continue
                
            has_coords = bool(tenant.longitude and tenant.latitude)
            
            if drug_id not in drug_supplier_map:
                drug = Drug.query.get(drug_id)
                drug_supplier_map[drug_id] = {
                    'drug': drug,
                    'suppliers_with_coords': [],
                    'suppliers_without_coords': []
                }
            
            if has_coords:
                drug_supplier_map[drug_id]['suppliers_with_coords'].append({
                    'tenant': tenant,
                    'supply': supply
                })
            else:
                drug_supplier_map[drug_id]['suppliers_without_coords'].append({
                    'tenant': tenant,
                    'supply': supply
                })
        
        searchable_drugs = [(drug_id, info) for drug_id, info in drug_supplier_map.items() 
                           if info['suppliers_with_coords']]
        
        print(f"\n   可搜索的药品数量: {len(searchable_drugs)}")
        
        if searchable_drugs:
            print("\n   可搜索的药品示例:")
            for drug_id, info in searchable_drugs[:5]:
                drug = info['drug']
                supplier_count = len(info['suppliers_with_coords'])
                print(f"   - {drug.generic_name} ({drug.brand_name})")
                print(f"     有 {supplier_count} 个有坐标的供应商")
                print(f"     示例供应商:")
                for item in info['suppliers_with_coords'][:2]:
                    print(f"       * {item['tenant'].name}")
                    print(f"         库存: {item['supply'].available_quantity}, 价格: ¥{item['supply'].unit_price}")
        
        # 5. 建议测试的药品名称
        print("\n5. 建议用于测试的药品名称:")
        if searchable_drugs:
            print("   可以使用以下药品名称进行测试:")
            for drug_id, info in searchable_drugs[:10]:
                drug = info['drug']
                supplier_count = len(info['suppliers_with_coords'])
                print(f"   - '{drug.generic_name}' 或 '{drug.brand_name}' ({supplier_count}个供应商)")
        else:
            print("   ⚠️ 没有可用的药品进行测试")
            print("   建议:")
            print("   1. 为供应商添加坐标信息")
            print("   2. 确保供应信息表中有活跃的库存数据")
        
        print("\n" + "=" * 60)


if __name__ == '__main__':
    test_nearby_drug_search()
