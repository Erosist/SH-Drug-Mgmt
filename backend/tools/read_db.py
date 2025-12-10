#!/usr/bin/env python3
"""
数据库读取脚本
用于查看 data.db 文件中的内容
支持终端输出和 HTML 文件输出
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# 数据库文件路径
DB_PATH = Path(__file__).resolve().parents[1] / 'instance' / 'data.db'
OUTPUT_HTML = Path(__file__).resolve().parents[1] / 'database_report.html'

def connect_db():
    """连接到数据库"""
    if not DB_PATH.exists():
        print(f"错误: 数据库文件不存在: {DB_PATH}")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        return conn
    except Exception as e:
        print(f"连接数据库失败: {e}")
        sys.exit(1)

def get_all_tables(conn):
    """获取所有表名"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def get_table_schema(conn, table_name):
    """获取表结构"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return columns

def get_table_count(conn, table_name):
    """获取表的记录数"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    except:
        return 0

def display_table_data(conn, table_name, limit=10):
    """显示表的数据"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"  表 '{table_name}' 中没有数据")
            return
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        
        # 显示数据
        print(f"\n  前 {min(len(rows), limit)} 条记录:")
        print("  " + "-" * 80)
        
        for row in rows:
            print(f"\n  记录:")
            for col_name, value in zip(columns, row):
                # 格式化显示
                if value is None:
                    display_value = "NULL"
                elif isinstance(value, (bytes, bytearray)):
                    display_value = f"<binary data, {len(value)} bytes>"
                elif isinstance(value, str) and len(value) > 100:
                    display_value = value[:100] + "..."
                else:
                    display_value = value
                print(f"    {col_name}: {display_value}")
        
    except Exception as e:
        print(f"  读取数据失败: {e}")

def generate_html_report(conn, tables):
    """生成 HTML 报告"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据库内容报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header .meta {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .summary {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 3px solid #667eea;
        }
        .summary h2 {
            color: #333;
            margin-bottom: 15px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .summary-card .label {
            color: #666;
            font-size: 0.9em;
        }
        .content {
            padding: 30px;
        }
        .table-section {
            margin-bottom: 40px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }
        .table-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .table-header:hover {
            background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%);
        }
        .table-header h3 {
            font-size: 1.5em;
        }
        .table-info {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .table-content {
            padding: 20px;
            background: #fafafa;
        }
        .schema-section {
            margin-bottom: 20px;
        }
        .schema-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .schema-list {
            background: white;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }
        .schema-item {
            padding: 8px;
            border-bottom: 1px solid #f0f0f0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .schema-item:last-child {
            border-bottom: none;
        }
        .primary-key {
            color: #e74c3c;
            font-weight: bold;
        }
        .not-null {
            color: #f39c12;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .data-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        .data-table td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        .data-table tr:hover {
            background: #f5f5f5;
        }
        .no-data {
            text-align: center;
            padding: 30px;
            color: #999;
            font-style: italic;
        }
        .record-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .record-field {
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .record-field:last-child {
            border-bottom: none;
        }
        .field-name {
            font-weight: bold;
            color: #667eea;
        }
        .field-value {
            color: #333;
            word-break: break-all;
        }
        .toggle-icon {
            transition: transform 0.3s;
        }
        .collapsed .toggle-icon {
            transform: rotate(-90deg);
        }
        .footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }
    </style>
    <script>
        function toggleTable(tableId) {
            const content = document.getElementById(tableId);
            const header = content.previousElementSibling;
            if (content.style.display === 'none') {
                content.style.display = 'block';
                header.classList.remove('collapsed');
            } else {
                content.style.display = 'none';
                header.classList.add('collapsed');
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 数据库内容报告</h1>
            <div class="meta">
                <p>数据库文件: """ + str(DB_PATH) + """</p>
                <p>生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
        </div>
        
        <div class="summary">
            <h2>📈 数据概览</h2>
            <div class="summary-grid">
"""
    
    # 添加统计卡片
    total_records = 0
    for table_name in tables:
        if not table_name.startswith('sqlite_') and table_name != 'alembic_version':
            count = get_table_count(conn, table_name)
            total_records += count
    
    table_count = len([t for t in tables if not t.startswith('sqlite_') and t != 'alembic_version'])
    
    html_content += f"""
                <div class="summary-card">
                    <div class="number">{table_count}</div>
                    <div class="label">数据表总数</div>
                </div>
                <div class="summary-card">
                    <div class="number">{total_records}</div>
                    <div class="label">记录总数</div>
                </div>
"""
    
    # 添加各表记录数
    for table_name in tables:
        if not table_name.startswith('sqlite_') and table_name != 'alembic_version':
            count = get_table_count(conn, table_name)
            html_content += f"""
                <div class="summary-card">
                    <div class="number">{count}</div>
                    <div class="label">{table_name}</div>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="content">
"""
    
    # 遍历每个表
    for idx, table_name in enumerate(tables):
        if table_name.startswith('sqlite_') or table_name == 'alembic_version':
            continue
        
        schema = get_table_schema(conn, table_name)
        count = get_table_count(conn, table_name)
        
        html_content += f"""
            <div class="table-section">
                <div class="table-header" onclick="toggleTable('table-{idx}')">
                    <h3>📋 {table_name}</h3>
                    <div class="table-info">
                        <span>{len(schema)} 列</span> | <span>{count} 条记录</span>
                        <span class="toggle-icon">▼</span>
                    </div>
                </div>
                <div id="table-{idx}" class="table-content">
                    <div class="schema-section">
                        <div class="schema-title">表结构:</div>
                        <div class="schema-list">
"""
        
        # 添加表结构
        for col in schema:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_html = '<span class="primary-key">[主键]</span>' if pk else ''
            null_html = '<span class="not-null">NOT NULL</span>' if not_null else ''
            default_html = f' DEFAULT {default_val}' if default_val else ''
            html_content += f"""
                            <div class="schema-item">
                                {col_name}: <strong>{col_type}</strong> {pk_html} {null_html}{default_html}
                            </div>
"""
        
        html_content += """
                        </div>
                    </div>
"""
        
        # 添加数据
        if count > 0:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            html_content += """
                    <div class="schema-section">
                        <div class="schema-title">数据记录 (前10条):</div>
"""
            
            for row_idx, row in enumerate(rows):
                html_content += f"""
                        <div class="record-card">
                            <strong style="color: #667eea;">记录 #{row_idx + 1}</strong>
"""
                for col_name, value in zip(columns, row):
                    if value is None:
                        display_value = '<em style="color: #999;">NULL</em>'
                    elif isinstance(value, (bytes, bytearray)):
                        display_value = f'<em style="color: #999;">&lt;二进制数据, {len(value)} 字节&gt;</em>'
                    elif isinstance(value, str) and len(value) > 200:
                        display_value = value[:200] + '...'
                    else:
                        display_value = str(value)
                    
                    html_content += f"""
                            <div class="record-field">
                                <div class="field-name">{col_name}:</div>
                                <div class="field-value">{display_value}</div>
                            </div>
"""
                html_content += """
                        </div>
"""
            html_content += """
                    </div>
"""
        else:
            html_content += """
                    <div class="no-data">该表暂无数据</div>
"""
        
        html_content += """
                </div>
            </div>
"""
    
    html_content += """
        </div>
        
        <div class="footer">
            <p>© 2025 SH-Drug-Mgmt 数据库报告系统</p>
            <p>由 read_db.py 自动生成</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def main():
    """主函数"""
    # 连接数据库
    conn = connect_db()
    
    try:
        # 获取所有表
        tables = get_all_tables(conn)
        
        # 生成 HTML 报告
        print(f"正在生成完整数据库报告 (共 {len(tables)} 个表)...")
        html_content = generate_html_report(conn, tables)
        
        # 写入文件
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ 报告生成成功！")
        print(f"📄 文件位置: {OUTPUT_HTML}")
        print(f"📊 包含表: {', '.join(tables)}")
        print(f"\n请在浏览器中打开该文件查看")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
