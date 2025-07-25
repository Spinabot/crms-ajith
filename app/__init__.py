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

    # Import and register Flask-RESTX API and all namespaces
    from app.swagger import api
    # Import all controllers that add namespaces to ensure registration
    from app.controllers import jobnimbus_controller, jobber_controller, hubspot_controller, builder_prime_controller, zoho_controller, client_controller
    api.init_app(app)

    # Only register blueprints if they have non-RESTX routes
    from app.controllers.jobber_auth_controller import jobber_auth_bp
    from app.controllers.zoho_controller import zoho_bp
    app.register_blueprint(jobber_auth_bp)
    app.register_blueprint(zoho_bp)
    # Removed jobnimbus_bp registration (RESTX only)

    return app