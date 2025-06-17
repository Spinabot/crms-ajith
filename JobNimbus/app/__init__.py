from flask import Flask

from app.config import Config
from app.database import db


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(Config)

    db.init_app(app)

    # Import and register your routes blueprint
    from .routes import main
    from .swagger import swagger_bp

    app.register_blueprint(main)
    app.register_blueprint(swagger_bp)

    return app
