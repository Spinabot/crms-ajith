from flask import Blueprint, request, jsonify, redirect, session, url_for
import logging
from services.jobber_service import (
    create_client,
    get_clients,
    get_client_by_id,
    update_client,
    delete_client,
    get_authorization_url,
    exchange_code_for_token,
    get_jobber_token,
    refresh_jobber_token,
    store_jobber_token
)
import time

# Configure logging
logger = logging.getLogger(__name__)

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
    logger.info("Starting Jobber OAuth authorization")
    
    # Generate authorization URL with secure state
    auth_url = get_authorization_url()
    
    # Store the state in session for additional security
    if 'jobber_oauth_state' not in session:
        session['jobber_oauth_state'] = 'initiated'
    
    logger.info("Redirecting user to Jobber authorization page")
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
      - name: state
        in: query
        type: string
        required: false
        description: State parameter for CSRF protection
    responses:
      200:
        description: Token stored successfully
      400:
        description: Missing authorization code or invalid state
      500:
        description: Error exchanging code for token
    """
    # Get parameters from callback
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")
    error_description = request.args.get("error_description")
    
    # Check for OAuth errors
    if error:
        logger.error(f"OAuth error from Jobber: {error} - {error_description}")
        return jsonify({
            "error": "OAuth authorization failed",
            "details": error_description or error
        }), 400
    
    if not code:
        logger.error("Missing authorization code in callback")
        return jsonify({
            "error": "Missing authorization code",
            "message": "No authorization code received from Jobber"
        }), 400

    try:
        logger.info("Processing OAuth callback with authorization code")
        logger.info(f"Authorization code received: {code[:10]}...")
        
        # Exchange code for token
        token_data = exchange_code_for_token(code, state)
        
        logger.info("OAuth callback completed successfully")
        
        # Return success response with helpful information
        return jsonify({
            "success": True, 
            "message": "Successfully authenticated with Jobber CRM!",
            "token_info": {
                "expires_in": token_data.get("expires_in"),
                "token_type": token_data.get("token_type", "Bearer"),
                "scope": token_data.get("scope")
            },
            "next_steps": [
                "You can now use Jobber CRM endpoints",
                "Try GET /api/jobber/clients to retrieve clients",
                "Try POST /api/jobber/clients to create a new client"
            ]
        })
        
    except ValueError as e:
        logger.error(f"OAuth callback failed - validation error: {str(e)}")
        return jsonify({
            "error": "OAuth validation failed",
            "message": str(e),
            "help": "Please try the authorization process again"
        }), 400
    except Exception as e:
        logger.error(f"OAuth callback failed - unexpected error: {str(e)}")
        return jsonify({
            "error": "OAuth callback failed",
            "message": "An unexpected error occurred during authentication",
            "details": str(e)
        }), 500


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
            return jsonify({
                "error": "No Jobber token found",
                "message": "You need to authenticate with Jobber first",
                "next_step": "Visit /api/jobber/auth to start OAuth flow"
            }), 404
        
        # Calculate time until expiration
        current_time = int(time.time())
        expires_in = token["expires_at"] - current_time
        
        return jsonify({
            "success": True,
            "token_exists": True,
            "expires_at": token["expires_at"],
            "expires_in_seconds": expires_in,
            "expires_in_human": f"{expires_in // 3600}h {(expires_in % 3600) // 60}m",
            "has_refresh_token": bool(token.get("refresh_token")),
            "is_expired": expires_in <= 0,
            "status": "expired" if expires_in <= 0 else "valid"
        })
    except Exception as e:
        logger.error(f"Error in token debug endpoint: {e}")
        return jsonify({"error": str(e)}), 500


# OAuth status endpoint
@jobber_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """
    Check OAuth authentication status
    ---
    tags:
      - Jobber CRM
    responses:
      200:
        description: Authentication status
    """
    try:
        token = get_jobber_token()
        if token:
            current_time = int(time.time())
            expires_in = token["expires_at"] - current_time
            
            return jsonify({
                "authenticated": True,
                "status": "authenticated",
                "expires_in_seconds": expires_in,
                "has_refresh_token": bool(token.get("refresh_token"))
            })
        else:
            return jsonify({
                "authenticated": False,
                "status": "not_authenticated",
                "message": "No Jobber access token found",
                "auth_url": "/api/jobber/auth"
            })
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return jsonify({
            "authenticated": False,
            "status": "error",
            "error": str(e)
        }), 500


# OAuth test page for easy testing
@jobber_bp.route("/auth/test", methods=["GET"])
def auth_test_page():
    """
    Simple HTML page to test OAuth flow
    ---
    tags:
      - Jobber CRM
    responses:
      200:
        description: OAuth test page
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jobber CRM OAuth Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }
            .btn:hover { background: #0056b3; }
            .status { padding: 15px; margin: 15px 0; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .endpoint { background: #e2e3e5; padding: 10px; margin: 10px 0; border-radius: 5px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔑 Jobber CRM OAuth Test</h1>
            
            <div class="info">
                <h3>📋 Current Status</h3>
                <p>Check your current authentication status and test the OAuth flow.</p>
            </div>
            
            <div id="status"></div>
            
            <h3>🚀 OAuth Actions</h3>
            <a href="/api/jobber/auth" class="btn">🔐 Start OAuth Authorization</a>
            <button onclick="checkStatus()" class="btn">🔄 Check Status</button>
            <button onclick="testEndpoints()" class="btn">🧪 Test Endpoints</button>
            
            <h3>📚 Available Endpoints</h3>
            <div class="endpoint">GET /api/jobber/auth/status - Check authentication status</div>
            <div class="endpoint">GET /api/jobber/token/debug - Debug token information</div>
            <div class="endpoint">GET /api/jobber/clients - Get all clients (requires auth)</div>
            <div class="endpoint">POST /api/jobber/clients - Create new client (requires auth)</div>
            
            <h3>📖 How to Use</h3>
            <ol>
                <li>Click "Start OAuth Authorization" to begin the authentication process</li>
                <li>You'll be redirected to Jobber to log in and authorize the app</li>
                <li>After authorization, you'll be redirected back with an access token</li>
                <li>Use "Check Status" to verify your authentication</li>
                <li>Test the endpoints to ensure everything is working</li>
            </ol>
            
            <div class="info">
                <h3>🔧 Troubleshooting</h3>
                <p>If you encounter issues:</p>
                <ul>
                    <li>Make sure your Jobber credentials are correct</li>
                    <li>Check that the redirect URI matches your Jobber app configuration</li>
                    <li>Verify your client ID and secret are correct</li>
                    <li>Check the application logs for detailed error information</li>
                </ul>
            </div>
        </div>
        
        <script>
            // Check status on page load
            window.onload = function() {
                checkStatus();
            };
            
            function checkStatus() {
                fetch('/api/jobber/auth/status')
                    .then(response => response.json())
                    .then(data => {
                        const statusDiv = document.getElementById('status');
                        if (data.authenticated) {
                            statusDiv.innerHTML = `
                                <div class="success">
                                    <h3>✅ Authenticated with Jobber CRM!</h3>
                                    <p>Status: ${data.status}</p>
                                    <p>Expires in: ${data.expires_in_seconds} seconds</p>
                                    <p>Refresh Token: ${data.has_refresh_token ? 'Available' : 'Not available'}</p>
                                </div>
                            `;
                        } else {
                            statusDiv.innerHTML = `
                                <div class="error">
                                    <h3>❌ Not Authenticated</h3>
                                    <p>${data.message}</p>
                                    <p>Click "Start OAuth Authorization" to authenticate</p>
                                </div>
                            `;
                        }
                    })
                    .catch(error => {
                        document.getElementById('status').innerHTML = `
                            <div class="error">
                                <h3>❌ Error Checking Status</h3>
                                <p>${error.message}</p>
                            </div>
                        `;
                    });
            }
            
            function testEndpoints() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="info"><h3>🧪 Testing Endpoints...</h3><p>Please wait...</p></div>';
                
                // Test clients endpoint
                fetch('/api/jobber/clients')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            statusDiv.innerHTML = `
                                <div class="success">
                                    <h3>✅ Endpoint Test Successful!</h3>
                                    <p>GET /api/jobber/clients is working correctly</p>
                                    <p>Response: ${JSON.stringify(data, null, 2)}</p>
                                </div>
                            `;
                        } else {
                            statusDiv.innerHTML = `
                                <div class="error">
                                    <h3>❌ Endpoint Test Failed</h3>
                                    <p>GET /api/jobber/clients returned an error</p>
                                    <p>Error: ${data.error}</p>
                                </div>
                            `;
                        }
                    })
                    .catch(error => {
                        statusDiv.innerHTML = `
                            <div class="error">
                                <h3>❌ Endpoint Test Error</h3>
                                <p>${error.message}</p>
                            </div>
                        `;
                    });
            }
        </script>
    </body>
    </html>
    """


# Refresh token endpoint
@jobber_bp.route("/token/refresh", methods=["POST"])
def refresh_token():
    """
    Refresh Jobber access token using refresh token
    ---
    tags:
      - Jobber CRM
    responses:
      200:
        description: Token refreshed successfully
      400:
        description: No refresh token available
      500:
        description: Error refreshing token
    """
    try:
        token = get_jobber_token()
        if not token or not token.get("refresh_token"):
            return jsonify({
                "error": "No refresh token available",
                "message": "You need to re-authenticate with Jobber"
            }), 400
        
        new_token = refresh_jobber_token(token["refresh_token"])
        if new_token:
            return jsonify({
                "success": True,
                "message": "Token refreshed successfully",
                "new_token": new_token[:20] + "..."
            })
        else:
            return jsonify({
                "error": "Failed to refresh token",
                "message": "Please re-authenticate with Jobber"
            }), 500
            
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({
            "error": "Token refresh failed",
            "message": str(e)
        }), 500


# Manual token insertion endpoint (for testing)
@jobber_bp.route("/token/insert", methods=["POST"])
def insert_token_manually():
    """
    Manually insert Jobber access token (for testing purposes)
    ---
    tags:
      - Jobber CRM
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: Jobber access token
            refresh_token:
              type: string
              description: Jobber refresh token (optional)
            expires_in:
              type: integer
              description: Token expiration time in seconds
    responses:
      200:
        description: Token inserted successfully
      400:
        description: Invalid request data
    """
    try:
        data = request.get_json()
        if not data or not data.get("access_token"):
            return jsonify({
                "error": "Missing access token",
                "message": "access_token is required"
            }), 400
        
        access_token = data["access_token"]
        refresh_token = data.get("refresh_token", "")
        expires_in = data.get("expires_in", 3600)
        
        store_jobber_token(access_token, refresh_token, expires_in)
        
        return jsonify({
            "success": True,
            "message": "Token inserted successfully",
            "token_info": {
                "access_token": access_token[:20] + "...",
                "has_refresh_token": bool(refresh_token),
                "expires_in": expires_in
            }
        })
        
    except Exception as e:
        logger.error(f"Error inserting token manually: {e}")
        return jsonify({
            "error": "Failed to insert token",
            "message": str(e)
        }), 500


# CREATE - Create a new client
@jobber_bp.route("/clients", methods=["POST"])
def create_client_route():
    try:
        data = request.json
        logger.info(f"Creating new Jobber client: {data.get('first_name')} {data.get('last_name')}")
        client = create_client(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            company_name=data.get("company_name")
        )
        logger.info(f"Successfully created Jobber client: {client.get('id')}")
        return jsonify({"success": True, "client": client}), 201
    except Exception as e:
        logger.error(f"Failed to create Jobber client: {str(e)}")
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
