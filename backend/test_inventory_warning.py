"""
库存预警功能测试脚本
测试库存预警API和业务逻辑
"""
import requests
import json
from datetime import datetime, timedelta

# 测试配置
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/v1"

# 测试用户登录信息
test_user = {
    "username": "pharmacy_user",  # 需要替换为实际的测试用户
    "password": "password123"
}

def login_user():
    """用户登录获取JWT token"""
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=test_user)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"登录失败: {response.json()}")
            return None
    except Exception as e:
        print(f"登录请求失败: {str(e)}")
        return None

def test_get_warnings(token):
    """测试获取预警列表"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试获取预警列表 ===")
    
    # 测试获取所有预警
    response = requests.get(f"{API_BASE}/inventory/warnings", headers=headers)
    print(f"获取所有预警 - 状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"预警数量: {data['data']['statistics']['total_warnings']}")
        print(f"低库存数量: {data['data']['statistics']['low_stock_count']}")
        print(f"近效期数量: {data['data']['statistics']['near_expiry_count']}")
    else:
        print(f"错误: {response.json()}")
    
    # 测试获取低库存预警
    response = requests.get(f"{API_BASE}/inventory/warnings?warning_type=low_stock", headers=headers)
    print(f"\n获取低库存预警 - 状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"低库存预警数量: {len(data['data']['warnings'])}")
    
    # 测试获取近效期预警
    response = requests.get(f"{API_BASE}/inventory/warnings?warning_type=near_expiry", headers=headers)
    print(f"获取近效期预警 - 状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"近效期预警数量: {len(data['data']['warnings'])}")

def test_warning_summary(token):
    """测试预警摘要"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试预警摘要 ===")
    
    response = requests.get(f"{API_BASE}/inventory/warning-summary", headers=headers)
    print(f"预警摘要 - 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        summary = data['data']['summary']
        print(f"总预警数: {summary['total_warnings']}")
        print(f"低库存数: {summary['low_stock_count']}")
        print(f"近效期数: {summary['near_expiry_count']}")
        print(f"严重预警数: {summary['critical_count']}")
        
        urgent_warnings = data['data']['urgent_warnings']
        print(f"\n紧急预警 ({len(urgent_warnings)} 项):")
        for warning in urgent_warnings:
            print(f"  - {warning['drug_name']}: {warning['message']} ({warning['severity']})")
    else:
        print(f"错误: {response.json()}")

def test_manual_scan(token):
    """测试手动触发预警扫描（需要管理员权限）"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试手动预警扫描 ===")
    
    response = requests.post(f"{API_BASE}/inventory/scan-warnings", headers=headers)
    print(f"手动扫描 - 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        scan_result = data['data']
        print(f"扫描时间: {scan_result['scan_time']}")
        print(f"总预警数: {scan_result['total_warnings']}")
        print(f"涉及企业数: {scan_result['affected_tenants']}")
    else:
        print(f"错误: {response.json()}")

def test_pagination(token):
    """测试分页功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试分页功能 ===")
    
    # 测试第一页
    response = requests.get(f"{API_BASE}/inventory/warnings?page=1&per_page=5", headers=headers)
    print(f"第一页 (每页5条) - 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        pagination = data['data']['pagination']
        print(f"当前页: {pagination['page']}")
        print(f"每页数量: {pagination['per_page']}")
        print(f"总记录数: {pagination['total']}")
        print(f"总页数: {pagination['pages']}")
        print(f"有下一页: {pagination['has_next']}")

def test_invalid_parameters(token):
    """测试无效参数"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试无效参数 ===")
    
    # 测试无效的预警类型
    response = requests.get(f"{API_BASE}/inventory/warnings?warning_type=invalid", headers=headers)
    print(f"无效预警类型 - 状态码: {response.status_code}")
    if response.status_code == 400:
        print("✓ 正确返回400错误")
    
    # 测试超大页码
    response = requests.get(f"{API_BASE}/inventory/warnings?page=999999", headers=headers)
    print(f"超大页码 - 状态码: {response.status_code}")

def main():
    """主测试函数"""
    print("开始库存预警功能测试...")
    
    # 1. 用户登录
    token = login_user()
    if not token:
        print("登录失败，无法继续测试")
        return
    
    print(f"登录成功，Token: {token[:20]}...")
    
    # 2. 执行各项测试
    test_get_warnings(token)
    test_warning_summary(token)
    test_pagination(token)
    test_invalid_parameters(token)
    
    # 3. 测试管理员功能（可能需要管理员token）
    # test_manual_scan(token)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
