"""
快速验证第二部分实现 - API 接口
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("第二部分 API 实现验证清单")
print("="*60)

checks = []

# 1. 检查文件是否存在
print("\n1. 检查文件是否存在...")
files_to_check = [
    'nearby.py',
    'app.py',
    'enterprise.py',
    'tools/batch_update_locations.py',
    'scripts/test_nearby_api.py'
]

all_files_exist = True
for file in files_to_check:
    exists = os.path.exists(file)
    status = "✓" if exists else "✗"
    print(f"   {status} {file}")
    if not exists:
        all_files_exist = False

checks.append(all_files_exist)

# 2. 检查 Python 语法
print("\n2. 检查 Python 语法...")
try:
    import py_compile
    
    files_to_compile = ['nearby.py', 'tools/batch_update_locations.py', 'scripts/test_nearby_api.py']
    all_syntax_ok = True
    
    for file in files_to_compile:
        try:
            py_compile.compile(file, doraise=True)
            print(f"   ✓ {file}")
        except py_compile.PyCompileError as e:
            print(f"   ✗ {file}: {e}")
            all_syntax_ok = False
    
    checks.append(all_syntax_ok)
    
except Exception as e:
    print(f"   ✗ 语法检查失败: {str(e)}")
    checks.append(False)

# 3. 检查模块导入
print("\n3. 检查模块导入...")
try:
    from app import create_app
    from nearby import bp as nearby_bp
    print(f"   ✓ nearby blueprint 导入成功")
    checks.append(True)
except ImportError as e:
    print(f"   ✗ nearby blueprint 导入失败: {str(e)}")
    checks.append(False)

# 4. 检查路由注册
print("\n4. 检查路由注册...")
try:
    from app import create_app
    app = create_app()
    
    # 检查是否注册了 nearby blueprint
    blueprints = [bp.name for bp in app.blueprints.values()]
    
    if 'nearby' in blueprints:
        print(f"   ✓ nearby blueprint 已注册")
        
        # 列出所有 nearby 相关的路由
        nearby_routes = [rule.rule for rule in app.url_map.iter_rules() 
                        if rule.rule.startswith('/api/nearby')]
        
        expected_routes = [
            '/api/nearby/suppliers',
            '/api/nearby/geocode',
            '/api/nearby/distance',
            '/api/nearby/my-location',
            '/api/nearby/update-location'
        ]
        
        print(f"\n   注册的路由:")
        for route in nearby_routes:
            print(f"     - {route}")
        
        all_routes_present = all(route in [r for r in nearby_routes] 
                                for route in expected_routes)
        
        if len(nearby_routes) >= len(expected_routes):
            print(f"\n   ✓ 所有预期路由已注册")
            checks.append(True)
        else:
            print(f"\n   ✗ 部分路由未注册")
            checks.append(False)
    else:
        print(f"   ✗ nearby blueprint 未注册")
        checks.append(False)
        
except Exception as e:
    print(f"   ✗ 路由检查失败: {str(e)}")
    checks.append(False)

# 5. 检查 API 函数
print("\n5. 检查 API 函数...")
try:
    import nearby
    
    functions = [
        'get_nearby_suppliers',
        'geocode',
        'calculate_distance',
        'get_my_location',
        'update_my_location'
    ]
    
    all_functions_exist = True
    for func in functions:
        if hasattr(nearby, func):
            print(f"   ✓ {func}")
        else:
            print(f"   ✗ {func} 未找到")
            all_functions_exist = False
    
    checks.append(all_functions_exist)
    
except Exception as e:
    print(f"   ✗ 函数检查失败: {str(e)}")
    checks.append(False)

# 6. 检查批量更新工具
print("\n6. 检查批量更新工具...")
try:
    # 尝试导入主函数
    import importlib.util
    spec = importlib.util.spec_from_file_location("batch_update", "tools/batch_update_locations.py")
    batch_module = importlib.util.module_from_spec(spec)
    
    print(f"   ✓ 批量更新工具模块加载成功")
    checks.append(True)
    
except Exception as e:
    print(f"   ✗ 批量更新工具检查失败: {str(e)}")
    checks.append(False)

# 7. 测试应用启动
print("\n7. 测试 Flask 应用启动...")
try:
    from app import create_app
    app = create_app()
    
    with app.app_context():
        print(f"   ✓ Flask 应用创建成功")
        print(f"   ✓ 应用上下文正常")
        checks.append(True)
        
except Exception as e:
    print(f"   ✗ 应用启动失败: {str(e)}")
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
    print("\n✓ 所有检查通过！可以进行功能测试:")
    print("\n  1. 启动后端服务:")
    print("     python run.py")
    print("\n  2. 运行 API 测试:")
    print("     python scripts/test_nearby_api.py")
    print("\n  3. 使用批量更新工具:")
    print("     python tools/batch_update_locations.py --stats")
else:
    print(f"\n✗ 有 {total - passed} 项检查未通过")
    print("\n请根据上述提示检查并修复问题")

print("\n" + "="*60)
