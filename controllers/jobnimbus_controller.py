import time
from flask import Blueprint, request, jsonify
from services.jobnimbus_service import (
    list_contacts, get_contact, create_contact, update_contact, delete_contact,
    list_jobs, create_job, JobNimbusError
)

jobnimbus_bp = Blueprint("jobnimbus", __name__, url_prefix="/api/jobnimbus")


@jobnimbus_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"success": True, "data": {"ts": int(time.time())}}), 200


@jobnimbus_bp.route("/config/debug", methods=["GET"])
def config_debug():
    """Debug endpoint to show current configuration"""
    try:
        import os
        from models import db, JobNimbusCredentials
        from flask import current_app
        
        with current_app.app_context():
            credentials = db.session.query(JobNimbusCredentials).filter_by(is_active=True).first()
            
            config_data = {
                "JOBNIMBUS_API_KEY_present": bool(credentials and credentials.api_key),
                "JOBNIMBUS_BASE_URL": credentials.base_url if credentials else None,
                "JOBNIMBUS_API_PREFIX": credentials.api_prefix if credentials else None,
                "database_credentials_id": credentials.id if credentials else None,
                "environment_vars": {
                    "JOBNIMBUS_API_KEY": bool(os.getenv("JOBNIMBUS_API_KEY")),
                    "JOBNIMBUS_BASE_URL": os.getenv("JOBNIMBUS_BASE_URL"),
                    "JOBNIMBUS_API_PREFIX": os.getenv("JOBNIMBUS_API_PREFIX"),
                    "USE_JOBNIMBUS_DB_KEY": os.getenv("USE_JOBNIMBUS_DB_KEY", "true")
                }
            }
            
            return jsonify({"success": True, "data": config_data}), 200
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@jobnimbus_bp.route("/config/key", methods=["POST"])
def set_api_key():
    """Set API key for current process (temporary)"""
    try:
        import os
        from datetime import datetime
        from models import db, JobNimbusCredentials
        from flask import current_app
        
        data = request.get_json()
        if not data or "api_key" not in data:
            return jsonify({"success": False, "error": "Missing api_key in request body"}), 400
        
        api_key = data["api_key"].strip()
        if not api_key:
            return jsonify({"success": False, "error": "API key cannot be empty"}), 400
        
        # Store in database
        try:
            with current_app.app_context():
                # Check if credentials exist
                credentials = db.session.query(JobNimbusCredentials).filter_by(is_active=True).first()
                
                if credentials:
                    # Update existing
                    credentials.api_key = api_key
                    credentials.updated_at = datetime.utcnow()
                else:
                    # Create new
                    credentials = JobNimbusCredentials(
                        api_key=api_key,
                        base_url="https://api.jobnimbus.com",
                        api_prefix="v1",
                        is_active=True
                    )
                    db.session.add(credentials)
                
                db.session.commit()
                
                return jsonify({
                    "success": True, 
                    "message": "API key stored in database successfully",
                    "data": {"id": credentials.id}
                }), 200
                
        except Exception as db_error:
            return jsonify({
                "success": False, 
                "error": f"Database error: {str(db_error)}"
            }), 500
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@jobnimbus_bp.route("/config/credentials", methods=["GET"])
def get_credentials():
    """Get current credentials from database"""
    try:
        import os
        from models import db, JobNimbusCredentials
        from flask import current_app
        
        with current_app.app_context():
            credentials = db.session.query(JobNimbusCredentials).filter_by(is_active=True).first()
            
            if not credentials:
                return jsonify({"success": False, "error": "No credentials found"}), 404
            
            return jsonify({
                "success": True,
                "data": {
                    "id": credentials.id,
                    "base_url": credentials.base_url,
                    "api_prefix": credentials.api_prefix,
                    "is_active": credentials.is_active,
                    "created_at": credentials.created_at.isoformat() if credentials.created_at else None,
                    "updated_at": credentials.updated_at.isoformat() if credentials.updated_at else None
                }
            }), 200
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@jobnimbus_bp.route("/config/credentials", methods=["PUT"])
def update_credentials():
    """Update credentials in database"""
    try:
        import os
        from datetime import datetime
        from models import db, JobNimbusCredentials
        from flask import current_app
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        with current_app.app_context():
            credentials = db.session.query(JobNimbusCredentials).filter_by(is_active=True).first()
            
            if not credentials:
                return jsonify({"success": False, "error": "No credentials found"}), 404
            
            # Update fields if provided
            if "api_key" in data and data["api_key"]:
                credentials.api_key = data["api_key"].strip()
            if "base_url" in data and data["base_url"]:
                credentials.base_url = data["base_url"].strip()
            if "api_prefix" in data and data["api_prefix"]:
                credentials.api_prefix = data["api_prefix"].strip()
            
            credentials.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Credentials updated successfully"
            }), 200
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Contacts

@jobnimbus_bp.route("/contacts", methods=["GET"])
def contacts_list_route():
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("pageSize", 100))
        q = request.args.get("q")
        data = list_contacts(page=page, page_size=page_size, query=q)
        return jsonify({"success": True, "data": data}), 200
    except JobNimbusError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@jobnimbus_bp.route("/contacts", methods=["POST"])
def create_contact_route():
    try:
        payload = request.get_json(force=True)
        data = create_contact(payload)
        return jsonify({"success": True, "data": data}), 201
    except JobNimbusError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@jobnimbus_bp.route("/contacts/<contact_id>", methods=["GET"])
def get_contact_route(contact_id):
    try:
        data = get_contact(contact_id)
        return jsonify({"success": True, "data": data}), 200
    except JobNimbusError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@jobnimbus_bp.route("/contacts/<contact_id>", methods=["PUT", "PATCH"])
def update_contact_route(contact_id):
    try:
        payload = request.get_json(force=True)
        data = update_contact(contact_id, payload)
        return jsonify({"success": True, "data": data}), 200
    except JobNimbusError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@jobnimbus_bp.route("/contacts/<contact_id>", methods=["DELETE"])
def delete_contact_route(contact_id):
    try:
        data = delete_contact(contact_id)
        return jsonify({"success": True, "data": data}), 200
    except JobNimbusError as e:
        return jsonify({"success": False, "message": str(e)}), 400


# Jobs

@jobnimbus_bp.route("/jobs", methods=["GET"])
def list_jobs_route():
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("pageSize", 100))
        status = request.args.get("status")
        data = list_jobs(page=page, page_size=page_size, status=status)
        return jsonify({"success": True, "data": data}), 200
    except JobNimbusError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@jobnimbus_bp.route("/jobs", methods=["POST"])
def create_job_route():
    try:
        payload = request.get_json(force=True)
        data = create_job(payload)
        return jsonify({"success": True, "data": data}), 201
    except JobNimbusError as e:
        return jsonify({"success": False, "message": str(e)}), 400 