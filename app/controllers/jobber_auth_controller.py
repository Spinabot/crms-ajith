import datetime
import jwt
import requests
import logging
from flask import Blueprint, request, redirect, jsonify, current_app, g
from app import db
from app.models.jobber import JobberAuth
from app.config import Config
from config.vault_config import get_secret

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for Jobber auth routes
jobber_auth_bp = Blueprint('jobber_auth', __name__, url_prefix='/auth/jobber')

# Global variable for redirect URI
REDIRECT_URI = None

def get_jobber_secrets():
    """Fetch Jobber client ID and secret from Vault, fallback to Config."""
    if hasattr(g, 'jobber_secrets'):
        return g.jobber_secrets
    client_id = None
    client_secret = None
    try:
        client_id = get_secret('JOBBER_CLIENT_ID')
        client_secret = get_secret('JOBBER_CLIENT_SECRET')
    except Exception as e:
        logger.warning(f"Could not fetch Jobber secrets from Vault: {e}. Falling back to config.")
        client_id = Config.JOBBER_CLIENT_ID
        client_secret = Config.JOBBER_CLIENT_SECRET
    if not client_id or not client_secret:
        raise RuntimeError("JOBBER_CLIENT_ID and JOBBER_CLIENT_SECRET must be set in Vault or environment")
    g.jobber_secrets = (client_id, client_secret)
    return client_id, client_secret

@jobber_auth_bp.route('/authorize')
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

        # Build redirect URI
        host = request.host.split(':')[0] if ':' in request.host else request.host
        port = request.host.split(':')[1] if ':' in request.host else '5000'
        REDIRECT_URI = f"http://{host}:{port}/auth/jobber/callback"

        # Build authorization URL
        client_id, _ = get_jobber_secrets()
        auth_url = (
            f"https://api.getjobber.com/api/oauth/authorize"
            f"?response_type=code&client_id={client_id}&redirect_uri={REDIRECT_URI}&state={userid_int}"
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
        client_id, client_secret = get_jobber_secrets()
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
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

            # Store in database using SQLAlchemy
            try:
                # Check if user already exists
                existing_auth = JobberAuth.query.filter_by(user_id=user_id).first()

                if existing_auth:
                    # Update existing record
                    existing_auth.access_token = access_token
                    existing_auth.refresh_token = refresh_token
                    existing_auth.expiration_time = expiration_time
                    existing_auth.updated_at = datetime.datetime.utcnow()
                else:
                    # Create new record
                    new_auth = JobberAuth(
                        user_id=user_id,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expiration_time=expiration_time
                    )
                    db.session.add(new_auth)

                db.session.commit()
                logger.info(f"Successfully stored Jobber auth for user {user_id}")

            except Exception as db_error:
                logger.error(f"Database error storing Jobber auth: {db_error}")
                db.session.rollback()
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
        auth_record = JobberAuth.query.filter_by(user_id=user_id).first()

        if not auth_record:
            return jsonify({
                "status": "not_authenticated",
                "message": "User not authenticated with Jobber"
            }), 404

        return jsonify({
            "status": "authenticated" if auth_record.has_valid_token() else "expired",
            "hasValidToken": auth_record.has_valid_token(),
            "createdAt": auth_record.created_at.isoformat() if auth_record.created_at else None,
            "updatedAt": auth_record.updated_at.isoformat() if auth_record.updated_at else None
        })

    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        return jsonify({"error": "Failed to get authentication status"}), 500

@jobber_auth_bp.route('/refresh/<user_id>')
def refresh_token(user_id):
    """Refresh the access token for a user."""
    try:
        auth_record = JobberAuth.query.filter_by(user_id=user_id).first()

        if not auth_record:
            return jsonify({"error": "User not found"}), 404

        # Prepare refresh token request
        client_id, client_secret = get_jobber_secrets()
        refresh_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": auth_record.refresh_token,
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

            # Update database
            auth_record.access_token = new_access_token
            auth_record.refresh_token = new_refresh_token
            auth_record.expiration_time = expiration_time
            auth_record.updated_at = datetime.datetime.utcnow()

            db.session.commit()

            logger.info(f"Successfully refreshed token for user {user_id}")
            return jsonify({
                "status": "success",
                "message": "Token refreshed successfully"
            })

        else:
            logger.error(f"Token refresh failed: {response.status_code}")
            return jsonify({"error": "Token refresh failed"}), response.status_code

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({"error": "Failed to refresh token"}), 500