import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPHQL_URL = "https://api.getjobber.com/api/graphql"


def get_access_token():
    expires = int(os.getenv("JOBBER_TOKEN_EXPIRES_AT", 0))
    if time.time() > expires:
        raise Exception("Access token expired; refresh required")
    return os.getenv("JOBBER_ACCESS_TOKEN")


def get_headers():
    token = get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def _execute(query, variables=None, operation_name=None):
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
