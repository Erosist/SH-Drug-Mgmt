"""
测试地址搜索API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from amap import search_address_suggestions

def test_address_search():
    """测试地址搜索功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("测试高德地图地址搜索API")
        print("=" * 60)
        
        # 测试关键词列表
        keywords = ['人民广场', '陆家嘴', '外滩', '同济大学', '虹桥机场']
        
        for keyword in keywords:
            print(f"\n🔍 搜索: {keyword}")
            print("-" * 60)
            
            try:
                suggestions = search_address_suggestions(keyword, '上海')
                
                if suggestions:
                    print(f"✅ 找到 {len(suggestions)} 个结果:")
                    for i, s in enumerate(suggestions[:5], 1):  # 只显示前5个
                        print(f"\n  {i}. {s['name']}")
                        print(f"     地址: {s['district']} {s['address']}")
                        print(f"     坐标: [{s['location']['longitude']}, {s['location']['latitude']}]")
                else:
                    print("❌ 未找到结果")
                    
            except Exception as e:
                print(f"❌ 搜索失败: {str(e)}")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

if __name__ == '__main__':
    test_address_search()
