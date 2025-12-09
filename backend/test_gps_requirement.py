#!/usr/bin/env python3
"""
测试GPS要求的流通数据上报功能
"""

import requests
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/circulation/report"

def test_report_without_gps():
    """测试不提供GPS坐标的情况"""
    print("=== 测试不提供GPS坐标 ===")
    
    # 模拟物流用户登录（需要先有有效的token）
    # 这里只是演示请求格式
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'  # 需要替换为真实token
    }
    
    data = {
        "tracking_number": "TEST123456",
        "transport_status": "SHIPPED",
        "timestamp": datetime.now().isoformat(),
        "remarks": "测试不提供GPS坐标"
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 注意：这个测试需要运行的后端服务和有效的JWT token
    # response = requests.post(API_URL, json=data, headers=headers)
    # print(f"响应状态码: {response.status_code}")
    # print(f"响应内容: {response.json()}")

def test_report_with_gps():
    """测试提供GPS坐标的情况"""
    print("=== 测试提供GPS坐标 ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'  # 需要替换为真实token
    }
    
    data = {
        "tracking_number": "TEST123456", 
        "transport_status": "SHIPPED",
        "timestamp": datetime.now().isoformat(),
        "latitude": 31.2304,  # 上海的大概坐标
        "longitude": 121.4737,
        "remarks": "测试提供GPS坐标"
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 注意：这个测试需要运行的后端服务和有效的JWT token
    # response = requests.post(API_URL, json=data, headers=headers)
    # print(f"响应状态码: {response.status_code}")
    # print(f"响应内容: {response.json()}")

def test_report_with_invalid_gps():
    """测试提供无效GPS坐标的情况"""
    print("=== 测试无效GPS坐标 ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'
    }
    
    # 测试超出范围的坐标
    data = {
        "tracking_number": "TEST123456",
        "transport_status": "SHIPPED", 
        "timestamp": datetime.now().isoformat(),
        "latitude": 91.0,  # 无效：超出-90到90的范围
        "longitude": 181.0,  # 无效：超出-180到180的范围
        "remarks": "测试无效GPS坐标"
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    print("GPS要求测试脚本")
    print("注意：需要运行的后端服务和有效的JWT token才能实际执行请求")
    print()
    
    test_report_without_gps()
    print()
    test_report_with_gps() 
    print()
    test_report_with_invalid_gps()
    print()
    
    print("预期结果:")
    print("1. 不提供GPS坐标 -> 400错误，提示'GPS坐标是必填项，请先使用GPS定位'")
    print("2. 提供有效GPS坐标 -> 200成功")
    print("3. 提供无效GPS坐标 -> 400错误，提示坐标范围无效")
