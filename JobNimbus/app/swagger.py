from flask_restx import Api, Resource, fields
from flask import Blueprint, request
from app.config import CONTACTS_ENDPOINT
from app.database import db
from app.models import Contact
from app.utils import jobnimbus_request

swagger_bp = Blueprint('swagger', __name__)

authorizations = {
    'bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Bearer token for JobNimbus API'
    }
}

api = Api(swagger_bp,
    title='JobNimbus API',
    version='1.0',
    description='''
    API for managing JobNimbus contacts
    
    Authentication:
    - Add your JobNimbus API token in the header: Authorization: bearer <token>
    
    Operations:
    - List Contacts: GET /contacts
    - Create Contact: POST /contacts
    - Get Contact: GET /contacts/{jnid}
    - Update Contact: PUT /contacts/{jnid}
    - Delete Contact: PUT /contacts/{jnid} (soft delete)
    ''',
    doc='/swagger',
    authorizations=authorizations,
    security='bearer'
)

contacts_ns = api.namespace('', description='Operations for managing JobNimbus contacts')

# Define models for Swagger documentation
geo_model = api.model('Geo', {
    'lat': fields.Float(example=37.149574, description='Latitude'),
    'lon': fields.Float(example=-88.687277, description='Longitude')
})

contact_model = api.model('Contact', {
    'jnid': fields.String(description='JobNimbus ID'),
    'first_name': fields.String(required=True, example="Sammy G", description='First name'),
    'last_name': fields.String(required=True, example="Kent", description='Last name'),
    'display_name': fields.String(example="Sammy G Kent", description='Display name'),
    'company': fields.String(example="Wayne Enterprises", description='Company name'),
    'status': fields.Integer(example=2, description='Status ID'),
    'status_name': fields.String(required=True, example="Lead", description='Status name'),
    'record_type': fields.Integer(example=1, description='Record type ID'),
    'record_type_name': fields.String(required=True, example="Customer", description='Record type name'),
    'source': fields.Integer(example=1, description='Source ID'),
    'source_name': fields.String(example="Referral", description='Source name'),
    'address_line1': fields.String(example="123 S. Bat Street", description='Address line 1'),
    'address_line2': fields.String(example="Apt C", description='Address line 2'),
    'city': fields.String(example="Heber City", description='City'),
    'state_text': fields.String(example="UT", description='State'),
    'zip': fields.String(example="84032", description='ZIP code'),
    'country_name': fields.String(example="United States", description='Country'),
    'created_by_name': fields.String(example="Sam Burnet", description='Created by'),
    'email': fields.String(example="bruce@batman.com", description='Email address'),
    'home_phone': fields.String(example="8882223333", description='Home phone'),
    'mobile_phone': fields.String(description='Mobile phone'),
    'work_phone': fields.String(description='Work phone'),
    'fax_number': fields.String(description='Fax number'),
    'website': fields.String(example="www.batman.com", description='Website'),
    'geo': fields.Nested(geo_model, description='Geographic coordinates'),
    'description': fields.String(example="Likes to wear costumes...", description='Contact description')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

success_model = api.model('Success', {
    'message': fields.String(description='Success message')
})

delete_request_model = api.model('DeleteRequest', {
    'is_active': fields.Boolean(required=True, example=False, description='Whether the contact is active')
})

# Query parameters for GET /contacts
get_parser = api.parser()
get_parser.add_argument('size', type=int, default=1000, help='Number of elements to return')
get_parser.add_argument('from', type=int, default=0, help='Zero based starting point for pagination')
get_parser.add_argument('sort_field', type=str, default='date_created', help='Field to sort by')
get_parser.add_argument('sort_direction', type=str, default='desc', help='Sort direction (asc/desc)')
get_parser.add_argument('fields', type=str, help='Comma-separated list of fields to include')
get_parser.add_argument('filter', type=str, help='URL encoded JSON filter object')

@contacts_ns.route('/contacts')
class ContactsResource(Resource):
    @api.doc('list_contacts',
        security='bearer',
        responses={
            200: 'Success',
            401: 'No API token provided',
            403: 'Invalid API token',
            500: 'Server error'
        }
    )
    @api.expect(get_parser)
    @api.marshal_with(contact_model, as_list=True)
    def get(self):
        """List all contacts with pagination and filtering"""
        args = get_parser.parse_args()
        data, status = jobnimbus_request("GET", CONTACTS_ENDPOINT, params=args)
        return data, status

    @api.doc('create_contact',
        security='bearer',
        responses={
            200: 'Contact created successfully',
            400: 'Invalid request data',
            401: 'No API token provided',
            403: 'Invalid API token',
            500: 'Server error'
        }
    )
    @api.expect(contact_model)
    @api.marshal_with(contact_model)
    def post(self):
        """Create a new contact
        
        Notes:
        - First Name, Last Name, First & Last Name, Display_Name, or Company Name are required
        - record_type_name is required and should be a workflow name defined in the customer's JobNimbus contact workflow settings
        - status_name is required and should be a status defined within the record_type_name workflow
        - source_name is optional but if provided should be set to one of the lead source names defined in the customer's settings
        """
        contact_data = request.get_json()
        if not contact_data:
            return {"error": "Missing JSON body"}, 400

        data, status = jobnimbus_request("POST", CONTACTS_ENDPOINT, json=contact_data)

        if status == 200:
            contact = Contact(
                jnid=data.get("jnid"),
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                display_name=data.get("display_name", ""),
                company=data.get("company", ""),
                status=data.get("status"),
                status_name=data.get("status_name"),
                record_type=data.get("record_type"),
                record_type_name=data.get("record_type_name"),
                address_line1=data.get("address_line1", ""),
                address_line2=data.get("address_line2", ""),
                city=data.get("city", ""),
                state_text=data.get("state_text", ""),
                zip=data.get("zip", ""),
                country_name=data.get("country_name", ""),
                created_by_name=data.get("created_by_name", ""),
                email=data.get("email", ""),
                home_phone=data.get("home_phone", ""),
                mobile_phone=data.get("mobile_phone", ""),
                work_phone=data.get("work_phone", ""),
                fax_number=data.get("fax_number", ""),
                website=data.get("website", ""),
            )
            db.session.add(contact)
            db.session.commit()

        return data, status

@contacts_ns.route('/contacts/<string:jnid>')
class ContactResource(Resource):
    @api.doc('get_contact',
        security='bearer',
        responses={
            200: 'Success',
            401: 'No API token provided',
            403: 'Invalid API token',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @api.marshal_with(contact_model)
    def get(self, jnid):
        """Get a contact by ID
        
        Notes:
        - Mandatory field(s): jnid
        """
        contact = db.session.get(Contact, jnid)
        if contact:
            return contact.to_dict(), 200
        return {"error": "Contact not found"}, 404

    @api.doc('update_contact',
        security='bearer',
        responses={
            200: 'Contact updated successfully',
            400: 'Invalid request data',
            401: 'No API token provided',
            403: 'Invalid API token',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @api.expect(contact_model)
    @api.marshal_with(contact_model)
    def put(self, jnid):
        """Update a contact
        
        Notes:
        - Mandatory field(s): jnid
        """
        data = request.get_json()
        contact = db.session.get(Contact, jnid)

        if not contact:
            return {"error": "Contact not found"}, 404

        for key, value in data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        db.session.commit()

        jn_data, jn_status = jobnimbus_request("PUT", f"{CONTACTS_ENDPOINT}/{jnid}", json=data)
        return jn_data, jn_status

    @api.doc('delete_contact',
        security='bearer',
        responses={
            200: 'Contact deleted successfully',
            400: 'Invalid request data',
            401: 'No API token provided',
            403: 'Invalid API token',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @api.expect(delete_request_model)
    @api.marshal_with(success_model)
    def delete(self, jnid):
        """Soft delete a contact
        
        Notes:
        - Mandatory field(s): jnid
        - This is a soft delete that sets is_active to false
        """
        contact = db.session.get(Contact, jnid)
        if not contact:
            return {"error": "Contact not found"}, 404

        data = request.get_json()
        if not data:
            return {"error": "Missing JSON body"}, 400

        is_active = data.get("is_active", False)

        contact.is_active = is_active
        db.session.commit()

        jn_data, jn_status = jobnimbus_request(
            "PUT",
            f"{CONTACTS_ENDPOINT}/{jnid}",
            json={"is_active": is_active},
        )

        if jn_status == 200:
            return {"message": "Contact deleted successfully"}, 200
        return {"error": "Failed to delete contact"}, jn_status 