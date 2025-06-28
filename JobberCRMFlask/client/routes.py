import requests
import logging
import redis
from flask import Blueprint, request, jsonify
from functools import wraps
from flasgger import swag_from

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
@swag_from({
    'tags': ['Client Management'],
    'summary': 'Create a new client in Jobber',
    'description': 'Creates a new client in the Jobber CRM system using GraphQL mutation.',
    'parameters': [
        {
            'name': 'userid',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Title (e.g., Mr, Ms, Dr, etc.)'},
                    'firstName': {'type': 'string', 'description': 'Client first name'},
                    'lastName': {'type': 'string', 'description': 'Client last name'},
                    'companyName': {'type': 'string', 'description': 'Company name'},
                    'emails': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'address': {'type': 'string', 'description': 'Email address'},
                                'primary': {'type': 'boolean', 'description': 'Whether this is the primary email'}
                            }
                        },
                        'description': 'List of email addresses'
                    },
                    'phones': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'number': {'type': 'string', 'description': 'Phone number'},
                                'primary': {'type': 'boolean', 'description': 'Whether this is the primary phone'}
                            }
                        },
                        'description': 'List of phone numbers'
                    },
                    'billingAddress': {
                        'type': 'object',
                        'properties': {
                            'street1': {'type': 'string', 'description': 'Primary street address'},
                            'street2': {'type': 'string', 'description': 'Secondary street address'},
                            'city': {'type': 'string', 'description': 'City'},
                            'province': {'type': 'string', 'description': 'State/Province'},
                            'country': {'type': 'string', 'description': 'Country'},
                            'postalCode': {'type': 'string', 'description': 'Postal/ZIP code'}
                        },
                        'description': 'Billing address information'
                    }
                },
                'example': {
                    'title': 'Mr',
                    'firstName': 'John',
                    'lastName': 'Doe',
                    'companyName': 'Acme Corp',
                    'emails': [
                        {
                            'address': 'john.doe@acme.com',
                            'primary': True
                        }
                    ],
                    'phones': [
                        {
                            'number': '+1234567890',
                            'primary': True
                        }
                    ],
                    'billingAddress': {
                        'street1': '123 Main St',
                        'street2': 'Suite 100',
                        'city': 'Metropolis',
                        'province': 'NY',
                        'country': 'USA',
                        'postalCode': '12345'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Client created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {'type': 'object'}
                }
            }
        },
        400: {
            'description': 'Bad request - validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
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
            'description': 'Internal server error or Jobber API error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def create_client(userid):
    """Create a new client in Jobber (converted from FastAPI implementation)."""
    try:
        logger.info(f"Starting client creation for user {userid}")

        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=int(Config.REDIS_PORT),
            decode_responses=True
        )

        try:
            tokens = get_token(userid, redis_client)
            logger.info(f"Token result type: {type(tokens)}, value: {tokens}")
        except Exception as e:
            logger.error(f"Error fetching tokens: {str(e)}")
            return jsonify({"error": f"Error fetching tokens: {str(e)}"}), 500

        if tokens is None:
            logger.warning(f"No tokens available for user {userid}")
            return jsonify({"error": "No token available, please authorize first"}), 401

        if not isinstance(tokens, list):
            logger.error(f"Unexpected token format received: {type(tokens)} - {tokens}")
            return jsonify({"error": "Unexpected token format received"}), 500

        if len(tokens) == 0:
            logger.error(f"Empty token list for user {userid}")
            return jsonify({"error": "No valid tokens found"}), 401

        if not isinstance(tokens[0], dict) or 'access_token' not in tokens[0]:
            logger.error(f"Invalid token format: {tokens[0]}")
            return jsonify({"error": "Invalid token format"}), 500

        try:
            request_data = request.get_json()
            if not request_data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Only keep the allowed fields from the request
            allowed_fields = ['title', 'firstName', 'lastName', 'companyName', 'emails', 'phones', 'billingAddress']
            filtered_data = {field: request_data.get(field) for field in allowed_fields if field in request_data}

            validated_data = validate_client_create_data(filtered_data)
            logger.info(f"Validated data: {validated_data}")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400

        headers = {
            "Authorization": f"Bearer {tokens[0]['access_token']}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
        }

        variables = {}
        for field, value in validated_data.items():
            if value is not None:
                variables[field] = value

        jobber_url = getattr(Config, 'jobber_api_url', 'https://api.getjobber.com/api/graphql')

        logger.info(f"Creating client for user {userid} with variables: {variables}")

        payload = {
            "query": create_client_mutation,
            "variables": {"input": variables}
        }

        logger.info(f"Sending GraphQL payload: {payload}")
        logger.info(f"GraphQL mutation: {create_client_mutation}")

        response = requests.post(jobber_url, json=payload, headers=headers)
        response_data = response.json()

        logger.info(f"Jobber API response status: {response.status_code}")
        logger.info(f"Jobber API response: {response_data}")

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
@swag_from({
    'tags': ['Client Management'],
    'summary': 'Update an existing client in Jobber',
    'description': 'Updates an existing client in the Jobber CRM system using GraphQL mutation.',
    'parameters': [
        {
            'name': 'userid',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clientId': {'type': 'string', 'required': True, 'description': 'Jobber client ID'},
                    'firstName': {'type': 'string', 'description': 'Client first name'},
                    'lastName': {'type': 'string', 'description': 'Client last name'},
                    'companyName': {'type': 'string', 'description': 'Company name'},
                    'emailsToAdd': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'address': {'type': 'string', 'description': 'Email address'},
                                'primary': {'type': 'boolean', 'description': 'Whether this is the primary email'}
                            }
                        },
                        'description': 'New email addresses to add'
                    },
                    'phonesToAdd': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'number': {'type': 'string', 'description': 'Phone number'},
                                'primary': {'type': 'boolean', 'description': 'Whether this is the primary phone'}
                            }
                        },
                        'description': 'New phone numbers to add'
                    },
                    'propertyAddressesToAdd': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'street1': {'type': 'string', 'description': 'Primary street address'},
                                'street2': {'type': 'string', 'description': 'Secondary street address'},
                                'city': {'type': 'string', 'description': 'City'},
                                'province': {'type': 'string', 'description': 'State/Province'},
                                'country': {'type': 'string', 'description': 'Country'},
                                'postalCode': {'type': 'string', 'description': 'Postal/ZIP code'}
                            }
                        },
                        'description': 'New property addresses to add'
                    },
                    'phonesToDelete': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Phone IDs to delete'
                    },
                    'emailsToDelete': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Email IDs to delete'
                    },
                    'propertyAddressesToDelete': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Property address IDs to delete'
                    }
                },
                'example': {
                    'clientId': 'Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyOTY3NDk=',
                    'firstName': 'Jane',
                    'lastName': 'Smith',
                    'companyName': 'FutureTech',
                    'emailsToAdd': [
                        {
                            'address': 'jane.smith@futuretech.com',
                            'primary': True
                        }
                    ],
                    'phonesToAdd': [
                        {
                            'number': '+1555123456',
                            'primary': True
                        }
                    ],
                    'propertyAddressesToAdd': [
                        {
                            'street1': '456 Elm St',
                            'street2': 'Apt 2B',
                            'city': 'Gotham',
                            'province': 'NJ',
                            'country': 'United States',
                            'postalCode': '54321'
                        }
                    ],
                    'phonesToDelete': ['phoneId1'],
                    'emailsToDelete': ['emailId1'],
                    'propertyAddressesToDelete': ['addressId1']
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Client updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {'type': 'object'}
                }
            }
        },
        400: {
            'description': 'Bad request - validation error or user errors',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'userErrors': {'type': 'array'}
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
            'description': 'Internal server error or Jobber API error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def update_client(userid):
    """Update an existing client in Jobber (customized for property address and add/delete logic)."""
    try:
        logger.info(f"Starting client update for user {userid}")

        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=int(Config.REDIS_PORT),
            decode_responses=True
        )

        try:
            tokens = get_token(userid, redis_client)
            logger.info(f"Token result type: {type(tokens)}, value: {tokens}")
        except Exception as e:
            logger.error(f"Error fetching tokens: {str(e)}")
            return jsonify({"error": f"Error fetching tokens: {str(e)}"}), 500

        if tokens is None:
            logger.warning(f"No tokens available for user {userid}")
            return jsonify({"error": "No token available, please authorize first"}), 401

        if not isinstance(tokens, list):
            logger.error(f"Unexpected token format received: {type(tokens)} - {tokens}")
            return jsonify({"error": "Unexpected token format received"}), 500

        if len(tokens) == 0:
            logger.error(f"Empty token list for user {userid}")
            return jsonify({"error": "No valid tokens found"}), 401

        if not isinstance(tokens[0], dict) or 'access_token' not in tokens[0]:
            logger.error(f"Invalid token format: {tokens[0]}")
            return jsonify({"error": "Invalid token format"}), 500

        try:
            request_data = request.get_json()
            if not request_data:
                return jsonify({"error": "No JSON data provided"}), 400

            allowed_fields = [
                'clientId', 'firstName', 'lastName', 'companyName',
                'emailsToAdd', 'phonesToAdd', 'propertyAddressesToAdd',
                'phonesToDelete', 'emailsToDelete', 'propertyAddressesToDelete'
            ]
            filtered_data = {field: request_data.get(field) for field in allowed_fields if field in request_data}

            validated_data = validate_update_client_data(filtered_data)
            logger.info(f"Validated data: {validated_data}")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400

        # Here, you would fetch the current client data from Jobber to check counts before allowing deletes
        # For now, we assume you have a function get_current_client_data(clientId, tokens) that returns the current state
        # Example:
        # current_client = get_current_client_data(validated_data['clientId'], tokens)
        # if 'phonesToDelete' in validated_data and current_client:
        #     if len(current_client['phones']) - len(validated_data['phonesToDelete']) < 1:
        #         return jsonify({"error": "Cannot delete the last phone number."}), 400
        # Repeat for emails and propertyAddresses

        headers = {
            "Authorization": f"Bearer {tokens[0]['access_token']}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
        }

        variables = {"clientId": validated_data["clientId"]}
        for field, value in validated_data.items():
            if field != "clientId" and value is not None:
                variables[field] = value

        jobber_url = getattr(Config, 'jobber_api_url', 'https://api.getjobber.com/api/graphql')

        logger.info(f"Updating client for user {userid} with variables: {variables}")

        payload = {
            "query": update_client_mutation,
            "variables": variables
        }

        response = requests.post(jobber_url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code != 200:
            logger.error(f"Jobber API request failed: {response.status_code} - {response_data}")
            return jsonify({"error": "Jobber API request failed"}), 500

        if "errors" in response_data:
            logger.error(f"GraphQL errors: {response_data['errors']}")
            return jsonify({"error": "GraphQL errors", "details": response_data["errors"]}), 500

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
@swag_from({
    'tags': ['Client Management'],
    'summary': 'Archive an existing client in Jobber',
    'description': 'Archives (soft deletes) an existing client in the Jobber CRM system using GraphQL mutation.',
    'parameters': [
        {
            'name': 'userid',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clientId': {'type': 'string', 'required': True, 'description': 'Jobber client ID to archive'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Client archived successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'object',
                        'properties': {
                            'clientArchive': {
                                'type': 'object',
                                'properties': {
                                    'client': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'string'},
                                            'firstName': {'type': 'string'},
                                            'lastName': {'type': 'string'},
                                            'companyName': {'type': 'string'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - validation error or user errors',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'userErrors': {'type': 'array'}
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
            'description': 'Internal server error or Jobber API error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
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