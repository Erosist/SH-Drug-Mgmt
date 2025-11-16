import pytest
from your_app import create_app  # 假设你的 app.py 里有 create_app
from your_app.models import User

# Pytest "Fixture": 创建一个可复用的测试客户端
@pytest.fixture
def client():
    app = create_app(config_object=TestConfig) # 你需要一个专门的测试配置
    with app.test_client() as client:
        with app.app_context():
            # (可选) 如果你需要一个真实的测试数据库
            # db.create_all() 
        yield client
    # (可选) db.drop_all()

# 测试登录成功 (mocker 是 pytest-mock 提供的)
def test_login_success(client, mocker):
    # 1. 准备一个“假用户”
    mock_user = User(username='test', email='test@test.com')
    mock_user.set_password('123') # 确保 check_password 能通过

    # 2. Mock 掉数据库查询
    # 当 auth.py 里的 find_user_by_identifier 被调用时，
    # 强行让它返回我们的 mock_user
    mocker.patch(
        'your_app.auth.find_user_by_identifier', 
        return_value=mock_user
    )
    
    # (或者 Mock check_password)
    # mocker.patch.object(mock_user, 'check_password', return_value=True)

    # 3. 发送请求
    response = client.post(
        '/api/auth/login',
        json={'username': 'test', 'password': '123'}
    )

    # 4. 断言结果
    assert response.status_code == 200
    assert 'access_token' in response.json

# 测试登录失败
def test_login_fail_bad_password(client, mocker):
    # 1. 模拟“找不到用户”
    mocker.patch(
        'your_app.auth.find_user_by_identifier', 
        return_value=None
    )
    
    # 2. 发送请求
    response = client.post(
        '/api/auth/login',
        json={'username': 'test', 'password': 'badpass'}
    )

    # 3. 断言结果
    assert response.status_code == 401
    assert response.json['msg'] == 'bad username or password'