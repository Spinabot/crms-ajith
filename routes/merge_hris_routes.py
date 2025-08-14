# routes/merge_hris_routes.py
from controllers.merge_hris_controller import hris_bp

def register_merge_hris_routes(app):
    app.register_blueprint(hris_bp) 