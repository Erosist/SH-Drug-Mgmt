#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# 1. 登录获取token
print("1. 登录sfexpress...")
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "sfexpress",
    "password": "sf123456"
})
print(f"登录响应: {login_resp.status_code}")

if login_resp.status_code == 200:
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试路径优化API - 使用正确的参数格式
    print("\n2. 测试路径优化API...")
    optimize_data = {
        "start": "同济大学",
        "destinations": [
            {"name": "药店A", "location": "121.48,31.23"},
            {"name": "药店B", "location": "121.50,31.22"}
        ],
        "use_api": False,
        "algorithm": "greedy"
    }
    print(f"请求数据: {json.dumps(optimize_data, ensure_ascii=False)}")
    
    opt_resp = requests.post(f"{BASE_URL}/dispatch/optimize_route", 
                             json=optimize_data, headers=headers)
    print(f"优化响应状态: {opt_resp.status_code}")
    
    try:
        result = opt_resp.json()
        print(f"优化响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应内容: {opt_resp.text}")
else:
    print("登录失败")
    print(login_resp.text)
