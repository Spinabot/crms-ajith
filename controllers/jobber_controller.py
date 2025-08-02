from flask import Blueprint, request, jsonify
from services.jobber_service import (
    create_client,
    get_clients,
    get_client_by_id,
    update_client,
    delete_client
)

jobber_bp = Blueprint("jobber", __name__, url_prefix="/api/jobber")


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
