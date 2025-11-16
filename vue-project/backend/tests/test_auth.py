# 这是 test_auth.py 文件的【正确】内容

import pytest
from backend.app import create_app  # 导入你 backend 里的 app 工厂
from backend.config import Config, DevelopmentConfig # 导入你已有的 Config

# --- 马上要创建的 TestConfig ---
class TestConfig(Config):
    """用于自动化测试的配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # 使用内存数据库
    JWT_SECRET_KEY = 'test-secret' # 设置一个假的密钥
    
# "Fixture"：帮我们创建 app
@pytest.fixture
def app():
    app = create_app(config_object=TestConfig)
    app.config.update({"TESTING": True})
    yield app

# "Fixture"：帮我们创建测试客户端
@pytest.fixture
def client(app):
    return app.test_client()

# --- 我们的第一个测试用例 ---
# Pytest 会自动找到这个 test_ 开头的函数并运行它
def test_hello_world(client):
    """
    测试一下你 app.py 里的 @app.route('/') 接口
    （这个测试非常简单，它 100% 会通过）
    """
    # 1. 访问 '/' 根路径
    response = client.get('/')
    
    # 2. 断言：状态码必须是 200
    assert response.status_code == 200
    
    # 3. 断言：返回的 JSON 必须和你的 app.py 一致
    assert response.json['msg'] == 'Flask auth backend is running'