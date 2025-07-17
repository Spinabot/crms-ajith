import os
import requests
import logging
from flask import current_app, g
from app.config import Config
from config.vault_config import get_secret

# Configure logging
logger = logging.getLogger(__name__)

def get_jobnimbus_secrets():
    """Fetch JobNimbus API key from Vault, fallback to Config."""
    if hasattr(g, 'jobnimbus_secrets'):
        return g.jobnimbus_secrets

    api_key = None
    try:
        api_key = get_secret('JOBNIMBUS_API_KEY')
    except Exception as e:
        logger.warning(f"Could not fetch JobNimbus secrets from Vault: {e}. Falling back to config.")
        api_key = Config.JOBNIMBUS_API_KEY

    if not api_key:
        raise RuntimeError("JOBNIMBUS_API_KEY must be set in Vault or environment")

    g.jobnimbus_secrets = api_key
    return api_key

def jobnimbus_headers():
    api_key = get_jobnimbus_secrets()
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def jobnimbus_request(method, endpoint, **kwargs):
    url = f"https://app.jobnimbus.com/api1{endpoint}"
    try:
        response = requests.request(method, url, headers=jobnimbus_headers(), **kwargs)
        try:
            data = response.json()
        except ValueError:
            return {
                "error": "JobNimbus returned non-JSON response",
                "status_code": response.status_code,
                "text": response.text,
            }, response.status_code
        return data, response.status_code
    except Exception as e:
        return {"error": "Failed to contact JobNimbus", "details": str(e)}, 500