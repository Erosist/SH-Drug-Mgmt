#!/usr/bin/env python3
"""
从 JSON 文件导入库存数据到 inventory_items 表
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 确保可以导入项目模块
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import InventoryItem

# JSON 文件路径
JSON_FILE = r"d:\xwechat_files\wxid_5tylomcbmtlm22_6f53\msg\file\2025-11\inventory_items_updated.json"

def import_inventory_items():
    """导入库存数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("开始导入库存数据")
        print("=" * 80)
        
        try:
            # 读取 JSON 文件
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                items = json.load(f)
            
            print(f"\n从 JSON 文件读取到 {len(items)} 条库存记录")
            
            # 检查现有数据
            existing_count = InventoryItem.query.count()
            if existing_count > 0:
                print(f"\n📊 数据库中已有 {existing_count} 条库存记录")
                print("将在保留现有数据的基础上添加新数据")
            
            added_count = 0
            skipped_count = 0
            error_count = 0
            
            # 获取现有的批次号,避免重复
            existing_batches = set()
            existing_items = InventoryItem.query.all()
            for ei in existing_items:
                existing_batches.add((ei.tenant_id, ei.drug_id, ei.batch_number))
            
            print(f"现有唯一批次: {len(existing_batches)} 个")
            
            print("\n开始导入...")
            for idx, item in enumerate(items, 1):
                try:
                    # 检查是否已存在相同的批次
                    batch_key = (item['tenant_id'], item['drug_id'], item['batch_number'])
                    if batch_key in existing_batches:
                        skipped_count += 1
                        continue
                    
                    # 解析日期
                    production_date = datetime.fromisoformat(item['production_date'].replace('Z', '+00:00')).date() if item.get('production_date') else None
                    expiry_date = datetime.fromisoformat(item['expiry_date'].replace('Z', '+00:00')).date() if item.get('expiry_date') else None
                    created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')) if item.get('created_at') else datetime.utcnow()
                    updated_at = datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00')) if item.get('updated_at') else datetime.utcnow()
                    
                    # 创建库存记录
                    inventory_item = InventoryItem(
                        tenant_id=item['tenant_id'],
                        drug_id=item['drug_id'],
                        batch_number=item['batch_number'],
                        production_date=production_date,
                        expiry_date=expiry_date,
                        quantity=item['quantity'],
                        unit_price=item['unit_price'],
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    
                    db.session.add(inventory_item)
                    existing_batches.add(batch_key)
                    added_count += 1
                    
                    # 每100条提交一次
                    if idx % 100 == 0:
                        db.session.commit()
                        print(f"  已处理 {idx}/{len(items)} 条记录...")
                
                except Exception as e:
                    error_count += 1
                    print(f"  ❌ 记录 {idx} 导入失败: {e}")
                    if error_count > 10:
                        print("\n错误过多,停止导入")
                        db.session.rollback()
                        return False
            
            # 提交剩余的记录
            db.session.commit()
            
            print("\n" + "=" * 80)
            print("导入完成:")
            print(f"  新增: {added_count} 条")
            print(f"  跳过: {skipped_count} 条 (已存在)")
            print(f"  失败: {error_count} 条")
            print(f"  总计: {len(items)} 条")
            print(f"  数据库总数: {existing_count + added_count} 条")
            print("=" * 80)
            print("\n✅ 成功导入库存数据到数据库")
            
            return True
            
        except FileNotFoundError:
            print(f"\n❌ 错误: 找不到文件 {JSON_FILE}")
            return False
        except json.JSONDecodeError as e:
            print(f"\n❌ 错误: JSON 文件格式不正确")
            print(f"详细信息: {e}")
            return False
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 导入失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = import_inventory_items()
    sys.exit(0 if success else 1)
