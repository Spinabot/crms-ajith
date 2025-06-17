from flask import Blueprint
from flask import jsonify, request
clients_blueprint = Blueprint('clients', __name__)
import requests
from flask import current_app as app
from token_handler.tokens import fetch_tokens
from utils.extension import limiter
from routes.zoho_constants import Constants

@clients_blueprint.route("/<int:entity_id>/leads", methods=["GET"])
@limiter.limit("5 per minute")  # Rate limit to prevent abuse (5 requests per minute)
def get_clients(entity_id):
    """
    Fetch leads from Zoho CRM.

    ---
    tags:
      - Leads
    parameters:
      - in: path
        name: entity_id
        required: true
        schema:
          type: integer
        description: entity_id used to fetch access token_data and Zoho leads.
    responses:
      200:
        description: Successful fetch of leads.
      401:
        description: Unauthorized or token_data issue.
      500:
        description: Internal server error.
      502:
        description: Invalid JSON response from Zoho.
    """
    try:
        # Fetch the access token for the given entity_id
        token_data = fetch_tokens(entity_id)
        if "error" in token_data:
            # If there is an error in fetching the token, return a 401 response
            return jsonify(token_data), 401
        token_data = token_data.get("access_token")
        if not token_data:
            # If the access token is missing, return a 401 response
            return jsonify({"error": "Access token_data not found"}), 401
    except Exception as e:
        # Handle any unexpected errors while fetching the token
        return jsonify({"error": "Error while fetching access token_data", "details": str(e)}), 500

    # Prepare the headers for the Zoho API request
    headers = {"Authorization": "Zoho-oauthtoken " + token_data}
    url = Constants.ZOHO_API_URL + "?" + Constants.ZOHO_QUERY_PARAMS

    # Check if a specific client_id is provided in the query parameters
    if request.args.get("client_id"):
        # Use the client_id from the query parameters to fetch specific client data
        client_id = request.args.get("client_id")
        url = Constants.ZOHO_API_URL + f"/{client_id}?" + Constants.ZOHO_QUERY_PARAMS

    try:
        # Make a GET request to the Zoho API
        response = requests.get(url, headers=headers)

        # Safely try parsing the JSON response
        try:
            data = response.json()
        except ValueError:
            # If the response is not valid JSON, return a 502 response
            return jsonify({"error": "Invalid JSON response from Zoho"}), 502

        # If the response status is 200 (OK), return the data
        if response.status_code == 200:
            return jsonify(data)
        else:
            # If the response status is not 200, return an error with details
            return jsonify({
                "error": "Failed to fetch clients",
                "status_code": response.status_code,
                "details": data
            }), response.status_code

    except requests.RequestException as e:
        # Handle network-related errors while making the API request
        return jsonify({
            "error": "Network error while accessing Zoho CRM",
            "details": str(e)
        }), 500
