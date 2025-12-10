#!/usr/bin/env python3
"""
为 supply_info 表添加地理位置字段
并从关联的 tenant 复制地址和坐标信息
"""

import sys
import os
from pathlib import Path

# 确保可以导入项目模块
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from sqlalchemy import text

def migrate_supply_info():
    """迁移 supply_info 表"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("开始迁移 supply_info 表")
        print("=" * 80)
        
        try:
            # 1. 添加新字段
            print("\n步骤 1: 添加 address, latitude, longitude 字段...")
            
            # 检查字段是否已存在
            result = db.session.execute(text("PRAGMA table_info(supply_info)"))
            columns = [row[1] for row in result]
            
            if 'address' not in columns:
                db.session.execute(text("ALTER TABLE supply_info ADD COLUMN address VARCHAR(255)"))
                print("✅ 添加 address 字段")
            else:
                print("⚠️  address 字段已存在")
            
            if 'latitude' not in columns:
                db.session.execute(text("ALTER TABLE supply_info ADD COLUMN latitude REAL"))
                print("✅ 添加 latitude 字段")
            else:
                print("⚠️  latitude 字段已存在")
            
            if 'longitude' not in columns:
                db.session.execute(text("ALTER TABLE supply_info ADD COLUMN longitude REAL"))
                print("✅ 添加 longitude 字段")
            else:
                print("⚠️  longitude 字段已存在")
            
            db.session.commit()
            
            # 2. 从 tenants 表复制数据到 supply_info
            print("\n步骤 2: 从 tenants 表复制地址和坐标到 supply_info...")
            
            update_sql = """
                UPDATE supply_info 
                SET 
                    address = (SELECT address FROM tenants WHERE tenants.id = supply_info.tenant_id),
                    latitude = (SELECT latitude FROM tenants WHERE tenants.id = supply_info.tenant_id),
                    longitude = (SELECT longitude FROM tenants WHERE tenants.id = supply_info.tenant_id)
            """
            
            result = db.session.execute(text(update_sql))
            db.session.commit()
            
            print(f"✅ 更新了供应信息的地址和坐标")
            
            # 3. 验证结果
            print("\n步骤 3: 验证更新结果...")
            result = db.session.execute(text("""
                SELECT id, tenant_id, drug_id, address, latitude, longitude 
                FROM supply_info 
                LIMIT 5
            """))
            
            print("\n供应信息样本数据:")
            print("-" * 80)
            for row in result:
                print(f"ID: {row[0]}, Tenant: {row[1]}, Drug: {row[2]}")
                print(f"  地址: {row[3]}")
                print(f"  坐标: ({row[4]}, {row[5]})")
                print()
            
            # 统计有坐标的记录
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM supply_info 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            """))
            count_with_coords = result.scalar()
            
            result = db.session.execute(text("SELECT COUNT(*) FROM supply_info"))
            total_count = result.scalar()
            
            print("=" * 80)
            print(f"✅ 迁移完成！")
            print(f"   总记录数: {total_count}")
            print(f"   有坐标的记录: {count_with_coords}")
            print(f"   无坐标的记录: {total_count - count_with_coords}")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate_supply_info()
    sys.exit(0 if success else 1)
