#!/usr/bin/env python3
"""
删除之前导入的供应商数据（ID 51-80）
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
from models import Tenant

def delete_imported_suppliers():
    """删除之前导入的供应商数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("开始删除之前导入的供应商数据")
        print("=" * 80)
        
        try:
            # 查询所有匹配的供应商
            suppliers_to_delete = Tenant.query.filter(
                Tenant.name.in_([
                    '嘉定康源医药供应有限公司',
                    '上海华安药品批发有限公司',
                    '嘉定瑞康医药贸易有限公司',
                    '上海永康医药配送有限公司',
                    '嘉定康泰药品代理有限公司',
                    '上海华康医药供应链管理有限公司',
                    '嘉定康宁中药材批发有限公司',
                    '上海永泰医药物流配送有限公司',
                    '嘉定康盛医药原料供应有限公司',
                    '上海华泰医疗器械代理有限公司',
                    '嘉定医药物流供应链管理有限公司',
                    '上海康达医药供应有限公司',
                    '华东医药物流配送有限公司',
                    '嘉定医药批发供应链有限公司',
                    '上海瑞康医药代理有限公司',
                    '嘉定医药物流仓储有限公司',
                    '上海华医药供应链管理有限公司',
                    '嘉定康达医疗器械供应有限公司',
                    '上海医药进出口贸易有限公司',
                    '嘉定中药材批发供应链有限公司',
                    '上海华仁医药配送有限公司',
                    '嘉定百草中药材批发有限公司',
                    '上海康泰医药贸易有限公司',
                    '嘉定安达医药供应链管理有限公司',
                    '上海仁济医疗器械供应有限公司',
                    '嘉定华康药品批发有限公司',
                    '上海康宁医药代理有限公司',
                    '嘉定瑞康医药配送有限公司',
                    '上海本草中药材供应有限公司'
                ])
            ).all()
            
            if not suppliers_to_delete:
                print("\n⚠️  没有找到需要删除的供应商")
                return True
            
            print(f"\n找到 {len(suppliers_to_delete)} 条需要删除的记录:\n")
            
            for supplier in suppliers_to_delete:
                print(f"  - ID: {supplier.id}, 名称: {supplier.name}")
            
            # 删除记录
            for supplier in suppliers_to_delete:
                db.session.delete(supplier)
            
            db.session.commit()
            
            print("\n" + "=" * 80)
            print(f"✅ 成功删除 {len(suppliers_to_delete)} 条供应商记录")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 删除失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = delete_imported_suppliers()
    sys.exit(0 if success else 1)
