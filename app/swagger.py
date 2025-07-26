from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint, request
from app.config import Config
from app.controllers.client_controller import client_ns

# Create API instance
api = Api(
    title='Unified CRM Integration API',
    version='1.0',
    description='''
    A unified API for managing leads across multiple CRM systems

    Supported CRM Systems:
    - BuilderPrime CRM (Fully implemented)
    - HubSpot CRM (Fully implemented)
    - Jobber CRM (Fully implemented)
    - JobNimbus CRM (Fully implemented)
    - Zoho CRM (Fully implemented)

    Operations:
    - Create Lead: POST /<client_id>/leads (BuilderPrime), POST /api/hubspot/leads, POST /api/jobber/leads, POST /jobnimbus/contacts, POST /zoho/{entity_id}/leads
    - List Leads: GET /<client_id>/leads (BuilderPrime), GET /api/hubspot/leads, GET /api/jobber/clients, GET /jobnimbus/contacts, GET /zoho/{entity_id}/leads
    - Update Lead: PUT /<client_id>/leads/{lead_id} (BuilderPrime), PUT /api/hubspot/leads/{external_id}, POST /api/jobber/clients/update, PUT /jobnimbus/contacts/{jnid}, PUT /zoho/{entity_id}/leads/{lead_id}
    - Delete Lead: DELETE /<client_id>/leads/{lead_id} (BuilderPrime), DELETE /api/hubspot/leads/{external_id}, POST /api/jobber/clients/archive, DELETE /jobnimbus/contacts/{jnid}, DELETE /zoho/{entity_id}/leads/{lead_id}
    - Sync Leads: POST /<client_id>/sync (BuilderPrime), POST /api/hubspot/leads/sync
    - Get Users: GET /zoho/{entity_id}/users
    - Get Metadata: GET /zoho/{entity_id}/leads/meta

    Note: All BuilderPrime endpoints now require a client_id path parameter to access the correct API key for the client.

    Client Registration:
    - Register Client: POST /clients/ — Register a new client (company) and store their BuilderPrime and HubSpot API keys for CRM integration.
    - Get Client: GET /clients/<client_id> — Retrieve a client by their unique client ID.

    OAuth Authorization Endpoints:
    - Jobber Auth: GET /auth/jobber/authorize?userid={user_id}, GET /auth/jobber/status/{user_id}, POST /auth/jobber/refresh/{user_id}
    - Zoho Auth: GET /zoho/{entity_id}/redirect, GET /zoho/{entity_id}/status, GET /zoho/{entity_id}/refresh

    Authorization:
    - BuilderPrime: Uses API key from Vault (BUILDER_PRIME_API_KEY) - No headers required
    - HubSpot: Uses API token from Vault (HUBSPOT_API_TOKEN) - No headers required
    - Jobber: OAuth flow via /auth/jobber/authorize?userid={user_id} (Browser-based authorization required)
    - JobNimbus: Uses API key from Vault (JOBNIMBUS_API_KEY) - No headers required
    - Zoho: OAuth flow via /zoho/{entity_id}/redirect (Uses ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET from Vault)

    IMPORTANT - Jobber Authorization (OAuth 2.0):
    Jobber uses OAuth 2.0 authorization code flow with browser-based authentication.

    Step-by-Step Authorization Process:
    1. Initiate Authorization: GET /auth/jobber/authorize?userid={user_id}
       - Replace {user_id} with a unique identifier for the user (e.g., 123)
       - This redirects to Jobber's OAuth authorization page
       - User must log in to Jobber and grant permissions

    2. Complete OAuth Flow:
       - User is redirected to Jobber's authorization page
       - After granting permissions, Jobber redirects back to /auth/jobber/callback
       - The system automatically exchanges the authorization code for access/refresh tokens
       - Tokens are stored securely in the database

    3. Check Authorization Status: GET /auth/jobber/status/{user_id}
       - Returns authentication status: "authenticated", "expired", or "not_authenticated"
       - Includes token validity information

    4. Refresh Token (if needed): POST /auth/jobber/refresh/{user_id}
       - Automatically refreshes expired access tokens using refresh tokens
       - No manual intervention required

    Important Notes:
    - Each user_id requires separate authorization
    - Access tokens expire after 1 hour, refresh tokens are valid for 30 days
    - Tokens are automatically refreshed when making API calls
    - All Jobber API calls require a valid user_id that has been authorized

    IMPORTANT - Zoho Authorization (OAuth 2.0):
    Zoho uses OAuth 2.0 authorization code flow with entity-based authentication.

    IMPORTANT - Entity ID 1 Exception:
    For entity_id = 1, Zoho APIs work without any authorization required.
    This is a special case for testing and development purposes.
    All other entity IDs require the OAuth authorization flow below.

    Step-by-Step Authorization Process (for entity_id > 1):
    1. Initiate Authorization: GET /zoho/{entity_id}/redirect
       - Replace {entity_id} with a unique identifier for the Zoho entity (e.g., 123)
       - This redirects to Zoho's OAuth authorization page
       - User must log in to Zoho and grant permissions

    2. Complete OAuth Flow:
       - User is redirected to Zoho's authorization page
       - After granting permissions, Zoho redirects back to /zoho/authorize/callback
       - The system automatically exchanges the authorization code for access/refresh tokens
       - Tokens are stored securely in the database with the entity_id

    3. Check Authorization Status: GET /zoho/{entity_id}/status
       - Returns authentication status: "authenticated", "expired", or "not_authenticated"
       - Includes token validity information

    4. Refresh Token (if needed): GET /zoho/{entity_id}/refresh
       - Automatically refreshes expired access tokens using refresh tokens
       - No manual intervention required

    Important Notes:
    - Entity ID 1 works without authorization (for testing/development)
    - Each entity_id > 1 requires separate authorization
    - Access tokens expire after 1 hour, refresh tokens are valid for 60 days
    - Tokens are automatically refreshed when making API calls
    - All Zoho API calls require a valid entity_id that has been authorized
    - Zoho supports multiple entities (organizations) per account

    IMPORTANT - Vault-based Authentication:
    BuilderPrime, HubSpot, JobNimbus, and Zoho APIs use secrets stored in HashiCorp Vault automatically.
    No API key headers or request body parameters are required.
    Secrets are fetched from Vault with fallback to environment variables.

    OAuth Secrets in Vault:
    - Jobber: JOBBER_CLIENT_ID, JOBBER_CLIENT_SECRET
    - Zoho: ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET

    Key Differences Between Jobber and Zoho:
    - Jobber: User-based authentication (each user needs separate authorization)
    - Zoho: Entity-based authentication (each organization/entity needs separate authorization)
    - Jobber: Focused on service businesses (contractors, landscapers, etc.)
    - Zoho: General-purpose CRM with extensive customization options
    - Jobber: Simpler data model with clients, estimates, and invoices
    - Zoho: Complex data model with leads, contacts, accounts, and custom modules
    ''',
    doc='/swagger',
    default='api',
    default_label='CRM Operations'
    # Removed authorizations and security since no global API key is required
)

# Define detailed lead model matching BuilderPrime format
lead_model = api.model('Lead', {
    'firstName': fields.String(required=True, example="John", description="First name of the lead (Required)"),
    'lastName': fields.String(required=True, example="Smith", description="Last name of the lead (Required)"),
    'email': fields.String(required=True, example="john.smith@example.com", description="Email address (Required)"),
    'mobilePhone': fields.String(required=True, example="+18005554444", description="Mobile phone number (Required)"),
    'mobilePhoneExtension': fields.String(example="1", description="Mobile phone extension"),
    'homePhone': fields.String(example="+18005554444", description="Home phone number"),
    'homePhoneExtension': fields.String(example="2", description="Home phone extension"),
    'officePhone': fields.String(example="+18005554444", description="Office phone number"),
    'officePhoneExtension': fields.String(example="3", description="Office phone extension"),
    'fax': fields.String(example="+18005554444", description="Fax number"),
    'addressLine1': fields.String(required=True, example="123 Main Street", description="Address line 1 (Required)"),
    'addressLine2': fields.String(example="Suite 2", description="Address line 2"),
    'city': fields.String(required=True, example="Los Angeles", description="City (Required)"),
    'state': fields.String(required=True, example="CA", description="State (Required)"),
    'zip': fields.String(required=True, example="12345", description="ZIP code (Required)"),
    'companyName': fields.String(example="Widgets Galore", description="Company name"),
    'title': fields.String(example="President", description="Title"),
    'notes': fields.String(example="Some notes", description="Additional notes"),
    'leadStatus': fields.String(example="Lead Received", description="Status of the lead"),
    'leadSource': fields.String(example="Facebook", description="Source of the lead"),
    'salesPersonFirstName': fields.String(example="Alice", description="Sales person's first name"),
    'salesPersonLastName': fields.String(example="Thompson", description="Sales person's last name"),
    'leadSetterFirstName': fields.String(example="Bob", description="Lead setter's first name"),
    'leadSetterLastName': fields.String(example="Roberts", description="Lead setter's last name"),
    'className': fields.String(example="Residential", description="Class name"),
    'projectType': fields.String(example="Kitchen Renovation", description="Type of project"),
    'externalId': fields.String(example="AB-4617", description="External identifier"),
    'dialerStatus': fields.String(example="1st Attempt", description="Dialer status")
})

lead_response_model = api.inherit('LeadResponse', lead_model, {
    'id': fields.Integer(description='Lead ID'),
    'crmSystem': fields.String(description='CRM system'),
    'crmExternalId': fields.String(description='External CRM ID'),
    'createdAt': fields.DateTime(description='Creation timestamp'),
    'updatedAt': fields.DateTime(description='Last update timestamp')
})

leads_list_model = api.model('LeadsList', {
    'total': fields.Integer(description='Total number of leads'),
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Number of leads per page'),
    'leads': fields.List(fields.Nested(lead_response_model), description='List of leads'),
})

# Jobber CRM Models
jobber_email_model = api.model('JobberEmail', {
    'address': fields.String(required=True, example="alice.johnson@wondertech.com", description="Email address"),
    'primary': fields.Boolean(example=True, description="Whether this is the primary email")
})

jobber_phone_model = api.model('JobberPhone', {
    'number': fields.String(required=True, example="+19876543210", description="Phone number"),
    'primary': fields.Boolean(example=True, description="Whether this is the primary phone")
})

jobber_address_model = api.model('JobberAddress', {
    'street1': fields.String(example="42 Rainbow Road", description="Primary street address"),
    'street2': fields.String(example="Building B", description="Secondary street address"),
    'city': fields.String(example="San Francisco", description="City"),
    'province': fields.String(example="CA", description="State/Province"),
    'country': fields.String(example="USA", description="Country"),
    'postalCode': fields.String(example="94107", description="Postal/ZIP code")
})

jobber_create_client_model = api.model('JobberCreateClient', {
    'firstName': fields.String(example="aLLEN", description="First name of the client"),
    'lastName': fields.String(example="wORKS", description="Last name of the client"),
    'companyName': fields.String(example="WonderTech Inc", description="Company name"),
    'emails': fields.List(fields.Nested(jobber_email_model), description="List of email addresses"),
    'phones': fields.List(fields.Nested(jobber_phone_model), description="List of phone numbers"),
    'billingAddress': fields.Nested(jobber_address_model, description="Billing address information")
})

jobber_update_client_model = api.model('JobberUpdateClient', {
    'clientId': fields.String(required=True, example="Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTI3MzI5MDA=", description="Jobber client ID (Required)"),
    'firstName': fields.String(example="Jane", description="First name of the client"),
    'lastName': fields.String(example="Smith", description="Last name of the client"),
    'companyName': fields.String(example="FutureTech", description="Company name"),
    'emailsToAdd': fields.List(fields.Nested(jobber_email_model), description="New email addresses to add"),
    'phonesToAdd': fields.List(fields.Nested(jobber_phone_model), description="New phone numbers to add"),
    'propertyAddressesToAdd': fields.List(fields.Nested(jobber_address_model), description="New property addresses to add"),
    'phonesToDelete': fields.List(fields.String, example=["Z2lkOi8vSm9iYmVyL0NsaWVudFBob25lTnVtYmVyLzEwNjE2NDk5Nw=="], description="Phone IDs to delete"),
    'emailsToDelete': fields.List(fields.String, example=["Z2lkOi8vSm9iYmVyL0VtYWlsLzc4MzMyMTMx"], description="Email IDs to delete")
})

jobber_archive_client_model = api.model('JobberArchiveClient', {
    'clientId': fields.String(required=True, example="Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTI3MzI5MDA=", description="Jobber client ID to archive (Required)")
})

jobber_client_response_model = api.model('JobberClientResponse', {
    'id': fields.String(description="Client ID"),
    'firstName': fields.String(description="First name"),
    'lastName': fields.String(description="Last name"),
    'companyName': fields.String(description="Company name"),
    'isLead': fields.Boolean(description="Whether this is a lead"),
    'isCompany': fields.Boolean(description="Whether this is a company"),
    'jobberWebUri': fields.String(description="Jobber web URI"),
    'balance': fields.Float(description="Account balance"),
    'emails': fields.List(fields.Raw, description="Email addresses"),
    'phones': fields.List(fields.Raw, description="Phone numbers"),
    'clientProperties': fields.Raw(description="Client properties"),
    'sourceAttribution': fields.Raw(description="Source attribution")
})

jobber_clients_list_model = api.model('JobberClientsList', {
    'data': fields.List(fields.Nested(jobber_client_response_model), description="List of clients"),
    'total_count': fields.Integer(description="Total number of clients"),
    'pages_fetched': fields.Integer(description="Number of pages fetched")
})



# Zoho CRM Models
zoho_lead_model = api.model('ZohoLead', {
    'First_Name': fields.String(example="John", description="First name of the lead"),
    'Last_Name': fields.String(example="Smith", description="Last name of the lead"),
    'Company': fields.String(example="Tech Solutions Inc", description="Company name"),
    'Lead_Source': fields.String(example="Website", description="Source of the lead"),
    'Lead_Status': fields.String(example="New", description="Status of the lead"),
    'Industry': fields.String(example="Technology", description="Industry"),
    'Annual_Revenue': fields.Float(example=1000000.0, description="Annual revenue"),
    'Phone': fields.String(example="+18005554444", description="Phone number"),
    'Mobile': fields.String(example="+18005554445", description="Mobile number"),
    'Email': fields.String(example="john.smith@example.com", description="Email address"),
    'Secondary_Email': fields.String(example="john.smith2@example.com", description="Secondary email"),
    'Skype_ID': fields.String(example="john.smith.skype", description="Skype ID"),
    'Website': fields.String(example="https://example.com", description="Website URL"),
    'Rating': fields.String(example="Hot", description="Lead rating"),
    'No_of_Employees': fields.Integer(example=50, description="Number of employees"),
    'Email_Opt_out': fields.Boolean(example=False, description="Email opt out status"),
    'Street': fields.String(example="123 Main Street", description="Street address"),
    'City': fields.String(example="Los Angeles", description="City"),
    'State': fields.String(example="CA", description="State"),
    'Zip_Code': fields.String(example="12345", description="ZIP code"),
    'Country': fields.String(example="USA", description="Country"),
    'Created_By': fields.String(description="User who created the lead"),
    'Modified_By': fields.String(description="User who last modified the lead"),
    'Created_Time': fields.String(description="Creation timestamp"),
    'Modified_Time': fields.String(description="Last modification timestamp"),
    'Owner': fields.String(description="Lead owner"),
    'Lead_Owner': fields.String(description="Lead owner"),
    'Twitter': fields.String(example="@johnsmith", description="Twitter handle"),
    'Secondary_URL': fields.String(example="https://secondary.example.com", description="Secondary URL"),
    'Address': fields.String(description="Full address")
})

zoho_leads_response_model = api.model('ZohoLeadsResponse', {
    'data': fields.List(fields.Nested(zoho_lead_model), description="List of leads"),
    'info': fields.Raw(description="Response metadata")
})

zoho_user_model = api.model('ZohoUser', {
    'id': fields.String(example="6707647000000503001", description="User ID"),
    'name': fields.String(example="John Doe", description="Full name"),
    'email': fields.String(example="john.doe@example.com", description="Email address")
})

zoho_users_response_model = api.model('ZohoUsersResponse', {
    'users': fields.List(fields.Nested(zoho_user_model), description="List of users")
})

zoho_metadata_response_model = api.model('ZohoMetadataResponse', {
    'status': fields.String(example="Success", description="Response status"),
    'data': fields.Raw(description="Metadata information")
})

zoho_auth_success_model = api.model('ZohoAuthSuccess', {
    'status': fields.String(example="success", description="Authorization status"),
    'message': fields.String(example="Authorization successful", description="Success message")
})

zoho_auth_error_model = api.model('ZohoAuthError', {
    'error': fields.String(example="Unauthorized", description="Error type"),
    'message': fields.String(example="Entity not authenticated with Zoho", description="Error message")
})

zoho_create_lead_model = api.model('ZohoCreateLead', {
    'data': fields.List(fields.Raw, required=True, description="Array of lead objects to create"),
    'layout_id': fields.String(required=False, description="Optional layout ID")
})

error_model = api.model('Error', {
    'error': fields.String(description='Error type'),
    'message': fields.String(description='Error message'),
})

success_model = api.model('Success', {
    'message': fields.String(description='Success message'),
    'id': fields.Integer(description='Lead ID'),
    'externalId': fields.String(description='External CRM ID'),
})

sync_result_model = api.model('SyncResult', {
    'message': fields.String(description='Sync result message'),
    'synced': fields.Integer(description='Number of leads synced'),
    'errors': fields.Integer(description='Number of errors'),
})

# Vault Models
vault_status_model = api.model('VaultStatus', {
    'initialized': fields.Boolean(description='Whether Vault is initialized'),
    'sealed': fields.Boolean(description='Whether Vault is sealed'),
    'standby': fields.Boolean(description='Whether Vault is in standby mode'),
    'performance_standby': fields.Boolean(description='Whether Vault is in performance standby mode'),
    'version': fields.String(description='Vault version'),
    'cluster_name': fields.String(description='Vault cluster name'),
    'cluster_id': fields.String(description='Vault cluster ID'),
    'error': fields.String(description='Error message if any')
})

vault_connection_model = api.model('VaultConnection', {
    'connected': fields.Boolean(description='Whether connected to Vault'),
    'authenticated': fields.Boolean(description='Whether authenticated with Vault'),
    'can_read_secrets': fields.Boolean(description='Whether can read secrets'),
    'vault_url': fields.String(description='Vault server URL'),
    'namespace': fields.String(description='Vault namespace'),
    'secret_path': fields.String(description='Default secret path'),
    'error': fields.String(description='Error message if any')
})

vault_secret_model = api.model('VaultSecret', {
    'path': fields.String(description='Secret path'),
    'data': fields.Raw(description='Secret data'),
    'message': fields.String(description='Response message')
})

vault_secrets_model = api.model('VaultSecrets', {
    'secrets': fields.Raw(description='Dictionary of secrets'),
    'count': fields.Integer(description='Number of secrets'),
    'message': fields.String(description='Response message')
})

# Define query parameters
get_parser = api.parser()
get_parser.add_argument('last-modified-since', type=str, help='Filter by last modified date (milliseconds since epoch)')
get_parser.add_argument('lead-status', type=str, help='Filter by lead status')
get_parser.add_argument('lead-source', type=str, help='Filter by lead source')
get_parser.add_argument('dialer-status', type=str, help='Filter by dialer status')
get_parser.add_argument('phone', type=str, help='Filter by phone number')
get_parser.add_argument('page', type=int, default=1, help='Page number (default: 1)')
get_parser.add_argument('per_page', type=int, default=10, help='Items per page (default: 10, max: 500)')

pagination_model = api.model('PaginationResponse', {
    'total': fields.Integer(description='Total number of leads'),
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Number of items per page'),
    'leads': fields.List(fields.Nested(lead_response_model))
})

# Create namespaces for each CRM
builder_prime_ns = Namespace('builder-prime', description='BuilderPrime CRM operations')
hubspot_ns = Namespace('hubspot', description='HubSpot CRM operations')
jobber_ns = Namespace('jobber', description='Jobber CRM operations')
zoho_ns = Namespace('zoho', description='Zoho CRM operations')
vault_ns = Namespace('vault', description='Vault operations')

# Add namespaces to API
api.add_namespace(builder_prime_ns)
api.add_namespace(hubspot_ns)
api.add_namespace(jobber_ns)
api.add_namespace(zoho_ns)
api.add_namespace(vault_ns)
api.add_namespace(client_ns, path='/clients')

# Import controllers to register them with the API
import app.controllers.builder_prime_controller
import app.controllers.hubspot_controller
import app.controllers.jobber_controller
import app.controllers.zoho_controller
import app.controllers.client_controller
# If you have a vault controller, update its import as well
# import app.controllers.vault_controller