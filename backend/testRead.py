#!/usr/bin/env python3
"""
检查 data.db 数据库的表结构和数据
"""

import sys
import os
import sqlite3
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import *


def get_table_info(cursor, table_name):
    """获取表的结构信息"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return columns


def get_table_data(cursor, table_name, limit=10):
    """获取表的数据"""
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    data = cursor.fetchall()
    return data


def inspect_database():
    """检查数据库表结构和数据"""
    app = create_app()
    
    with app.app_context():
        # 获取数据库文件路径
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_path.startswith('sqlite:///'):
            db_file = db_path.replace('sqlite:///', '')
            if not os.path.isabs(db_file):
                db_file = os.path.join(app.instance_path, db_file)
        else:
            print("错误：不是 SQLite 数据库")
            return
        
        if not os.path.exists(db_file):
            print(f"错误：数据库文件不存在 - {db_file}")
            return
        
        print(f"=== 数据库检查报告 ===")
        print(f"数据库文件: {db_file}")
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 连接到 SQLite 数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        try:
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"\n数据库中共有 {len(tables)} 个表:")
            for table in tables:
                print(f"  - {table[0]}")
            
            print("\n" + "=" * 60)
            
            # 检查每个表的结构和数据
            for table_tuple in tables:
                table_name = table_tuple[0]
                print(f"\n【表名: {table_name}】")
                
                # 获取表结构
                print("\n表结构:")
                columns = get_table_info(cursor, table_name)
                print("  序号 | 列名              | 类型              | 非空 | 默认值 | 主键")
                print("  " + "-" * 70)
                for col in columns:
                    cid, name, type_, notnull, default, pk = col
                    print(f"  {cid:4} | {name:16} | {type_:16} | {notnull:4} | {str(default):6} | {pk:4}")
                
                # 获取数据数量
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"\n数据总数: {count} 条")
                
                if count > 0:
                    # 获取所有数据
                    print(f"\n所有 {count} 条数据:")
                    cursor.execute(f"SELECT * FROM {table_name}")
                    data = cursor.fetchall()
                    
                    if data:
                        # 打印列标题
                        col_names = [col[1] for col in columns]
                        
                        # 计算每列的最大宽度
                        widths = [len(name) for name in col_names]
                        for row in data:
                            for i, val in enumerate(row):
                                if i < len(widths):
                                    widths[i] = max(widths[i], len(str(val)))
                        
                        # 打印表头
                        header = " | ".join([f"{name:{width}}" for name, width in zip(col_names, widths)])
                        print("  " + header)
                        print("  " + "-" * len(header))
                        
                        # 打印数据行
                        for row in data:
                            row_str = " | ".join([f"{str(val):{width}}" for val, width in zip(row, widths)])
                            print("  " + row_str)
                else:
                    print("  (无数据)")
                
                print("\n" + "-" * 60)
        
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
        
        finally:
            conn.close()


def inspect_specific_table(table_name, limit=20):
    """检查指定表的详细信息"""
    app = create_app()
    
    with app.app_context():
        # 获取数据库文件路径
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_path.startswith('sqlite:///'):
            db_file = db_path.replace('sqlite:///', '')
            if not os.path.isabs(db_file):
                db_file = os.path.join(app.instance_path, db_file)
        else:
            print("错误：不是 SQLite 数据库")
            return
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        try:
            print(f"=== 表 {table_name} 详细信息 ===")
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                print(f"错误：表 '{table_name}' 不存在")
                return
            
            # 表结构
            print("\n表结构:")
            columns = get_table_info(cursor, table_name)
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                constraints = []
                if pk:
                    constraints.append("PRIMARY KEY")
                if notnull:
                    constraints.append("NOT NULL")
                if default is not None:
                    constraints.append(f"DEFAULT {default}")
                
                constraint_str = " ".join(constraints) if constraints else ""
                print(f"  {name}: {type_} {constraint_str}")
            
            # 数据统计
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            print(f"\n总记录数: {total_count}")
            
            # 显示数据
            if total_count > 0:
                print(f"\n显示前 {min(limit, total_count)} 条记录:")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
                data = cursor.fetchall()
                
                col_names = [col[1] for col in columns]
                
                # 计算每列的最大宽度
                widths = [len(name) for name in col_names]
                for row in data:
                    for i, val in enumerate(row):
                        widths[i] = max(widths[i], len(str(val)))
                
                # 打印表头
                header = " | ".join([f"{name:{width}}" for name, width in zip(col_names, widths)])
                print(f"  {header}")
                print(f"  {'-' * len(header)}")
                
                # 打印数据
                for row in data:
                    row_str = " | ".join([f"{str(val):{width}}" for val, width in zip(row, widths)])
                    print(f"  {row_str}")
        
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
        
        finally:
            conn.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='检查数据库表结构和数据')
    parser.add_argument('-t', '--table', help='指定要检查的表名')
    parser.add_argument('-l', '--limit', type=int, default=20, help='限制显示的记录数量')
    parser.add_argument('-a', '--all', action='store_true', help='显示所有表的概览')
    
    args = parser.parse_args()
    
    if args.table:
        inspect_specific_table(args.table, args.limit)
    else:
        inspect_database()


if __name__ == '__main__':
    main()