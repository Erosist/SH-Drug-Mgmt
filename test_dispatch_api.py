#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. 登录获取token...
print("1. 登录获取token...")
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "sfexpress",
    "password": "Test123456"
})
print(f"Login status: {login_resp.status_code}")
print(f"Login response: {login_resp.text[:200]}")

if login_resp.status_code != 200:
    print("登录失败!")
    exit(1)

token = login_resp.json().get("access_token")
print(f"Token: {token[:50]}...")

# 2. 测试路径优化API
print("\n2. 测试路径优化API...")
headers = {"Authorization": f"Bearer {token}"}
optimize_data = {
    "origin": "同济大学",
    "destinations": [
        {"name": "药店A", "coords": "121.48,31.23"},
        {"name": "药店B", "coords": "121.50,31.22"}
    ],
    "use_driving": False
}

try:
    resp = requests.post(f"{BASE_URL}/api/dispatch/optimize_route", 
                        json=optimize_data, 
                        headers=headers,
                        timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"Error: {e}")
