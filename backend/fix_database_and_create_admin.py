#!/usr/bin/env python3
"""
数据库诊断和管理员账号创建脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app import create_app
from extensions import db
from models import User, Tenant


def diagnose_database():
    """诊断数据库状态"""
    print("=== 数据库诊断开始 ===")
    
    try:
        # 检查数据库连接
        print("1. 检查数据库连接...")
        db.session.execute(db.text("SELECT 1"))
        print("✅ 数据库连接正常")
        
        # 检查用户表
        print("\n2. 检查用户表...")
        user_count = User.query.count()
        print(f"用户表总数: {user_count}")
        
        if user_count > 0:
            print("现有用户列表:")
            users = User.query.all()
            for user in users:
                print(f"  - ID: {user.id}, 用户名: {user.username}, 角色: {user.role}, "
                      f"邮箱: {user.email}, 是否认证: {user.is_authenticated}, "
                      f"是否激活: {user.is_active}")
        else:
            print("⚠️ 用户表为空")
        
        # 检查企业表
        print("\n3. 检查企业表...")
        tenant_count = Tenant.query.count()
        print(f"企业表总数: {tenant_count}")
        
        if tenant_count > 0:
            print("现有企业列表:")
            tenants = Tenant.query.all()
            for tenant in tenants:
                print(f"  - ID: {tenant.id}, 名称: {tenant.name}, 类型: {tenant.type}")
        else:
            print("⚠️ 企业表为空")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库诊断失败: {str(e)}")
        return False


def create_admin_account():
    """创建管理员账号"""
    print("\n=== 创建管理员账号 ===")
    
    try:
        # 检查是否已存在admin用户
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print(f"⚠️ 用户名'admin'已存在 (ID: {existing_admin.id})")
            
            # 询问是否要重置密码
            response = input("是否要重置现有admin账号的密码? (y/n): ").strip().lower()
            if response == 'y':
                existing_admin.set_password('admin123')
                existing_admin.role = 'admin'
                existing_admin.is_authenticated = True
                existing_admin.is_active = True
                existing_admin.updated_at = datetime.utcnow()
                
                db.session.commit()
                print("✅ admin账号密码已重置为'admin123'")
                return True
            else:
                print("❌ 取消操作")
                return False
        
        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(email='admin@system.com').first()
        if existing_email:
            print(f"⚠️ 邮箱'admin@system.com'已被用户 {existing_email.username} 使用")
            # 使用不同的邮箱
            admin_email = 'admin@local.system'
        else:
            admin_email = 'admin@system.com'
        
        # 创建新的管理员账号
        admin_user = User(
            username='admin',
            email=admin_email,
            real_name='系统管理员',
            role='admin',
            is_authenticated=True,
            is_active=True
        )
        admin_user.set_password('admin123')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✅ 管理员账号创建成功!")
        print(f"   用户名: admin")
        print(f"   密码: admin123")
        print(f"   邮箱: {admin_email}")
        print(f"   角色: admin")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 创建管理员账号失败: {str(e)}")
        return False


def check_password_hashing():
    """检查密码加密功能"""
    print("\n=== 检查密码加密功能 ===")
    
    try:
        # 测试密码加密和验证
        test_user = User(username='test_temp', email='test@temp.com')
        test_password = 'testpass123'
        test_user.set_password(test_password)
        
        # 验证密码
        if test_user.check_password(test_password):
            print("✅ 密码加密和验证功能正常")
            return True
        else:
            print("❌ 密码验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 密码加密功能测试失败: {str(e)}")
        return False


def fix_existing_users():
    """修复现有用户的问题"""
    print("\n=== 修复现有用户问题 ===")
    
    try:
        users = User.query.all()
        fixed_count = 0
        
        for user in users:
            changed = False
            
            # 确保用户是激活状态
            if not user.is_active:
                user.is_active = True
                changed = True
                print(f"修复用户 {user.username}: 设置为激活状态")
            
            # 确保认证用户是已认证状态
            if user.role in ['admin', 'pharmacy', 'supplier', 'logistics'] and not user.is_authenticated:
                user.is_authenticated = True
                changed = True
                print(f"修复用户 {user.username}: 设置为已认证状态")
            
            # 检查密码哈希是否存在
            if not user.password_hash:
                print(f"⚠️ 用户 {user.username} 没有密码哈希，需要重置密码")
                user.set_password('password123')  # 设置默认密码
                changed = True
                print(f"修复用户 {user.username}: 设置默认密码 'password123'")
            
            if changed:
                user.updated_at = datetime.utcnow()
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"✅ 修复了 {fixed_count} 个用户的问题")
        else:
            print("✅ 没有发现需要修复的用户问题")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 修复用户问题失败: {str(e)}")
        return False


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("数据库诊断和修复工具")
        print("=" * 50)
        
        # 1. 诊断数据库
        if not diagnose_database():
            print("❌ 数据库诊断失败，程序退出")
            return
        
        # 2. 检查密码加密功能
        check_password_hashing()
        
        # 3. 修复现有用户问题
        fix_existing_users()
        
        # 4. 创建管理员账号
        create_admin_account()
        
        print("\n=== 最终用户列表 ===")
        users = User.query.all()
        for user in users:
            print(f"用户名: {user.username}, 角色: {user.role}, "
                  f"是否认证: {user.is_authenticated}, 是否激活: {user.is_active}")
        
        print("\n🎉 数据库诊断和修复完成!")


if __name__ == '__main__':
    main()
