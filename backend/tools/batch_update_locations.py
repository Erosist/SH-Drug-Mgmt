"""
批量为现有租户添加地理坐标
使用场景：为已有的供应商、药店等租户批量添加经纬度信息
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Tenant
from amap import AmapService
from extensions import db


def update_tenant_locations(tenant_type=None, force_update=False, delay=0.5):
    """
    批量更新租户位置坐标
    
    Args:
        tenant_type: 租户类型过滤（PHARMACY, SUPPLIER, LOGISTICS），None 表示全部
        force_update: 是否强制更新已有坐标的租户
        delay: 每次 API 调用之间的延迟（秒），避免超出配额
    """
    app = create_app()
    
    with app.app_context():
        # 查询租户
        query = Tenant.query.filter_by(is_active=True)
        if tenant_type:
            query = query.filter_by(type=tenant_type)
        
        tenants = query.all()
        
        print(f"\n找到 {len(tenants)} 个活跃租户")
        
        if not force_update:
            # 过滤掉已有坐标的租户
            tenants = [t for t in tenants if not (t.longitude and t.latitude)]
            print(f"其中 {len(tenants)} 个租户缺少坐标信息\n")
        else:
            print("将强制更新所有租户的坐标\n")
        
        if not tenants:
            print("没有需要更新的租户")
            return
        
        # 确认操作
        print("即将更新以下租户的坐标:")
        for i, tenant in enumerate(tenants[:5], 1):
            print(f"  {i}. [{tenant.type}] {tenant.name} - {tenant.address}")
        
        if len(tenants) > 5:
            print(f"  ... 还有 {len(tenants) - 5} 个租户")
        
        confirm = input(f"\n确认更新 {len(tenants)} 个租户的坐标? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("操作已取消")
            return
        
        # 开始更新
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        print("\n开始更新...\n")
        print("="*80)
        
        for i, tenant in enumerate(tenants, 1):
            print(f"\n[{i}/{len(tenants)}] 处理: {tenant.name}")
            print(f"  类型: {tenant.type}")
            print(f"  地址: {tenant.address}")
            
            # 检查是否有地址
            if not tenant.address or tenant.address.strip() == '':
                print(f"  ✗ 跳过：缺少地址信息")
                skipped_count += 1
                continue
            
            try:
                # 调用地理编码 API
                print(f"  正在获取坐标...")
                result = AmapService.geocode_address(tenant.address)
                
                if result:
                    tenant.longitude = result['longitude']
                    tenant.latitude = result['latitude']
                    
                    print(f"  ✓ 成功获取坐标:")
                    print(f"    经度: {result['longitude']}")
                    print(f"    纬度: {result['latitude']}")
                    print(f"    详细地址: {result.get('formatted_address', 'N/A')}")
                    
                    success_count += 1
                else:
                    print(f"  ✗ 失败：无法解析地址")
                    failed_count += 1
                
                # 延迟，避免API频率限制
                if delay > 0 and i < len(tenants):
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  ✗ 错误: {str(e)}")
                failed_count += 1
        
        # 提交更改
        print("\n" + "="*80)
        print("\n保存更改到数据库...")
        
        try:
            db.session.commit()
            print("✓ 数据库更新成功\n")
        except Exception as e:
            db.session.rollback()
            print(f"✗ 数据库更新失败: {str(e)}\n")
            return
        
        # 统计结果
        print("="*80)
        print("更新完成!")
        print("="*80)
        print(f"成功: {success_count}")
        print(f"失败: {failed_count}")
        print(f"跳过: {skipped_count}")
        print(f"总计: {len(tenants)}")
        print("="*80)


def show_tenant_stats():
    """显示租户坐标统计信息"""
    app = create_app()
    
    with app.app_context():
        types = ['PHARMACY', 'SUPPLIER', 'LOGISTICS', 'REGULATOR']
        
        print("\n租户坐标统计:")
        print("="*80)
        print(f"{'类型':<15} {'总数':<10} {'有坐标':<10} {'缺少坐标':<10} {'完成率':<10}")
        print("-"*80)
        
        total_all = 0
        has_location_all = 0
        
        for tenant_type in types:
            total = Tenant.query.filter_by(type=tenant_type, is_active=True).count()
            has_location = Tenant.query.filter_by(type=tenant_type, is_active=True).filter(
                Tenant.longitude.isnot(None),
                Tenant.latitude.isnot(None)
            ).count()
            missing = total - has_location
            percentage = (has_location / total * 100) if total > 0 else 0
            
            print(f"{tenant_type:<15} {total:<10} {has_location:<10} {missing:<10} {percentage:.1f}%")
            
            total_all += total
            has_location_all += has_location
        
        print("-"*80)
        missing_all = total_all - has_location_all
        percentage_all = (has_location_all / total_all * 100) if total_all > 0 else 0
        print(f"{'总计':<15} {total_all:<10} {has_location_all:<10} {missing_all:<10} {percentage_all:.1f}%")
        print("="*80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量更新租户地理坐标')
    parser.add_argument('--stats', action='store_true', help='显示坐标统计信息')
    parser.add_argument('--type', choices=['PHARMACY', 'SUPPLIER', 'LOGISTICS', 'REGULATOR'],
                       help='指定要更新的租户类型')
    parser.add_argument('--force', action='store_true', help='强制更新已有坐标的租户')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='每次API调用之间的延迟（秒），默认0.5秒')
    
    args = parser.parse_args()
    
    if args.stats:
        show_tenant_stats()
    else:
        update_tenant_locations(
            tenant_type=args.type,
            force_update=args.force,
            delay=args.delay
        )


if __name__ == '__main__':
    main()
