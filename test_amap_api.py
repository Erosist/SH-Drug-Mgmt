#!/usr/bin/env python3
import requests
import os

# 测试高德地图API
AMAP_REST_KEY = "143117d600102600e70696533eb39a5b"

print("Testing AMap API...")
print(f"Using key: {AMAP_REST_KEY}")

# 测试地理编码
url = "https://restapi.amap.com/v3/geocode/geo"
params = {
    "key": AMAP_REST_KEY,
    "address": "同济大学",
    "city": "上海"
}

try:
    r = requests.get(url, params=params, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
except Exception as e:
    print(f"Error: {e}")
