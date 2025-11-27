"""
pytest配置文件
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 设置测试环境变量
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'True'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-testing'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
