import requests
import time
import logging
from flask import g
from app import db
from app.models import ZohoCreds
from app.config import Config
from app.services.vault_service import VaultService

logger = logging.getLogger(__name__)

def get_zoho_secrets():
    """Fetch Zoho client ID and secret from Vault, fallback to Config."""
    if hasattr(g, 'zoho_secrets'):
        return g.zoho_secrets

    client_id = None
    client_secret = None
    try:
        vault_service = VaultService()
        secrets = vault_service.get_all_crm_secrets()
        client_id = secrets.get('ZOHO_CLIENT_ID')
        client_secret = secrets.get('ZOHO_CLIENT_SECRET')
    except Exception as e:
        logger.warning(f"Could not fetch Zoho secrets from Vault: {e}. Falling back to config.")
        client_id = Config.ZOHO_CLIENT_ID
        client_secret = Config.ZOHO_CLIENT_SECRET

    if not client_id or not client_secret:
        raise RuntimeError("ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET must be set in Vault or environment")

    g.zoho_secrets = (client_id, client_secret)
    return client_id, client_secret

def refresh_zoho_token(entity_id, refresh_token):
    """
    Refresh Zoho access token using refresh token.

    Args:
        entity_id (int): The entity ID
        refresh_token (str): The refresh token

    Returns:
        dict: Success/error response
    """
    if not entity_id or not refresh_token:
        return {"error": "Entity ID and refresh token are required"}

    try:
        # Get Zoho secrets from Vault
        client_id, client_secret = get_zoho_secrets()

        # Build refresh token URL
        url = (
            f"{Config.ZOHO_ACCOUNTS_URL}/oauth/v2/token"
            f"?refresh_token={refresh_token}"
            f"&client_id={client_id}"
            f"&client_secret={client_secret}"
            "&grant_type=refresh_token"
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        logger.info(f"Refreshing token for entity {entity_id}")

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            expires_in = data.get("expires_in")

            if not access_token or not expires_in:
                return {"error": "Invalid token response from Zoho"}

            # Calculate new expiration time
            current_time = int(time.time())
            expiration_time = current_time + expires_in

            # Update credentials in database
            try:
                creds = ZohoCreds.query.filter_by(entity_id=entity_id).first()
                if creds:
                    creds.access_token = access_token
                    creds.expiration_time = expiration_time
                    db.session.commit()

                    logger.info(f"Successfully refreshed token for entity {entity_id}")
                    return {
                        "status": "success",
                        "access_token": access_token,
                        "expires_in": expires_in
                    }
                else:
                    return {"error": "Entity credentials not found"}

            except Exception as db_error:
                logger.error(f"Database error updating refreshed token: {db_error}")
                db.session.rollback()
                return {"error": "Failed to update token in database"}

        else:
            logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
            return {"error": f"Token refresh failed: {response.text}"}

    except requests.RequestException as e:
        logger.error(f"Request error during token refresh: {e}")
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        return {"error": "Internal error during token refresh"}

def get_zoho_credentials(entity_id):
    """
    Get Zoho credentials for an entity, refreshing if necessary.

    Args:
        entity_id (int): The entity ID

    Returns:
        dict: Credentials or error response
    """
    try:
        creds = ZohoCreds.query.filter_by(entity_id=entity_id).first()

        if not creds:
            return {"error": "Entity not authenticated with Zoho"}

        # Check if token is expired
        if not creds.has_valid_token():
            logger.info(f"Token expired for entity {entity_id}, refreshing...")
            refresh_result = refresh_zoho_token(entity_id, creds.refresh_token)

            if refresh_result.get("error"):
                return refresh_result

            # Get updated credentials after refresh
            creds = ZohoCreds.query.filter_by(entity_id=entity_id).first()

            # Check if creds still exists after refresh
            if not creds:
                return {"error": "Entity credentials not found after token refresh"}

        return {
            "access_token": creds.access_token,
            "refresh_token": creds.refresh_token,
            "expiration_time": creds.expiration_time
        }

    except Exception as e:
        logger.error(f"Error getting Zoho credentials: {e}")
        return {"error": "Failed to get credentials"}

def make_zoho_api_request(entity_id, endpoint, method="GET", data=None, params=None):
    """
    Make an authenticated request to Zoho API.

    Args:
        entity_id (int): The entity ID
        endpoint (str): API endpoint (without base URL)
        method (str): HTTP method
        data (dict): Request data
        params (dict): Query parameters

    Returns:
        dict: API response or error
    """
    try:
        # Get valid credentials
        creds = get_zoho_credentials(entity_id)
        if creds.get("error"):
            return creds

        # Build request
        url = f"{Config.ZOHO_API_DOMAIN}/crm/v2/{endpoint}"
        headers = {
            "Authorization": f"Zoho-oauthtoken {creds['access_token']}",
            "Content-Type": "application/json"
        }

        logger.info(f"Making {method} request to Zoho API: {endpoint}")

        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Zoho API request failed: {response.status_code} - {response.text}")
            return {"error": f"API request failed: {response.text}"}

    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Internal error"}