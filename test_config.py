#!/usr/bin/env python3
import os
print("Current dir:", os.getcwd())
print(".env exists:", os.path.exists('.env'))

from config import Config
print("AMAP_WEB_KEY:", Config.AMAP_WEB_KEY)
print("AMAP_REST_KEY:", Config.AMAP_REST_KEY)
print("AMAP_API_SECRET:", Config.AMAP_API_SECRET)

# 测试实际API调用
import requests
key = Config.AMAP_REST_KEY
address = "同济大学"
url = f"https://restapi.amap.com/v3/geocode/geo?key={key}&address={address}"
print(f"\nTesting geocode API...")
resp = requests.get(url)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:200]}")
