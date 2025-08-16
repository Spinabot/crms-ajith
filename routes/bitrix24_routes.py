# routes/bitrix24_routes.py
from controllers.bitrix24_controller import bitrix_bp

def register_bitrix24_routes(app):
    app.register_blueprint(bitrix_bp) 