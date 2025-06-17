from functools import wraps
from flask import request, jsonify
from app.config import Config

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        
        if not api_key and request.is_json:
            api_key = request.get_json().get('secretKey')
            
        if not api_key:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'API key is required. Provide it in x-api-key header or secretKey in JSON body'
            }), 401
            
        if api_key != Config.API_KEY:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid API key'
            }), 401
            
        return f(*args, **kwargs)
    return decorated_function 