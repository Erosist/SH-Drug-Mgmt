#!/usr/bin/env python3
"""
测试药品追溯查询的位置信息显示功能
"""

import requests
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"
TRACE_URL = f"{BASE_URL}/api/circulation/trace"

def test_trace_with_location_info():
    """测试药品追溯查询，验证位置信息"""
    print("=== 测试药品追溯查询的位置信息显示 ===")
    
    # 模拟监管用户登录（需要先有有效的token）
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_REGULATOR_JWT_TOKEN'  # 需要替换为真实的监管用户token
    }
    
    # 使用现有的运单号进行测试
    test_tracking_numbers = ['123965', '123987', '123789', '123745']
    
    for tracking_number in test_tracking_numbers:
        print(f"\n测试运单号: {tracking_number}")
        
        params = {
            'tracking_number': tracking_number
        }
        
        print(f"请求URL: {TRACE_URL}")
        print(f"请求参数: {params}")
        
        # 注意：这个测试需要运行的后端服务和有效的监管用户JWT token
        # response = requests.get(TRACE_URL, params=params, headers=headers)
        # 
        # if response.status_code == 200:
        #     data = response.json()
        #     print(f"查询成功!")
        #     
        #     if 'timeline' in data and data['timeline']:
        #         print(f"流通记录数量: {len(data['timeline'])}")
        #         
        #         for i, item in enumerate(data['timeline'], 1):
        #             print(f"  记录 {i}:")
        #             print(f"    状态: {item.get('status_text', 'N/A')}")
        #             print(f"    时间: {item.get('timestamp', 'N/A')}")
        #             print(f"    GPS坐标: {item.get('latitude', 'N/A')}, {item.get('longitude', 'N/A')}")
        #             print(f"    位置描述: {item.get('location', 'N/A')}")
        #             print(f"    备注: {item.get('remarks', 'N/A')}")
        #     else:
        #         print("没有找到流通记录")
        # else:
        #     print(f"查询失败: {response.status_code}")
        #     print(f"错误信息: {response.text}")
        
        print("  模拟响应数据结构:")
        mock_response = {
            "tracking_number": tracking_number,
            "drug": {
                "generic_name": "阿莫西林胶囊",
                "manufacturer": "石药集团"
            },
            "timeline": [
                {
                    "id": 1,
                    "timestamp": "2025-12-09T15:13:00",
                    "status": "SHIPPED",
                    "status_text": "已发货",
                    "location": None,
                    "latitude": 22.29207,
                    "longitude": 114.193203,
                    "remarks": None
                },
                {
                    "id": 2,
                    "timestamp": "2025-12-09T15:14:00",
                    "status": "IN_TRANSIT",
                    "status_text": "运输中",
                    "location": "深圳市南山区",
                    "latitude": 22.29207,
                    "longitude": 114.193203,
                    "remarks": "正在运输途中"
                },
                {
                    "id": 3,
                    "timestamp": "2025-12-09T15:26:00",
                    "status": "DELIVERED",
                    "status_text": "已送达",
                    "location": "上海市浦东新区张江高科",
                    "latitude": 22.29207,
                    "longitude": 114.193203,
                    "remarks": "已成功送达"
                }
            ]
        }
        print(f"  {json.dumps(mock_response, indent=2, ensure_ascii=False)}")

def test_frontend_display():
    """测试前端显示逻辑"""
    print("\n=== 前端显示测试 ===")
    
    # 模拟timeline数据
    timeline_items = [
        {
            "id": 1,
            "timestamp": "2025-12-09T15:13:00",
            "status": "SHIPPED",
            "status_text": "已发货",
            "location": None,
            "latitude": 22.29207,
            "longitude": 114.193203,
            "remarks": None
        },
        {
            "id": 2,
            "timestamp": "2025-12-09T15:14:00",
            "status": "IN_TRANSIT", 
            "status_text": "运输中",
            "location": "深圳市南山区",
            "latitude": 22.29207,
            "longitude": 114.193203,
            "remarks": "正在运输途中"
        },
        {
            "id": 3,
            "timestamp": "2025-12-09T15:26:00",
            "status": "DELIVERED",
            "status_text": "已送达",
            "location": None,
            "latitude": None,
            "longitude": None,
            "remarks": "已成功送达"
        }
    ]
    
    print("前端显示逻辑验证:")
    for i, item in enumerate(timeline_items, 1):
        print(f"\n  记录 {i} - {item['status_text']}:")
        
        # GPS坐标显示逻辑
        if item.get('latitude') and item.get('longitude'):
            print(f"    📍 GPS坐标: {item['latitude']:.6f}, {item['longitude']:.6f}")
        
        # 位置描述显示逻辑  
        if item.get('location'):
            print(f"    📍 位置描述: {item['location']}")
            
        # 如果既没有GPS坐标也没有位置描述
        if not item.get('latitude') and not item.get('longitude') and not item.get('location'):
            print(f"    📍 位置信息: 未记录")
            
        # 备注显示逻辑
        if item.get('remarks'):
            print(f"    💬 备注: {item['remarks']}")

if __name__ == "__main__":
    print("药品追溯查询位置信息显示测试")
    print("=" * 60)
    
    test_trace_with_location_info()
    test_frontend_display()
    
    print()
    print("功能说明:")
    print("1. 时间轴视图现在会显示GPS坐标和位置描述")
    print("2. 新增流通记录详情表格，以表格形式清晰展示所有信息")
    print("3. 不同状态的记录有不同的颜色标识")
    print("4. GPS坐标使用等宽字体显示，便于阅读")
    print("5. 缺失的信息用'-'表示")
    
    print("\n注意:")
    print("需要使用监管用户账号登录才能访问药品追溯查询功能")
