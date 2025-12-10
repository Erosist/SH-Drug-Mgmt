#!/usr/bin/env python3
"""
清空并重新导入药品数据
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
from models import Drug

# JSON 文件路径
JSON_FILE = r"d:\xwechat_files\wxid_5tylomcbmtlm22_6f53\msg\file\2025-11\drugs(1).json"

def import_drugs():
    """导入药品数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("清空并重新导入药品数据")
        print("=" * 80)
        
        try:
            # 读取 JSON 文件
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                drugs = json.load(f)
            
            print(f"\n从 JSON 文件读取到 {len(drugs)} 条药品记录")
            
            # 清空现有药品数据
            existing_count = Drug.query.count()
            if existing_count > 0:
                print(f"\n正在清空现有的 {existing_count} 条药品数据...")
                Drug.query.delete()
                db.session.commit()
                print(f"✅ 已清空 {existing_count} 条记录")
            
            added_count = 0
            error_count = 0
            
            print("\n开始导入新数据...")
            for idx, drug in enumerate(drugs, 1):
                try:
                    # 解析日期
                    created_at = datetime.fromisoformat(drug['created_at'].replace('+08:00', '')) if drug.get('created_at') else datetime.utcnow()
                    updated_at = datetime.fromisoformat(drug['updated_at'].replace('+08:00', '')) if drug.get('updated_at') else datetime.utcnow()
                    
                    # 创建药品记录
                    new_drug = Drug(
                        generic_name=drug['generic_name'],
                        brand_name=drug['brand_name'],
                        approval_number=drug['approval_number'],
                        dosage_form=drug['dosage_form'],
                        specification=drug['specification'],
                        manufacturer=drug['manufacturer'],
                        category=drug['category'],
                        prescription_type=drug['prescription_type'],
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    
                    db.session.add(new_drug)
                    added_count += 1
                    
                    # 每50条提交一次
                    if idx % 50 == 0:
                        db.session.commit()
                        print(f"  已处理 {idx}/{len(drugs)} 条记录...")
                
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
            print(f"  成功: {added_count} 条")
            print(f"  失败: {error_count} 条")
            print(f"  总计: {len(drugs)} 条")
            print("=" * 80)
            print("\n✅ 成功替换药品数据")
            
            # 显示一些示例
            print("\n前10条药品数据:")
            sample_drugs = Drug.query.limit(10).all()
            for drug in sample_drugs:
                print(f"  ID {drug.id:2d}: {drug.generic_name} ({drug.brand_name}) - {drug.manufacturer}")
            
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
    success = import_drugs()
    sys.exit(0 if success else 1)
