import os
import time
import requests
from urllib.parse import urlencode
from models import db, CapsuleToken

# OAuth2 settings
CLIENT_ID = os.getenv("CAPSULE_CLIENT_ID")
CLIENT_SECRET = os.getenv("CAPSULE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5001/api/capsule/callback"
AUTH_URL = "https://api.capsulecrm.com/oauth/authorise"
TOKEN_URL = "https://api.capsulecrm.com/oauth/token"
API_BASE_URL = "https://api.capsulecrm.com/api/v2"


def get_authorization_url(state="secure_random_state"):
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "state": state,
        "scope": "read write"
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    token_data = response.json()

    # Store token in DB using SQLAlchemy
    token = CapsuleToken.query.first()
    if not token:
        token = CapsuleToken()
        db.session.add(token)
    
    token.access_token = token_data["access_token"]
    token.refresh_token = token_data.get("refresh_token")
    token.expires_at = int(time.time()) + token_data["expires_in"]
    
    db.session.commit()
    return token_data


def get_token_from_db():
    token = CapsuleToken.query.first()
    if token:
        return {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "expires_at": token.expires_at
        }
    return None


def refresh_access_token(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    token_data = response.json()

    # Update token in DB using SQLAlchemy
    token = CapsuleToken.query.first()
    if token:
        token.access_token = token_data["access_token"]
        token.refresh_token = token_data.get("refresh_token")
        token.expires_at = int(time.time()) + token_data["expires_in"]
        db.session.commit()
    
    return token_data


def get_valid_token():
    token_row = get_token_from_db()
    if not token_row:
        raise Exception("No Capsule token found")

    if int(time.time()) > token_row["expires_at"]:
        return refresh_access_token(token_row["refresh_token"])["access_token"]

    return token_row["access_token"]


def make_capsule_request(method, endpoint, data=None, params=None):
    token = get_valid_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{API_BASE_URL}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=data, params=params)
    response.raise_for_status()
    return response.json()


def get_capsule_organizations():
    """
    Fetch all organizations from Capsule CRM
    """
    return make_capsule_request("GET", "organizations")


def get_capsule_opportunities():
    """
    Fetch all opportunities from Capsule CRM
    """
    return make_capsule_request("GET", "opportunities")
