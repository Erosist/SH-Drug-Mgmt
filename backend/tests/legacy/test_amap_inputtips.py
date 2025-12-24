"""
快速测试高德地图API配置
"""
import requests

# 使用后端配置的REST API Key
AMAP_REST_KEY = '143117d600102600e70696533eb39a5b'

def test_inputtips_api():
    """测试输入提示API"""
    print("=" * 60)
    print("测试高德地图输入提示API")
    print("=" * 60)
    
    url = 'https://restapi.amap.com/v3/assistant/inputtips'
    
    test_keywords = ['人民广场', '陆家嘴', '外滩']
    
    for keyword in test_keywords:
        print(f"\n🔍 搜索: {keyword}")
        print("-" * 60)
        
        params = {
            'key': AMAP_REST_KEY,
            'keywords': keyword,
            'city': '上海',
            'citylimit': 'true',
            'output': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"状态码: {response.status_code}")
            print(f"API状态: {data.get('status')}")
            print(f"API消息: {data.get('info')}")
            
            if data.get('status') == '1' and data.get('tips'):
                tips = data['tips']
                print(f"✅ 找到 {len(tips)} 个结果")
                
                for i, tip in enumerate(tips[:3], 1):
                    print(f"\n  {i}. {tip.get('name')}")
                    print(f"     地址: {tip.get('district', '')} {tip.get('address', '')}")
                    if tip.get('location'):
                        print(f"     坐标: {tip['location']}")
            else:
                print(f"❌ 搜索失败")
                print(f"完整响应: {data}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_inputtips_api()
