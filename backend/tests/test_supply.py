"""
供应信息模块测试
"""
from datetime import date, timedelta

import pytest

from app import create_app
from config import TestingConfig
from extensions import db
from models import Tenant, User, Drug, InventoryItem
from tests.base import BaseTestCase

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()

        tenant = Tenant(
            name='示例供应商',
            type='SUPPLIER',
            unified_social_credit_code='SUP-00001',
            legal_representative='供应商法人',
            contact_person='供应联系人',
            contact_phone='13900000000',
            contact_email='supplier@example.com',
            address='上海市浦东新区测试路123号',
            business_scope='药品批发',
            is_active=True
        )
        db.session.add(tenant)
        db.session.flush()

        drug = Drug(
            generic_name='头孢氨苄',
            brand_name='示例品牌',
            approval_number='H00000001',
            dosage_form='capsule',
            specification='0.25g*20粒',
            manufacturer='示例药业',
            category='Antibiotic',
            prescription_type='OTC'
        )
        db.session.add(drug)
        db.session.flush()

        user = User(
            username='testuser',
            email='supplier@example.com',
            role='supplier',
            tenant_id=tenant.id,
            is_authenticated=True
        )
        user.set_password('password123')
        db.session.add(user)

        inventory_item = InventoryItem(
            tenant_id=tenant.id,
            drug_id=drug.id,
            batch_number='B20250101',
            production_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            quantity=500,
            unit_price=6.8
        )
        db.session.add(inventory_item)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestSupply(BaseTestCase):
    """供应信息功能测试类"""

    def _get_seed_context(self, client):
        with client.application.app_context():
            user = User.query.filter_by(username='testuser').first()
            drug = Drug.query.first()
            if not user or not drug:
                return {'tenant_id': None, 'drug_id': None, 'inventory_total': 0}
            inventory_total = sum(
                item.quantity for item in InventoryItem.query.filter_by(
                    tenant_id=user.tenant_id,
                    drug_id=drug.id
                )
            )
            return {
                'tenant_id': user.tenant_id,
                'drug_id': drug.id,
                'inventory_total': inventory_total
            }

    def _create_supply(self, client, headers, quantity=50):
        context = self._get_seed_context(client)
        if not context['drug_id']:
            pytest.skip('Seed data missing drug information')
        supply_quantity = max(1, min(quantity, context['inventory_total']))
        payload = {
            'drug_id': context['drug_id'],
            'available_quantity': supply_quantity,
            'unit_price': 10.5,
            'valid_until': (date.today() + timedelta(days=30)).isoformat(),
            'min_order_quantity': 5,
            'description': '用于测试的供应'
        }
        response = client.post('/api/supply/info', headers=headers, json=payload)
        self.assert_status_code(response, 201)
        return response.get_json()['data']

    def test_get_supply_info_list(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        response = client.get('/api/supply/info', headers=headers)
        data = self.assert_success_response(response)
        assert 'items' in data['data']
        assert 'pagination' in data['data']

    def test_get_supply_info_with_search(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)

        response = client.get('/api/supply/info?drug_name=头孢', headers=headers)
        self.assert_status_code(response, 200)

        response = client.get('/api/supply/info?supplier_name=示例供应商', headers=headers)
        self.assert_status_code(response, 200)

    def test_get_supply_info_pagination(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        response = client.get('/api/supply/info?page=1&per_page=5', headers=headers)
        data = self.assert_success_response(response)
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['per_page'] == 5

    def test_get_supply_info_detail(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        created_supply = self._create_supply(client, headers, quantity=20)
        response = client.get(f"/api/supply/info/{created_supply['id']}", headers=headers)
        data = self.assert_success_response(response)
        assert data['data']['id'] == created_supply['id']
        assert data['data']['drug']['id'] == created_supply['drug_id']

    def test_get_nonexistent_supply_info(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        response = client.get('/api/supply/info/99999', headers=headers)
        self.assert_status_code(response, 404)

    def test_create_supply_info_success_when_inventory_available(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        created_supply = self._create_supply(client, headers, quantity=80)
        assert created_supply['available_quantity'] == 80

    def test_create_supply_info_requires_existing_inventory(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        future_date = (date.today() + timedelta(days=45)).isoformat()

        with client.application.app_context():
            new_drug = Drug(
                generic_name='新的药品',
                brand_name='无库存品牌',
                approval_number='H00000099',
                dosage_form='tablet',
                specification='10mg*10片',
                manufacturer='无库存药业',
                category='Other',
                prescription_type='RX'
            )
            db.session.add(new_drug)
            db.session.commit()
            new_drug_id = new_drug.id

        payload = {
            'drug_id': new_drug_id,
            'available_quantity': 10,
            'unit_price': 15.0,
            'valid_until': future_date,
            'min_order_quantity': 5
        }
        response = client.post('/api/supply/info', headers=headers, json=payload)
        self.assert_status_code(response, 400)
        body = response.get_json()
        assert '库存' in body.get('msg', '')

    def test_create_supply_info_rejects_quantity_above_inventory(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        context = self._get_seed_context(client)
        future_date = (date.today() + timedelta(days=60)).isoformat()
        payload = {
            'drug_id': context['drug_id'],
            'available_quantity': context['inventory_total'] + 1,
            'unit_price': 12.0,
            'valid_until': future_date,
            'min_order_quantity': 5
        }
        response = client.post('/api/supply/info', headers=headers, json=payload)
        self.assert_status_code(response, 400)
        body = response.get_json()
        assert '不能超过当前库存' in body.get('msg', '')

    def test_update_supply_info_rejects_quantity_above_inventory(self, client):
        token = self.login_user(client)
        if not token:
            pytest.skip('No test user available')

        headers = self.get_auth_headers(token)
        created_supply = self._create_supply(client, headers, quantity=50)
        context = self._get_seed_context(client)
        excessive_payload = {'available_quantity': context['inventory_total'] + 10}
        response = client.put(
            f"/api/supply/info/{created_supply['id']}",
            headers=headers,
            json=excessive_payload
        )
        self.assert_status_code(response, 400)
        body = response.get_json()
        assert '不能超过当前库存' in body.get('msg', '')