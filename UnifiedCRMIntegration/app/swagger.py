from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint, request
from app.config import Config

# Create API instance
api = Api(
    title='Unified CRM Integration API',
    version='1.0',
    description='''
    A unified API for managing leads across multiple CRM systems

    Supported CRM Systems:
    - BuilderPrime CRM (Fully implemented)
    - HubSpot CRM (Fully implemented)

    Operations:
    - Create Lead: POST /api/builder-prime/leads or POST /api/hubspot/leads
    - List Leads: GET /api/builder-prime/leads or GET /api/hubspot/leads
    - Update Lead: PUT /api/builder-prime/leads/{lead_id} or PUT /api/hubspot/leads/{external_id}
    - Delete Lead: DELETE /api/builder-prime/leads/{lead_id} or DELETE /api/hubspot/leads/{external_id}
    - Sync Leads: POST /api/builder-prime/sync or POST /api/hubspot/leads/sync
    ''',
    doc='/swagger',
    default='api',
    default_label='CRM Operations',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'x-api-key'
        }
    },
    security='apikey'
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

# Add namespaces to API
api.add_namespace(builder_prime_ns)
api.add_namespace(hubspot_ns)
api.add_namespace(jobber_ns)

# Import routes to register them with the API
import app.routes.builder_prime
import app.routes.hubspot
import app.routes.jobber