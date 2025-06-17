from flask_restx import Api, Resource, fields
from flask import Blueprint, request
from app.config import CONTACTS_ENDPOINT
from app.database import db
from app.models import Contact
from app.utils import jobnimbus_request

swagger_bp = Blueprint('swagger', __name__)

api = Api(swagger_bp,
    title='JobNimbus Contacts API',
    version='1.0',
    description='''
    Flask-based REST API for managing contacts using JobNimbus. 
    Supports full CRUD operations and is backed by a PostgreSQL database.
    
    Features:
    - Create, Read, Update, and Delete JobNimbus contacts
    - PostgreSQL database integration with SQLAlchemy
    - Modular Flask project structure
    - Environment-specific configuration support
    
    Operations:
    - Health Check: GET /
    - List Contacts: GET /contacts
    - Create Contact: POST /contacts
    - Get Contact: GET /contacts/{jnid}
    - Update Contact: PUT /contacts/{jnid}
    - Archive Contact: DELETE /contacts/{jnid}
    ''',
    doc='/swagger'
)

contacts_ns = api.namespace('', description='Operations for managing JobNimbus contacts')

# Define models for Swagger documentation
geo_model = api.model('Geo', {
    'lat': fields.Float(example=37.149574, description='Latitude'),
    'lon': fields.Float(example=-88.687277, description='Longitude')
})

contact_model = api.model('Contact', {
    'jnid': fields.String(description='JobNimbus ID'),
    'first_name': fields.String(required=True, example="John", description='First name'),
    'last_name': fields.String(required=True, example="Doe", description='Last name'),
    'display_name': fields.String(example="JD", description='Display name'),
    'company': fields.String(example="Acme", description='Company name'),
    'company_name': fields.String(example="Acme Corp", description='Company name (alternative field)'),
    'status': fields.Integer(example=2, description='Status ID'),
    'status_name': fields.String(required=True, example="Active", description='Status name'),
    'record_type': fields.Integer(example=1, description='Record type ID'),
    'record_type_name': fields.String(required=True, example="Lead", description='Record type name'),
    'source': fields.Integer(example=1, description='Source ID'),
    'source_name': fields.String(example="Facebook", description='Source name'),
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

contact_create_model = api.model('ContactCreate', {
    'first_name': fields.String(required=True, example="John", description='First name'),
    'last_name': fields.String(required=True, example="Doe", description='Last name'),
    'display_name': fields.String(example="JD", description='Display name'),
    'company_name': fields.String(example="Acme", description='Company name'),
    'record_type_name': fields.String(required=True, example="Lead", description='Record type name'),
    'status_name': fields.String(required=True, example="Active", description='Status name'),
    'source_name': fields.String(example="Facebook", description='Source name')
})

contact_update_model = api.model('ContactUpdate', {
    'status_name': fields.String(example="Prospect", description='Status name to update'),
    'first_name': fields.String(example="John", description='First name'),
    'last_name': fields.String(example="Doe", description='Last name'),
    'company': fields.String(example="Acme Corp", description='Company name'),
    'email': fields.String(example="john.doe@example.com", description='Email address'),
    'phone': fields.String(example="+1234567890", description='Phone number')
})

contact_response = api.model('ContactResponse', {
    'jnid': fields.String(description="JobNimbus contact ID"),
    'first_name': fields.String(description="Contact's first name"),
    'last_name': fields.String(description="Contact's last name"),
    'display_name': fields.String(description="Contact's display name"),
    'company': fields.String(description="Contact's company"),
    'email': fields.String(description="Contact's email address"),
    'status_name': fields.String(description="Contact's status"),
    'record_type_name': fields.String(description="Contact's record type"),
    'source_name': fields.String(description="Contact's source"),
    'created_by_name': fields.String(description="Created by"),
    'is_active': fields.Boolean(description="Whether the contact is active")
})

delete_request_model = api.model('DeleteRequest', {
    'is_active': fields.Boolean(required=True, example=False, description='Whether the contact is active')
})

delete_response = api.model('DeleteResponse', {
    'message': fields.String(description="Success message"),
    'jnid': fields.String(description="Archived contact ID")
})

health_model = api.model('Health', {
    'status': fields.String(description='Service status'),
    'message': fields.String(description='Health check message')
})

# Query parameters for GET /contacts
get_parser = api.parser()
get_parser.add_argument('size', type=int, default=1000, help='Number of elements to return')
get_parser.add_argument('from', type=int, default=0, help='Zero based starting point for pagination')
get_parser.add_argument('sort_field', type=str, default='date_created', help='Field to sort by')
get_parser.add_argument('sort_direction', type=str, default='desc', help='Sort direction (asc/desc)')
get_parser.add_argument('fields', type=str, help='Comma-separated list of fields to include')
get_parser.add_argument('filter', type=str, help='URL encoded JSON filter object')

@api.route('/')
class HealthResource(Resource):
    @api.doc('health_check',
        responses={
            200: 'Service is healthy',
            500: 'Service is unhealthy'
        }
    )
    @api.marshal_with(health_model)
    def get(self):
        """Health check endpoint
        
        Returns the health status of the service.
        """
        return {
            'status': 'healthy',
            'message': 'JobNimbus Contacts API is running'
        }, 200

@contacts_ns.route('/contacts')
class ContactsResource(Resource):
    @api.doc('list_contacts',
        responses={
            200: 'Success',
            500: 'Server error'
        }
    )
    @api.expect(get_parser)
    @api.marshal_with(contact_response, as_list=True)
    def get(self):
        """List all contacts with pagination and filtering
        
        Retrieves all contacts from JobNimbus with support for:
        - Pagination (size, from parameters)
        - Sorting (sort_field, sort_direction)
        - Field filtering (fields parameter)
        - JSON filtering (filter parameter)
        """
        args = get_parser.parse_args()
        data, status = jobnimbus_request("GET", CONTACTS_ENDPOINT, params=args)
        return data, status

    @api.doc('create_contact',
        responses={
            200: 'Contact created successfully',
            400: 'Invalid request data',
            500: 'Server error'
        }
    )
    @api.expect(contact_create_model)
    @api.marshal_with(contact_response)
    def post(self):
        """Create a new contact
        
        Notes:
        - First Name, Last Name, First & Last Name, Display_Name, or Company Name are required
        - record_type_name is required and should be a workflow name defined in the customer's JobNimbus contact workflow settings
        - status_name is required and should be a status defined within the record_type_name workflow
        - source_name is optional but if provided should be set to one of the lead source names defined in the customer's settings
        
        Example request body:
        {
          "first_name": "John",
          "last_name": "Doe",
          "display_name": "JD",
          "company_name": "Acme",
          "record_type_name": "Lead",
          "status_name": "Active",
          "source_name": "Facebook"
        }
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
        responses={
            200: 'Success',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @api.marshal_with(contact_response)
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
        responses={
            200: 'Contact updated successfully',
            400: 'Invalid request data',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @api.expect(contact_update_model)
    @api.marshal_with(contact_response)
    def put(self, jnid):
        """Update a contact
        
        Notes:
        - Mandatory field(s): jnid
        
        Example request body:
        {
          "status_name": "Prospect"
        }
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

    @api.doc('archive_contact',
        responses={
            200: 'Contact archived successfully',
            400: 'Invalid request data',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @api.expect(delete_request_model)
    @api.marshal_with(delete_response)
    def delete(self, jnid):
        """Archive a contact (soft delete)
        
        Notes:
        - Mandatory field(s): jnid
        - This is a soft delete that sets is_active to false
        - The contact is archived rather than permanently deleted
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
            return {"message": "Contact archived successfully", "jnid": jnid}, 200
        return {"error": "Failed to archive contact"}, jn_status 