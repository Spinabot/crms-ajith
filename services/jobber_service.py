import os
import time
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from models import db, JobberToken

load_dotenv()

# OAuth2 settings
CLIENT_ID = os.getenv("JOBBER_CLIENT_ID", "6c6a5fb3-9c6b-4887-80cb-c65f1cc2825a")
CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET", "dddff56b393da10a8519f36e4d7b13e273c83a80c1044f6d41e4d16aa92645b4")
REDIRECT_URI = "http://localhost:5001/api/jobber/callback"
AUTH_URL = "https://api.getjobber.com/oauth/authorize"
TOKEN_URL = "https://api.getjobber.com/oauth/token"
GRAPHQL_URL = "https://api.getjobber.com/api/graphql"


def get_authorization_url(state="secure_random_state"):
    """Generate OAuth authorization URL for Jobber"""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "state": state,
        "scope": "read write"
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
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
    token = JobberToken.query.first()
    if not token:
        token = JobberToken()
        db.session.add(token)
    
    token.access_token = token_data["access_token"]
    token.refresh_token = token_data.get("refresh_token")
    token.expires_at = int(time.time()) + token_data["expires_in"]
    
    db.session.commit()
    return token_data


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
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to refresh access token: {response.text}")

    token_data = response.json()
    store_jobber_token(
        token_data["access_token"],
        token_data.get("refresh_token", refresh_token),
        token_data["expires_in"]
    )
    return get_jobber_token()


def get_valid_token():
    """Get a valid Jobber token, refreshing if necessary"""
    token_data = get_jobber_token()
    if not token_data:
        raise Exception("Access token not found. Please authenticate with Jobber first.")

    # Check if token is expired (with 5-minute buffer)
    if token_data["expires_at"] < (int(time.time()) + 300):
        if not token_data["refresh_token"]:
            raise Exception("Access token expired and no refresh token available. Please re-authenticate.")
        
        # Refresh the token
        token_data = refresh_jobber_token(token_data["refresh_token"])
    
    return token_data["access_token"]


def get_headers():
    """Get headers with valid access token"""
    token = get_valid_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def _execute(query, variables=None, operation_name=None):
    """Execute GraphQL query with automatic token refresh"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    if operation_name:
        payload["operationName"] = operation_name

    response = requests.post(GRAPHQL_URL, json=payload, headers=get_headers())

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("GraphQL Request Payload:", payload)
        print("GraphQL Response:", response.status_code, response.text)
        raise e

    data = response.json()
    if "errors" in data:
        raise Exception(data["errors"][0].get("message"))
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
        raise Exception(errors[0]["message"])
    return result["clientCreate"]["client"]


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
