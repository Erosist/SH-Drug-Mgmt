#!/usr/bin/env python3
"""
测试供应信息自动上下架功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
from app import create_app
from extensions import db
from models import User, Tenant, Drug, SupplyInfo, Order, OrderItem
from supply_utils import update_supply_info_quantity


def setup_test_data():
    """创建测试数据"""
    
    # 创建测试药店企业
    pharmacy_tenant = Tenant(
        name='测试药店',
        type='PHARMACY',
        unified_social_credit_code='91000000000000001X',
        legal_representative='张三',
        contact_person='张三',
        contact_phone='13800138001',
        contact_email='pharmacy@test.com',
        address='北京市朝阳区',
        business_scope='药品零售'
    )
    
    # 创建测试供应商企业
    supplier_tenant = Tenant(
        name='测试供应商',
        type='SUPPLIER',
        unified_social_credit_code='91000000000000002X',
        legal_representative='李四',
        contact_person='李四',
        contact_phone='13800138002',
        contact_email='supplier@test.com',
        address='北京市海淀区',
        business_scope='药品批发'
    )
    
    db.session.add_all([pharmacy_tenant, supplier_tenant])
    db.session.flush()
    
    # 创建测试用户
    pharmacy_user = User(
        username='pharmacy_user',
        email='pharmacy@test.com',
        real_name='药店用户',
        role='pharmacy',
        tenant_id=pharmacy_tenant.id,
        is_authenticated=True
    )
    pharmacy_user.set_password('password123')
    
    supplier_user = User(
        username='supplier_user',
        email='supplier@test.com',
        real_name='供应商用户',
        role='supplier',
        tenant_id=supplier_tenant.id,
        is_authenticated=True
    )
    supplier_user.set_password('password123')
    
    db.session.add_all([pharmacy_user, supplier_user])
    db.session.flush()
    
    # 创建测试药品
    drug = Drug(
        generic_name='阿莫西林',
        brand_name='阿莫西林胶囊',
        approval_number='H20201234',
        dosage_form='胶囊剂',
        specification='0.25g',
        manufacturer='测试制药厂',
        category='抗感染药',
        prescription_type='非处方药'
    )
    
    db.session.add(drug)
    db.session.flush()
    
    # 创建测试供应信息，初始数量为5
    supply_info = SupplyInfo(
        tenant_id=supplier_tenant.id,
        drug_id=drug.id,
        available_quantity=5,
        unit_price=10.50,
        valid_until=date(2024, 12, 31),
        min_order_quantity=1,
        description='测试供应信息',
        status='ACTIVE'
    )
    
    db.session.add(supply_info)
    db.session.commit()
    
    return {
        'pharmacy_tenant': pharmacy_tenant,
        'supplier_tenant': supplier_tenant,
        'pharmacy_user': pharmacy_user,
        'supplier_user': supplier_user,
        'drug': drug,
        'supply_info': supply_info
    }


def test_supply_info_auto_status():
    """测试供应信息自动上下架功能"""
    app = create_app()
    
    with app.app_context():
        print("=== 开始测试供应信息自动上下架功能 ===")
        
        # 清理旧数据
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
        db.session.query(SupplyInfo).delete()
        db.session.query(Drug).delete()
        db.session.query(User).delete()
        db.session.query(Tenant).delete()
        db.session.commit()
        
        # 设置测试数据
        test_data = setup_test_data()
        supply_info = test_data['supply_info']
        
        print(f"初始状态: 可供数量={supply_info.available_quantity}, 状态={supply_info.status}")
        
        # 测试1: 减少数量但不为0
        print("\n=== 测试1: 减少数量但不为0 ===")
        result = update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            -2,
            "测试减少2个"
        )
        db.session.commit()
        
        if result:
            print(f"更新后: 可供数量={result.available_quantity}, 状态={result.status}")
            assert result.available_quantity == 3, f"期望数量为3，实际为{result.available_quantity}"
            assert result.status == 'ACTIVE', f"期望状态为ACTIVE，实际为{result.status}"
            print("✅ 测试1通过")
        else:
            print("❌ 测试1失败：更新失败")
            return
        
        # 测试2: 减少数量至0，应该自动下架
        print("\n=== 测试2: 减少数量至0，应该自动下架 ===")
        result = update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            -3,
            "测试减少3个至0"
        )
        db.session.commit()
        
        if result:
            print(f"更新后: 可供数量={result.available_quantity}, 状态={result.status}")
            assert result.available_quantity == 0, f"期望数量为0，实际为{result.available_quantity}"
            assert result.status == 'INACTIVE', f"期望状态为INACTIVE，实际为{result.status}"
            print("✅ 测试2通过：数量为0时自动下架")
        else:
            print("❌ 测试2失败：更新失败")
            return
        
        # 测试3: 从0恢复数量，应该自动上架
        print("\n=== 测试3: 从0恢复数量，应该自动上架 ===")
        result = update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            10,
            "测试从0恢复10个"
        )
        db.session.commit()
        
        if result:
            print(f"更新后: 可供数量={result.available_quantity}, 状态={result.status}")
            assert result.available_quantity == 10, f"期望数量为10，实际为{result.available_quantity}"
            assert result.status == 'ACTIVE', f"期望状态为ACTIVE，实际为{result.status}"
            print("✅ 测试3通过：从0恢复时自动上架")
        else:
            print("❌ 测试3失败：更新失败")
            return
        
        # 测试4: 尝试减少超过可用数量（应该失败）
        print("\n=== 测试4: 尝试减少超过可用数量（应该失败） ===")
        result = update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            -15,
            "测试减少超量"
        )
        
        if result is None:
            # 刷新供应信息状态
            db.session.refresh(supply_info)
            print(f"更新失败（符合预期）: 可供数量={supply_info.available_quantity}, 状态={supply_info.status}")
            assert supply_info.available_quantity == 10, f"数量应保持不变，期望10，实际{supply_info.available_quantity}"
            assert supply_info.status == 'ACTIVE', f"状态应保持不变，期望ACTIVE，实际{supply_info.status}"
            print("✅ 测试4通过：减少超量时正确拒绝")
        else:
            print("❌ 测试4失败：应该拒绝超量减少")
            return
        
        print("\n=== 所有测试通过! ===")


def test_order_cancel_flow():
    """测试完整的下单-取消流程"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 开始测试完整的下单-取消流程 ===")
        
        # 使用现有测试数据
        supply_info = SupplyInfo.query.first()
        if not supply_info:
            print("❌ 没有找到测试供应信息")
            return
        
        test_data = {
            'supplier_tenant': supply_info.tenant,
            'drug': supply_info.drug
        }
        
        # 确保供应信息有足够库存
        update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            10 - supply_info.available_quantity,
            "重置为10个"
        )
        db.session.commit()
        
        print(f"重置后状态: 可供数量={supply_info.available_quantity}, 状态={supply_info.status}")
        
        # 模拟创建5个单品的订单
        print("\n=== 模拟创建5个单品的订单 ===")
        result = update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            -5,
            "模拟订单扣减5个"
        )
        db.session.commit()
        
        if result:
            print(f"下单后: 可供数量={result.available_quantity}, 状态={result.status}")
            assert result.available_quantity == 5, f"期望数量为5，实际为{result.available_quantity}"
            assert result.status == 'ACTIVE', f"期望状态为ACTIVE，实际为{result.status}"
            print("✅ 下单扣减成功")
        else:
            print("❌ 下单扣减失败")
            return
        
        # 模拟再次创建5个单品的订单（数量归0）
        print("\n=== 模拟再次创建5个单品的订单（数量归0） ===")
        result = update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            -5,
            "模拟第二个订单扣减5个"
        )
        db.session.commit()
        
        if result:
            print(f"再次下单后: 可供数量={result.available_quantity}, 状态={result.status}")
            assert result.available_quantity == 0, f"期望数量为0，实际为{result.available_quantity}"
            assert result.status == 'INACTIVE', f"期望状态为INACTIVE，实际为{result.status}"
            print("✅ 库存为0时自动下架")
        else:
            print("❌ 第二次下单失败")
            return
        
        # 模拟取消第一个订单（恢复5个）
        print("\n=== 模拟取消第一个订单（恢复5个） ===")
        result = update_supply_info_quantity(
            supply_info.tenant_id,
            supply_info.drug_id,
            5,
            "模拟取消第一个订单恢复5个"
        )
        db.session.commit()
        
        if result:
            print(f"取消订单后: 可供数量={result.available_quantity}, 状态={result.status}")
            assert result.available_quantity == 5, f"期望数量为5，实际为{result.available_quantity}"
            assert result.status == 'ACTIVE', f"期望状态为ACTIVE，实际为{result.status}"
            print("✅ 取消订单后自动上架")
        else:
            print("❌ 取消订单失败")
            return
        
        print("\n=== 订单流程测试通过! ===")


if __name__ == '__main__':
    print("开始测试供应信息自动上下架功能...")
    
    test_supply_info_auto_status()
    test_order_cancel_flow()
    
    print("\n🎉 所有测试完成!")
