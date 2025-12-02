import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from app import create_app
from config import DevelopmentConfig
from extensions import db
from models import User, AdminAuditLog


class TestConfig(DevelopmentConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-jwt-secret'


class AdminAuditFeatureTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            admin = User(username='admin_user', email='admin@example.com', role='admin')
            admin.set_password('AdminPass123')

            other = User(username='pharmacy_user', email='pharmacy@example.com', role='pharmacy')
            other.set_password('Pharmacy123')

            db.session.add_all([admin, other])
            db.session.commit()

            self.admin_username = admin.username
            self.admin_id = admin.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _login(self, username, password):
        resp = self.client.post('/api/auth/login', json={'username': username, 'password': password})
        self.assertEqual(resp.status_code, 200)
        return resp.get_json()['access_token']

    def test_list_users_creates_audit_log(self):
        token = self._login(self.admin_username, 'AdminPass123')
        resp = self.client.get('/api/admin/users', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            logs = AdminAuditLog.query.filter_by(action='list_users').all()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0].admin_id, self.admin_id)

    def test_export_users_returns_csv_and_logs(self):
        token = self._login(self.admin_username, 'AdminPass123')
        resp = self.client.get('/api/admin/users/export?format=csv', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp.content_type)
        self.assertIn('users-', resp.headers.get('Content-Disposition', ''))

        csv_payload = resp.data.decode('utf-8')
        self.assertIn('username,email', csv_payload)

        with self.app.app_context():
            logs = AdminAuditLog.query.filter_by(action='export_users').all()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0].details.get('format'), 'csv')

    def test_audit_logs_endpoint_lists_entries(self):
        token = self._login(self.admin_username, 'AdminPass123')
        self.client.get('/api/admin/users', headers={'Authorization': f'Bearer {token}'})
        self.client.get('/api/admin/users/export?format=json', headers={'Authorization': f'Bearer {token}'})

        resp = self.client.get('/api/admin/audit-logs', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(data['total'], 2)
        self.assertTrue(any(item['action'] == 'export_users' for item in data['items']))

    def test_enable_disable_user_creates_specific_logs(self):
        token = self._login(self.admin_username, 'AdminPass123')

        with self.app.app_context():
            target = User.query.filter_by(username='pharmacy_user').first()
            target_id = target.id

        # disable target user
        resp = self.client.post(
            f'/api/admin/users/{target_id}/status',
            headers={'Authorization': f'Bearer {token}'},
            json={'action': 'disable'},
        )
        self.assertEqual(resp.status_code, 200)

        # enable target user
        resp = self.client.post(
            f'/api/admin/users/{target_id}/status',
            headers={'Authorization': f'Bearer {token}'},
            json={'action': 'enable'},
        )
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            disable_log = AdminAuditLog.query.filter_by(action='disable_user', target_user_id=target_id).first()
            enable_log = AdminAuditLog.query.filter_by(action='enable_user', target_user_id=target_id).first()
            self.assertIsNotNone(disable_log)
            self.assertIsNotNone(enable_log)
            self.assertEqual(disable_log.details.get('is_active'), False)
            self.assertEqual(enable_log.details.get('is_active'), True)

    def test_delete_user_action_logged(self):
        token = self._login(self.admin_username, 'AdminPass123')

        with self.app.app_context():
            target = User.query.filter_by(username='pharmacy_user').first()
            target_id = target.id

        resp = self.client.delete(
            f'/api/admin/users/{target_id}',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            log = AdminAuditLog.query.filter_by(action='delete_user', target_user_id=target_id).first()
            self.assertIsNotNone(log)

    def test_update_role_action_logged(self):
        token = self._login(self.admin_username, 'AdminPass123')

        with self.app.app_context():
            target = User.query.filter_by(username='pharmacy_user').first()
            target_id = target.id

        resp = self.client.post(
            f'/api/admin/users/{target_id}/role',
            headers={'Authorization': f'Bearer {token}'},
            json={'role': 'supplier', 'mark_authenticated': True},
        )
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            log = AdminAuditLog.query.filter_by(action='update_user_role', target_user_id=target_id).first()
            self.assertIsNotNone(log)
            self.assertEqual(log.details.get('new_role'), 'supplier')
            self.assertTrue(log.details.get('mark_authenticated'))

    def test_system_status_action_logged(self):
        token = self._login(self.admin_username, 'AdminPass123')

        resp = self.client.get('/api/admin/system/status', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            log = AdminAuditLog.query.filter_by(action='system_status').first()
            self.assertIsNotNone(log)

    def test_list_audit_logs_action_logged(self):
        token = self._login(self.admin_username, 'AdminPass123')

        # create at least one log entry to list
        self.client.get('/api/admin/users', headers={'Authorization': f'Bearer {token}'})

        resp = self.client.get('/api/admin/audit-logs', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            log = AdminAuditLog.query.filter_by(action='list_audit_logs').first()
            self.assertIsNotNone(log)


if __name__ == '__main__':
    unittest.main()
