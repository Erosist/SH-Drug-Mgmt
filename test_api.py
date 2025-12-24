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
print(login_resp.text)

if login_resp.status_code == 200:
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试路径优化API
    print("\n2. 测试路径优化API...")
    optimize_data = {
        "origin": "同济大学",
        "destinations": [
            {"name": "药店A", "coords": "121.48,31.23"},
            {"name": "药店B", "coords": "121.50,31.22"}
        ],
        "use_driving": False
    }
    opt_resp = requests.post(f"{BASE_URL}/dispatch/optimize_route", 
                             json=optimize_data, headers=headers)
    print(f"优化响应: {opt_resp.status_code}")
    print(opt_resp.text[:500] if len(opt_resp.text) > 500 else opt_resp.text)
else:
    print("登录失败，无法继续测试")
