#!/usr/bin/env python3
"""
检查阿莫西林胶囊供应信息
"""
from app import create_app
from models import SupplyInfo, Drug, Tenant, User

def check_supply_data():
    app = create_app()
    with app.app_context():
        print('=== 检查阿莫西林胶囊的供应信息 ===')
        
        # 查找阿莫西林胶囊
        drug = Drug.query.filter(Drug.generic_name.like('%阿莫西林%')).first()
        if drug:
            print(f'找到药品: {drug.generic_name} (ID: {drug.id})')
            
            # 查找该药品的所有供应信息
            supplies = SupplyInfo.query.filter_by(drug_id=drug.id, status='ACTIVE').all()
            print(f'该药品有 {len(supplies)} 个活跃供应信息:')
            
            for supply in supplies:
                supplier = Tenant.query.get(supply.tenant_id)
                print(f'  供应信息ID: {supply.id}')
                print(f'  供应商: {supplier.name if supplier else "未知"} (企业ID: {supply.tenant_id})')
                print(f'  单价: ¥{supply.unit_price}')
                print(f'  可用数量: {supply.available_quantity}')
                print(f'  最小起订量: {supply.min_order_quantity}')
                print(f'  状态: {supply.status}')
                print()
        else:
            print('❌ 没有找到阿莫西林胶囊')
        
        print('=== 检查上海医药集团 ===')
        shanghai_pharma = Tenant.query.filter(Tenant.name.like('%上海医药集团%')).first()
        if shanghai_pharma:
            print(f'找到企业: {shanghai_pharma.name} (ID: {shanghai_pharma.id})')
            print(f'企业类型: {shanghai_pharma.type}')
            
            # 查看该企业的所有供应信息
            supplies = SupplyInfo.query.filter_by(tenant_id=shanghai_pharma.id, status='ACTIVE').all()
            print(f'该企业有 {len(supplies)} 个活跃供应信息:')
            
            for supply in supplies:
                drug_obj = Drug.query.get(supply.drug_id)
                print(f'  {drug_obj.generic_name if drug_obj else "未知药品"} - ¥{supply.unit_price} (ID: {supply.id})')
        else:
            print('❌ 没有找到上海医药集团')
        
        print('\n=== 检查pharmacy_dev用户企业信息 ===')
        user = User.query.filter_by(username='pharmacy_dev').first()
        if user and user.tenant:
            print(f'用户企业: {user.tenant.name} (ID: {user.tenant_id})')
            print(f'企业类型: {user.tenant.type}')
        else:
            print('❌ 用户企业信息异常')
        
        print('\n=== 检查是否存在"向自己企业下单"的情况 ===')
        if user and shanghai_pharma:
            if user.tenant_id == shanghai_pharma.id:
                print('⚠️ 警告: pharmacy_dev用户的企业ID与上海医药集团相同!')
                print('   这会导致"不能向自己的企业下单"错误')
            else:
                print('✅ 用户企业和上海医药集团不同，可以正常下单')
        
        print('\n=== 所有企业列表 ===')
        all_tenants = Tenant.query.all()
        for tenant in all_tenants:
            print(f'企业: {tenant.name} (ID: {tenant.id}, 类型: {tenant.type})')

if __name__ == "__main__":
    check_supply_data()
