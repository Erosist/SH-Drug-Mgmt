"""订单发货与库存联动测试"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app import create_app
from config import TestingConfig
from extensions import db
from models import (
    Tenant,
    User,
    Drug,
    InventoryItem,
    Order,
    OrderItem,
    InventoryTransaction,
)
from tests.base import BaseTestCase


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()

        supplier = Tenant(
            name='发货供应商',
            type='SUPPLIER',
            unified_social_credit_code='SUP-SHIP-001',
            legal_representative='供应负责人',
            contact_person='供应联系人',
            contact_phone='13811112222',
            contact_email='shipper@example.com',
            address='上海市自贸区发货路88号',
            business_scope='药品批发',
            is_active=True,
        )
        buyer = Tenant(
            name='收货药房',
            type='PHARMACY',
            unified_social_credit_code='PHR-0001',
            legal_representative='药房负责人',
            contact_person='药房联系人',
            contact_phone='13700001111',
            contact_email='pharmacy@example.com',
            address='上海市浦东新区药房路66号',
            business_scope='药品零售',
            is_active=True,
        )
        db.session.add_all([supplier, buyer])
        db.session.flush()

        drug = Drug(
            generic_name='阿莫西林胶囊',
            brand_name='示例品牌',
            approval_number='H20250001',
            dosage_form='capsule',
            specification='0.25g*24粒',
            manufacturer='示例制药',
            category='Antibiotic',
            prescription_type='OTC',
        )
        db.session.add(drug)
        db.session.flush()

        supplier_user = User(
            username='testuser',
            email='shipper@example.com',
            role='supplier',
            tenant_id=supplier.id,
            is_authenticated=True,
        )
        supplier_user.set_password('password123')
        db.session.add(supplier_user)

        inventory_item = InventoryItem(
            tenant_id=supplier.id,
            drug_id=drug.id,
            batch_number='SHIP-2025-01',
            production_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=365),
            quantity=120,
            unit_price=9.5,
        )
        db.session.add(inventory_item)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestOrderShipmentInventory(BaseTestCase):
    def _get_base_context(self, client):
        with client.application.app_context():
            supplier = Tenant.query.filter_by(type='SUPPLIER').first()
            buyer = Tenant.query.filter_by(type='PHARMACY').first()
            drug = Drug.query.first()
            inventory = InventoryItem.query.filter_by(
                tenant_id=supplier.id,
                drug_id=drug.id,
            ).first()
            return {
                'supplier_id': supplier.id,
                'buyer_id': buyer.id,
                'drug_id': drug.id,
                'inventory_id': inventory.id,
            }

    def _create_confirmed_order(self, client, quantity):
        with client.application.app_context():
            ctx = self._get_base_context(client)
            supplier_user = User.query.filter_by(username='testuser').first()
            order = Order(
                buyer_tenant_id=ctx['buyer_id'],
                supplier_tenant_id=ctx['supplier_id'],
                status='CONFIRMED',
                created_by=supplier_user.id,
            )
            item = OrderItem(
                drug_id=ctx['drug_id'],
                unit_price=Decimal('8.50'),
                quantity=quantity,
                batch_number=None,
            )
            order.items.append(item)
            db.session.add(order)
            db.session.commit()
            return order.id

    def _get_supplier_headers(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No supplier test user available')
        return self.get_auth_headers(token)

    def test_ship_order_deducts_inventory(self, client):
        headers = self._get_supplier_headers(client)
        order_id = self._create_confirmed_order(client, quantity=60)

        response = client.post(f'/api/orders/{order_id}/ship', headers=headers, json={})
        self.assert_status_code(response, 200)

        with client.application.app_context():
            inventory = InventoryItem.query.first()
            assert inventory.quantity == 60
            transactions = InventoryTransaction.query.filter_by(related_order_id=order_id).all()
            assert any(t.transaction_type == 'OUT' and t.quantity_delta == -60 for t in transactions)

    def test_ship_order_rejects_when_inventory_insufficient(self, client):
        headers = self._get_supplier_headers(client)
        order_id = self._create_confirmed_order(client, quantity=500)

        response = client.post(f'/api/orders/{order_id}/ship', headers=headers, json={})
        self.assert_status_code(response, 400)
        body = response.get_json()
        assert '库存' in body.get('msg', '')

        with client.application.app_context():
            order = Order.query.get(order_id)
            assert order.status == 'CONFIRMED'
            inventory = InventoryItem.query.first()
            assert inventory.quantity == 120
