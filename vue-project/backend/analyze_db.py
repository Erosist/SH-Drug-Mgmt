#!/usr/bin/env python
"""
检查数据库结构和索引
"""
from app import create_app
from extensions import db
from sqlalchemy import inspect

def analyze_database():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        print('=== 数据库表和索引分析 ===')
        
        # 检查供应信息表
        print('\n--- supply_info 表结构 ---')
        columns = inspector.get_columns('supply_info')
        for col in columns:
            name = col['name']
            col_type = col['type']
            nullable = col['nullable']
            print(f'  {name}: {col_type} (nullable: {nullable})')
        
        indexes = inspector.get_indexes('supply_info')
        print('  索引:')
        for idx in indexes:
            name = idx['name'] 
            columns = idx['column_names']
            print(f'    {name}: {columns}')
        
        # 检查外键
        fks = inspector.get_foreign_keys('supply_info')
        print('  外键:')
        for fk in fks:
            name = fk.get('name', 'unnamed')
            constrained = fk['constrained_columns']
            referred_table = fk['referred_table']
            referred_cols = fk['referred_columns']
            print(f'    {name}: {constrained} -> {referred_table}.{referred_cols}')
        
        # 检查其他重要表
        for table_name in ['drugs', 'tenants', 'users']:
            print(f'\n--- {table_name} 表索引 ---')
            indexes = inspector.get_indexes(table_name)
            for idx in indexes:
                name = idx['name'] 
                columns = idx['column_names']
                print(f'  {name}: {columns}')

if __name__ == "__main__":
    analyze_database()
