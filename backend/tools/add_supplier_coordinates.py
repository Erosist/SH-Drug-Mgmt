"""
为数据库中的供应商自动添加地理坐标
使用高德地图API进行地理编码
"""
import sys
import time
from app import create_app
from models import db, Tenant
from amap import AmapService

def add_coordinates_to_suppliers():
    """为供应商添加坐标信息"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("为供应商添加地理坐标")
        print("=" * 60)
        
        # 查找所有没有坐标的活跃供应商
        suppliers_without_coords = Tenant.query.filter(
            Tenant.type == 'SUPPLIER',
            Tenant.is_active == True,
            db.or_(
                Tenant.longitude == None,
                Tenant.latitude == None
            )
        ).all()
        
        print(f"\n找到 {len(suppliers_without_coords)} 个没有坐标的供应商")
        
        if not suppliers_without_coords:
            print("所有供应商都已有坐标信息！")
            return
        
        success_count = 0
        fail_count = 0
        
        for i, supplier in enumerate(suppliers_without_coords, 1):
            print(f"\n[{i}/{len(suppliers_without_coords)}] 处理: {supplier.name}")
            print(f"地址: {supplier.address}")
            
            try:
                # 使用高德地图API进行地理编码
                result = AmapService.geocode_address(supplier.address)
                
                if result:
                    supplier.longitude = result['longitude']
                    supplier.latitude = result['latitude']
                    db.session.commit()
                    
                    print(f"✓ 成功添加坐标: ({supplier.longitude}, {supplier.latitude})")
                    success_count += 1
                else:
                    print(f"✗ 无法解析地址")
                    fail_count += 1
                
                # 避免API请求过快，稍作延迟
                time.sleep(0.2)
                
            except Exception as e:
                print(f"✗ 错误: {str(e)}")
                fail_count += 1
                db.session.rollback()
        
        print("\n" + "=" * 60)
        print(f"处理完成:")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        print("=" * 60)


if __name__ == '__main__':
    print("\n⚠️  此脚本将使用高德地图API为供应商添加坐标")
    print("确保 config.py 中已配置有效的高德地图API Key")
    
    response = input("\n是否继续? (y/n): ")
    if response.lower() == 'y':
        add_coordinates_to_suppliers()
    else:
        print("已取消")
