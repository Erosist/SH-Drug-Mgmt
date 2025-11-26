import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from app import create_app
from config import DevelopmentConfig
from extensions import db
from models import User


class TestConfig(DevelopmentConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-jwt-secret'


class AdminResetPasswordTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            admin = User(
                username='admin_user',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('AdminPass123')

            regular = User(
                username='pharmacy_user',
                email='pharmacy@example.com',
                role='pharmacy'
            )
            regular.set_password('Pharmacy123')

            target = User(
                username='target_user',
                email='target@example.com',
                role='supplier'
            )
            target.set_password('TargetPwd123')

            db.session.add_all([admin, regular, target])
            db.session.commit()

            self.admin_username = admin.username
            self.regular_username = regular.username
            self.target_user_id = target.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _login(self, username, password):
        resp = self.client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        self.assertEqual(resp.status_code, 200)
        return resp.get_json()['access_token']

    def test_admin_can_reset_other_user_password(self):
        token = self._login(self.admin_username, 'AdminPass123')
        resp = self.client.post(
            '/api/auth/admin/reset-user-password',
            headers={'Authorization': f'Bearer {token}'},
            json={'user_id': self.target_user_id, 'new_password': 'ResetPwd123'}
        )
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            user = User.query.get(self.target_user_id)
            self.assertTrue(user.check_password('ResetPwd123'))

    def test_non_admin_cannot_reset_password(self):
        token = self._login(self.regular_username, 'Pharmacy123')
        resp = self.client.post(
            '/api/auth/admin/reset-user-password',
            headers={'Authorization': f'Bearer {token}'},
            json={'user_id': self.target_user_id, 'new_password': 'ResetPwd123'}
        )
        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
