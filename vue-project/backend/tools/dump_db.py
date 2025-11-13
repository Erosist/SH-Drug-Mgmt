import argparse
import json
import os
import sys
from typing import Optional

# 允许从 tools 子目录运行脚本
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from app import create_app
from extensions import db
from sqlalchemy import inspect, text


def to_serializable(value):
    if hasattr(value, 'isoformat'):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def dump_table(table: str, limit: Optional[int] = None):
    with db.engine.connect() as conn:
        # count
        count = conn.execute(text(f"SELECT COUNT(1) AS c FROM {table}"))
        total = count.scalar_one()
        print(f"\n== Table: {table} (rows: {total})")
        # rows
        sql = f"SELECT * FROM {table}"
        if isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"
        result = conn.execute(text(sql))
        cols = result.keys()
        rows = []
        for row in result:
            m = row._mapping  # SQLAlchemy RowMapping
            obj = {k: to_serializable(m[k]) for k in cols}
            rows.append(obj)
        print(json.dumps(rows, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Dump all tables from the current database (read-only).')
    parser.add_argument('--table', help='Only dump a specific table name')
    parser.add_argument('--limit', type=int, default=None, help='Limit rows per table for display')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if not tables:
            print('No tables found.')
            return
        if args.table:
            if args.table not in tables:
                print(f"Table '{args.table}' not found. Available: {tables}")
                return
            dump_table(args.table, args.limit)
        else:
            for t in tables:
                dump_table(t, args.limit)


if __name__ == '__main__':
    main()
