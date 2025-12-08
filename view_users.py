#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看数据库中所有注册用户的脚本
"""
import sqlite3
from datetime import datetime
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent / 'instance' / 'data.db'

def view_all_users():
    """查询并显示所有用户"""
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return
    
    print(f"📂 正在读取数据库: {DB_PATH}\n")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询所有用户
        cursor.execute("""
            SELECT 
                id, username, email, phone, real_name, company_name, 
                role, tenant_id, is_authenticated, is_active, 
                last_login_at, created_at, updated_at
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ 数据库中没有用户数据")
            return
        
        print(f"📊 共找到 {len(users)} 个用户:\n")
        print("=" * 150)
        
        for user in users:
            user_id, username, email, phone, real_name, company_name, \
            role, tenant_id, is_authenticated, is_active, \
            last_login_at, created_at, updated_at = user
            
            print(f"用户ID: {user_id}")
            print(f"  用户名: {username}")
            print(f"  邮箱: {email}")
            print(f"  电话: {phone or '未设置'}")
            print(f"  真实姓名: {real_name or '未设置'}")
            print(f"  公司名称: {company_name or '未设置'}")
            print(f"  角色: {role}")
            print(f"  租户ID: {tenant_id or '未绑定'}")
            print(f"  已认证: {'✓' if is_authenticated else '✗'}")
            print(f"  账户状态: {'激活' if is_active else '禁用'}")
            print(f"  最后登录: {last_login_at or '从未登录'}")
            print(f"  创建时间: {created_at}")
            print(f"  更新时间: {updated_at}")
            print("-" * 150)
        
        # 统计信息
        print("\n📈 统计信息:")
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        role_stats = cursor.fetchall()
        for role, count in role_stats:
            print(f"  {role}: {count} 人")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_authenticated = 1")
        auth_count = cursor.fetchone()[0]
        print(f"\n  已认证用户: {auth_count} 人")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        print(f"  激活用户: {active_count} 人")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == '__main__':
    view_all_users()
