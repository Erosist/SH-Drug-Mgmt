"""
Utility script to import the provided JSON files into the SQLite database.

Usage:
    python tools/import_seed_data.py
    python tools/import_seed_data.py --data-dir "C:/path/to/json"
"""
import argparse
import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Type

CURRENT_DIR = Path(__file__).resolve()
BACKEND_DIR = CURRENT_DIR.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

import sys
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app  # noqa
from extensions import db
from models import Drug, InventoryItem, Tenant  # noqa


def parse_datetime(value: str) -> datetime:
    if value is None:
        return None
    value = value.replace('Z', '+00:00')
    return datetime.fromisoformat(value)


def parse_date(value: str) -> date:
    if value is None:
        return None
    return date.fromisoformat(value)


DATASETS = [
    {
        'filename': 'tenants_pharmacy.json',
        'model': Tenant,
        'casters': {
            'created_at': parse_datetime,
            'updated_at': parse_datetime,
        },
    },
    {
        'filename': 'drugs.json',
        'model': Drug,
        'casters': {
            'created_at': parse_datetime,
            'updated_at': parse_datetime,
        },
    },
    {
        'filename': 'inventory_items.json',
        'model': InventoryItem,
        'casters': {
            'production_date': parse_date,
            'expiry_date': parse_date,
            'created_at': parse_datetime,
            'updated_at': parse_datetime,
        },
    },
]


def load_records(path: Path) -> List[Dict[str, Any]]:
    content = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(content, dict):
        return list(content.values())
    if isinstance(content, list):
        return content
    raise ValueError(f'Unsupported JSON structure in {path}')


def import_file(path: Path, model: Type[db.Model], casters: Dict[str, Any]) -> int:
    records = load_records(path)
    model.query.delete()
    db.session.commit()

    objs: List[db.Model] = []
    for record in records:
        for field, caster in casters.items():
            if field in record and record[field] not in (None, ''):
                record[field] = caster(record[field])
        objs.append(model(**record))
    db.session.bulk_save_objects(objs)
    db.session.commit()
    return len(objs)


def main(argv: Iterable[str] = None):
    parser = argparse.ArgumentParser(description='Import JSON seed data into the database.')
    parser.add_argument('--data-dir', default=str(PROJECT_ROOT), help='Directory containing JSON files')
    args = parser.parse_args(list(argv) if argv is not None else None)

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        raise SystemExit(f'Data directory {data_dir} does not exist')

    app = create_app()
    with app.app_context():
        for config in DATASETS:
            json_path = data_dir / config['filename']
            if not json_path.exists():
                raise SystemExit(f'Missing file: {json_path}')
            count = import_file(json_path, config['model'], config['casters'])
            print(f'Imported {count} rows from {json_path.name}')


if __name__ == '__main__':
    main()
