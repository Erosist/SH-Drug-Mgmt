"""
快速验证脚本 - 检查第一部分实现是否正确
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("第一部分实现验证清单")
print("="*60)

checks = []

# 1. 检查文件是否存在
print("\n1. 检查文件是否存在...")
files_to_check = [
    'config.py',
    'amap.py',
    'models.py',
    'test_amap.py'
]

for file in files_to_check:
    exists = os.path.exists(file)
    status = "✓" if exists else "✗"
    print(f"   {status} {file}")
    checks.append(exists)

# 2. 检查 Python 语法
print("\n2. 检查 Python 语法...")
try:
    import py_compile
    py_compile.compile('amap.py', doraise=True)
    print(f"   ✓ amap.py 语法正确")
    checks.append(True)
except py_compile.PyCompileError as e:
    print(f"   ✗ amap.py 语法错误: {e}")
    checks.append(False)

# 3. 检查配置
print("\n3. 检查配置...")
try:
    from app import create_app
    app = create_app()
    
    has_web_key = app.config.get('AMAP_WEB_KEY') is not None
    has_rest_key = app.config.get('AMAP_REST_KEY') is not None
    
    if has_web_key and has_rest_key:
        print(f"   ✓ AMAP API Keys 已配置")
        print(f"     AMAP_WEB_KEY: {app.config['AMAP_WEB_KEY'][:20]}...")
        print(f"     AMAP_REST_KEY: {app.config['AMAP_REST_KEY'][:20]}...")
        checks.append(True)
    else:
        print(f"   ✗ AMAP API Keys 未配置")
        checks.append(False)
except Exception as e:
    print(f"   ✗ 配置检查失败: {str(e)}")
    checks.append(False)

# 4. 检查模块导入
print("\n4. 检查模块导入...")
try:
    from amap import AmapService, find_nearby_suppliers
    print(f"   ✓ amap 模块导入成功")
    print(f"     - AmapService 类")
    print(f"     - find_nearby_suppliers 函数")
    checks.append(True)
except ImportError as e:
    print(f"   ✗ amap 模块导入失败: {str(e)}")
    checks.append(False)

# 5. 检查核心方法
print("\n5. 检查核心方法...")
try:
    from amap import AmapService
    methods = [
        'geocode_address',
        'calculate_distance_haversine',
        'calculate_distance_api',
        'format_distance'
    ]
    
    all_methods_exist = True
    for method in methods:
        if hasattr(AmapService, method):
            print(f"   ✓ {method}")
        else:
            print(f"   ✗ {method} 未找到")
            all_methods_exist = False
    
    checks.append(all_methods_exist)
except Exception as e:
    print(f"   ✗ 方法检查失败: {str(e)}")
    checks.append(False)

# 6. 检查数据库模型
print("\n6. 检查数据库模型...")
try:
    from app import create_app
    from models import Tenant
    
    app = create_app()
    with app.app_context():
        has_latitude = hasattr(Tenant, 'latitude')
        has_longitude = hasattr(Tenant, 'longitude')
        
        if has_latitude and has_longitude:
            print(f"   ✓ Tenant 模型包含经纬度字段")
            print(f"     - latitude: {Tenant.latitude.type}")
            print(f"     - longitude: {Tenant.longitude.type}")
            checks.append(True)
        else:
            print(f"   ✗ Tenant 模型缺少经纬度字段")
            checks.append(False)
except Exception as e:
    print(f"   ✗ 模型检查失败: {str(e)}")
    checks.append(False)

# 7. 测试基本功能
print("\n7. 测试基本功能...")
try:
    from amap import AmapService
    
    # 测试距离格式化
    formatted = AmapService.format_distance(1500)
    if formatted == "1.5km":
        print(f"   ✓ 距离格式化正常: {formatted}")
        checks.append(True)
    else:
        print(f"   ✗ 距离格式化异常: {formatted}")
        checks.append(False)
    
    # 测试 Haversine 计算
    distance = AmapService.calculate_distance_haversine(
        116.397128, 39.916527,  # 天安门
        116.427281, 39.903738   # 北京站
    )
    
    if 2500 < distance < 3500:  # 实际约 2.8km
        print(f"   ✓ Haversine 距离计算正常: {distance}米")
        checks.append(True)
    else:
        print(f"   ✗ Haversine 距离计算异常: {distance}米")
        checks.append(False)
        
except Exception as e:
    print(f"   ✗ 功能测试失败: {str(e)}")
    checks.append(False)
    checks.append(False)

# 8. 检查依赖
print("\n8. 检查依赖...")
try:
    import requests
    print(f"   ✓ requests 已安装")
    checks.append(True)
except ImportError:
    print(f"   ✗ requests 未安装，请运行: pip install requests")
    checks.append(False)

# 总结
print("\n" + "="*60)
print("验证结果")
print("="*60)

passed = sum(checks)
total = len(checks)
percentage = (passed / total * 100) if total > 0 else 0

print(f"\n通过: {passed}/{total} ({percentage:.1f}%)")

if passed == total:
    print("\n✓ 所有检查通过！可以运行完整测试:")
    print("  python test_amap.py")
else:
    print(f"\n✗ 有 {total - passed} 项检查未通过，请根据上述提示修复")
    print("\n常见问题解决:")
    print("  1. 模块导入失败 -> 检查文件是否在正确位置")
    print("  2. 依赖缺失 -> pip install requests")
    print("  3. 配置缺失 -> 检查 config.py 中的 AMAP Keys")

print("\n" + "="*60)
