from flask import Blueprint, jsonify, request
from token_handler.tokens import fetch_tokens
import requests
from utils.extension import limiter
from routes.zoho_constants import Constants

# Define a Flask blueprint for the "delete" route
delete_blueprint = Blueprint("delete", __name__)

@delete_blueprint.route("/<int:entity_id>/leads", methods=['DELETE'])
@limiter.limit("5 per minute")  # Rate limit to prevent abuse (5 requests per minute)
def delete_clients(entity_id):
    """
    Delete Leads in Zoho CRM.

    ---
    tags:
      - Leads
    parameters:
      - in: path
        name: entity_id
        required: true
        schema:
          type: integer
        description: The ID of the entity project.
      - in: query
        name: ids
        required: true
        schema:
          type: string
        description: Comma-separated list of lead IDs to delete (e.g., "id1,id2").
    responses:
      200:
        description: Leads deleted successfully.
      400:
        description: No lead IDs provided or invalid input.
      401:
        description: Unauthorized access.
      500:
        description: Internal server error.
    """
    
    # Extract the "ids" query parameter from the request
    ids = request.args.get("ids")
    if not ids:
        # If no IDs are provided, return a 400 Bad Request response
        return jsonify({"error": "No lead IDs provided"}), 400

    try:
        # Fetch the access token for the given entity_id
        token_data = fetch_tokens(entity_id)
        if "error" in token_data:
            # If there is an error in fetching the token, return a 401 Unauthorized response
            return jsonify(token_data), 401
        access_token = token_data.get("access_token")
        if not access_token:
            # If the access token is missing, return a 401 Unauthorized response
            return jsonify({"error": "No access token_data found"}), 401
    except Exception as e:
        # Handle any unexpected errors while fetching the token
        return jsonify({"error": "Failed to fetch access token_data", "details": str(e)}), 500

    # Prepare the Zoho API URL and headers
    zoho_url = Constants.ZOHO_API_URL
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    params = {"ids": ids}  # Pass the IDs as query parameters

    try:
        # Send a DELETE request to the Zoho API
        response = requests.delete(zoho_url, headers=headers, params=params)

        # Try to parse the JSON response from Zoho
        try:
            res_json = response.json()
        except ValueError:
            # If the response is not valid JSON, return a default message
            res_json = {"message": "No JSON response from Zoho"}
        
        # Return the response with a success or failure status
        return jsonify({
            "status": "success" if response.status_code == 200 else "failure",
            "response": res_json
        }), response.status_code

    except requests.RequestException as e:
        # Handle network-related errors while making the API request
        return jsonify({"error": "Network error", "details": str(e)}), 500
    except Exception as e:
        # Handle any unexpected server errors
        return jsonify({"error": "Unexpected server error", "details": str(e)}), 500

