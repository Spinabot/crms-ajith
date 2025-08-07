from flask import Blueprint, redirect, request, jsonify
from services import capsule_service

capsule_bp = Blueprint("capsule", __name__, url_prefix="/api/capsule")


# OAuth Step 1: Redirect to authorization
@capsule_bp.route("/auth")
def start_auth():
    """
    Start OAuth authorization for Capsule CRM
    ---
    tags:
      - Capsule CRM
    responses:
      302:
        description: Redirect to Capsule authorization page
    """
    auth_url = capsule_service.get_authorization_url()
    return redirect(auth_url)


# OAuth Step 2: Handle callback and exchange code
@capsule_bp.route("/callback")
def auth_callback():
    """
    Handle OAuth callback from Capsule CRM
    ---
    tags:
      - Capsule CRM
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: Authorization code from Capsule
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
        capsule_service.exchange_code_for_token(code)
        return jsonify({"success": True, "message": "Token stored successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Debug endpoint to check token status
@capsule_bp.route("/token/debug", methods=["GET"])
def debug_token():
    """
    Debug endpoint to check token status
    ---
    tags:
      - Capsule CRM
    responses:
      200:
        description: Token information
      404:
        description: No token found
    """
    try:
        token = capsule_service.get_token_from_db()
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


# ---------- People (Contacts) ----------

@capsule_bp.route("/people", methods=["GET"])
def list_people():
    """
    List all Capsule contacts (people)
    ---
    tags:
      - Capsule CRM
    responses:
      200:
        description: List of people
    """
    people = capsule_service.make_capsule_request("GET", "parties")
    return jsonify({"people": people})


@capsule_bp.route("/people", methods=["POST"])
def create_person():
    """
    Create a new contact (person) in Capsule
    ---
    tags:
      - Capsule CRM
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Person
          properties:
            first_name:
              type: string
            last_name:
              type: string
            email:
              type: string
            phone:
              type: string
    responses:
      201:
        description: Created person
    """
    data = request.get_json()
    result = capsule_service.make_capsule_request("POST", "parties", data=data)
    return jsonify(result), 201


@capsule_bp.route("/people/<person_id>", methods=["GET"])
def get_person(person_id):
    """
    Get a Capsule Person by ID
    ---
    tags:
      - Capsule CRM
    parameters:
      - name: person_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Person details
    """
    person = capsule_service.make_capsule_request("GET", f"parties/{person_id}")
    return jsonify({"person": person})


@capsule_bp.route("/people/<person_id>", methods=["PUT"])
def update_person(person_id):
    """
    Update an existing Capsule contact (person)
    ---
    tags:
      - Capsule CRM
    parameters:
      - name: person_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          id: PersonUpdate
          properties:
            first_name:
              type: string
            last_name:
              type: string
            email:
              type: string
            phone:
              type: string
    responses:
      200:
        description: Updated contact
    """
    data = request.get_json()
    updated = capsule_service.make_capsule_request("PUT", f"parties/{person_id}", data=data)
    return jsonify(updated)


@capsule_bp.route("/people/<person_id>", methods=["DELETE"])
def delete_person(person_id):
    """
    Delete a Capsule contact (person)
    ---
    tags:
      - Capsule CRM
    parameters:
      - name: person_id
        in: path
        type: string
        required: true
    responses:
      204:
        description: Person deleted
    """
    capsule_service.make_capsule_request("DELETE", f"parties/{person_id}")
    return '', 204


# ---------- Organizations ----------

@capsule_bp.route("/organizations", methods=["GET"])
def list_organizations():
    """
    Get all organizations from Capsule CRM
    ---
    tags:
      - Capsule CRM
    responses:
      200:
        description: List of organizations
    """
    return jsonify(capsule_service.get_capsule_organizations())


# ---------- Opportunities ----------

@capsule_bp.route("/opportunities", methods=["GET"])
def list_opportunities():
    """
    Get all opportunities from Capsule CRM
    ---
    tags:
      - Capsule CRM
    responses:
      200:
        description: List of opportunities
    """
    return jsonify(capsule_service.get_capsule_opportunities())
