from datetime import datetime

from extensions import db
from models import User, EnterpriseCertification, Tenant
from tests.base import BaseTestCase


class TestEnterpriseApproval(BaseTestCase):
	def _create_user_with_cert(self, app, username: str, company_name: str, credit_code: str):
		"""Helper to seed a pending certification for a new user"""
		with app.app_context():
			user = User(
				username=username,
				email=f'{username}@example.com',
				role='unauth',
				is_active=True,
			)
			user.set_password('Password123!')
			db.session.add(user)
			db.session.commit()

			cert = EnterpriseCertification(
				user_id=user.id,
				role='pharmacy',
				company_name=company_name,
				unified_social_credit_code=credit_code,
				contact_person='李四',
				contact_phone='13800009998',
				contact_email=f'contact_{username}@example.com',
				registered_address='上海市徐汇区',
				business_scope='药品零售',
				status='pending',
				submitted_at=datetime.utcnow(),
			)
			db.session.add(cert)
			db.session.commit()

			return user.id, cert.id

	def test_approving_cert_creates_tenant_and_links_user(self, app, client):
		user_id, cert_id = self._create_user_with_cert(
			app,
			username='pending_pharmacy_user',
			company_name='新认证药店',
			credit_code='CERT_TEST_CODE_001'
		)

		token = self.login_user(client, username='testadmin', password='admin123')
		assert token
		headers = self.get_auth_headers(token)

		response = client.post(
			f'/api/enterprise/review/{cert_id}',
			headers=headers,
			json={'decision': 'approved'}
		)

		self.assert_status_code(response, 200)

		with app.app_context():
			user = User.query.get(user_id)
			tenant = Tenant.query.filter_by(unified_social_credit_code='CERT_TEST_CODE_001').first()

			assert user.role == 'pharmacy'
			assert user.is_authenticated is True
			assert user.tenant_id == tenant.id
			assert tenant is not None
			assert tenant.name == '新认证药店'

	def test_approving_cert_reuses_existing_tenant(self, app, client):
		with app.app_context():
			tenant = Tenant(
				name='已有药店',
				type='PHARMACY',
				unified_social_credit_code='EXISTING_CODE_001',
				legal_representative='旧联系人',
				contact_person='旧联系人',
				contact_phone='13800001234',
				contact_email='old@example.com',
				address='旧地址',
				business_scope='旧业务'
			)
			db.session.add(tenant)
			db.session.commit()
			existing_tenant_id = tenant.id

		user_id, cert_id = self._create_user_with_cert(
			app,
			username='reuse_tenant_user',
			company_name='继承药店',
			credit_code='EXISTING_CODE_001'
		)

		token = self.login_user(client, username='testadmin', password='admin123')
		assert token
		headers = self.get_auth_headers(token)

		response = client.post(
			f'/api/enterprise/review/{cert_id}',
			headers=headers,
			json={'decision': 'approved'}
		)

		self.assert_status_code(response, 200)

		with app.app_context():
			user = User.query.get(user_id)
			tenant = Tenant.query.filter_by(unified_social_credit_code='EXISTING_CODE_001').all()

			assert len(tenant) == 1
			tenant = tenant[0]
			assert tenant.id == existing_tenant_id
			assert tenant.name == '继承药店'
			assert tenant.contact_person == '李四'
			assert user.tenant_id == existing_tenant_id
			assert user.is_authenticated is True
