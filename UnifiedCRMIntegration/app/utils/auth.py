from functools import wraps
from flask import request, jsonify
from app.models import CRMConnection

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key and request.is_json:
            api_key = request.get_json().get('secretKey')

        if not api_key:
            return {'error': 'Unauthorized', 'message': 'Missing API key'}, 401

        # Check if any CRM connection has this API key
        connection = CRMConnection.query.filter_by(
            api_key=api_key,
            is_active=True
        ).first()

        if not connection:
            return {'error': 'Unauthorized', 'message': 'Invalid API key'}, 401

        return f(*args, **kwargs)
    return decorated_function

def require_crm_connection(crm_system):
    """Decorator to require specific CRM connection"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            connection = CRMConnection.query.filter_by(
                crm_system=crm_system,
                is_active=True
            ).first()

            if not connection:
                return {
                    'error': 'Service Unavailable',
                    'message': f'{crm_system} CRM not configured'
                }, 503

            return f(*args, **kwargs)
        return decorated_function
    return decorator