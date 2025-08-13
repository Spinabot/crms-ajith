from flask_restx import Api, Resource, fields
from flask import Blueprint
from controllers.client_controller import ClientController
from controllers.builderprime_controller import BuilderPrimeController
from controllers import jobber_controller

# Create blueprint for Swagger
swagger_bp = Blueprint('swagger', __name__)

# Create API instance
api = Api(
    swagger_bp,
    title='CRM Integration API',
    version='1.0',
    description='A comprehensive API for managing CRM integrations with multiple platforms',
    doc='/swagger',
    default='clients',
    default_label='Client Management Operations'
)

# Define namespaces
client_ns = api.namespace('api/clients', description='Client operations')
builderprime_ns = api.namespace('api/builderprime', description='BuilderPrime CRM operations')
jobber_ns = api.namespace('api/jobber', description='Jobber CRM operations')
capsule_ns = api.namespace('api/capsule', description='Capsule CRM operations')
jobnimbus_ns = api.namespace('api/jobnimbus', description='JobNimbus CRM operations')

# Define CRM integration model
crm_integration_model = api.model('CRMIntegration', {
    'crm_name': fields.String(description='CRM system name'),
    'crm_id': fields.Integer(description='CRM system ID'),
    'domain': fields.String(description='Client domain (for BuilderPrime)'),
    'has_api_key': fields.Boolean(description='Whether API key is configured'),
    'credentials': fields.Raw(description='Full credentials JSON object'),
    'created_at': fields.String(description='CRM integration creation timestamp'),
    'updated_at': fields.String(description='CRM integration last update timestamp')
})

# Define models for request/response documentation
client_model = api.model('Client', {
    'id': fields.Integer(readonly=True, description='Client ID'),
    'company_name': fields.String(required=True, description='Company name', example='Spinabot'),
    'email': fields.String(required=True, description='Client email', example='contact@spinabot.com'),
    'other_contact_info': fields.String(description='Additional contact information', example='Phone: 123-456-7890'),
    'created_at': fields.String(description='Client creation timestamp'),
    'updated_at': fields.String(description='Client last update timestamp'),
    'crm_integrations': fields.List(fields.Nested(crm_integration_model), description='CRM integrations with full details'),
    'total_crm_integrations': fields.Integer(description='Total number of CRM integrations')
})

# Define nested BuilderPrime credentials model
builderprime_credentials_model = api.model('BuilderPrimeCredentials', {
    'api_key': fields.String(required=True, description='BuilderPrime API key', example='bp_api_key_abc123'),
    'domain': fields.String(required=True, description='BuilderPrime subdomain', example='spinbot')
})

client_create_model = api.model('ClientCreate', {
    'company_name': fields.String(required=True, description='Company name', example='Spinabot'),
    'email': fields.String(required=True, description='Client email', example='contact@spinabot.com'),
    'other_contact_info': fields.String(description='Additional contact information', example='Phone: 555-123-4567'),
    'builderprime': fields.Nested(builderprime_credentials_model, description='BuilderPrime credentials'),
    'hubspot_api_key': fields.String(description='HubSpot API key', example='hs_api_key_def456')
})

client_update_model = api.model('ClientUpdate', {
    'company_name': fields.String(description='Company name', example='Updated Spinabot'),
    'email': fields.String(description='Client email', example='updated@spinabot.com'),
    'other_contact_info': fields.String(description='Additional contact information', example='Phone: 555-123-4567'),
    'builderprime': fields.Nested(builderprime_credentials_model, description='BuilderPrime credentials'),
    'hubspot_api_key': fields.String(description='HubSpot API key', example='new_hs_api_key_def456')
})

client_list_model = api.model('ClientList', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.List(fields.Nested(client_model), description='List of clients')
})

client_response_model = api.model('ClientResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Nested(client_model, description='Client data')
})

error_model = api.model('Error', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Error message'),
    'data': fields.Raw(description='Error data')
})

# Define BuilderPrime models
custom_field_model = api.model('CustomField', {
    'name': fields.String(required=True, description='Custom field name', example='Budget'),
    'value': fields.String(required=True, description='Custom field value', example='5000')
})

builderprime_lead_model = api.model('BuilderPrimeLead', {
    'first_name': fields.String(required=True, description='First name', example='Marcus'),
    'last_name': fields.String(required=True, description='Last name', example='Rodriguez'),
    'email': fields.String(required=True, description='Email address', example='marcus.rodriguez@techcorp.com'),
    'mobile_phone': fields.String(description='Mobile phone number', example='+15551234567'),
    'mobile_phone_extension': fields.String(description='Mobile phone extension', example='1'),
    'home_phone': fields.String(description='Home phone number', example='+15559876543'),
    'home_phone_extension': fields.String(description='Home phone extension', example='2'),
    'office_phone': fields.String(description='Office phone number', example='+15555555555'),
    'office_phone_extension': fields.String(description='Office phone extension', example='3'),
    'fax': fields.String(description='Fax number', example='+15554443333'),
    'address_line1': fields.String(description='Address line 1', example='456 Innovation Drive'),
    'address_line2': fields.String(description='Address line 2', example='Floor 3'),
    'city': fields.String(description='City', example='Austin'),
    'state': fields.String(description='State', example='TX'),
    'zip': fields.String(description='ZIP code', example='78701'),
    'company_name': fields.String(description='Company name', example='TechCorp Solutions'),
    'title': fields.String(description='Job title', example='Senior Developer'),
    'notes': fields.String(description='Additional notes', example='Interested in custom software development for their startup'),
    'lead_status_name': fields.String(description='Lead status', example='Qualified Lead'),
    'lead_source_name': fields.String(description='Lead source', example='LinkedIn'),
    'sales_person_first_name': fields.String(description='Sales person first name', example='Sarah'),
    'sales_person_last_name': fields.String(description='Sales person last name', example='Johnson'),
    'lead_setter_first_name': fields.String(description='Lead setter first name', example='Mike'),
    'lead_setter_last_name': fields.String(description='Lead setter last name', example='Chen'),
    'class_name': fields.String(description='Class name', example='Commercial'),
    'project_type_name': fields.String(description='Project type', example='Custom Software Development'),
    'external_id': fields.String(description='External ID', example='TC-2024-001'),
    'dialer_status': fields.String(description='Dialer status', example='2nd Attempt'),
    'custom_fields': fields.List(fields.Nested(custom_field_model), description='Custom fields')
})

builderprime_response_model = api.model('BuilderPrimeResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='BuilderPrime API response data')
})

builderprime_lead_response_model = api.model('BuilderPrimeLeadResponse', {
    'id': fields.Integer(description='Database record ID'),
    'source_client_id': fields.String(description='Source client ID'),
    'crm_client_id': fields.String(description='BuilderPrime client ID'),
    'name': fields.String(description='Lead name'),
    'email': fields.String(description='Lead email'),
    'phone_number': fields.String(description='Lead phone number'),
    'opportunity_id': fields.String(description='BuilderPrime opportunity ID'),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
})

builderprime_leads_response_model = api.model('BuilderPrimeLeadsResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.List(fields.Nested(builderprime_lead_response_model), description='List of BuilderPrime leads')
})

# Define model for BuilderPrime API data response
builderprime_api_data_model = api.model('BuilderPrimeAPIData', {
    'id': fields.Integer(description='Internal opportunity identifier'),
    'firstName': fields.String(description='First name'),
    'lastName': fields.String(description='Last name'),
    'phoneNumber': fields.String(description='Phone number'),
    'homePhoneNumber': fields.String(description='Home phone number'),
    'officePhoneNumber': fields.String(description='Office phone number'),
    'emailAddress': fields.String(description='Email address'),
    'type': fields.String(description='Type (NEW or REHASH)'),
    'addressLine1': fields.String(description='Address line 1'),
    'addressLine2': fields.String(description='Address line 2'),
    'city': fields.String(description='City'),
    'state': fields.String(description='State'),
    'zip': fields.String(description='ZIP code'),
    'companyName': fields.String(description='Company name'),
    'doNotContact': fields.Boolean(description='Do not contact flag'),
    'dialerStatus': fields.String(description='Dialer status'),
    'clientId': fields.Integer(description='Internal client identifier'),
    'leadStatusName': fields.String(description='Lead status name'),
    'leadSourceDescription': fields.String(description='Lead source description'),
    'salesPersonFirstName': fields.String(description='Sales person first name'),
    'salesPersonLastName': fields.String(description='Sales person last name'),
    'leadSetterFirstName': fields.String(description='Lead setter first name'),
    'leadSetterLastName': fields.String(description='Lead setter last name'),
    'projectTypeDescription': fields.String(description='Project type description'),
    'locationName': fields.String(description='Location name'),
    'buildingTypeDescription': fields.String(description='Building type description'),
    'bestContactTime': fields.String(description='Best contact time'),
    'bestContactMethod': fields.String(description='Best contact method'),
    'estimatedValue': fields.Integer(description='Estimated value'),
    'closeProbability': fields.Integer(description='Close probability'),
    'createdDate': fields.Integer(description='Created date (milliseconds since epoch)'),
    'lastModifiedDate': fields.Integer(description='Last modified date (milliseconds since epoch)')
})

builderprime_api_response_model = api.model('BuilderPrimeAPIResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='BuilderPrime API response data including builderprime_data array')
})

# Define Jobber models
jobber_client_create_model = api.model('JobberClientCreate', {
    'first_name': fields.String(required=True, description='First name', example='John'),
    'last_name': fields.String(required=True, description='Last name', example='Doe'),
    'email': fields.String(required=True, description='Email address', example='john.doe@example.com'),
    'company_name': fields.String(description='Company name', example='Acme Corp')
})

jobber_response_model = api.model('JobberResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Jobber API response data')
})

# Define Capsule CRM models
capsule_person_model = api.model('CapsulePerson', {
    'id': fields.String(description='Person ID'),
    'firstName': fields.String(description='First name'),
    'lastName': fields.String(description='Last name'),
    'emailAddresses': fields.List(fields.Raw, description='Email addresses'),
    'type': fields.String(description='Person type', example='person')
})

capsule_person_create_model = api.model('CapsulePersonCreate', {
    'party': fields.Nested(api.model('CapsuleParty', {
        'type': fields.String(required=True, description='Party type', example='person'),
        'firstName': fields.String(description='First name'),
        'lastName': fields.String(description='Last name'),
        'emailAddresses': fields.List(fields.Nested(api.model('CapsuleEmail', {
            'address': fields.String(description='Email address')
        })), description='Email addresses')
    }), description='Party information')
})

capsule_response_model = api.model('CapsuleResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Capsule API response data')
})

# Define JobNimbus models
jobnimbus_contact_model = api.model('JobNimbusContact', {
    'firstName': fields.String(required=True, description='First name', example='Jane'),
    'lastName': fields.String(required=True, description='Last name', example='Roofer'),
    'email': fields.String(description='Email', example='jane@example.com'),
    'phone': fields.String(description='Phone', example='555-1212'),
    'type': fields.String(description='Contact type', example='lead')
})

jobnimbus_response_model = api.model('JobNimbusResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'data': fields.Raw(description='JobNimbus API response data')
})

@client_ns.route('/')
class ClientList(Resource):
    @client_ns.doc('create_client')
    @client_ns.expect(client_create_model)
    @client_ns.marshal_with(client_response_model, code=201)
    @client_ns.response(400, 'Validation Error', error_model)
    @client_ns.response(500, 'Internal Server Error', error_model)
    def post(self):
        """
        Create a new client

        Create a new client with company name, email, and optional CRM integrations.
        Supports BuilderPrime and HubSpot API key configuration.
        """
        return ClientController.create_client()

    @client_ns.doc('get_all_clients')
    @client_ns.marshal_with(client_list_model)
    @client_ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """
        Get all clients

        Retrieve a list of all registered clients in the system with their CRM integrations.
        """
        return ClientController.get_all_clients()

@client_ns.route('/<int:client_id>')
@client_ns.param('client_id', 'The client identifier')
class ClientDetail(Resource):
    @client_ns.doc('get_client')
    @client_ns.marshal_with(client_response_model)
    @client_ns.response(404, 'Client not found', error_model)
    @client_ns.response(400, 'Invalid client ID', error_model)
    @client_ns.response(500, 'Internal Server Error', error_model)
    def get(self, client_id):
        """
        Get client by ID

        Retrieve a specific client by their unique identifier with CRM integration details.
        """
        return ClientController.get_client_by_id(client_id)

    @client_ns.doc('update_client')
    @client_ns.expect(client_update_model)
    @client_ns.marshal_with(client_response_model)
    @client_ns.response(200, 'Client updated successfully', client_response_model)
    @client_ns.response(400, 'Validation Error', error_model)
    @client_ns.response(404, 'Client not found', error_model)
    @client_ns.response(409, 'Email already exists', error_model)
    @client_ns.response(500, 'Internal Server Error', error_model)
    def put(self, client_id):
        """
        Update client by ID

        Update an existing client's information and CRM authentication details.
        All fields are optional - only provided fields will be updated.
        """
        return ClientController.update_client(client_id)

@builderprime_ns.route('/clients/<int:client_id>/leads')
@builderprime_ns.param('client_id', 'The client identifier')
class BuilderPrimeLead(Resource):
    @builderprime_ns.doc('create_builderprime_lead')
    @builderprime_ns.expect(builderprime_lead_model)
    @builderprime_ns.marshal_with(builderprime_response_model, code=201)
    @builderprime_ns.response(400, 'Validation Error', error_model)
    @builderprime_ns.response(404, 'Client not found', error_model)
    @builderprime_ns.response(503, 'BuilderPrime API Error', error_model)
    @builderprime_ns.response(500, 'Internal Server Error', error_model)
    def post(self, client_id):
        """
        Create a new lead/opportunity in BuilderPrime

        Create a new lead in BuilderPrime CRM for the specified client.
        Uses the client's BuilderPrime domain and API key from their CRM authentication.
        Data is also stored in the local database for tracking.
        """
        return BuilderPrimeController.create_lead(client_id)

    @builderprime_ns.doc('get_builderprime_client_leads')
    @builderprime_ns.marshal_with(builderprime_leads_response_model)
    @builderprime_ns.response(400, 'Invalid client ID', error_model)
    @builderprime_ns.response(500, 'Internal Server Error', error_model)
    def get(self, client_id):
        """
        Get BuilderPrime leads for a specific client from the database

        Retrieve all BuilderPrime leads that were created for the specified client.
        """
        return BuilderPrimeController.get_leads(client_id)

@builderprime_ns.route('/leads')
class BuilderPrimeAllLeads(Resource):
    @builderprime_ns.doc('get_all_builderprime_leads')
    @builderprime_ns.marshal_with(builderprime_leads_response_model)
    @builderprime_ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """
        Get all BuilderPrime leads from database

        Retrieve all BuilderPrime leads from the database, ordered by creation date.
        """
        return BuilderPrimeController.get_leads()

@builderprime_ns.route('/clients/<int:client_id>/data')
@builderprime_ns.param('client_id', 'The client identifier')
class BuilderPrimeAPIData(Resource):
    @builderprime_ns.doc('fetch_builderprime_api_data')
    @builderprime_ns.marshal_with(builderprime_api_response_model)
    @builderprime_ns.response(400, 'Invalid client ID or parameters', error_model)
    @builderprime_ns.response(404, 'Client not found', error_model)
    @builderprime_ns.response(503, 'BuilderPrime API Error', error_model)
    @builderprime_ns.response(500, 'Internal Server Error', error_model)
    def get(self, client_id):
        """
        Fetch data from BuilderPrime API from builderprime directly

        Fetch data directly from BuilderPrime API for the specified client.
        Uses the client's BuilderPrime domain and API key from their CRM authentication.

        Query Parameters:
        - last-modified-since (int, optional): Date in milliseconds since epoch (up to 1 year ago)
        - lead-status (string, optional): Lead status name to filter by
        - lead-source (string, optional): Lead source name to filter by
        - dialer-status (string, optional): Dialer status to filter by
        - phone (string, optional): Phone number to search for (E.164 format recommended)
        - limit (int, optional): Number of records to return (max 500)
        - page (int, optional): Page number (starts with 0)
        """
        return BuilderPrimeController.fetch_builderprime_data(client_id)

@builderprime_ns.route('/clients/<int:client_id>/leads/<opportunity_id>')
@builderprime_ns.param('client_id', 'The client identifier')
@builderprime_ns.param('opportunity_id', 'The BuilderPrime opportunity identifier')
class BuilderPrimeLeadUpdate(Resource):
    @builderprime_ns.doc('update_builderprime_lead')
    @builderprime_ns.expect(builderprime_lead_model)
    @builderprime_ns.marshal_with(builderprime_response_model)
    @builderprime_ns.response(400, 'Invalid client ID or opportunity ID', error_model)
    @builderprime_ns.response(404, 'Client not found', error_model)
    @builderprime_ns.response(503, 'BuilderPrime API Error', error_model)
    @builderprime_ns.response(500, 'Internal Server Error', error_model)
    def put(self, client_id, opportunity_id):
        """
        Update a lead/opportunity in BuilderPrime

        Update an existing lead in BuilderPrime CRM for the specified client and opportunity.
        Uses the client's BuilderPrime domain and API key from their CRM authentication.
        Only non-blank values will be updated - omit fields that don't need to be modified.
        Data is also updated in the local database for tracking.
        """
        return BuilderPrimeController.update_lead(client_id, opportunity_id)

@jobber_ns.route('/clients')
class JobberClients(Resource):
    @jobber_ns.doc('get_jobber_clients')
    @jobber_ns.marshal_with(jobber_response_model)
    @jobber_ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """
        Get all clients from Jobber

        Retrieve a list of all clients from the Jobber CRM system.
        """
        from controllers.jobber_controller import list_clients_route
        return list_clients_route()

    @jobber_ns.doc('create_jobber_client')
    @jobber_ns.expect(jobber_client_create_model)
    @jobber_ns.marshal_with(jobber_response_model, code=201)
    @jobber_ns.response(400, 'Validation Error', error_model)
    @jobber_ns.response(500, 'Internal Server Error', error_model)
    def post(self):
        """
        Create a new client in Jobber

        Create a new client in the Jobber CRM system with the provided information.
        """
        from controllers.jobber_controller import create_client_route
        return create_client_route()

@jobber_ns.route('/jobs')
class JobberJobs(Resource):
    @jobber_ns.doc('get_jobber_jobs')
    @jobber_ns.marshal_with(jobber_response_model)
    @jobber_ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """
        Get all jobs from Jobber

        Retrieve a list of all jobs from the Jobber CRM system.
        """
        from services.jobber_service import fetch_jobs
        try:
            data = fetch_jobs()
            if data and "jobs" in data and "nodes" in data["jobs"]:
                jobs = []
                for job in data["jobs"]["nodes"]:
                    job_data = {
                        "id": str(job.get("id", "")),
                        "job_number": job.get("jobNumber", ""),
                        "title": job.get("title", ""),
                        "status": job.get("status", "")
                    }
                    jobs.append(job_data)
                
                return {"success": True, "message": "Jobs retrieved successfully", "data": jobs}, 200
            else:
                return {"success": False, "message": "No job data found", "data": []}, 200
        except Exception as e:
            return {"success": False, "message": f"Error fetching jobs: {str(e)}", "data": None}, 500

@jobber_ns.route('/clients/<string:client_id>')
@jobber_ns.param('client_id', 'The Jobber client identifier')
class JobberClientDetail(Resource):
    @jobber_ns.doc('get_jobber_client_by_id')
    @jobber_ns.marshal_with(jobber_response_model)
    @jobber_ns.response(404, 'Client not found', error_model)
    @jobber_ns.response(500, 'Internal Server Error', error_model)
    def get(self, client_id):
        """
        Get a specific Jobber client by ID

        Retrieve a single client from the Jobber CRM system by their unique identifier.
        """
        from controllers.jobber_controller import get_client_route
        return get_client_route(client_id)

    @jobber_ns.doc('update_jobber_client')
    @jobber_ns.expect(jobber_client_create_model)
    @jobber_ns.marshal_with(jobber_response_model)
    @jobber_ns.response(400, 'Validation Error', error_model)
    @jobber_ns.response(404, 'Client not found', error_model)
    @jobber_ns.response(500, 'Internal Server Error', error_model)
    def put(self, client_id):
        """
        Update a Jobber client by ID

        Update an existing client in the Jobber CRM system with the provided information.
        """
        from controllers.jobber_controller import update_client_route
        return update_client_route(client_id)

    @jobber_ns.doc('delete_jobber_client')
    @jobber_ns.marshal_with(jobber_response_model)
    @jobber_ns.response(404, 'Client not found', error_model)
    @jobber_ns.response(500, 'Internal Server Error', error_model)
    def delete(self, client_id):
        """
        Delete a Jobber client by ID

        Remove a client from the Jobber CRM system by their unique identifier.
        """
        from controllers.jobber_controller import delete_client_route
        return delete_client_route(client_id)


# ---------- Capsule CRM Routes ----------

@capsule_ns.route('/auth')
class CapsuleAuth(Resource):
    @capsule_ns.doc('start_capsule_auth')
    @capsule_ns.response(302, 'Redirect to Capsule authorization page')
    def get(self):
        """
        Start OAuth authorization for Capsule CRM

        Redirects to Capsule's OAuth authorization page to begin the authentication process.
        """
        from controllers.capsule_controller import start_auth
        return start_auth()


@capsule_ns.route('/callback')
class CapsuleCallback(Resource):
    @capsule_ns.doc('handle_capsule_callback')
    @capsule_ns.param('code', 'Authorization code from Capsule', required=True)
    @capsule_ns.response(200, 'Token stored successfully')
    @capsule_ns.response(400, 'Missing authorization code')
    @capsule_ns.response(500, 'Error exchanging code for token')
    def get(self):
        """
        Handle OAuth callback from Capsule CRM

        Processes the authorization code returned by Capsule and exchanges it for access tokens.
        """
        from controllers.capsule_controller import auth_callback
        return auth_callback()


@capsule_ns.route('/people')
class CapsulePeople(Resource):
    @capsule_ns.doc('get_capsule_people')
    @capsule_ns.marshal_with(capsule_response_model)
    @capsule_ns.response(200, 'A list of contacts')
    @capsule_ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """
        Get all Capsule People (Contacts)

        Retrieve a list of all people/contacts from the Capsule CRM system.
        """
        from controllers.capsule_controller import get_people
        return get_people()

    @capsule_ns.doc('create_capsule_person')
    @capsule_ns.expect(capsule_person_create_model)
    @capsule_ns.marshal_with(capsule_response_model, code=201)
    @capsule_ns.response(201, 'Person created')
    @capsule_ns.response(400, 'Validation Error', error_model)
    @capsule_ns.response(500, 'Internal Server Error', error_model)
    def post(self):
        """
        Create a Capsule Person

        Create a new person/contact in the Capsule CRM system.
        """
        from controllers.capsule_controller import create_person
        return create_person()


@capsule_ns.route('/people/<string:person_id>')
@capsule_ns.param('person_id', 'The Capsule person identifier')
class CapsulePersonDetail(Resource):
    @capsule_ns.doc('get_capsule_person')
    @capsule_ns.marshal_with(capsule_response_model)
    @capsule_ns.response(200, 'Person details')
    @capsule_ns.response(404, 'Person not found', error_model)
    @capsule_ns.response(500, 'Internal Server Error', error_model)
    def get(self, person_id):
        """
        Get a Capsule Person by ID

        Retrieve a single person/contact from the Capsule CRM system by their unique identifier.
        """
        from controllers.capsule_controller import get_person
        return get_person(person_id)

    @capsule_ns.doc('update_capsule_person')
    @capsule_ns.expect(capsule_person_create_model)
    @capsule_ns.marshal_with(capsule_response_model)
    @capsule_ns.response(200, 'Person updated')
    @capsule_ns.response(400, 'Validation Error', error_model)
    @capsule_ns.response(404, 'Person not found', error_model)
    @capsule_ns.response(500, 'Internal Server Error', error_model)
    def put(self, person_id):
        """
        Update a Capsule Person

        Update an existing person/contact in the Capsule CRM system.
        """
        from controllers.capsule_controller import update_person
        return update_person(person_id)

    @capsule_ns.doc('delete_capsule_person')
    @capsule_ns.response(204, 'Person deleted')
    @capsule_ns.response(404, 'Person not found', error_model)
    @capsule_ns.response(500, 'Internal Server Error', error_model)
    def delete(self, person_id):
        """
        Delete a Capsule Person

        Remove a person/contact from the Capsule CRM system by their unique identifier.
        """
        from controllers.capsule_controller import delete_person
        return delete_person(person_id)

# ---------- JobNimbus Routes ----------

@jobnimbus_ns.route('/health')
class JobNimbusHealth(Resource):
    @jobnimbus_ns.doc('jobnimbus_health')
    @jobnimbus_ns.marshal_with(jobnimbus_response_model)
    def get(self):
        """
        Health check for JobNimbus integration
        """
        from controllers.jobnimbus_controller import health
        return health()

@jobnimbus_ns.route('/contacts')
class JobNimbusContacts(Resource):
    @jobnimbus_ns.doc('list_jobnimbus_contacts')
    @jobnimbus_ns.marshal_with(jobnimbus_response_model)
    def get(self):
        """
        List JobNimbus contacts
        """
        from controllers.jobnimbus_controller import contacts_list
        return contacts_list()

    @jobnimbus_ns.doc('create_jobnimbus_contact')
    @jobnimbus_ns.expect(jobnimbus_contact_model)
    @jobnimbus_ns.marshal_with(jobnimbus_response_model, code=201)
    def post(self):
        """
        Create a JobNimbus contact
        """
        from controllers.jobnimbus_controller import contacts_create
        return contacts_create()

@jobnimbus_ns.route('/contacts/<string:contact_id>')
@jobnimbus_ns.param('contact_id', 'The JobNimbus contact identifier')
class JobNimbusContactDetail(Resource):
    @jobnimbus_ns.doc('get_jobnimbus_contact')
    @jobnimbus_ns.marshal_with(jobnimbus_response_model)
    def get(self, contact_id):
        """
        Get a JobNimbus contact by ID
        """
        from controllers.jobnimbus_controller import contacts_get
        return contacts_get(contact_id)

    @jobnimbus_ns.doc('update_jobnimbus_contact')
    @jobnimbus_ns.expect(jobnimbus_contact_model)
    @jobnimbus_ns.marshal_with(jobnimbus_response_model)
    def put(self, contact_id):
        """
        Update a JobNimbus contact
        """
        from controllers.jobnimbus_controller import contacts_update
        return contacts_update(contact_id)

    @jobnimbus_ns.doc('delete_jobnimbus_contact')
    @jobnimbus_ns.marshal_with(jobnimbus_response_model)
    def delete(self, contact_id):
        """
        Delete a JobNimbus contact
        """
        from controllers.jobnimbus_controller import contacts_delete
        return contacts_delete(contact_id)

@jobnimbus_ns.route('/jobs')
class JobNimbusJobs(Resource):
    @jobnimbus_ns.doc('list_jobnimbus_jobs')
    @jobnimbus_ns.marshal_with(jobnimbus_response_model)
    def get(self):
        """
        List JobNimbus jobs
        """
        from controllers.jobnimbus_controller import jobs_list
        return jobs_list()

    @jobnimbus_ns.doc('create_jobnimbus_job')
    @jobnimbus_ns.marshal_with(jobnimbus_response_model, code=201)
    def post(self):
        """
        Create a JobNimbus job
        """
        from controllers.jobnimbus_controller import jobs_create
        return jobs_create()