#!/usr/bin/env python3
"""
更新 inventory_items.json 中的 tenant_id 以匹配新的数据库结构
"""

import json
import sys
from pathlib import Path

# 文件路径
INPUT_FILE = r"d:\xwechat_files\wxid_5tylomcbmtlm22_6f53\msg\file\2025-11\inventory_items.json"
OUTPUT_FILE = r"d:\xwechat_files\wxid_5tylomcbmtlm22_6f53\msg\file\2025-11\inventory_items_updated.json"

# 添加项目路径
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import Tenant

def get_pharmacy_mapping():
    """从数据库获取当前的药店 ID"""
    app = create_app()
    
    with app.app_context():
        # 获取所有药店
        pharmacies = Tenant.query.filter_by(type='PHARMACY').order_by(Tenant.id).all()
        
        print(f"\n当前数据库中有 {len(pharmacies)} 个药店:")
        print("=" * 80)
        
        # 创建映射: 旧 ID (1-50) -> 新 ID
        # 策略: 将旧的 1-50 映射到新导入的药店 ID 15-64
        pharmacy_ids = [p.id for p in pharmacies if p.id >= 15]  # 只使用新导入的药店
        
        mapping = {}
        for old_id in range(1, 51):
            # 循环使用新导入的药店 ID
            new_id = pharmacy_ids[(old_id - 1) % len(pharmacy_ids)]
            mapping[old_id] = new_id
        
        # 显示前10个映射
        print("\n映射规则 (前10个):")
        for i in range(1, 11):
            pharmacy = next(p for p in pharmacies if p.id == mapping[i])
            print(f"  旧ID {i:2d} -> 新ID {mapping[i]:2d} ({pharmacy.name})")
        
        print(f"\n... (共 {len(mapping)} 个映射)")
        print("=" * 80)
        
        return mapping

def update_tenant_ids():
    """更新 JSON 文件中的 tenant_id"""
    try:
        # 读取 JSON 文件
        print(f"\n正在读取文件: {INPUT_FILE}")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        print(f"读取到 {len(items)} 条库存记录")
        
        # 获取映射关系
        mapping = get_pharmacy_mapping()
        
        # 更新 tenant_id
        print("\n正在更新 tenant_id...")
        updated_count = 0
        
        for item in items:
            old_tenant_id = item['tenant_id']
            if old_tenant_id in mapping:
                item['tenant_id'] = mapping[old_tenant_id]
                updated_count += 1
        
        # 写入新文件
        print(f"\n正在保存到: {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print(f"✅ 更新完成!")
        print(f"   总记录数: {len(items)}")
        print(f"   更新记录: {updated_count}")
        print(f"   输出文件: {OUTPUT_FILE}")
        print("=" * 80)
        
        return True
        
    except FileNotFoundError:
        print(f"\n❌ 错误: 找不到文件 {INPUT_FILE}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n❌ 错误: JSON 格式错误 - {e}")
        return False
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = update_tenant_ids()
    sys.exit(0 if success else 1)
