#inthis we will create a route to update user infor based on his record id 
from flask import Blueprint, request, jsonify
from database.schemas import ZohoCreds
from routes.CRUD.clients import clients_blueprint
from token_handler.tokens import fetch_tokens
from database.insert_data_db import insert_audit_data
import requests
from utils.extension import limiter
from routes.zoho_constants import Constants

# Define a Flask blueprint for the "update" route
update_blueprint = Blueprint('update', __name__)

@clients_blueprint.route("/<int:entity_id>/leads", methods=["PUT"])
@limiter.limit("5 per minute")  # Rate limit to prevent abuse (5 requests per minute)
def update_clients(entity_id):
    """
    Update Leads in Zoho CRM.

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
        name: client_id
        required: true
        schema:
          type: string
        description: Comma-separated list of Zoho lead IDs to be updated (max 10).
      - in: body
        name: body
        required: true
        description: JSON object containing lead data to update. IDs will be injected automatically.
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  Annual_Revenue:
                    type: integer
                    example: 1600000
                  City:
                    type: string
                    example: "Los Angeles Updated"
                  Company:
                    type: string
                    example: "Innovatech Solutions Updated"
                  Email:
                    type: string
                    example: "elon.musk.updated@example.com"
                  First_Name:
                    type: string
                    example: "Elon Dusk"
                  Last_Name:
                    type: string
                    example: "Musk Updated"
                  Phone:
                    type: string
                    example: "555-555-9998"
                  Lead_Status:
                    type: string
                    example: "Contacted"
    responses:
      200:
        description: Leads updated successfully.
      400:
        description: Invalid input or missing required fields.
      401:
        description: Unauthorized access.
      500:
        description: Internal server error.
    """
    try:
        # Fetch the access token for the given entity_id
        token_data = fetch_tokens(entity_id)
        if "error" in token_data:
            # If there is an error in fetching the token, return a 401 Unauthorized response
            return jsonify(token_data), 401
        access_token = token_data.get("access_token")
        if not access_token:
            # If the access token is missing, return a 401 Unauthorized response
            return jsonify({"message": "User tokens not found. Please reauthorize."}), 401
    except Exception as e:
        # Handle any unexpected errors while fetching the token
        return jsonify({"error": "token_data fetch failed", "details": str(e)}), 500

    # Prepare headers for the Zoho API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    zoho_url = Constants.ZOHO_API_URL

    try:
        # Extract the "client_id" query parameter from the request
        client_data = request.args.get("client_id")  # Comma-separated list of client IDs
        # Limit the number of client IDs to 10 for a single update request
        if client_data and len(client_data.split(",")) > 10:
            return jsonify({"error": "Too many client IDs provided. Maximum is 10."}), 400
        if not client_data:
            # If no client IDs are provided, return a 400 Bad Request response
            return jsonify({"error": "client_id is required"}), 400

        # Split the client_data by commas to get a list of client IDs
        client_data_list = client_data.split(",") if client_data else []
        if not client_data_list:
            # If the list is empty, return a 400 Bad Request response
            return jsonify({"error": "No client data provided"}), 400

        try:
            # Parse the JSON body from the request
            data = request.get_json(force=True)
            # For each client ID in the list, pair it with the data to update
            for i, client_id in enumerate(client_data_list):
                data["data"][i]["id"] = client_id
        except Exception:
            # If the JSON body is invalid, return a 400 Bad Request response
            return jsonify({"error": "Invalid JSON body"}), 400

        # Send a PUT request to the Zoho API with the updated data
        response = requests.put(zoho_url, json=data, headers=headers)

        try:
            # Try to parse the JSON response from Zoho
            res_json = response.json()
        except ValueError:
            # If the response is not valid JSON, return a 502 Bad Gateway response
            return jsonify({"error": "Invalid response from Zoho"}), 502

        if response.status_code == 200:
            # If the update is successful, insert audit data into the database
            insert_audit_data(entity_id, response.json(), mode="update")
            return jsonify(res_json), 200
        else:
            # If the update fails, return the error details from Zoho
            return jsonify({"status": "error", "message": "Error updating data", "details": res_json}), response.status_code

    except requests.RequestException as e:
        # Handle network-related errors while making the API request
        return jsonify({"error": "Network error", "details": str(e)}), 500
    except Exception as e:
        # Handle any unexpected server errors
        return jsonify({"error": "Unexpected server error", "details": str(e)}), 500
