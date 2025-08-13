import os
import time
import secrets
import requests
import logging
from urllib.parse import urlencode
from dotenv import load_dotenv
from models import db, JobberToken

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jobber.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Jobber OAuth configuration ===
CLIENT_ID     = os.getenv("JOBBER_CLIENT_ID", "6c6a5fb3-9c6b-4887-80cb-c65f1cc2825a")
CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET", "dddff56b393da10a8519f36e4d7b13e273c83a80c1044f6d41e4d16aa92645b4")
REDIRECT_URI  = os.getenv("JOBBER_REDIRECT_URI", "http://localhost:5001/api/jobber/callback")

# IMPORTANT: both endpoints include /api/
AUTH_URL   = "https://api.getjobber.com/api/oauth/authorize"
TOKEN_URL  = "https://api.getjobber.com/api/oauth/token"

# GraphQL stays the same
GRAPHQL_URL = "https://api.getjobber.com/api/graphql"

# Store state tokens for CSRF protection (in production, use Redis or database)
oauth_states = {}

def generate_secure_state():
    """Generate a secure random state parameter for CSRF protection"""
    return secrets.token_urlsafe(32)

def store_oauth_state(state):
    """Store OAuth state for validation"""
    oauth_states[state] = time.time()
    # Clean up old states (older than 10 minutes)
    current_time = time.time()
    oauth_states = {k: v for k, v in oauth_states.items() if current_time - v < 600}

def validate_oauth_state(state):
    """Validate OAuth state parameter"""
    if state not in oauth_states:
        return False
    # Remove used state
    del oauth_states[state]
    return True

def get_authorization_url(state=None):
    """Generate OAuth authorization URL for Jobber with proper scopes"""
    if not state:
        state = generate_secure_state()
    
    # Store state for validation
    store_oauth_state(state)
    
    # According to Jobber docs, these are the available scopes
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "state": state,
        "scope": "read write"  # Jobber supports: read, write, admin
    }
    
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    logger.info(f"Generated OAuth authorization URL with state: {state[:8]}...")
    return auth_url

def exchange_code_for_token(code, state=None):
    """Exchange authorization code for access token with proper error handling"""
    logger.info("Exchanging authorization code for access token")
    
    # Validate state if provided
    if state and not validate_oauth_state(state):
        raise ValueError("Invalid or expired OAuth state parameter")
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    try:
        response = requests.post(TOKEN_URL, data=data, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        
        logger.info("Successfully received token response from Jobber")
        logger.debug(f"Token response keys: {list(token_data.keys())}")
        
        # Validate required fields
        if "access_token" not in token_data:
            raise ValueError("No access_token in response")
        
        # Store token in DB using SQLAlchemy
        token = JobberToken.query.first()
        if not token:
            token = JobberToken()
            db.session.add(token)
            logger.info("Creating new JobberToken record")
        else:
            logger.info("Updating existing JobberToken record")
        
        token.access_token = token_data["access_token"]
        token.refresh_token = token_data.get("refresh_token", "")
        
        # Calculate expiration time
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
        token.expires_at = int(time.time()) + expires_in
        
        db.session.commit()
        logger.info("Successfully stored Jobber access and refresh tokens")
        logger.info(f"Token expires in {expires_in} seconds")
        
        return token_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error during token exchange: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        raise ValueError(f"Failed to exchange code for token: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during token exchange: {e}")
        raise


def get_jobber_token():
    """Get Jobber token data from database"""
    token = JobberToken.query.first()
    if token:
        return {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "expires_at": token.expires_at
        }
    return None


def store_jobber_token(access_token, refresh_token, expires_in):
    """Store Jobber tokens in database"""
    expires_at = int(time.time()) + expires_in
    
    token = JobberToken.query.first()
    if not token:
        token = JobberToken()
        db.session.add(token)
    
    token.access_token = access_token
    token.refresh_token = refresh_token
    token.expires_at = expires_at
    
    db.session.commit()


def refresh_jobber_token(refresh_token):
    """Refresh Jobber access token using refresh token"""
    logger.info("Refreshing Jobber access token")
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(TOKEN_URL, data=data, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        
        logger.info("Successfully refreshed Jobber access token")
        
        # Update stored token
        token = JobberToken.query.first()
        if token:
            token.access_token = token_data["access_token"]
            if "refresh_token" in token_data:
                token.refresh_token = token_data["refresh_token"]
            
            expires_in = token_data.get("expires_in", 3600)
            token.expires_at = int(time.time()) + expires_in
            
            db.session.commit()
            logger.info("Updated Jobber tokens in database")
            
            return token_data["access_token"]
        else:
            logger.error("No Jobber token found in database for refresh")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error during token refresh: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        return None


def get_valid_token():
    """Get a valid Jobber access token, refreshing if necessary"""
    token = get_jobber_token()
    if not token:
        logger.warning("No Jobber token found in database")
        return None
    
    current_time = int(time.time())
    expires_in = token["expires_at"] - current_time
    
    # If token expires in less than 5 minutes, refresh it
    if expires_in < 300:
        if token.get("refresh_token"):
            logger.info("Token expires soon, refreshing...")
            new_token = refresh_jobber_token(token["refresh_token"])
            if new_token:
                return new_token
            else:
                logger.error("Failed to refresh token")
                return None
        else:
            logger.warning("Token expired and no refresh token available")
            return None
    
    logger.info(f"Using existing token, expires in {expires_in} seconds")
    return token["access_token"]


def get_headers():
    """Get headers with valid access token for Jobber API requests"""
    access_token = get_valid_token()
    if not access_token:
        raise ValueError("No valid access token available. Please authenticate with Jobber first.")
    
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


def _execute(query, variables=None, operation_name=None):
    """Execute GraphQL query with automatic token refresh"""
    logger.info(f"Executing GraphQL query: {operation_name or 'unnamed'}")
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    if operation_name:
        payload["operationName"] = operation_name

    response = requests.post(GRAPHQL_URL, json=payload, headers=get_headers())

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error(f"GraphQL request failed: {response.status_code} - {response.text}")
        logger.error(f"GraphQL Request Payload: {payload}")
        raise e

    data = response.json()
    if "errors" in data:
        error_msg = data["errors"][0].get("message")
        logger.error(f"GraphQL errors: {error_msg}")
        raise Exception(error_msg)
    
    logger.info(f"GraphQL query successful: {operation_name or 'unnamed'}")
    return data.get("data")


def fetch_clients(first: int = 50, after: str = None):
    """Fetch clients from Jobber with pagination"""
    query = """
    query GetClients($first: Int!, $after: String) {
      clients(first: $first, after: $after) {
        edges {
          node {
            id
            firstName
            lastName
            emails {
              primary
              address
            }
            companyName
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    
    variables = {"first": first}
    if after:
        variables["after"] = after
    
    result = _execute(query, variables)
    return result.get("clients", {})


# CREATE
def create_client(first_name: str, last_name: str, email: str, company_name: str = None):
    """Create a new client in Jobber with improved mutation"""
    logger.info(f"Creating new Jobber client: {first_name} {last_name} ({email})")
    mutation = """
    mutation CreateClient($input: ClientCreateInput!) {
      clientCreate(input: $input) {
        client {
          id
          firstName
          lastName
        }
        userErrors {
          message
          path
        }
      }
    }
    """
    
    input_obj = {
        "firstName": first_name,
        "lastName": last_name,
        "emails": [{"primary": True, "address": email}]
    }
    if company_name:
        input_obj["companyName"] = company_name

    result = _execute(mutation, variables={"input": input_obj}, operation_name="CreateClient")
    errors = result["clientCreate"].get("userErrors")
    if errors:
        error_msg = errors[0]["message"]
        logger.error(f"Failed to create Jobber client: {error_msg}")
        raise Exception(error_msg)
    
    client = result["clientCreate"]["client"]
    logger.info(f"Successfully created Jobber client: {client['id']}")
    return client


# READ (List)
def get_clients(first: int = 50, after: str = None):
    """Get clients from Jobber (alias for fetch_clients)"""
    return fetch_clients(first, after)


# READ (Single)
def get_client_by_id(client_id: str):
    """Get a specific client by ID from Jobber"""
    query = """
    query ($id: ID!) {
      client(id: $id) {
        id
        firstName
        lastName
        emails {
          primary
          address
        }
        companyName
      }
    }"""
    result = _execute(query, {"id": client_id})
    if not result or not result.get("client"):
        raise Exception("Client not found")
    return result["client"]


# UPDATE
def update_client(client_id: str, first_name: str = None, last_name: str = None, email: str = None, company_name: str = None):
    """Update a client in Jobber"""
    mutation = """
    mutation UpdateClient($input: ClientUpdateInput!) {
      clientUpdate(input: $input) {
        client {
          id
          firstName
          lastName
          emails {
            primary
            address
          }
          companyName
        }
        userErrors {
          message
          path
        }
      }
    }
    """
    
    input_obj = {"id": client_id}
    if first_name:
        input_obj["firstName"] = first_name
    if last_name:
        input_obj["lastName"] = last_name
    if email:
        input_obj["emails"] = [{"primary": True, "address": email}]
    if company_name:
        input_obj["companyName"] = company_name

    result = _execute(mutation, variables={"input": input_obj}, operation_name="UpdateClient")
    errors = result["clientUpdate"].get("userErrors")
    if errors:
        raise Exception(errors[0]["message"])
    return result["clientUpdate"]["client"]


# DELETE
def delete_client(client_id: str):
    """Delete a client from Jobber"""
    mutation = """
    mutation DeleteClient($input: ClientDeleteInput!) {
      clientDelete(input: $input) {
        deletedClientId
        userErrors {
          message
          path
        }
      }
    }
    """
    
    result = _execute(mutation, variables={"input": {"id": client_id}}, operation_name="DeleteClient")
    errors = result["clientDelete"].get("userErrors")
    if errors:
        raise Exception(errors[0]["message"])
    return {"id": result["clientDelete"]["deletedClientId"]}
