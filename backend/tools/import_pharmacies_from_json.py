#!/usr/bin/env python3
"""
从 JSON 文件导入药店数据到 tenants 表
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
JSON_FILE = r"d:\xwechat_files\wxid_5tylomcbmtlm22_6f53\msg\file\2025-11\tenants_pharmacy.json"

def import_pharmacies():
    """导入药店数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("开始导入药店数据")
        print("=" * 80)
        
        try:
            # 读取 JSON 文件
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                pharmacies = json.load(f)
            
            print(f"\n从 JSON 文件读取到 {len(pharmacies)} 条药店记录")
            
            added_count = 0
            updated_count = 0
            skipped_count = 0
            
            for pharmacy in pharmacies:
                # 检查是否已存在（通过统一社会信用代码）
                existing = Tenant.query.filter_by(
                    unified_social_credit_code=pharmacy['unified_social_credit_code']
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.name = pharmacy.get('name', existing.name)
                    existing.type = pharmacy.get('type', existing.type)
                    existing.legal_representative = pharmacy.get('legal_representative', existing.legal_representative)
                    existing.contact_person = pharmacy.get('contact_person', existing.contact_person)
                    existing.contact_phone = pharmacy.get('contact_phone', existing.contact_phone)
                    existing.contact_email = pharmacy.get('contact_email', existing.contact_email)
                    existing.address = pharmacy.get('address', existing.address)
                    existing.business_scope = pharmacy.get('business_scope', existing.business_scope)
                    existing.is_active = pharmacy.get('is_active', existing.is_active)
                    existing.updated_at = datetime.utcnow()
                    
                    updated_count += 1
                    print(f"  更新: {pharmacy['name']} (ID: {existing.id})")
                else:
                    # 创建新记录 - 不指定 ID,让数据库自动分配
                    new_pharmacy = Tenant(
                        name=pharmacy['name'],
                        type=pharmacy['type'],
                        unified_social_credit_code=pharmacy['unified_social_credit_code'],
                        legal_representative=pharmacy['legal_representative'],
                        contact_person=pharmacy['contact_person'],
                        contact_phone=pharmacy['contact_phone'],
                        contact_email=pharmacy['contact_email'],
                        address=pharmacy['address'],
                        business_scope=pharmacy.get('business_scope', ''),
                        is_active=pharmacy.get('is_active', True),
                        created_at=datetime.fromisoformat(pharmacy['created_at'].replace('Z', '+00:00')) if 'created_at' in pharmacy else datetime.utcnow(),
                        updated_at=datetime.fromisoformat(pharmacy['updated_at'].replace('Z', '+00:00')) if 'updated_at' in pharmacy else datetime.utcnow()
                    )
                    
                    db.session.add(new_pharmacy)
                    db.session.flush()  # 刷新以获取自动分配的 ID
                    added_count += 1
                    print(f"  添加: {pharmacy['name']} (ID: {new_pharmacy.id})")
            
            # 提交事务
            db.session.commit()
            
            print("\n" + "=" * 80)
            print("导入完成:")
            print(f"  新增: {added_count} 条")
            print(f"  更新: {updated_count} 条")
            print(f"  跳过: {skipped_count} 条")
            print(f"  总计处理: {added_count + updated_count + skipped_count} 条")
            print("=" * 80)
            print("\n✅ 成功导入药店数据到数据库")
            
        except FileNotFoundError:
            print(f"\n❌ 错误: 找不到文件 {JSON_FILE}")
            print("请确认文件路径是否正确")
        except json.JSONDecodeError as e:
            print(f"\n❌ 错误: JSON 文件格式不正确")
            print(f"详细信息: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 导入失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    import_pharmacies()
