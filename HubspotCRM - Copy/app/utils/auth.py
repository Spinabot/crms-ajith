from functools import wraps
from flask import request, current_app
from app.config import Config

def require_hubspot_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('X-HubSpot-Token')
        
        if not auth_header:
            return {'error': 'No API token provided'}, 401
            
        if auth_header != Config.HUBSPOT_API_TOKEN:
            return {'error': 'Invalid API token'}, 403
            
        return f(*args, **kwargs)
    return decorated 