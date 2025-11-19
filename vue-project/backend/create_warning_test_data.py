"""
创建库存预警测试数据
用于测试库存预警功能的示例数据
"""
from datetime import datetime, timedelta
from models import db, Tenant, User, Drug, InventoryItem
from werkzeug.security import generate_password_hash


def create_test_data():
    """创建测试数据"""
    try:
        # 创建测试租户（药店）
        test_tenant = Tenant(
            name="测试药店",
            type="PHARMACY",
            unified_social_credit_code="91310000TEST001",
            legal_representative="张三",
            contact_person="李四",
            contact_phone="13800138001",
            contact_email="test@pharmacy.com",
            address="上海市浦东新区测试路123号",
            business_scope="药品零售"
        )
        db.session.add(test_tenant)
        db.session.flush()
        
        # 创建测试用户
        test_user = User(
            username="test_pharmacy",
            email="test@pharmacy.com",
            phone="13800138001",
            password_hash=generate_password_hash("password123"),
            role="PHARMACY",
            tenant_id=test_tenant.id,
            is_authenticated=True
        )
        db.session.add(test_user)
        db.session.flush()
        
        # 创建测试药品
        drugs_data = [
            {
                "generic_name": "阿司匹林肠溶片",
                "brand_name": "拜阿司匹林",
                "approval_number": "H20013142",
                "dosage_form": "片剂",
                "specification": "100mg",
                "manufacturer": "拜耳医药保健有限公司",
                "category": "化学药品",
                "prescription_type": "OTC"
            },
            {
                "generic_name": "布洛芬缓释胶囊",
                "brand_name": "芬必得",
                "approval_number": "H10900012",
                "dosage_form": "胶囊",
                "specification": "300mg",
                "manufacturer": "中美天津史克制药有限公司",
                "category": "化学药品",
                "prescription_type": "OTC"
            },
            {
                "generic_name": "阿莫西林胶囊",
                "brand_name": "阿莫仙",
                "approval_number": "H44020378",
                "dosage_form": "胶囊",
                "specification": "250mg",
                "manufacturer": "东北制药集团沈阳第一制药有限公司",
                "category": "抗生素",
                "prescription_type": "处方药"
            },
            {
                "generic_name": "维生素C片",
                "brand_name": "维C银翘片",
                "approval_number": "Z20025001",
                "dosage_form": "片剂",
                "specification": "100mg",
                "manufacturer": "华北制药股份有限公司",
                "category": "维生素类",
                "prescription_type": "OTC"
            }
        ]
        
        created_drugs = []
        for drug_data in drugs_data:
            drug = Drug(**drug_data)
            db.session.add(drug)
            created_drugs.append(drug)
        
        db.session.flush()
        
        # 创建库存测试数据（包含预警场景）
        now = datetime.now()
        
        inventory_data = [
            # 正常库存
            {
                "drug_id": created_drugs[0].id,
                "batch_number": "20240501A01",
                "production_date": now.date() - timedelta(days=90),
                "expiry_date": now.date() + timedelta(days=365),  # 1年后过期
                "quantity": 50,
                "unit_price": 15.80
            },
            
            # 低库存预警（数量 < 10）
            {
                "drug_id": created_drugs[0].id,
                "batch_number": "20240502B01", 
                "production_date": now.date() - timedelta(days=60),
                "expiry_date": now.date() + timedelta(days=300),
                "quantity": 5,  # 低库存
                "unit_price": 15.80
            },
            
            # 库存为0（严重预警）
            {
                "drug_id": created_drugs[1].id,
                "batch_number": "20240503C01",
                "production_date": now.date() - timedelta(days=120),
                "expiry_date": now.date() + timedelta(days=180),
                "quantity": 0,  # 零库存
                "unit_price": 28.50
            },
            
            # 近效期预警（30天内过期）
            {
                "drug_id": created_drugs[1].id,
                "batch_number": "20240401D01",
                "production_date": now.date() - timedelta(days=300),
                "expiry_date": now.date() + timedelta(days=20),  # 20天后过期
                "quantity": 25,
                "unit_price": 28.50
            },
            
            # 即将过期（7天内，严重预警）
            {
                "drug_id": created_drugs[2].id,
                "batch_number": "20240301E01",
                "production_date": now.date() - timedelta(days=330),
                "expiry_date": now.date() + timedelta(days=5),  # 5天后过期
                "quantity": 15,
                "unit_price": 42.00
            },
            
            # 已过期（严重预警）
            {
                "drug_id": created_drugs[2].id,
                "batch_number": "20231201F01", 
                "production_date": now.date() - timedelta(days=400),
                "expiry_date": now.date() - timedelta(days=10),  # 已过期10天
                "quantity": 8,
                "unit_price": 42.00
            },
            
            # 双重预警（低库存 + 近效期）
            {
                "drug_id": created_drugs[3].id,
                "batch_number": "20240315G01",
                "production_date": now.date() - timedelta(days=200),
                "expiry_date": now.date() + timedelta(days=25),  # 25天后过期
                "quantity": 3,  # 低库存
                "unit_price": 12.50
            },
            
            # 正常库存2
            {
                "drug_id": created_drugs[3].id,
                "batch_number": "20240520H01",
                "production_date": now.date() - timedelta(days=30),
                "expiry_date": now.date() + timedelta(days=400),
                "quantity": 80,
                "unit_price": 12.50
            }
        ]
        
        for inv_data in inventory_data:
            inventory = InventoryItem(
                tenant_id=test_tenant.id,
                **inv_data
            )
            db.session.add(inventory)
        
        # 提交所有更改
        db.session.commit()
        
        print("测试数据创建成功！")
        print(f"创建租户: {test_tenant.name}")
        print(f"创建用户: {test_user.username}")
        print(f"创建药品: {len(created_drugs)} 个")
        print(f"创建库存记录: {len(inventory_data)} 个")
        
        # 统计预警情况
        print("\n预警情况统计:")
        print("- 正常库存: 2 个")
        print("- 低库存预警: 2 个")
        print("- 零库存: 1 个") 
        print("- 近效期预警: 3 个")
        print("- 已过期: 1 个")
        print("- 双重预警: 1 个")
        
        return test_tenant, test_user, created_drugs
        
    except Exception as e:
        db.session.rollback()
        print(f"创建测试数据失败: {str(e)}")
        raise


def clear_test_data():
    """清理测试数据"""
    try:
        # 删除测试库存
        InventoryItem.query.filter(
            InventoryItem.batch_number.like('202%')
        ).delete()
        
        # 删除测试用户
        User.query.filter(User.username == 'test_pharmacy').delete()
        
        # 删除测试租户
        Tenant.query.filter(Tenant.name == '测试药店').delete()
        
        # 删除测试药品（谨慎操作，可能影响其他数据）
        test_drugs = ['阿司匹林肠溶片', '布洛芬缓释胶囊', '阿莫西林胶囊', '维生素C片']
        Drug.query.filter(Drug.generic_name.in_(test_drugs)).delete()
        
        db.session.commit()
        print("测试数据清理完成！")
        
    except Exception as e:
        db.session.rollback()
        print(f"清理测试数据失败: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_test_data()
    else:
        create_test_data()
