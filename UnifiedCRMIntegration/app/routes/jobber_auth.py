import datetime
import jwt
import requests
import redis
import logging
from flask import Blueprint, request, redirect, jsonify, current_app
from functools import wraps
from app import db
from app.models import JobberAuth
from app.config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for Jobber auth routes
jobber_auth_bp = Blueprint('jobber_auth', __name__, url_prefix='/auth/jobber')

# Global variable for redirect URI
REDIRECT_URI = None

# Validate required configuration
if not Config.JOBBER_CLIENT_ID or not Config.JOBBER_CLIENT_SECRET:
    raise RuntimeError("JOBBER_CLIENT_ID and JOBBER_CLIENT_SECRET must be set in the environment")

# Rate limiting decorator
def rate_limit(max_requests=5, window=60):
    """Simple rate limiting decorator using Redis."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                redis_client = redis.Redis(
                    host=Config.CACHE_REDIS_HOST,
                    port=int(Config.CACHE_REDIS_PORT),
                    decode_responses=True,
                    socket_connect_timeout=1,  # 1 second timeout
                    socket_timeout=1
                )
                # Test connection
                redis_client.ping()

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
                logger.warning(f"Redis not available for rate limiting: {e}")
                # If Redis is not available, allow the request without rate limiting
                return f(*args, **kwargs)
        return decorated_function
    return decorator

@jobber_auth_bp.route('/authorize')
@rate_limit(max_requests=5, window=60)
def authorize():
    """Authorize user with Jobber OAuth."""
    global REDIRECT_URI

    try:
        # Get userid from query parameters
        userid = request.args.get('userid')
        if not userid:
            return jsonify({"error": "userid parameter is required"}), 400

        # Convert userid to int
        try:
            userid_int = int(userid)
        except ValueError:
            return jsonify({"error": "userid must be an integer"}), 400

        # Clear outdated Redis data
        try:
            redis_client = redis.Redis(
                host=Config.CACHE_REDIS_HOST,
                port=int(Config.CACHE_REDIS_PORT),
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1
            )
            redis_client.ping()  # Test connection
            key = f"userid:{userid_int}#"
            redis_client.delete(key)  # remove outdated redis data
        except Exception as e:
            logger.warning(f"Redis not available for clearing data: {e}")

        # Build redirect URI
        host = request.host.split(':')[0] if ':' in request.host else request.host
        port = request.host.split(':')[1] if ':' in request.host else '5000'
        REDIRECT_URI = f"http://{host}:{port}/auth/jobber/callback"

        # Build authorization URL
        auth_url = (
            f"https://api.getjobber.com/api/oauth/authorize"
            f"?response_type=code&client_id={Config.JOBBER_CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={userid_int}"
        )

        logger.info(f"Redirecting user {userid_int} to Jobber authorization")
        return redirect(auth_url, code=302)

    except Exception as e:
        logger.error(f"Authorization error: {e}")
        return jsonify({"error": "Authorization failed"}), 500

@jobber_auth_bp.route('/callback')
def get_callback():
    """Handle OAuth callback from Jobber."""
    global REDIRECT_URI

    try:
        # Get code and state from query parameters
        code = request.args.get('code')
        state = request.args.get('state')

        if not code or not state:
            logger.error("Missing code or state in callback")
            return jsonify({"error": "Missing code or state in callback"}), 400

        user_id = state  # passing userid in state params

        # Prepare token request data
        token_data = {
            "client_id": Config.JOBBER_CLIENT_ID,
            "client_secret": Config.JOBBER_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }

        logger.info(f"Requesting token for user {user_id}")

        # Request access token
        response = requests.post(
            Config.JOBBER_TOKENS_URL,
            data=token_data
        )

        logger.info(f"Token response status: {response.status_code}")

        if response.status_code == 200:
            # Extract tokens from response
            response_data = response.json()
            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")

            # Decode JWT to get expiration time
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            expiration_time = decoded.get("exp")

            # Store in database using direct connection (like JobberCRMFlask)
            try:
                import psycopg2

                # Create database connection
                conn = psycopg2.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD
                )
                cursor = conn.cursor()

                # Insert or update the authorization data
                insert_query = """
                INSERT INTO jobber_auth (user_id, access_token, refresh_token, expiration_time)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    access_token = EXCLUDED.access_token,
                    refresh_token = EXCLUDED.refresh_token,
                    expiration_time = EXCLUDED.expiration_time,
                    updated_at = CURRENT_TIMESTAMP;
                """

                logger.info(f"Inserting/updating Jobber auth for user {user_id}")
                cursor.execute(insert_query, (user_id, access_token, refresh_token, expiration_time))
                conn.commit()

                logger.info(f"Successfully stored Jobber auth for user {user_id}")

                cursor.close()
                conn.close()

            except Exception as db_error:
                logger.error(f"Database error storing Jobber auth: {db_error}")
                if 'conn' in locals():
                    conn.rollback()
                    conn.close()
                return jsonify({"error": "Failed to store authentication data"}), 500

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

@jobber_auth_bp.route('/status/<user_id>')
def get_auth_status(user_id):
    """Get authentication status for a user."""
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor()

        # Get the most recent token for the user
        query = """
        SELECT access_token, refresh_token, expiration_time, created_at, updated_at
        FROM jobber_auth
        WHERE user_id = %s
        ORDER BY updated_at DESC
        LIMIT 1
        """

        cursor.execute(query, (str(user_id),))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({
                "status": "not_authenticated",
                "message": "User not authenticated with Jobber"
            }), 404

        access_token, refresh_token, expiration_time, created_at, updated_at = result

        # Check if token is expired (same logic as JobberCRMFlask)
        current_time = datetime.datetime.now().timestamp()
        has_valid_token = current_time < expiration_time

        cursor.close()
        conn.close()

        return jsonify({
            "status": "authenticated" if has_valid_token else "expired",
            "hasValidToken": has_valid_token,
            "createdAt": created_at.isoformat() if created_at else None,
            "updatedAt": updated_at.isoformat() if updated_at else None
        })

    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"error": "Failed to get authentication status"}), 500

@jobber_auth_bp.route('/refresh/<user_id>')
def refresh_token(user_id):
    """Refresh the access token for a user."""
    try:

        # Get current refresh token from database
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            cursor = conn.cursor()

            # Get current refresh token
            query = """
            SELECT refresh_token
            FROM jobber_auth
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """

            cursor.execute(query, (str(user_id),))
            result = cursor.fetchone()

            if not result:
                logger.error(f"No authentication record found for user {user_id}")
                cursor.close()
                conn.close()
                return jsonify({"error": "User not found"}), 404

            refresh_token = result[0]
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Database error getting refresh token: {e}")
            return jsonify({"error": "Database error"}), 500

        # Prepare refresh token request
        refresh_data = {
            "client_id": Config.JOBBER_CLIENT_ID,
            "client_secret": Config.JOBBER_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        logger.info(f"Refreshing token for user {user_id}")

        # Request new access token
        response = requests.post(
            Config.JOBBER_TOKENS_URL,
            data=refresh_data
        )

        if response.status_code == 200:
            response_data = response.json()
            new_access_token = response_data.get("access_token")
            new_refresh_token = response_data.get("refresh_token")

            # Decode JWT to get expiration time
            decoded = jwt.decode(new_access_token, options={"verify_signature": False})
            expiration_time = decoded.get("exp")

            # Update database using direct connection
            try:
                conn = psycopg2.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD
                )
                cursor = conn.cursor()

                update_query = """
                UPDATE jobber_auth
                SET access_token = %s, refresh_token = %s, expiration_time = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """

                cursor.execute(update_query, (
                    new_access_token,
                    new_refresh_token,
                    expiration_time,
                    str(user_id)
                ))
                conn.commit()

                logger.info(f"Successfully refreshed token for user {user_id}")
                cursor.close()
                conn.close()

                return jsonify({
                    "status": "success",
                    "message": "Token refreshed successfully"
                })

            except Exception as e:
                logger.error(f"Database error updating token: {e}")
                if 'conn' in locals():
                    conn.rollback()
                    conn.close()
                return jsonify({"error": "Database error"}), 500

        else:
            logger.error(f"Token refresh failed: {response.status_code}")
            return jsonify({"error": "Token refresh failed"}), response.status_code

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({"error": "Failed to refresh token"}), 500