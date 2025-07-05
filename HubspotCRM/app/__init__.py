from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'HubSpot CRM API is running'
        }), 200

    from app.swagger import swagger_bp
    app.register_blueprint(swagger_bp)

    return app
