from datetime import date, timedelta

import pytest

from app import create_app
from extensions import db
from models import User, Tenant, Drug
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()

        tenant = Tenant(
            name='Sample Pharmacy',
            type='PHARMACY',
            unified_social_credit_code='SH0001',
            legal_representative='Pharma Owner',
            contact_person='Manager Lee',
            contact_phone='13800000000',
            contact_email='pharmacy@example.com',
            address='100 Test Road, Shanghai',
            business_scope='Retail medicines',
            is_active=True
        )
        db.session.add(tenant)
        db.session.flush()

        drug = Drug(
            generic_name='Amoxicillin',
            brand_name='Demo Brand',
            approval_number='H20000001',
            dosage_form='capsule',
            specification='0.25g*24',
            manufacturer='Shanghai Pharma',
            category='Antibiotic',
            prescription_type='OTC'
        )
        db.session.add(drug)
        db.session.flush()

        user = User(
            username='pharmacy_user',
            email='pharmacy@example.com',
            role='pharmacy',
            tenant_id=tenant.id,
            is_authenticated=True
        )
        user.set_password('Secret123')
        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    resp = client.post('/api/auth/login', json={'username': 'pharmacy_user', 'password': 'Secret123'})
    assert resp.status_code == 200
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


class TestInventoryItems:
    def test_create_and_adjust_inventory_item(self, client, auth_headers):
        payload = {
            'drug_id': 1,
            'batch_number': 'P20251201001',
            'production_date': date.today().isoformat(),
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
            'quantity': 100,
            'unit_price': 12.5,
            'notes': '首次建档'
        }
        response = client.post('/api/v1/inventory/items', json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.get_json()
        item_id = data['item']['id']
        assert data['item']['quantity'] == 100

        list_resp = client.get('/api/v1/inventory/items', headers=auth_headers)
        assert list_resp.status_code == 200
        list_data = list_resp.get_json()
        assert list_data['total'] == 1
        assert list_data['items'][0]['batch_number'] == 'P20251201001'

        adjust_resp = client.put(
            f'/api/v1/inventory/items/{item_id}',
            json={'quantity_delta': -20, 'notes': 'Sales deduction'},
            headers=auth_headers
        )
        assert adjust_resp.status_code == 200
        adjust_data = adjust_resp.get_json()
        assert adjust_data['item']['quantity'] == 80

        # Adjusting beyond current stock must fail
        invalid_resp = client.put(
            f'/api/v1/inventory/items/{item_id}',
            json={'quantity_delta': -1000},
            headers=auth_headers
        )
        assert invalid_resp.status_code == 400
        error = invalid_resp.get_json()
        assert 'remaining inventory' in error['description'] or 'remaining inventory' in error.get('msg', '')