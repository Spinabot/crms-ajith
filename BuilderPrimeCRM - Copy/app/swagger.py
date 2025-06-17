from flask_restx import Api, Resource, fields
from flask import Blueprint, request
from app.config import Config
from app.utils.auth import require_api_key

swagger_bp = Blueprint('swagger', __name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-api-key'
    }
}

api = Api(
    title='Leads API',
    version='1.0',
    description='''
    API for managing leads
    
    Operations:
    - Create Lead: POST /api/clients/v1
    - List Leads: GET /api/clients
    - Update Lead: PUT /api/clients/v1/{lead_id}
    - Delete Lead: DELETE /api/clients/v1/{lead_id}
    ''',
    doc='/swagger',
    default='api',
    default_label='Leads Operations',
    prefix='/api',
    authorizations=authorizations,
    security='apikey' 
)

leads_ns = api.namespace('', 
    description='Operations for managing leads'
)

@swagger_bp.before_request
def add_api_key():
    request.environ['HTTP_X_API_KEY'] = Config.API_KEY

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
    'leadStatusName': fields.String(example="Lead Received", description="Status of the lead"),
    'leadSourceName': fields.String(example="Facebook", description="Source of the lead"),
    'salesPersonFirstName': fields.String(example="Alice", description="Sales person's first name"),
    'salesPersonLastName': fields.String(example="Thompson", description="Sales person's last name"),
    'leadSetterFirstName': fields.String(example="Bob", description="Lead setter's first name"),
    'leadSetterLastName': fields.String(example="Roberts", description="Lead setter's last name"),
    'className': fields.String(example="Residential", description="Class name"),
    'projectTypeName': fields.String(example="Kitchen Renovation", description="Type of project"),
    'externalId': fields.String(example="AB-4617", description="External identifier"),
    'dialerStatus': fields.String(example="1st Attempt", description="Dialer status")
})

lead_response = api.inherit('LeadResponse', lead_model, {
    'id': fields.Integer(description='Lead ID'),
    'createdAt': fields.DateTime(description='Creation timestamp'),
    'updatedAt': fields.DateTime(description='Last update timestamp')
})

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
    'leads': fields.List(fields.Nested(lead_response))
})

 
