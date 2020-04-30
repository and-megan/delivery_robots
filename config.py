import os
basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config(BaseConfig):
    print("HELLO!")
    print(os.environ.get('DATABASE_URL'))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://delivery:1234@localhost:5432/delivery_db'
    DEBUG = True

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://delivery:1234@localhost:5432/delivery_test_db'
    TESTING = True
