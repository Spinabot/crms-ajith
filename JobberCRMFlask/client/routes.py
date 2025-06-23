import requests
import logging
import redis
from flask import Blueprint, request, jsonify
from functools import wraps

from config import Config
from queries.create_client_query import create_client_mutation
from queries.update_client_query import update_client_mutation
from queries.archive_client_query import archive_client_mutation
from schemas.schemas import validate_client_create_data, validate_update_client_data, validate_archive_client_data
from utils.token_handler import get_token

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for client routes
client_bp = Blueprint('client', __name__, url_prefix='/client')

# Rate limiting decorator
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

@client_bp.route('/create/<int:userid>', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def create_client(userid):
    """Create a new client in Jobber (converted from FastAPI implementation)."""
    try:
        logger.info(f"Starting client creation for user {userid}")

        # Get Redis client for token caching
        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=int(Config.REDIS_PORT),
            decode_responses=True
        )

        # Get token data for the user
        try:
            tokens = get_token(userid, redis_client)
            logger.info(f"Token result type: {type(tokens)}, value: {tokens}")

        except Exception as e:
            logger.error(f"Error fetching tokens: {str(e)}")
            return jsonify({"error": f"Error fetching tokens: {str(e)}"}), 500

        # Check if tokens are available
        if tokens is None:  # No tokens available (expired or not found)
            logger.warning(f"No tokens available for user {userid}")
            return jsonify({"error": "No token available, please authorize first"}), 401

        # Check if tokens is a list (matching FastAPI implementation)
        if not isinstance(tokens, list):
            logger.error(f"Unexpected token format received: {type(tokens)} - {tokens}")
            return jsonify({"error": "Unexpected token format received"}), 500

        # Verify token structure
        if len(tokens) == 0:
            logger.error(f"Empty token list for user {userid}")
            return jsonify({"error": "No valid tokens found"}), 401

        if not isinstance(tokens[0], dict) or 'access_token' not in tokens[0]:
            logger.error(f"Invalid token format: {tokens[0]}")
            return jsonify({"error": "Invalid token format"}), 500

        # Validate request data
        try:
            request_data = request.get_json()
            if not request_data:
                return jsonify({"error": "No JSON data provided"}), 400

            validated_data = validate_client_create_data(request_data)
            logger.info(f"Validated data: {validated_data}")

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400

        # Prepare headers for Jobber API request
        headers = {
            "Authorization": f"Bearer {tokens[0]['access_token']}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
        }

        # Prepare variables for GraphQL mutation
        variables = {}
        for field, value in validated_data.items():
            if value is not None:
                variables[field] = value

        # Make request to Jobber API
        jobber_url = getattr(Config, 'jobber_api_url', 'https://api.getjobber.com/api/graphql')

        logger.info(f"Creating client for user {userid} with variables: {variables}")

        payload = {
            "query": create_client_mutation,
            "variables": variables
        }

        response = requests.post(jobber_url, json=payload, headers=headers)
        response_data = response.json()

        # Check for errors
        if response.status_code != 200:
            logger.error(f"Jobber API request failed: {response.status_code} - {response_data}")
            return jsonify({"error": "Jobber API request failed"}), 500

        if "errors" in response_data:
            logger.error(f"GraphQL errors: {response_data['errors']}")
            return jsonify({"error": "GraphQL errors", "details": response_data["errors"]}), 500

        logger.info(f"Successfully created client for user {userid}")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Unexpected error creating client: {e}")
        return jsonify({"error": "Internal server error"}), 500

@client_bp.route('/update/<int:userid>', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def update_client(userid):
    """Update an existing client in Jobber (converted from FastAPI implementation)."""
    try:
        logger.info(f"Starting client update for user {userid}")

        # Get Redis client for token caching
        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=int(Config.REDIS_PORT),
            decode_responses=True
        )

        # Get token data for the user
        try:
            tokens = get_token(userid, redis_client)
            logger.info(f"Token result type: {type(tokens)}, value: {tokens}")

        except Exception as e:
            logger.error(f"Error fetching tokens: {str(e)}")
            return jsonify({"error": f"Error fetching tokens: {str(e)}"}), 500

        # Check if tokens are available
        if tokens is None:  # No tokens available (expired or not found)
            logger.warning(f"No tokens available for user {userid}")
            return jsonify({"error": "No token available, please authorize first"}), 401

        # Check if tokens is a list (matching FastAPI implementation)
        if not isinstance(tokens, list):
            logger.error(f"Unexpected token format received: {type(tokens)} - {tokens}")
            return jsonify({"error": "Unexpected token format received"}), 500

        # Verify token structure
        if len(tokens) == 0:
            logger.error(f"Empty token list for user {userid}")
            return jsonify({"error": "No valid tokens found"}), 401

        if not isinstance(tokens[0], dict) or 'access_token' not in tokens[0]:
            logger.error(f"Invalid token format: {tokens[0]}")
            return jsonify({"error": "Invalid token format"}), 500

        # Validate request data
        try:
            request_data = request.get_json()
            if not request_data:
                return jsonify({"error": "No JSON data provided"}), 400

            validated_data = validate_update_client_data(request_data)
            logger.info(f"Validated data: {validated_data}")

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400

        # Prepare headers for Jobber API request
        headers = {
            "Authorization": f"Bearer {tokens[0]['access_token']}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
        }

        # Prepare variables for GraphQL mutation
        variables = {"clientId": validated_data["clientId"]}
        for field, value in validated_data.items():
            if field != "clientId" and value is not None:
                variables[field] = value

        # Make request to Jobber API
        jobber_url = getattr(Config, 'jobber_api_url', 'https://api.getjobber.com/api/graphql')

        logger.info(f"Updating client for user {userid} with variables: {variables}")

        payload = {
            "query": update_client_mutation,
            "variables": variables
        }

        response = requests.post(jobber_url, json=payload, headers=headers)
        response_data = response.json()

        # Check for errors
        if response.status_code != 200:
            logger.error(f"Jobber API request failed: {response.status_code} - {response_data}")
            return jsonify({"error": "Jobber API request failed"}), 500

        if "errors" in response_data:
            logger.error(f"GraphQL errors: {response_data['errors']}")
            return jsonify({"error": "GraphQL errors", "details": response_data["errors"]}), 500

        # Check for user errors in the response
        if "data" in response_data and "clientEdit" in response_data["data"]:
            user_errors = response_data["data"]["clientEdit"].get("userErrors", [])
            if user_errors:
                logger.error(f"User errors in client update: {user_errors}")
                return jsonify({"error": "Client update failed", "userErrors": user_errors}), 400

        logger.info(f"Successfully updated client for user {userid}")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Unexpected error updating client: {e}")
        return jsonify({"error": "Internal server error"}), 500

@client_bp.route('/archive/<int:userid>', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def archive_client(userid):
    """Archive an existing client in Jobber (converted from FastAPI implementation)."""
    try:
        logger.info(f"Starting client archive for user {userid}")

        # Get Redis client for token caching
        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=int(Config.REDIS_PORT),
            decode_responses=True
        )

        # Get token data for the user
        try:
            tokens = get_token(userid, redis_client)
            logger.info(f"Token result type: {type(tokens)}, value: {tokens}")

        except Exception as e:
            logger.error(f"Error fetching tokens: {str(e)}")
            return jsonify({"error": f"Error fetching tokens: {str(e)}"}), 500

        # Check if tokens are available
        if tokens is None:  # No tokens available (expired or not found)
            logger.warning(f"No tokens available for user {userid}")
            return jsonify({"error": "No token available, please authorize first"}), 401

        # Check if tokens is a list (matching FastAPI implementation)
        if not isinstance(tokens, list):
            logger.error(f"Unexpected token format received: {type(tokens)} - {tokens}")
            return jsonify({"error": "Unexpected token format received"}), 500

        # Verify token structure
        if len(tokens) == 0:
            logger.error(f"Empty token list for user {userid}")
            return jsonify({"error": "No valid tokens found"}), 401

        if not isinstance(tokens[0], dict) or 'access_token' not in tokens[0]:
            logger.error(f"Invalid token format: {tokens[0]}")
            return jsonify({"error": "Invalid token format"}), 500

        # Validate request data
        try:
            request_data = request.get_json()
            if not request_data:
                return jsonify({"error": "No JSON data provided"}), 400

            validated_data = validate_archive_client_data(request_data)
            logger.info(f"Validated data: {validated_data}")

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400

        # Prepare headers for Jobber API request
        headers = {
            "Authorization": f"Bearer {tokens[0]['access_token']}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
        }

        # Prepare variables for GraphQL mutation
        variables = {"clientId": validated_data["clientId"]}

        # Make request to Jobber API
        jobber_url = getattr(Config, 'jobber_api_url', 'https://api.getjobber.com/api/graphql')

        logger.info(f"Archiving client for user {userid} with variables: {variables}")

        payload = {
            "query": archive_client_mutation,
            "variables": variables
        }

        response = requests.post(jobber_url, json=payload, headers=headers)
        response_data = response.json()

        # Check for errors
        if response.status_code != 200:
            logger.error(f"Jobber API request failed: {response.status_code} - {response_data}")
            return jsonify({"error": "Jobber API request failed"}), 500

        if "errors" in response_data:
            logger.error(f"GraphQL errors: {response_data['errors']}")
            return jsonify({"error": "GraphQL errors", "details": response_data["errors"]}), 500

        # Check for user errors in the response
        if "data" in response_data and "clientArchive" in response_data["data"]:
            user_errors = response_data["data"]["clientArchive"].get("userErrors", [])
            if user_errors:
                logger.error(f"User errors in client archive: {user_errors}")
                return jsonify({"error": "Client archive failed", "userErrors": user_errors}), 400

        logger.info(f"Successfully archived client for user {userid}")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Unexpected error archiving client: {e}")
        return jsonify({"error": "Internal server error"}), 500