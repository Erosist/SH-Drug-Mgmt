"""
简单查看数据库内容
"""
import sqlite3
import os

db_path = 'backend/instance/data.db'

if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("数据库表和数据统计")
print("=" * 60)

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\n数据库中的表 ({len(tables)}):")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  - {table_name}: {count} 条记录")

# 查看企业数据
print("\n" + "=" * 60)
print("企业 (tenants) 表数据:")
print("=" * 60)
cursor.execute("SELECT id, name, type, address FROM tenants LIMIT 10")
tenants = cursor.fetchall()
if tenants:
    for tenant in tenants:
        print(f"ID:{tenant[0]} | {tenant[1]} | {tenant[2]} | {tenant[3]}")
else:
    print("  没有数据")

# 查看用户数据
print("\n" + "=" * 60)
print("用户 (users) 表数据:")
print("=" * 60)
cursor.execute("SELECT id, username, email, role FROM users LIMIT 10")
users = cursor.fetchall()
if users:
    for user in users:
        print(f"ID:{user[0]} | {user[1]} | {user[2]} | {user[3]}")
else:
    print("  没有数据")

# 查看监管用户
print("\n监管用户:")
cursor.execute("SELECT id, username, email FROM users WHERE role='regulator'")
regulators = cursor.fetchall()
if regulators:
    for reg in regulators:
        print(f"  ID:{reg[0]} | {reg[1]} | {reg[2]}")
else:
    print("  没有监管用户")

# 查看库存数据
print("\n" + "=" * 60)
print("库存 (supply_info) 表数据:")
print("=" * 60)
cursor.execute("SELECT COUNT(*) FROM supply_info")
supply_count = cursor.fetchone()[0]
print(f"总记录数: {supply_count}")

if supply_count > 0:
    cursor.execute("SELECT id, tenant_id, drug_id, available_quantity, status FROM supply_info LIMIT 5")
    supplies = cursor.fetchall()
    for supply in supplies:
        print(f"  ID:{supply[0]} | Tenant:{supply[1]} | Drug:{supply[2]} | Qty:{supply[3]} | Status:{supply[4]}")

# 查看订单数据
print("\n" + "=" * 60)
print("订单 (orders) 表数据:")
print("=" * 60)
cursor.execute("SELECT COUNT(*) FROM orders")
order_count = cursor.fetchone()[0]
print(f"总记录数: {order_count}")

if order_count > 0:
    cursor.execute("SELECT id, order_number, buyer_tenant_id, supplier_tenant_id, status FROM orders LIMIT 5")
    orders = cursor.fetchall()
    for order in orders:
        print(f"  ID:{order[0]} | Order#:{order[1]} | Buyer:{order[2]} | Supplier:{order[3]} | Status:{order[4]}")

conn.close()
print("\n" + "=" * 60)
