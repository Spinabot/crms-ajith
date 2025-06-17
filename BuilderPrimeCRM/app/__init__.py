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

    from app.routes.leads import leads_bp
    from app.swagger import swagger_bp, api

    api.init_app(app)
    
    app.register_blueprint(swagger_bp)
    app.register_blueprint(leads_bp)

    return app
