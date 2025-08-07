from flask import Blueprint, request, jsonify, redirect
from services.jobber_service import (
    create_client,
    get_clients,
    get_client_by_id,
    update_client,
    delete_client,
    get_authorization_url,
    exchange_code_for_token,
    get_jobber_token
)

jobber_bp = Blueprint("jobber", __name__, url_prefix="/api/jobber")


# OAuth Step 1: Redirect to authorization
@jobber_bp.route("/auth")
def authorize_jobber():
    """
    Start OAuth authorization for Jobber CRM
    ---
    tags:
      - Jobber CRM
    responses:
      302:
        description: Redirect to Jobber authorization page
    """
    auth_url = get_authorization_url()
    return redirect(auth_url)


# OAuth Step 2: Handle callback and exchange code
@jobber_bp.route("/callback")
def jobber_callback():
    """
    Handle OAuth callback from Jobber CRM
    ---
    tags:
      - Jobber CRM
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: Authorization code from Jobber
    responses:
      200:
        description: Token stored successfully
      400:
        description: Missing authorization code
      500:
        description: Error exchanging code for token
    """
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing code"}), 400

    try:
        exchange_code_for_token(code)
        return jsonify({"success": True, "message": "Token stored successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Debug endpoint to check token status
@jobber_bp.route("/token/debug", methods=["GET"])
def debug_token():
    """
    Debug endpoint to check token status
    ---
    tags:
      - Jobber CRM
    responses:
      200:
        description: Token information
      404:
        description: No token found
    """
    try:
        token = get_jobber_token()
        if not token:
            return jsonify({"error": "No token found"}), 404
        return jsonify({
            "success": True,
            "token_exists": True,
            "expires_at": token["expires_at"],
            "has_refresh_token": bool(token.get("refresh_token"))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# CREATE - Create a new client
@jobber_bp.route("/clients", methods=["POST"])
def create_client_route():
    try:
        data = request.json
        client = create_client(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            company_name=data.get("company_name")
        )
        return jsonify({"success": True, "client": client}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# READ - List all clients with optional pagination
@jobber_bp.route("/clients", methods=["GET"])
def list_clients_route():
    try:
        first = int(request.args.get("first", 20))
        after = request.args.get("after")
        result = get_clients(first=first, after=after)
        return jsonify({"success": True, "clients": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# READ - Get a single client by ID
@jobber_bp.route("/clients/<string:client_id>", methods=["GET"])
def get_client_route(client_id):
    try:
        client = get_client_by_id(client_id)
        return jsonify({"success": True, "client": client}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404


# UPDATE - Update an existing client
@jobber_bp.route("/clients/<string:client_id>", methods=["PUT"])
def update_client_route(client_id):
    try:
        data = request.json
        updated_client = update_client(
            client_id=client_id,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            company_name=data.get("company_name")
        )
        return jsonify({"success": True, "client": updated_client}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# DELETE - Delete a client by ID
@jobber_bp.route("/clients/<string:client_id>", methods=["DELETE"])
def delete_client_route(client_id):
    try:
        deleted_client = delete_client(client_id)
        return jsonify({"success": True, "client": deleted_client}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
