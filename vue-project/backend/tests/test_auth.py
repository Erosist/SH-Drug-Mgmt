# backend/tests/test_auth.py
# 【修复版】我们（在 backend/ 里）不需要 'from backend.'

import pytest
from app import create_app  # <--- 修正！(删掉了 'backend.')
from config import Config   # <--- 修正！(删掉了 'backend.')

# --- TestConfig 必须在这里，或者在 config.py 里 ---
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 
    JWT_SECRET_KEY = 'test-secret' 
    
@pytest.fixture
def app():
    # 确保 create_app 能接受 config_object
    app = create_app(config_object=TestConfig) 
    app.config.update({"TESTING": True})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['msg'] == 'Flask auth backend is running'