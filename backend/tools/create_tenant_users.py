#!/usr/bin/env python3
"""
为每个 tenant 创建对应的管理员用户
逻辑: 1个tenant对应1个默认管理员用户 (可以后续添加更多用户)
"""

import sys
from pathlib import Path

# 确保可以导入项目模块
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models import Tenant, User

def create_users_for_tenants():
    """为每个 tenant 创建管理员用户"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("为 Tenants 创建管理员用户")
        print("=" * 80)
        
        # 获取所有 tenants
        tenants = Tenant.query.order_by(Tenant.id).all()
        print(f"\n数据库中共有 {len(tenants)} 个 tenants")
        
        # 获取已有用户的 tenant_id
        existing_users = User.query.filter(User.tenant_id.isnot(None)).all()
        existing_tenant_ids = {user.tenant_id for user in existing_users}
        print(f"已有用户关联的 tenant: {len(existing_tenant_ids)} 个")
        
        created_count = 0
        skipped_count = 0
        
        print("\n开始创建用户...")
        print("-" * 80)
        
        for tenant in tenants:
            # 检查是否已有用户
            if tenant.id in existing_tenant_ids:
                skipped_count += 1
                print(f"  跳过: Tenant #{tenant.id:3d} ({tenant.type:10s}) {tenant.name} - 已有用户")
                continue
            
            # 根据 tenant 类型确定角色
            role_mapping = {
                'PHARMACY': 'pharmacy',
                'SUPPLIER': 'supplier',
                'LOGISTICS': 'logistics',
                'REGULATOR': 'regulator'
            }
            role = role_mapping.get(tenant.type, 'pharmacy')
            
            # 生成用户名和邮箱
            # 用户名: tenant类型_tenantID (例如: pharmacy_15)
            username = f"{tenant.type.lower()}_{tenant.id}"
            
            # 邮箱: 使用 tenant 的联系邮箱或生成一个
            email = tenant.contact_email if tenant.contact_email else f"{username}@example.com"
            
            # 检查邮箱是否已存在
            if User.query.filter_by(email=email).first():
                # 如果邮箱已存在,使用带ID的邮箱
                email = f"{username}@sh-drug-mgmt.com"
            
            # 检查用户名是否已存在
            if User.query.filter_by(username=username).first():
                print(f"  ⚠️  用户名 {username} 已存在,跳过")
                skipped_count += 1
                continue
            
            # 检查电话号码是否重复
            phone = None
            if tenant.contact_phone:
                existing_phone = User.query.filter_by(phone=tenant.contact_phone).first()
                if not existing_phone:
                    phone = tenant.contact_phone
                # 如果电话号码重复,就不设置电话号码
            
            # 创建用户
            user = User(
                username=username,
                email=email,
                phone=phone,
                real_name=tenant.contact_person,
                company_name=tenant.name,
                role=role,
                tenant_id=tenant.id,
                is_authenticated=True,  # 默认已认证
                is_active=tenant.is_active
            )
            
            # 设置默认密码: Password123!
            user.set_password('Password123!')
            
            db.session.add(user)
            created_count += 1
            
            print(f"  ✅ 创建: {username:20s} | {role:10s} | {tenant.name[:30]}")
            
            # 每50个提交一次
            if created_count % 50 == 0:
                db.session.commit()
                print(f"\n  已提交 {created_count} 个用户...\n")
        
        # 提交剩余的
        db.session.commit()
        
        print("\n" + "=" * 80)
        print("创建完成:")
        print(f"  新增用户: {created_count} 个")
        print(f"  跳过: {skipped_count} 个 (已有用户)")
        print(f"  总 tenants: {len(tenants)} 个")
        print("=" * 80)
        
        print("\n📝 用户登录信息:")
        print("  用户名格式: {tenant类型}_{tenant_id}")
        print("  例如: pharmacy_15, supplier_65")
        print("  默认密码: Password123!")
        print("=" * 80)
        
        # 显示一些示例
        print("\n示例用户 (前10个新创建的):")
        new_users = User.query.filter(User.tenant_id.isnot(None)).order_by(User.id.desc()).limit(10).all()
        for user in reversed(new_users[:min(10, created_count)]):
            print(f"  用户名: {user.username:20s} | 角色: {user.role:10s} | 企业: {user.company_name}")
        
        return True

if __name__ == '__main__':
    try:
        success = create_users_for_tenants()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
