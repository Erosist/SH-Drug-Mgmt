#!/usr/bin/env python3
"""
修改 JSON 文件中的 id，每个 id 加 14
"""

import json

# JSON 文件路径
JSON_FILE_INPUT = r"d:\xwechat_files\wxid_5tylomcbmtlm22_6f53\msg\file\2025-11\tenants_pharmacy.json"
JSON_FILE_OUTPUT = r"d:\Desktop\软件工程\SH-Drug-Mgmt\backend\tenants_pharmacy_updated.json"

def update_ids():
    """更新所有记录的 id"""
    try:
        # 读取 JSON 文件
        with open(JSON_FILE_INPUT, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"原始 id 范围: {data[0]['id']} - {data[-1]['id']}")
        
        # 更新每个记录的 id
        for item in data:
            item['id'] = item['id'] + 14
        
        # 写入新文件
        with open(JSON_FILE_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"新的 id 范围: {data[0]['id']} - {data[-1]['id']}")
        print(f"✅ 成功更新 {len(data)} 条记录的 id（每个 +14）")
        print(f"📄 新文件保存在: {JSON_FILE_OUTPUT}")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    update_ids()
