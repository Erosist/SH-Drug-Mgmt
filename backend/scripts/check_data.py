#!/usr/bin/env python3
"""
检查当前数据库中的供应信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import User, Tenant, Drug, SupplyInfo


def check_database_data():
    """检查数据库中的数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 数据库数据检查 ===")
        
        # 检查供应信息
        print("\n供应信息列表:")
        supplies = SupplyInfo.query.all()
        for supply in supplies:
            print(f"  ID: {supply.id}, 企业ID: {supply.tenant_id}, 药品ID: {supply.drug_id}, "
                  f"数量: {supply.available_quantity}, 状态: {supply.status}")
        
        # 检查企业
        print("\n企业列表:")
        tenants = Tenant.query.all()
        for tenant in tenants:
            print(f"  ID: {tenant.id}, 名称: {tenant.name}, 类型: {tenant.type}")
        
        # 检查药品
        print("\n药品列表:")
        drugs = Drug.query.all()
        for drug in drugs:
            print(f"  ID: {drug.id}, 通用名: {drug.generic_name}, 商品名: {drug.brand_name}")


if __name__ == '__main__':
    check_database_data()
