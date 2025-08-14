# routes/merge_routes.py
from controllers.merge_controller import merge_bp

def register_merge_routes(app):
    app.register_blueprint(merge_bp) 