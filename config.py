import os


class Config(object):
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'production_uri'
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

class DevelopmentConfig(Config):
    #SQLALCHEMY_DATABASE_URI = "sqlite:///hr_streamline_app.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'testing_uri'
    TESTING = True