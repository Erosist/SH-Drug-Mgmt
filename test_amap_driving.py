"""
高德地图驾车路径功能测试脚本
用于验证API配置和签名是否正确
"""
import sys
import os

# 推荐使用包路径导入（在项目根目录运行本脚本）
# Ensure project root and backend folder are on sys.path so imports in backend/ (which use
# top-level imports like `from config import ...`) can be resolved when running this script
# from the project root.
ROOT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.app import create_app
from backend.amap import AmapService

def test_amap_configuration():
    """测试高德地图API配置"""
    print("=" * 60)
    print("高德地图驾车路径功能配置测试")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # 1. 检查配置
        print("\n1. 检查API配置...")
        rest_key = AmapService.get_api_key()
        secret = AmapService.get_api_secret()
        
        if not rest_key:
            print("  ❌ AMAP_REST_KEY 未配置")
            print("     请在 backend/.env 中设置 AMAP_REST_KEY")
            return False
        else:
            print(f"  ✓ AMAP_REST_KEY: {rest_key[:20]}...")
        
        if not secret:
            print("  ⚠️  AMAP_API_SECRET 未配置（将不使用签名）")
            print("     如需使用签名，请在 backend/.env 中设置 AMAP_API_SECRET")
        else:
            print(f"  ✓ AMAP_API_SECRET: {secret[:10]}...（已配置）")
        
        # 2. 测试地理编码
        print("\n2. 测试地理编码功能...")
        test_address = "上海市浦东新区张江高科技园区"
        result = AmapService.geocode_address(test_address)
        
        if result:
            print(f"  ✓ 地理编码成功")
            print(f"     地址: {result['formatted_address']}")
            print(f"     坐标: {result['longitude']}, {result['latitude']}")
        else:
            print(f"  ❌ 地理编码失败")
            print(f"     可能原因: AMAP_REST_KEY 无效或网络问题")
            return False
        
        # 3. 测试驾车路径规划
        print("\n3. 测试驾车路径规划功能...")
        origin = (121.48, 31.23)  # 上海市中心
        destination = (121.50, 31.22)  # 附近位置
        
        route = AmapService.get_driving_route(origin, destination)
        
        if route:
            print(f"  ✓ 驾车路径规划成功")
            print(f"     距离: {AmapService.format_distance(route['distance'])}")
            print(f"     预计耗时: {route['duration'] // 60}分钟")
            print(f"     路径点数: {len(route['path'])} 个")
            if len(route['path']) > 0:
                print(f"     起点: {route['path'][0]}")
                print(f"     终点: {route['path'][-1]}")
        else:
            print(f"  ❌ 驾车路径规划失败")
            print(f"     可能原因:")
            print(f"       1. AMAP_REST_KEY 未启用驾车路径规划服务")
            print(f"       2. 需要配置 AMAP_API_SECRET 进行签名验证")
            print(f"       3. API配额已用尽")
            print(f"       4. IP白名单或域名限制")
            return False
        
        # 4. 测试签名功能
        if secret:
            print("\n4. 测试签名功能...")
            test_params = {
                'key': rest_key,
                'origin': '121.48,31.23',
                'destination': '121.50,31.22',
                'output': 'json'
            }
            sig = AmapService.generate_signature(test_params, secret)
            print(f"  ✓ 签名生成成功: {sig[:20]}...")
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！驾车路径功能已正确配置")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 重启后端服务: cd backend && python run.py")
        print("  2. 在浏览器访问智能调度页面: http://localhost:5173/service")
        print("  3. 选择'驾车距离（精确）'并测试路径规划")
        return True

if __name__ == '__main__':
    try:
        success = test_amap_configuration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
