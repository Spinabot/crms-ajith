import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPHQL_URL = "https://api.getjobber.com/api/graphql"

def get_access_token():
    """Get access token and check if it's expired"""
    expires = int(os.getenv("JOBBER_TOKEN_EXPIRES_AT", 0))
    if time.time() > expires:
        raise Exception("Access token expired; refresh required")
    return os.getenv("JOBBER_ACCESS_TOKEN")

def get_headers():
    """Get headers with Bearer token"""
    token = get_access_token()
    if not token:
        raise Exception("No access token found. Please authorize with Jobber first.")
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def _execute(query, variables=None, operation_name=None):
    """Execute GraphQL query/mutation with improved error handling"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    if operation_name:
        payload["operationName"] = operation_name

    try:
        resp = requests.post(GRAPHQL_URL, json=payload, headers=get_headers())
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("🔧 GraphQL Request Payload:", payload)
        print("🔧 GraphQL Response:", resp.status_code, resp.text)
        if resp.status_code == 401:
            raise Exception("Access token expired or invalid. Please refresh your token.")
        raise Exception(f"HTTP Error: {resp.status_code} - {resp.text}")

    data = resp.json()
    if "errors" in data:
        print("🔧 GraphQL Errors:", data["errors"])
        raise Exception(data["errors"][0].get("message"))
    return data.get("data")

def fetch_clients(first: int = 50, after: str = None):
    """Fetch clients from Jobber"""
    query = """
    query ($first: Int!, $after: String) {
      clients(first: $first, after: $after) {
        nodes {
          id
          firstName
          lastName
          emails {
            primary
            address
          }
          companyName
        }
        pageInfo { 
          hasNextPage 
          endCursor 
        }
        totalCount
      }
    }"""
    return _execute(query, {"first": first, "after": after})

def fetch_jobs(first: int = 50, after: str = None):
    """Fetch jobs from Jobber"""
    query = """
    query ($first: Int!, $after: String) {
      jobs(first: $first, after: $after) {
        nodes {
          id
          jobNumber
          title
          status
        }
        pageInfo { 
          hasNextPage 
          endCursor 
        }
      }
    }"""
    return _execute(query, {"first": first, "after": after})

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
