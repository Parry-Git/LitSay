import os
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的环境变量

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret'

    # OceanBase Configuration
    OB_HOST = os.environ.get('OB_HOST')
    OB_PORT = int(os.environ.get('OB_PORT', 3306))
    OB_USER = os.environ.get('OB_USER')
    OB_PASSWORD = os.environ.get('OB_PASSWORD')
    OB_DATABASE = os.environ.get('OB_DATABASE')

    # SQLAlchemy (如果将来使用)
    # SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{OB_USER}:{OB_PASSWORD}@{OB_HOST}:{OB_PORT}/{OB_DATABASE}"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    # For testing, you might use a separate test database or mock the DB
    OB_DATABASE = os.environ.get('TEST_OB_DATABASE') or 'paperdb-alpha' # 假设测试用不同数据库

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}