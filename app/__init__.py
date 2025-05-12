from flask import Flask
from .routes import main_bp


def create_app(config_object='app.config.DevelopmentConfig'):
    """
    Create and configure the Flask application using the application
    factory pattern.

    Args:
        config_object (str): The import path of the configuration class to load

    Returns:
        Flask: An instance of the configured Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.config.from_pyfile('config.py', silent=True)

    app.register_blueprint(main_bp)
    return app
