import os
from datetime import timedelta


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///taskish.db'
    )


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

    @staticmethod
    def get_database_uri():
        """Get database URI, fixing postgres:// to postgresql:// for SQLAlchemy."""
        uri = os.environ.get('DATABASE_URL')
        if uri and uri.startswith('postgres://'):
            uri = uri.replace('postgres://', 'postgresql://', 1)
        return uri

    SQLALCHEMY_DATABASE_URI = property(lambda self: ProductionConfig.get_database_uri())

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Fix DATABASE_URL for Render/Heroku compatibility
        db_uri = cls.get_database_uri()
        if db_uri:
            app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        # Production-specific initialization
        assert db_uri, 'DATABASE_URL must be set'
        assert cls.SECRET_KEY != 'dev-secret-key', 'SECRET_KEY must be changed'
        assert cls.JWT_SECRET_KEY != 'dev-jwt-secret-key', 'JWT_SECRET_KEY must be changed'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
