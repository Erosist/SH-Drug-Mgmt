#!/usr/bin/env python3
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# 登录
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "sfexpress",
    "password": "sf123456"
})
token = login_resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# 测试地址搜索API
print("测试地址搜索API...")
resp = requests.post(f"{BASE_URL}/dispatch/search_address", 
                     json={"keyword": "同济"},
                     headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")
