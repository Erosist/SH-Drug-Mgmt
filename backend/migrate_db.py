"""
使用 Flask-Migrate 应用数据库迁移
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from flask_migrate import upgrade, stamp

def apply_migration():
    """应用数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("正在应用数据库迁移...")
            
            # 应用所有待处理的迁移
            upgrade()
            
            print("✓ 数据库迁移成功！")
            
            # 验证字段
            from models import Tenant
            from sqlalchemy import inspect
            
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('tenants')]
            
            print(f"\ntenants 表的所有字段: {', '.join(columns)}")
            
            if 'latitude' in columns and 'longitude' in columns:
                print("\n✓ 经纬度字段已成功添加")
            else:
                print("\n✗ 警告: 经纬度字段未找到")
            
        except Exception as e:
            print(f"\n✗ 迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    apply_migration()
