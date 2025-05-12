"""
Configuration module defining base and environment-specific settings for the
application.
"""
import os

from app.constants import ENV_SECRET_KEY_VALUE, SECRET_KEY_DEF_VALUE, \
    UPLOADS_FOLDER_NAME


class Config:
    """
    Base configuration with default settings.

    Attributes:
        SECRET_KEY (str): Secret key for session management.
        UPLOAD_FOLDER (str): Path to the uploads directory.
    """
    SECRET_KEY = os.environ.get(ENV_SECRET_KEY_VALUE, SECRET_KEY_DEF_VALUE)
    UPLOAD_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), UPLOADS_FOLDER_NAME)


class DevelopmentConfig(Config):
    """
    Development configuration enabling debug mode.
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Production configuration with debug mode disabled.
    """
    DEBUG = False


class TestingConfig(Config):
    """
    Testing configuration enabling testing and debug modes.
    """
    TESTING = True
    DEBUG = True
