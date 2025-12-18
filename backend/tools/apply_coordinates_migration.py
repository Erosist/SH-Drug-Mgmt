"""
手动应用数据库迁移 - 添加经纬度字段
适用于无法使用 flask db upgrade 的情况
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_coordinates_to_tenants():
    """直接在 SQLite 数据库中添加经纬度字段"""
    
    # 数据库路径
    db_path = 'instance/data.db'
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    print(f"连接到数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(tenants)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\n当前 tenants 表的字段: {', '.join(columns)}")
        
        if 'latitude' in columns and 'longitude' in columns:
            print("\n✓ 经纬度字段已存在，无需添加")
            return True
        
        # 添加字段
        print("\n正在添加字段...")
        
        if 'latitude' not in columns:
            print("  添加 latitude 字段...")
            cursor.execute("ALTER TABLE tenants ADD COLUMN latitude FLOAT")
            print("  ✓ latitude 字段添加成功")
        
        if 'longitude' not in columns:
            print("  添加 longitude 字段...")
            cursor.execute("ALTER TABLE tenants ADD COLUMN longitude FLOAT")
            print("  ✓ longitude 字段添加成功")
        
        conn.commit()
        
        # 验证
        cursor.execute("PRAGMA table_info(tenants)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
        print(f"\n更新后的字段: {', '.join(columns_after)}")
        
        if 'latitude' in columns_after and 'longitude' in columns_after:
            print("\n✓ 数据库迁移成功！")
            return True
        else:
            print("\n✗ 字段添加失败")
            return False
            
    except sqlite3.Error as e:
        print(f"\n✗ 数据库错误: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


def check_migration_status():
    """检查迁移状态"""
    db_path = 'instance/data.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 tenants 表结构
        cursor.execute("PRAGMA table_info(tenants)")
        columns = cursor.fetchall()
        
        print("\ntenants 表结构:")
        print("-" * 60)
        print(f"{'列名':<20} {'类型':<15} {'可空':<10}")
        print("-" * 60)
        
        has_coords = False
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            nullable = "YES" if col[3] == 0 else "NO"
            print(f"{col_name:<20} {col_type:<15} {nullable:<10}")
            
            if col_name in ['latitude', 'longitude']:
                has_coords = True
        
        print("-" * 60)
        
        if has_coords:
            print("\n✓ 经纬度字段已存在")
        else:
            print("\n✗ 缺少经纬度字段")
            print("\n请运行: python apply_coordinates_migration.py")
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='添加经纬度字段到 tenants 表')
    parser.add_argument('--check', action='store_true', help='检查迁移状态')
    
    args = parser.parse_args()
    
    print("="*60)
    print("数据库迁移工具 - 添加租户坐标字段")
    print("="*60)
    
    if args.check:
        check_migration_status()
    else:
        result = add_coordinates_to_tenants()
        
        if result:
            print("\n现在可以运行测试了:")
            print("  python scripts/test_nearby_api.py")
        else:
            print("\n迁移失败，请检查错误信息")
