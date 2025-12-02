import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    # 设置JWT token有效期为2小时，避免频繁过期
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    
    # 高德地图 API 配置
    AMAP_WEB_KEY = os.getenv('AMAP_WEB_KEY', '7fdb9359ad81879b1f935cfa51dc43f0')
    AMAP_REST_KEY = os.getenv('AMAP_REST_KEY', '143117d600102600e70696533eb39a5b')

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
