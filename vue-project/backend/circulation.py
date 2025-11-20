from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from extensions import db
from models import InventoryItem, InventoryTransaction, Tenant

bp = Blueprint('circulation', __name__, url_prefix='/api/circulation')

TIME_RANGE_DAYS = {
    '7d': 7,
    '30d': 30,
    '90d': 90,
}


def _extract_region(address: str) -> str:
    """Try to normalize address string into a district/region label."""
    if not address:
        return '其他'
    for marker in ('区', '县', '市'):
        idx = address.find(marker)
        if idx != -1:
            return address[: idx + 1]
    return address[:4] if len(address) >= 2 else '其他'


def _available_regions():
    rows = db.session.query(Tenant.address).filter(Tenant.address.isnot(None)).all()
    regions = {_extract_region(addr) for (addr,) in rows if addr}
    if '其他' in regions:
        regions.remove('其他')
    return sorted(regions)


@bp.route('/dashboard', methods=['GET'])
def circulation_dashboard():
    time_range_key = (request.args.get('time_range') or '7d').lower()
    region_filter = (request.args.get('region') or '').strip()

    days = TIME_RANGE_DAYS.get(time_range_key, 7)
    start_time = datetime.utcnow() - timedelta(days=days)

    inventory_query = db.session.query(func.coalesce(func.sum(InventoryItem.quantity), 0)).join(
        Tenant, InventoryItem.tenant_id == Tenant.id
    )
    if region_filter:
        inventory_query = inventory_query.filter(Tenant.address.contains(region_filter))
    total_inventory = int(inventory_query.scalar() or 0)

    tx_query = (
        db.session.query(
            InventoryTransaction.created_at,
            InventoryTransaction.transaction_type,
            InventoryTransaction.quantity_delta,
            InventoryItem.quantity.label('item_quantity'),
            InventoryItem.updated_at.label('item_updated_at'),
            Tenant.address.label('tenant_address'),
        )
        .join(InventoryTransaction.inventory_item)
        .join(InventoryItem.tenant)
        .filter(InventoryTransaction.created_at >= start_time)
    )
    if region_filter:
        tx_query = tx_query.filter(Tenant.address.contains(region_filter))

    tx_rows = tx_query.all()

    today = datetime.utcnow().date()
    start_date = start_time.date()
    day_buckets = {}
    for offset in range((today - start_date).days + 1):
        day = start_date + timedelta(days=offset)
        day_buckets[day] = {'inbound': 0, 'outbound': 0}

    region_stats = defaultdict(int)
    in_transit = 0
    delayed_reports = 0
    mismatch_reports = 0
    active_regions = set()
    last_activity = None

    for tx in tx_rows:
        created_at = tx.created_at or datetime.utcnow()
        last_activity = max(last_activity, created_at) if last_activity else created_at
        day_key = created_at.date()
        if day_key not in day_buckets:
            day_buckets[day_key] = {'inbound': 0, 'outbound': 0}

        qty = abs(int(tx.quantity_delta or 0))
        region = _extract_region(tx.tenant_address)
        active_regions.add(region)
        region_stats[region] += qty

        if tx.quantity_delta >= 0:
            day_buckets[day_key]['inbound'] += qty
        else:
            day_buckets[day_key]['outbound'] += qty

        if tx.transaction_type in {'TRANSFER', 'OUT'} and tx.quantity_delta < 0:
            in_transit += qty

        item_updated_at = tx.item_updated_at
        if item_updated_at and (item_updated_at - created_at).total_seconds() > 24 * 3600:
            delayed_reports += 1

        item_qty = tx.item_quantity or 0
        if tx.quantity_delta < 0 and abs(tx.quantity_delta) > item_qty:
            mismatch_reports += 1

    region_distribution = [
        {'region': region, 'value': volume}
        for region, volume in sorted(region_stats.items(), key=lambda x: x[1], reverse=True)
    ]

    map_heat = [{'name': data['region'], 'value': data['value']} for data in region_distribution]

    time_series = [
        {
            'date': day.strftime('%Y-%m-%d'),
            'inbound': values['inbound'],
            'outbound': values['outbound'],
        }
        for day, values in sorted(day_buckets.items())
    ]

    anomaly_total = delayed_reports + mismatch_reports

    last_inventory_update = db.session.query(func.max(InventoryItem.updated_at)).scalar()
    if last_inventory_update:
        last_activity = (
            max(last_activity, last_inventory_update)
            if last_activity
            else last_inventory_update
        )

    return jsonify(
        {
            'generated_at': datetime.utcnow().isoformat(),
            'last_activity': last_activity.isoformat() if last_activity else None,
            'filters': {
                'time_range': time_range_key,
                'region': region_filter or None,
                'available_ranges': [
                    {'label': '近7天', 'value': '7d'},
                    {'label': '近30天', 'value': '30d'},
                    {'label': '近90天', 'value': '90d'},
                ],
                'available_regions': _available_regions(),
            },
            'summary': {
                'total_inventory': total_inventory,
                'in_transit': in_transit,
                'region_count': len(active_regions),
                'anomaly_total': anomaly_total,
            },
            'time_series': time_series,
            'region_distribution': region_distribution,
            'map_heat': map_heat,
            'anomalies': {
                'delayed_reports': delayed_reports,
                'data_mismatch': mismatch_reports,
            },
            'auto_refresh_seconds': 300,
        }
    )
