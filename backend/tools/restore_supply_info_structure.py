#!/usr/bin/env python3
"""
从 supply_info 表移除 address, latitude, longitude 字段
恢复到原始的表结构
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

def remove_location_fields():
    """移除 supply_info 表的地理位置字段"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("开始恢复 supply_info 表结构")
        print("=" * 80)
        
        try:
            # SQLite 不支持 DROP COLUMN，需要重建表
            print("\n步骤 1: 创建新的 supply_info 表...")
            
            # 创建临时表
            db.session.execute(text("""
                CREATE TABLE supply_info_new (
                    id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    drug_id INTEGER NOT NULL,
                    available_quantity INTEGER NOT NULL,
                    unit_price NUMERIC(10,2) NOT NULL,
                    valid_until DATE NOT NULL,
                    min_order_quantity INTEGER NOT NULL DEFAULT 1,
                    description TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (drug_id) REFERENCES drugs(id)
                )
            """))
            
            print("✅ 创建临时表成功")
            
            # 复制数据（只复制原始字段）
            print("\n步骤 2: 复制数据到新表...")
            db.session.execute(text("""
                INSERT INTO supply_info_new 
                (id, tenant_id, drug_id, available_quantity, unit_price, valid_until, 
                 min_order_quantity, description, status, created_at, updated_at)
                SELECT id, tenant_id, drug_id, available_quantity, unit_price, valid_until,
                       min_order_quantity, description, status, created_at, updated_at
                FROM supply_info
            """))
            
            print("✅ 数据复制成功")
            
            # 删除旧表
            print("\n步骤 3: 删除旧表...")
            db.session.execute(text("DROP TABLE supply_info"))
            print("✅ 删除旧表成功")
            
            # 重命名新表
            print("\n步骤 4: 重命名新表...")
            db.session.execute(text("ALTER TABLE supply_info_new RENAME TO supply_info"))
            print("✅ 重命名成功")
            
            # 重建索引
            print("\n步骤 5: 重建索引...")
            db.session.execute(text("CREATE INDEX idx_supply_tenant ON supply_info(tenant_id)"))
            db.session.execute(text("CREATE INDEX idx_supply_drug ON supply_info(drug_id)"))
            db.session.execute(text("CREATE INDEX idx_supply_status ON supply_info(status)"))
            print("✅ 索引创建成功")
            
            db.session.commit()
            
            # 验证结果
            print("\n步骤 6: 验证表结构...")
            result = db.session.execute(text("PRAGMA table_info(supply_info)"))
            columns = [row[1] for row in result]
            
            print("\n当前字段列表:")
            for col in columns:
                print(f"  - {col}")
            
            print("\n" + "=" * 80)
            print("✅ supply_info 表已恢复到原始结构！")
            print("   移除了: address, latitude, longitude")
            print("   保留了原始的 11 个字段")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 恢复失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = remove_location_fields()
    sys.exit(0 if success else 1)
