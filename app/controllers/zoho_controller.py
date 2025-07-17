import requests
import time
import logging
from flask import Blueprint, request, redirect, session, jsonify, current_app, g
from flask_restx import Resource, Namespace, fields
from app import db
from app.models.zoho import ZohoCreds, ZohoClients
from app.config import Config
from config.vault_config import get_secret
from app.swagger import api, zoho_ns, zoho_leads_response_model, zoho_users_response_model, zoho_metadata_response_model, zoho_auth_success_model, zoho_auth_error_model, zoho_create_lead_model, error_model
from app.services.zoho_service import make_zoho_api_request

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for Zoho routes
zoho_bp = Blueprint('zoho', __name__, url_prefix='/zoho')

def get_zoho_secrets():
    """Fetch Zoho client ID and secret from Vault, fallback to Config."""
    if hasattr(g, 'zoho_secrets'):
        return g.zoho_secrets

    client_id = None
    client_secret = None
    try:
        client_id = get_secret('ZOHO_CLIENT_ID')
        client_secret = get_secret('ZOHO_CLIENT_SECRET')
    except Exception as e:
        logger.warning(f"Could not fetch Zoho secrets from Vault: {e}. Falling back to config.")
        client_id = Config.ZOHO_CLIENT_ID
        client_secret = Config.ZOHO_CLIENT_SECRET

    if not client_id or not client_secret:
        raise RuntimeError("ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET must be set in Vault or environment")

    g.zoho_secrets = (client_id, client_secret)
    return client_id, client_secret

@zoho_bp.route("/<int:entity_id>/redirect", methods=["GET"])
def authorize(entity_id):
    """Authorize user with Zoho OAuth."""
    try:
        # Check if user credentials already exist
        existing_creds = ZohoCreds.query.filter_by(entity_id=entity_id).first()
        if existing_creds:
            return "User already authorized"  # Simple text response like original

        # Store entity_id in session for callback
        session['entity_id'] = entity_id

        # Get Zoho secrets from Vault
        client_id, _ = get_zoho_secrets()

        # Build authorization URL
        auth_url = (
            f"{Config.ZOHO_ACCOUNTS_URL}/oauth/v2/auth"
            "?scope=ZohoCRM.users.ALL,ZohoCRM.modules.ALL"
            f"&client_id={client_id}"
            "&response_type=code"
            "&access_type=offline"
            f"&redirect_uri={Config.ZOHO_REDIRECT_URI}"
        )

        logger.info(f"Redirecting entity {entity_id} to Zoho authorization")
        return redirect(auth_url)

    except Exception as e:
        logger.error(f"Authorization error: {e}")
        return jsonify({"error": "Authorization failed"}), 500

@zoho_bp.route("/authorize/callback")
def callback():
    """Handle OAuth callback from Zoho."""
    try:
        entity_id = session.get('entity_id')
        if not entity_id:
            return jsonify({"error": "No entity_id found in session"}), 400

        code = request.args.get("code")
        accounts_server = request.args.get("accounts-server", Config.ZOHO_ACCOUNTS_URL)

        if not code:
            return jsonify({"error": "No authorization code received"}), 400

        # Get Zoho secrets from Vault
        client_id, client_secret = get_zoho_secrets()

        # Exchange grant code for access token
        token_url = f"{accounts_server}/oauth/v2/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": Config.ZOHO_REDIRECT_URI
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        logger.info(f"Requesting token for entity {entity_id}")

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]
            expires_in = token_data["expires_in"]

            # Calculate expiration time
            current_time = int(time.time())
            expiration_time = current_time + expires_in

            # Store credentials in database
            try:
                # Check if credentials already exist
                existing_creds = ZohoCreds.query.filter_by(entity_id=entity_id).first()

                if existing_creds:
                    # Update existing credentials
                    existing_creds.access_token = access_token
                    existing_creds.refresh_token = refresh_token
                    existing_creds.expiration_time = expiration_time
                else:
                    # Create new credentials
                    new_creds = ZohoCreds(
                        entity_id=entity_id,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expiration_time=expiration_time
                    )
                    db.session.add(new_creds)

                db.session.commit()
                logger.info(f"Successfully stored Zoho credentials for entity {entity_id}")

                # Clear session
                session.pop('entity_id', None)

                return jsonify({
                    "status": "success",
                    "message": "Authorization successful"
                })

            except Exception as db_error:
                logger.error(f"Database error storing Zoho credentials: {db_error}")
                db.session.rollback()
                return jsonify({"error": "Failed to store credentials"}), 500

        else:
            logger.error(f"Token request failed: {response.status_code} - {response.text}")
            return jsonify({"error": f"Token request failed: {response.text}"}), response.status_code

    except Exception as e:
        logger.error(f"Callback error: {e}")
        return jsonify({"error": "Callback processing failed"}), 500

@zoho_bp.route("/<int:entity_id>/status")
def get_auth_status(entity_id):
    """Get authentication status for an entity."""
    try:
        creds = ZohoCreds.query.filter_by(entity_id=entity_id).first()

        if not creds:
            return jsonify({
                "status": "not_authenticated",
                "message": "Entity not authenticated with Zoho"
            }), 404

        return jsonify({
            "status": "authenticated" if creds.has_valid_token() else "expired",
            "hasValidToken": creds.has_valid_token(),
            "createdAt": creds.created_at.isoformat() if creds.created_at else None,
            "updatedAt": creds.updated_at.isoformat() if creds.updated_at else None
        })

    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        return jsonify({"error": "Failed to get authentication status"}), 500

@zoho_bp.route("/<int:entity_id>/refresh")
def refresh_token_route(entity_id):
    """Refresh the access token for an entity."""
    try:
        creds = ZohoCreds.query.filter_by(entity_id=entity_id).first()

        if not creds:
            return jsonify({"error": "Entity not found"}), 404

        # Import the refresh function
        from app.services.zoho_service import refresh_zoho_token

        result = refresh_zoho_token(entity_id, creds.refresh_token)

        if result.get("error"):
            return jsonify(result), 400

        return jsonify({
            "status": "success",
            "message": "Token refreshed successfully"
        })

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({"error": "Failed to refresh token"}), 500

# Flask-RESTX Resource classes for Swagger documentation
@zoho_ns.route('/<int:entity_id>/leads')
@zoho_ns.param('entity_id', 'Entity ID used to fetch access token and Zoho leads')
@zoho_ns.param('client_id', 'Optional client_id to fetch specific client data', required=False)
class ZohoLeadsResource(Resource):
    @zoho_ns.doc('get_zoho_leads',
        description='Fetch leads from Zoho CRM',
        responses={
            200: ('Success', zoho_leads_response_model),
            401: ('Unauthorized', zoho_auth_error_model),
            500: ('Internal Server Error', error_model),
            502: ('Bad Gateway', error_model)
        })
    def get(self, entity_id):
        """Fetch leads from Zoho CRM."""
        params = dict(request.args)
        result = make_zoho_api_request(entity_id, 'Leads', method='GET', params=params)
        return result, 200 if 'error' not in result else 400

    @zoho_ns.doc('create_zoho_leads',
        description='Create leads in Zoho CRM',
        body=zoho_create_lead_model,
        responses={
            201: ('Created', zoho_leads_response_model),
            400: ('Bad Request', error_model),
            401: ('Unauthorized', zoho_auth_error_model),
            500: ('Internal Server Error', error_model),
            502: ('Bad Gateway', error_model)
        })
    def post(self, entity_id):
        """Create leads in Zoho CRM."""
        data = request.get_json()
        result = make_zoho_api_request(entity_id, 'Leads', method='POST', data=data)
        return result, 201 if 'error' not in result else 400

@zoho_ns.route('/<int:entity_id>/leads/<string:lead_id>')
@zoho_ns.param('entity_id', 'Entity ID used to fetch access token and Zoho leads')
@zoho_ns.param('lead_id', 'Zoho Lead ID')
class ZohoLeadResource(Resource):
    @zoho_ns.doc('get_zoho_lead', description='Get a single lead from Zoho CRM')
    def get(self, entity_id, lead_id):
        result = make_zoho_api_request(entity_id, f'Leads/{lead_id}', method='GET')
        return result, 200 if 'error' not in result else 400

    @zoho_ns.doc('update_zoho_lead', description='Update a lead in Zoho CRM', body=zoho_create_lead_model)
    def put(self, entity_id, lead_id):
        data = request.get_json()
        result = make_zoho_api_request(entity_id, f'Leads/{lead_id}', method='PUT', data=data)
        return result, 200 if 'error' not in result else 400

    @zoho_ns.doc('delete_zoho_lead', description='Delete a lead in Zoho CRM')
    def delete(self, entity_id, lead_id):
        result = make_zoho_api_request(entity_id, f'Leads/{lead_id}', method='DELETE')
        return result, 200 if 'error' not in result else 400

@zoho_ns.route('/<int:entity_id>/users')
@zoho_ns.param('entity_id', 'Entity ID used to fetch access token and Zoho users')
class ZohoUsersResource(Resource):
    @zoho_ns.doc('get_zoho_users',
        description='Fetch users from Zoho CRM',
        responses={
            200: ('Success', zoho_users_response_model),
            401: ('Unauthorized', zoho_auth_error_model),
            500: ('Internal Server Error', error_model)
        })
    def get(self, entity_id):
        """Fetch users from Zoho CRM."""
        try:
            # Get Zoho credentials for the entity
            from app.services.zoho_service import get_zoho_credentials
            creds = get_zoho_credentials(entity_id)

            if creds.get("error"):
                return creds, 401

            access_token = creds.get("access_token")
            if not access_token:
                return {"error": "Access token not found"}, 401

        except Exception as e:
            logger.error(f"Error fetching access token: {e}")
            return {"error": "Error while fetching access token", "details": str(e)}, 500

        try:
            logger.info(f"Fetching users for entity {entity_id}")

            url = "https://www.zohoapis.com/crm/v8/users?type=AdminUsers"
            headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                users_data = response.json()
                users = users_data.get("users", [])

                # Format user data
                total_users = []
                for user in users:
                    total_users.append({
                        "id": user.get('id'),
                        "name": user.get('full_name'),
                        "email": user.get("email")
                    })

                logger.info(f"Successfully fetched {len(total_users)} users for entity {entity_id}")
                return {"users": total_users}
            else:
                logger.error(f"Failed to fetch users: {response.status_code} - {response.text}")
                return {"message": "Could not retrieve user details"}, response.status_code

        except requests.RequestException as e:
            logger.error(f"Network error while fetching users: {e}")
            return {"error": "Network error while fetching users", "details": str(e)}, 500

@zoho_ns.route('/<int:entity_id>/leads/meta')
@zoho_ns.param('entity_id', 'Entity ID used to fetch access token and metadata')
@zoho_ns.param('module', 'Module name (default: Leads)', required=False)
@zoho_ns.param('type', 'Type of fields (default: all)', required=False)
class ZohoMetadataResource(Resource):
    @zoho_ns.doc('get_zoho_metadata',
        description='Fetch metadata for Zoho CRM modules',
        responses={
            200: ('Success', zoho_metadata_response_model),
            401: ('Unauthorized', zoho_auth_error_model),
            500: ('Internal Server Error', error_model)
        })
    def get(self, entity_id):
        """Fetch metadata for Zoho CRM modules."""
        try:
            # Get Zoho credentials for the entity
            from app.services.zoho_service import get_zoho_credentials
            creds = get_zoho_credentials(entity_id)

            if creds.get("error"):
                return creds, 401

            access_token = creds.get("access_token")
            if not access_token:
                return {"error": "Access token not found"}, 401

        except Exception as e:
            logger.error(f"Error fetching access token: {e}")
            return {"error": "Error while fetching access token", "details": str(e)}, 500

        try:
            module = request.args.get('module', 'Leads')  # Default to 'Leads' if not provided
            field_type = request.args.get('type', 'all')  # Default to 'all' if not provided

            logger.info(f"Fetching metadata for module '{module}', type '{field_type}' for entity {entity_id}")

            url = "https://www.zohoapis.com/crm/v8/settings/fields"
            params = {
                "module": module,
                "type": field_type
            }
            headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                logger.info(f"Successfully fetched metadata for entity {entity_id}")
                return {"status": "Success", "data": response.json()}
            else:
                logger.error(f"Failed to fetch metadata: {response.status_code} - {response.text}")
                return {
                    "status": "failure",
                    "message": "error getting metadata",
                    "status_code": response.status_code
                }, response.status_code

        except requests.RequestException as e:
            logger.error(f"Network error while fetching metadata: {e}")
            return {"error": "Network error while fetching metadata", "details": str(e)}, 500

# Create lead model for Swagger
zoho_create_lead_model = api.model('ZohoCreateLead', {
    'data': fields.List(fields.Raw, required=True, description="Array of lead objects to create"),
    'layout_id': fields.String(required=False, description="Optional layout ID")
})

@zoho_ns.route('/<int:entity_id>/leads/update')
@zoho_ns.param('entity_id', 'Entity ID used to fetch access token and update leads')
@zoho_ns.param('client_id', 'Comma-separated list of Zoho lead IDs to be updated (max 10)', required=True)
class ZohoUpdateLeadResource(Resource):
    @zoho_ns.doc('update_zoho_leads',
        description='Update leads in Zoho CRM',
        body=zoho_create_lead_model,
        responses={
            200: ('Success', zoho_leads_response_model),
            400: ('Bad Request', error_model),
            401: ('Unauthorized', zoho_auth_error_model),
            500: ('Internal Server Error', error_model),
            502: ('Bad Gateway', error_model)
        })
    def put(self, entity_id):
        """Update leads in Zoho CRM."""
        try:
            # Get Zoho credentials for the entity
            from app.services.zoho_service import get_zoho_credentials
            creds = get_zoho_credentials(entity_id)

            if creds.get("error"):
                return creds, 401

            access_token = creds.get("access_token")
            if not access_token:
                return {"message": "User tokens not found. Please reauthorize."}, 401

            # Prepare headers for the Zoho API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Zoho-oauthtoken {access_token}"
            }
            zoho_url = "https://www.zohoapis.com/crm/v8/Leads"

            # Extract the "client_id" query parameter from the request
            client_data = request.args.get("client_id")  # Comma-separated list of client IDs
            # Limit the number of client IDs to 10 for a single update request
            if client_data and len(client_data.split(",")) > 10:
                return {"error": "Too many client IDs provided. Maximum is 10."}, 400
            if not client_data:
                # If no client IDs are provided, return a 400 Bad Request response
                return {"error": "client_id is required"}, 400

            # Split the client_data by commas to get a list of client IDs
            client_data_list = client_data.split(",") if client_data else []
            if not client_data_list:
                # If the list is empty, return a 400 Bad Request response
                return {"error": "No client data provided"}, 400

            try:
                # Parse the JSON body from the request
                data = request.get_json(force=True)
                # For each client ID in the list, pair it with the data to update
                for i, client_id in enumerate(client_data_list):
                    data["data"][i]["id"] = client_id
            except Exception:
                # If the JSON body is invalid, return a 400 Bad Request response
                return {"error": "Invalid JSON body"}, 400

            logger.info(f"Updating {len(client_data_list)} leads for entity {entity_id}")

            # Send a PUT request to the Zoho API with the updated data
            response = requests.put(zoho_url, json=data, headers=headers)

            try:
                # Try to parse the JSON response from Zoho
                res_json = response.json()
            except ValueError:
                # If the response is not valid JSON, return a 502 Bad Gateway response
                return {"error": "Invalid response from Zoho"}, 502

            if response.status_code == 200:
                # If the update is successful
                logger.info(f"Successfully updated leads for entity {entity_id}")
                return res_json, 200
            else:
                # If the update fails, return the error details from Zoho
                logger.error(f"Failed to update leads: {response.status_code} - {res_json}")
                return {"status": "error", "message": "Error updating data", "details": res_json}, response.status_code

        except requests.RequestException as e:
            logger.error(f"Network error updating leads: {e}")
            return {"error": "Network error", "details": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected server error updating leads: {e}")
            return {"error": "Unexpected server error", "details": str(e)}, 500

@zoho_ns.route('/<int:entity_id>/leads/delete')
@zoho_ns.param('entity_id', 'Entity ID used to fetch access token and delete leads')
@zoho_ns.param('ids', 'Comma-separated list of lead IDs to delete (e.g., "id1,id2")', required=True)
class ZohoDeleteLeadResource(Resource):
    @zoho_ns.doc('delete_zoho_leads',
        description='Delete leads in Zoho CRM',
        responses={
            200: ('Success', api.model('DeleteResponse', {
                'status': fields.String(example='success'),
                'response': fields.Raw(description='Zoho API response')
            })),
            400: ('Bad Request', error_model),
            401: ('Unauthorized', zoho_auth_error_model),
            500: ('Internal Server Error', error_model)
        })
    def delete(self, entity_id):
        """Delete leads in Zoho CRM."""
        # Extract the "ids" query parameter from the request
        ids = request.args.get("ids")
        if not ids:
            # If no IDs are provided, return a 400 Bad Request response
            return {"error": "No lead IDs provided"}, 400

        try:
            # Get Zoho credentials for the entity
            from app.services.zoho_service import get_zoho_credentials
            creds = get_zoho_credentials(entity_id)

            if creds.get("error"):
                return creds, 401

            access_token = creds.get("access_token")
            if not access_token:
                return {"error": "No access token found"}, 401

            # Prepare the Zoho API URL and headers
            zoho_url = "https://www.zohoapis.com/crm/v8/Leads"
            headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
            params = {"ids": ids}  # Pass the IDs as query parameters

            logger.info(f"Deleting leads with IDs: {ids} for entity {entity_id}")

            # Send a DELETE request to the Zoho API
            response = requests.delete(zoho_url, headers=headers, params=params)

            # Try to parse the JSON response from Zoho
            try:
                res_json = response.json()
            except ValueError:
                # If the response is not valid JSON, return a default message
                res_json = {"message": "No JSON response from Zoho"}

            # Return the response with a success or failure status
            if response.status_code == 200:
                logger.info(f"Successfully deleted leads for entity {entity_id}")
            else:
                logger.error(f"Failed to delete leads: {response.status_code} - {res_json}")

            return {
                "status": "success" if response.status_code == 200 else "failure",
                "response": res_json
            }, response.status_code

        except requests.RequestException as e:
            logger.error(f"Network error deleting leads: {e}")
            return {"error": "Network error", "details": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected server error deleting leads: {e}")
            return {"error": "Unexpected server error", "details": str(e)}, 500