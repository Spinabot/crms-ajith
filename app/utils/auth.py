from functools import wraps
from flask import request, jsonify

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
        # This part of the code is no longer relevant as CRMConnection model is removed.
        # Keeping it for now as per instructions to only remove imports and code referencing CRMConnection.
        # If the user wants to remove this entire block, a new edit would be needed.
        # For now, it will return a placeholder error.
        return {'error': 'API key authentication not fully implemented', 'message': 'CRMConnection model removed'}, 501

    return decorated_function

def require_crm_connection(crm_system):
    """Decorator to require specific CRM connection"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This part of the code is no longer relevant as CRMConnection model is removed.
            # Keeping it for now as per instructions to only remove imports and code referencing CRMConnection.
            # If the user wants to remove this entire block, a new edit would be needed.
            # For now, it will return a placeholder error.
            return {'error': 'CRM connection not fully implemented', 'message': 'CRMConnection model removed'}, 501
        return decorated_function
    return decorator