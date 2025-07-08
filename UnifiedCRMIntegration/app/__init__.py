from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route('/')
    def index():
        return redirect('/swagger')

    # Import and register Flask-RESTX API
    from app.swagger import api
    api.init_app(app)

    # Register blueprints
    from app.routes.jobber_auth import jobber_auth_bp
    from app.routes.zoho import zoho_bp
    from app.routes.jobnimbus import jobnimbus_bp
    app.register_blueprint(jobber_auth_bp)
    app.register_blueprint(zoho_bp)
    app.register_blueprint(jobnimbus_bp)

    return app