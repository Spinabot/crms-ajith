import requests
import logging
import time
from flask import Blueprint, request, jsonify
from functools import wraps
import redis
from flasgger import swag_from

from config import Config
from queries.get_client_query import get_client_data
from utils.token_handler import get_token

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for data routes
data_bp = Blueprint('data', __name__, url_prefix='/data')

# Rate limiting decorator (matching the FastAPI implementation)
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

@data_bp.route('/jobber/<int:userid>', methods=['POST'])
@rate_limit(max_requests=5, window=60)
@swag_from({
    'tags': ['Data Retrieval'],
    'summary': 'Get client data from Jobber',
    'description': 'Retrieves all client data from Jobber CRM system using GraphQL queries with pagination support.',
    'parameters': [
        {
            'name': 'userid',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID for authentication'
        }
    ],
    'responses': {
        200: {
            'description': 'Client data retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                            'firstName': {'type': 'string'},
                            'lastName': {'type': 'string'},
                            'companyName': {'type': 'string'},
                            'emails': {'type': 'array'},
                            'phones': {'type': 'array'},
                            'billingAddress': {'type': 'object'}
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized - no token available',
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
            'description': 'Internal server error or GraphQL error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_data(userid):
    """Get client data from Jobber (converted from FastAPI implementation)."""
    try:
        logger.info(f"Starting data retrieval for user {userid}")

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

        # Prepare headers for Jobber API request
        headers = {
            "Authorization": f"Bearer {tokens[0]['access_token']}",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
        }

        # Make request to Jobber API
        jobber_url = getattr(Config, 'jobber_api_url', 'https://api.getjobber.com/api/graphql')

        logger.info(f"Fetching client data for user {userid}")

        # Initialize pagination variables
        hasNextPage = True
        end_cursor = None
        variables = {"cursor": end_cursor}
        data = []
        request_count = 0

        # Fetch data with pagination (matching FastAPI implementation)
        while hasNextPage:
            try:
                # Make GraphQL request
                payload = {
                    "query": get_client_data,
                    "variables": variables
                }

                logger.info(f"Making GraphQL request {request_count + 1} with cursor: {end_cursor}")
                response = requests.post(jobber_url, json=payload, headers=headers)
                response_data = response.json()

                # Check for errors
                if response.status_code != 200 or "errors" in response_data:
                    logger.error(f"GraphQL query failed: {response_data}")
                    return jsonify({"error": "GraphQL query failed"}), 500

                # Extract data from response
                data.append(response_data["data"]["clients"]["nodes"])
                page_info = response_data["data"]["clients"]["pageInfo"]
                hasNextPage = page_info["hasNextPage"]
                end_cursor = page_info["endCursor"]
                variables = {"cursor": end_cursor}
                request_count += 1

                logger.info(f"Page {request_count}: {len(response_data['data']['clients']['nodes'])} clients, hasNextPage: {hasNextPage}")

                # Sleep after every 5 requests to avoid rate limiting (matching FastAPI implementation)
                if request_count % 5 == 0:
                    logger.info(f"Sleeping for 3 seconds after {request_count} requests")
                    time.sleep(3)

            except Exception as e:
                logger.error(f"Error during pagination: {e}")
                return jsonify({"error": f"Error fetching data: {str(e)}"}), 500

        logger.info(f"Successfully fetched client data for user {userid} in {request_count} requests")
        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Unexpected error getting client data: {e}")
        return jsonify({"error": "Internal server error"}), 500