import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(Config):
    """用于自动化测试的配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # 使用内存数据库
    JWT_SECRET_KEY = 'test-secret' # 设置一个假的密钥
    

class ProductionConfig(Config):
    DEBUG = False
