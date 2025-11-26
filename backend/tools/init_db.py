#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建测试数据，包括企业、药品和用户数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import User, Tenant, Drug, SupplyInfo, Order, OrderItem
from datetime import datetime, date, timedelta

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建企业数据
        create_tenants()
        
        # 创建药品数据
        create_drugs()
        
        # 创建测试用户
        create_test_users()
        
        # 创建测试供应信息
        create_test_supply_info()
        
        # 创建测试订单
        create_test_orders()
        
        print("数据库初始化完成！")

def create_tenants():
    """创建企业数据"""
    tenants_data = [
        {
            'name': '上海医药集团股份有限公司',
            'type': 'SUPPLIER',
            'unified_social_credit_code': '91310000100010001X',
            'legal_representative': '李明',
            'contact_person': '张华',
            'contact_phone': '021-12345678',
            'contact_email': 'contact@shmedical.com',
            'address': '上海市浦东新区张江高科技园区',
            'business_scope': '药品批发、医疗器械销售'
        },
        {
            'name': '华润医药商业集团有限公司',
            'type': 'SUPPLIER',
            'unified_social_credit_code': '91310000200020002Y',
            'legal_representative': '王强',
            'contact_person': '陈丽',
            'contact_phone': '021-87654321',
            'contact_email': 'sales@crpharm.com',
            'address': '上海市静安区南京西路',
            'business_scope': '药品经营、医疗服务'
        },
        {
            'name': '复星医药集团',
            'type': 'SUPPLIER',
            'unified_social_credit_code': '91310000300030003Z',
            'legal_representative': '郭广昌',
            'contact_person': '刘芳',
            'contact_phone': '021-11223344',
            'contact_email': 'info@fosunpharma.com',
            'address': '上海市黄浦区中山南路',
            'business_scope': '药品研发生产、医疗健康服务'
        },
        {
            'name': '仁济医院药房',
            'type': 'PHARMACY',
            'unified_social_credit_code': '91310000400040004A',
            'legal_representative': '夏强',
            'contact_person': '护士长李红',
            'contact_phone': '021-58752345',
            'contact_email': 'pharmacy@renji.com',
            'address': '上海市浦东新区东方路1630号',
            'business_scope': '医疗服务、药品零售'
        },
        {
            'name': '华山医院药房',
            'type': 'PHARMACY',
            'unified_social_credit_code': '91310000500050005B',
            'legal_representative': '毛颖',
            'contact_person': '药剂科主任王医生',
            'contact_phone': '021-52889999',
            'contact_email': 'pharm@huashan.com',
            'address': '上海市静安区乌鲁木齐中路12号',
            'business_scope': '医疗服务、处方药调剂'
        }
    ]
    
    for tenant_data in tenants_data:
        existing_tenant = Tenant.query.filter_by(
            unified_social_credit_code=tenant_data['unified_social_credit_code']
        ).first()
        
        if not existing_tenant:
            tenant = Tenant(**tenant_data)
            db.session.add(tenant)
    
    db.session.commit()
    print("企业数据创建完成")

def create_drugs():
    """创建药品数据"""
    drugs_data = [
        {
            'generic_name': '阿莫西林胶囊',
            'brand_name': '阿莫仙',
            'approval_number': '国药准字H10930005',
            'dosage_form': '胶囊剂',
            'specification': '0.25g',
            'manufacturer': '石药集团中诺药业（石家庄）有限公司',
            'category': '抗菌药物',
            'prescription_type': '处方药'
        },
        {
            'generic_name': '布洛芬片',
            'brand_name': '芬必得',
            'approval_number': '国药准字H10900041',
            'dosage_form': '片剂',
            'specification': '0.2g',
            'manufacturer': '中美天津史克制药有限公司',
            'category': '解热镇痛药',
            'prescription_type': '非处方药'
        },
        {
            'generic_name': '连花清瘟胶囊',
            'brand_name': '连花清瘟',
            'approval_number': '国药准字Z20040063',
            'dosage_form': '胶囊剂',
            'specification': '0.35g',
            'manufacturer': '石家庄以岭药业股份有限公司',
            'category': '中成药',
            'prescription_type': '非处方药'
        },
        {
            'generic_name': '头孢克肟胶囊',
            'brand_name': '世福素',
            'approval_number': '国药准字H20000426',
            'dosage_form': '胶囊剂',
            'specification': '0.1g',
            'manufacturer': '齐鲁制药有限公司',
            'category': '抗菌药物',
            'prescription_type': '处方药'
        },
        {
            'generic_name': '奥美拉唑肠溶胶囊',
            'brand_name': '洛赛克',
            'approval_number': '国药准字H10950061',
            'dosage_form': '胶囊剂',
            'specification': '20mg',
            'manufacturer': '阿斯利康制药有限公司',
            'category': '消化系统用药',
            'prescription_type': '处方药'
        },
        {
            'generic_name': '氨溴索口服溶液',
            'brand_name': '沐舒坦',
            'approval_number': '国药准字H20100119',
            'dosage_form': '口服溶液',
            'specification': '15mg/5ml',
            'manufacturer': '勃林格殷格翰药业有限公司',
            'category': '呼吸系统用药',
            'prescription_type': '非处方药'
        },
        {
            'generic_name': '感冒灵颗粒',
            'brand_name': '三九感冒灵',
            'approval_number': '国药准字Z44020289',
            'dosage_form': '颗粒剂',
            'specification': '10g',
            'manufacturer': '华润三九医药股份有限公司',
            'category': '中成药',
            'prescription_type': '非处方药'
        },
        {
            'generic_name': '复方甘草片',
            'brand_name': '复方甘草片',
            'approval_number': '国药准字Z13020795',
            'dosage_form': '片剂',
            'specification': '每片含甘草流浸膏112.5mg',
            'manufacturer': '太极集团重庆桐君阁药厂有限公司',
            'category': '中成药',
            'prescription_type': '处方药'
        }
    ]
    
    for drug_data in drugs_data:
        existing_drug = Drug.query.filter_by(
            approval_number=drug_data['approval_number']
        ).first()
        
        if not existing_drug:
            drug = Drug(**drug_data)
            db.session.add(drug)
    
    db.session.commit()
    print("药品数据创建完成")

def create_test_users():
    """创建测试用户"""
    users_data = [
        {
            'username': 'supplier1',
            'email': 'supplier1@test.com',
            'phone': '13800001001',
            'role': 'supplier',
            'tenant_name': '上海医药集团股份有限公司',
            'is_authenticated': True,
            'password': 'password123'
        },
        {
            'username': 'supplier2',
            'email': 'supplier2@test.com',
            'phone': '13800001002',
            'role': 'supplier',
            'tenant_name': '华润医药商业集团有限公司',
            'is_authenticated': True,
            'password': 'password123'
        },
        {
            'username': 'supplier3',
            'email': 'supplier3@test.com',
            'phone': '13800001003',
            'role': 'supplier',
            'tenant_name': '复星医药集团',
            'is_authenticated': True,
            'password': 'password123'
        },
        {
            'username': 'pharmacy1',
            'email': 'pharmacy1@test.com',
            'phone': '13800002001',
            'role': 'pharmacy',
            'tenant_name': '仁济医院药房',
            'is_authenticated': True,
            'password': 'password123'
        },
        {
            'username': 'pharmacy2',
            'email': 'pharmacy2@test.com',
            'phone': '13800002002',
            'role': 'pharmacy',
            'tenant_name': '华山医院药房',
            'is_authenticated': True,
            'password': 'password123'
        }
    ]
    
    for user_data in users_data:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            # 查找对应的企业
            tenant = Tenant.query.filter_by(name=user_data['tenant_name']).first()
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                phone=user_data['phone'],
                role=user_data['role'],
                tenant_id=tenant.id if tenant else None,
                is_authenticated=user_data['is_authenticated']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
    
    db.session.commit()
    print("测试用户创建完成")

def create_test_supply_info():
    """创建测试供应信息"""
    # 获取供应商和药品
    suppliers = Tenant.query.filter_by(type='SUPPLIER').all()
    drugs = Drug.query.all()
    
    if not suppliers or not drugs:
        print("缺少供应商或药品数据，跳过供应信息创建")
        return
    
    # 创建一些测试供应信息
    supply_data = [
        {
            'supplier_name': '上海医药集团股份有限公司',
            'drug_name': '阿莫西林胶囊',
            'available_quantity': 5000,
            'unit_price': 15.80,
            'min_order_quantity': 100,
            'description': '质量优良，现货充足，支持大批量采购'
        },
        {
            'supplier_name': '上海医药集团股份有限公司',
            'drug_name': '布洛芬片',
            'available_quantity': 3000,
            'unit_price': 12.50,
            'min_order_quantity': 50,
            'description': '解热镇痛，疗效确切'
        },
        {
            'supplier_name': '华润医药商业集团有限公司',
            'drug_name': '连花清瘟胶囊',
            'available_quantity': 8000,
            'unit_price': 28.90,
            'min_order_quantity': 200,
            'description': '清热解毒，抗病毒感冒良药'
        },
        {
            'supplier_name': '华润医药商业集团有限公司',
            'drug_name': '头孢克肟胶囊',
            'available_quantity': 2500,
            'unit_price': 45.60,
            'min_order_quantity': 30,
            'description': '第三代头孢菌素，广谱抗菌'
        },
        {
            'supplier_name': '复星医药集团',
            'drug_name': '奥美拉唑肠溶胶囊',
            'available_quantity': 4500,
            'unit_price': 23.70,
            'min_order_quantity': 80,
            'description': '胃酸分泌抑制剂，治疗消化性溃疡'
        },
        {
            'supplier_name': '复星医药集团',
            'drug_name': '氨溴索口服溶液',
            'available_quantity': 1800,
            'unit_price': 18.40,
            'min_order_quantity': 40,
            'description': '祛痰药，适用于急慢性呼吸道疾病'
        }
    ]
    
    for data in supply_data:
        # 查找供应商
        supplier = next((s for s in suppliers if s.name == data['supplier_name']), None)
        if not supplier:
            continue
            
        # 查找药品
        drug = next((d for d in drugs if d.generic_name == data['drug_name']), None)
        if not drug:
            continue
        
        # 检查是否已存在
        existing = SupplyInfo.query.filter_by(
            tenant_id=supplier.id,
            drug_id=drug.id,
            status='ACTIVE'
        ).first()
        
        if not existing:
            supply_info = SupplyInfo(
                tenant_id=supplier.id,
                drug_id=drug.id,
                available_quantity=data['available_quantity'],
                unit_price=data['unit_price'],
                valid_until=date.today() + timedelta(days=365),  # 一年后过期
                min_order_quantity=data['min_order_quantity'],
                description=data['description'],
                status='ACTIVE'
            )
            db.session.add(supply_info)
    
    db.session.commit()
    print("测试供应信息创建完成")

def create_test_orders():
    """创建测试订单"""
    # 获取药店、供应商和供应信息
    pharmacy_users = User.query.filter_by(role='pharmacy', is_authenticated=True).all()
    supply_infos = SupplyInfo.query.filter_by(status='ACTIVE').all()
    
    if not pharmacy_users or not supply_infos:
        print("缺少药店用户或供应信息数据，跳过订单创建")
        return
    
    orders_data = [
        {
            'pharmacy_username': 'pharmacy1',
            'supply_info_index': 0,  # 阿莫西林胶囊
            'quantity': 200,
            'status': 'PENDING',
            'expected_delivery_date': date.today() + timedelta(days=3),
            'notes': '急需补货，请尽快发货'
        },
        {
            'pharmacy_username': 'pharmacy1',
            'supply_info_index': 2,  # 连花清瘟胶囊
            'quantity': 500,
            'status': 'CONFIRMED',
            'expected_delivery_date': date.today() + timedelta(days=5),
            'notes': '感冒季节备货',
            'days_ago': 1  # 1天前创建，已确认
        },
        {
            'pharmacy_username': 'pharmacy2',
            'supply_info_index': 1,  # 布洛芬片
            'quantity': 100,
            'status': 'SHIPPED',
            'expected_delivery_date': date.today() + timedelta(days=2),
            'notes': '常规补货',
            'days_ago': 2,  # 2天前创建
            'tracking_number': 'SF1234567890'
        },
        {
            'pharmacy_username': 'pharmacy2',
            'supply_info_index': 4,  # 奥美拉唑肠溶胶囊
            'quantity': 150,
            'status': 'COMPLETED',
            'expected_delivery_date': date.today() - timedelta(days=3),
            'notes': '已收货，药品质量良好',
            'days_ago': 5,  # 5天前创建
            'tracking_number': 'SF0987654321'
        }
    ]
    
    for data in orders_data:
        try:
            # 查找药店用户
            pharmacy_user = User.query.filter_by(username=data['pharmacy_username']).first()
            if not pharmacy_user or data['supply_info_index'] >= len(supply_infos):
                continue
            
            supply_info = supply_infos[data['supply_info_index']]
            
            # 检查是否已存在类似订单
            existing_order = Order.query.filter_by(
                buyer_tenant_id=pharmacy_user.tenant_id,
                supplier_tenant_id=supply_info.tenant_id
            ).join(OrderItem).filter_by(drug_id=supply_info.drug_id).first()
            
            if existing_order:
                continue
            
            # 计算创建时间
            created_at = datetime.utcnow()
            if data.get('days_ago'):
                created_at = datetime.utcnow() - timedelta(days=data['days_ago'])
            
            # 创建订单
            order = Order(
                buyer_tenant_id=pharmacy_user.tenant_id,
                supplier_tenant_id=supply_info.tenant_id,
                expected_delivery_date=data['expected_delivery_date'],
                notes=data['notes'],
                status=data['status'],
                created_by=pharmacy_user.id,
                created_at=created_at,
                updated_at=created_at
            )
            
            # 创建订单明细
            order_item = OrderItem(
                drug_id=supply_info.drug_id,
                unit_price=supply_info.unit_price,
                quantity=data['quantity']
            )
            order.items.append(order_item)
            
            # 根据订单状态设置额外字段
            if data['status'] in ['CONFIRMED', 'SHIPPED', 'COMPLETED']:
                # 模拟供应商确认
                supplier_user = User.query.filter_by(
                    tenant_id=supply_info.tenant_id, 
                    role='supplier'
                ).first()
                if supplier_user:
                    order.confirmed_by = supplier_user.id
                    order.confirmed_at = created_at + timedelta(hours=2)
            
            if data['status'] in ['SHIPPED', 'COMPLETED']:
                # 设置发货信息
                order.shipped_at = created_at + timedelta(hours=4)
                if data.get('tracking_number'):
                    order.tracking_number = data['tracking_number']
            
            if data['status'] == 'COMPLETED':
                # 设置收货信息
                order.delivered_at = created_at + timedelta(days=2)
                order.received_at = created_at + timedelta(days=2, hours=1)
                order.received_confirmed_by = pharmacy_user.id
            
            db.session.add(order)
            
            # 更新供应信息库存（模拟已占用的库存）
            supply_info.available_quantity = max(0, supply_info.available_quantity - data['quantity'])
            
        except Exception as e:
            print(f"创建测试订单失败: {str(e)}")
            continue
    
    db.session.commit()
    print("测试订单创建完成")

if __name__ == '__main__':
    init_database()
