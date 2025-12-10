#!/usr/bin/env python3
"""
从 JSON 文件导入供应商数据到 tenants 表
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 确保可以导入项目模块
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import Tenant

# JSON 文件路径
JSON_FILE = r"d:\xwechat_files\wxid_5tylomcbmtlm22_6f53\msg\file\2025-12\tenants_supplier.json"

def import_suppliers():
    """导入供应商数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("开始导入供应商数据")
        print("=" * 80)
        
        try:
            # 读取 JSON 文件
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                suppliers = json.load(f)
            
            print(f"\n从 JSON 文件读取到 {len(suppliers)} 条供应商记录")
            
            added_count = 0
            updated_count = 0
            skipped_count = 0
            
            for supplier in suppliers:
                # 检查是否已存在（通过统一社会信用代码）
                existing = Tenant.query.filter_by(
                    unified_social_credit_code=supplier['unified_social_credit_code']
                ).first()
                
                if existing:
                    print(f"  跳过: {supplier['name']} - 已存在")
                    skipped_count += 1
                    continue
                
                # 解析日期时间
                created_at = datetime.fromisoformat(supplier['created_at'].replace('Z', '+00:00'))
                updated_at = datetime.fromisoformat(supplier['updated_at'].replace('Z', '+00:00'))
                
                # 创建新的 Tenant 记录 - 不指定 ID,让数据库自动分配
                tenant = Tenant(
                    name=supplier['name'],
                    type=supplier['type'],
                    unified_social_credit_code=supplier['unified_social_credit_code'],
                    legal_representative=supplier['legal_representative'],
                    contact_person=supplier['contact_person'],
                    contact_phone=supplier['contact_phone'],
                    contact_email=supplier['contact_email'],
                    address=supplier['address'],
                    business_scope=supplier['business_scope'],
                    is_active=supplier['is_active'],
                    created_at=created_at,
                    updated_at=updated_at,
                    latitude=None,  # 稍后需要通过地址解析获取
                    longitude=None
                )
                
                db.session.add(tenant)
                db.session.flush()  # 刷新以获取自动分配的 ID
                print(f"  添加: {supplier['name']} (ID: {tenant.id})")
                added_count += 1
            
            # 提交所有更改
            db.session.commit()
            
            print("\n" + "=" * 80)
            print(f"✅ 导入完成！")
            print(f"   新增: {added_count} 条")
            print(f"   跳过: {skipped_count} 条 (已存在)")
            print("=" * 80)
            print("\n提示: 这些供应商的经纬度坐标为 NULL，需要单独添加坐标信息")
            
            return True
            
        except FileNotFoundError:
            print(f"\n❌ 错误: 找不到文件 {JSON_FILE}")
            return False
        except json.JSONDecodeError as e:
            print(f"\n❌ 错误: JSON 格式错误 - {e}")
            return False
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 导入失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = import_suppliers()
    sys.exit(0 if success else 1)
