import datetime
import os
import jwt
import requests
from flask import Blueprint, request, redirect, url_for, jsonify, current_app
from functools import wraps
import redis
import logging
from flasgger import swag_from

from config import Config
from utils.db_conn import insert_jobber

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Global variable for redirect URI (matching FastAPI implementation)
REDIRECT_URI = None

# Validate required configuration (matching FastAPI implementation)
if not Config.Remodel_ID or not Config.Remodel_SECRET:
    raise RuntimeError("Remodel_ID and Remodel_SECRET must be set in the environment")

# Rate limiting decorator (simplified version)
def rate_limit(max_requests=5, window=60):
    """Simple rate limiting decorator using Redis."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                redis_client = redis.Redis(
                    host=Config.REDIS_HOST,
                    port=int(Config.REDIS_PORT),
                    decode_responses=True
                )

                # Get client IP for rate limiting
                client_ip = request.remote_addr
                key = f"rate_limit:{client_ip}:{f.__name__}"

                # Check current requests
                current_requests = redis_client.get(key)
                if current_requests and int(current_requests) >= max_requests:
                    return jsonify({"error": "Rate limit exceeded"}), 429

                # Increment request count
                pipe = redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, window)
                pipe.execute()

                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                # If Redis is not available, allow the request
                return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/jobber')
@rate_limit(max_requests=5, window=60)
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Authorize user with Jobber OAuth',
    'description': 'Initiates OAuth flow with Jobber API. Redirects user to Jobber authorization page.',
    'parameters': [
        {
            'name': 'userid',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'User ID for the authorization'
        }
    ],
    'responses': {
        302: {
            'description': 'Redirect to Jobber authorization page'
        },
        400: {
            'description': 'Bad request - missing or invalid userid',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        429: {
            'description': 'Rate limit exceeded'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def authorize():
    """Authorize user with Jobber OAuth (matching FastAPI implementation)."""
    global REDIRECT_URI

    try:
        # Get userid from query parameters (matching FastAPI parameter handling)
        userid = request.args.get('userid')
        if not userid:
            return jsonify({"error": "userid parameter is required"}), 400

        # Convert userid to int to match FastAPI implementation
        try:
            userid_int = int(userid)
        except ValueError:
            return jsonify({"error": "userid must be an integer"}), 400

        # Clear outdated Redis data (matching FastAPI implementation)
        try:
            redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=int(Config.REDIS_PORT),
                decode_responses=True
            )
            key = f"userid:{userid_int}#"
            redis_client.delete(key)  # remove outdated redis data
        except Exception as e:
            logger.warning(f"Could not clear Redis data: {e}")

        # Build redirect URI (matching FastAPI implementation)
        host = request.host.split(':')[0] if ':' in request.host else request.host
        port = request.host.split(':')[1] if ':' in request.host else '5000'
        REDIRECT_URI = f"http://{host}:{port}/auth/callback"

        # Build authorization URL (matching FastAPI implementation exactly)
        auth_url = (
            f"https://api.getjobber.com/api/oauth/authorize"
            f"?response_type=code&client_id={Config.Remodel_ID}&redirect_uri={REDIRECT_URI}&state={userid_int}"
        )

        logger.info(f"Redirecting user {userid_int} to Jobber authorization")
        return redirect(auth_url, code=302)

    except Exception as e:
        logger.error(f"Authorization error: {e}")
        return jsonify({"error": "Authorization failed"}), 500

@auth_bp.route('/callback')
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Handle OAuth callback from Jobber',
    'description': 'Processes the OAuth callback from Jobber, exchanges authorization code for access tokens, and stores them in the database.',
    'parameters': [
        {
            'name': 'code',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Authorization code from Jobber'
        },
        {
            'name': 'state',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'State parameter containing user ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Authorization successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string', 'example': 'Authorization successful'}
                }
            }
        },
        400: {
            'description': 'Bad request - missing code or state, or invalid credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        401: {
            'description': 'Unauthorized - invalid credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        403: {
            'description': 'Forbidden - access denied',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_callback():
    """Handle OAuth callback from Jobber (matching FastAPI implementation)."""
    global REDIRECT_URI

    try:
        # Get code and state from query parameters (matching FastAPI implementation)
        code = request.args.get('code')
        state = request.args.get('state')

        if not code or not state:
            logger.error("Missing code or state in callback")
            return jsonify({"error": "Missing code or state in callback"}), 400

        user_id = state  # passing userid in state params (matching FastAPI)

        # Prepare token request data (matching FastAPI implementation exactly)
        token_data = {
            "client_id": Config.Remodel_ID,
            "client_secret": Config.Remodel_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }

        logger.info(f"Requesting token for user {user_id}")

        # Request access token (matching FastAPI implementation)
        response = requests.post(
            "https://api.getjobber.com/api/oauth/token",
            data=token_data
        )

        logger.info(f"Token response status: {response.status_code}")

        if response.status_code == 200:
            # Extract tokens from response (matching FastAPI implementation)
            response_data = response.json()
            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")

            # Decode JWT to get expiration time (matching FastAPI implementation)
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            expiration_time = decoded.get("exp")

            # Store in database (matching FastAPI implementation)
            insert_jobber(user_id, access_token, refresh_token, expiration_time)

            logger.info(f"Successfully authorized user {user_id}")
            return jsonify({
                "status": "success",
                "message": "Authorization successful"
            })

        elif response.status_code == 400:
            logger.error("Bad Request – check input fields")
            return jsonify({"error": "Bad Request – check input fields"}), 400

        elif response.status_code == 401:
            logger.error("Unauthorized – invalid credentials")
            return jsonify({"error": "Unauthorized – invalid credentials"}), 401

        elif response.status_code == 403:
            logger.error("Forbidden – access denied")
            return jsonify({"error": "Forbidden – access denied"}), 403

        else:
            logger.error(f"Unexpected error during OAuth flow: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return jsonify({"error": "Unexpected error during OAuth flow"}), 500

    except Exception as e:
        logger.error(f"Callback error: {e}")
        return jsonify({"error": "Callback processing failed"}), 500