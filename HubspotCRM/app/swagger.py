from flask_restx import Api, Resource, fields
from flask import Blueprint, request
from app.config import Config
from app.services.contact_service import ContactService
from app.utils.auth import require_hubspot_auth

swagger_bp = Blueprint('swagger', __name__)
contact_service = ContactService() 

authorizations = {
    'hubspot_token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-HubSpot-Token',
        'description': 'HubSpot API Token'
    }
}

api = Api(swagger_bp,
    title='HubSpot CRM API',
    version='1.0',
    description='''
    API for managing HubSpot CRM contacts
    
    Authentication:
    - Add your HubSpot API token in the header: X-HubSpot-Token
    
    Operations:
    - Create Contact: POST /api/contacts
    - List Contacts: GET /api/contacts
    - Get Contact: GET /api/contacts/{contact_id}
    - Update Contact: PUT /api/contacts/{contact_id}
    - Delete Contact: DELETE /api/contacts/{contact_id}
    - Search Contacts: POST /api/contacts/search
    - Batch Operations: POST /api/contacts/batch
    ''',
    doc='/swagger',
    authorizations=authorizations,
    security='hubspot_token'
)

contacts_ns = api.namespace('', description='Operations for managing HubSpot contacts')

contact_model = api.model('Contact', {
    'email': fields.String(required=True, example="john.doe@example.com", description="Contact's email address"),
    'firstname': fields.String(example="John", description="Contact's first name"),
    'lastname': fields.String(example="Doe", description="Contact's last name"),
    'phone': fields.String(example="+1234567890", description="Contact's phone number"),
    'company': fields.String(example="ABC Corp", description="Contact's company"),
    'website': fields.String(example="https://example.com", description="Contact's website"),
    'lifecyclestage': fields.String(example="lead", description="Contact's lifecycle stage")
})

contact_response = api.model('ContactResponse', {
    'id': fields.String(description="HubSpot contact ID"),
    'properties': fields.Raw(description="Contact properties", example={
        "createdate": "2025-04-01T15:09:14.652Z",
        "email": "emailmaria@hubspot.com",
        "firstname": "Maria",
        "hs_object_id": "102322994896",
        "lastmodifieddate": "2025-04-01T15:09:36.570Z",
        "lastname": "Johnson (Sample Contact)"
    }),
    'createdAt': fields.DateTime(description="Creation timestamp"),
    'updatedAt': fields.DateTime(description="Last update timestamp"),
    'archived': fields.Boolean(description="Whether the contact is archived")
})

search_model = api.model('SearchFilters', {
    'email': fields.String(example="john@example.com", description="Filter by email"),
    'name': fields.String(example="John", description="Filter by name"),
    'company': fields.String(example="ABC Corp", description="Filter by company"),
    'page': fields.Integer(example=1, description="Page number"),
    'per_page': fields.Integer(example=10, description="Items per page")
})

batch_operation_model = api.model('BatchOperation', {
    'operation': fields.String(required=True, enum=['create', 'update', 'delete'], description="Batch operation type"),
    'contacts': fields.List(fields.Raw, description="List of contacts or contact IDs")
})

contact_create_model = api.model('ContactCreate', {
    'properties': fields.Raw(required=True, example={
        "email": "example@hubspot.com",
        "firstname": "Jane",
        "lastname": "Doe",
        "phone": "(555) 555-5555",
        "company": "HubSpot",
        "website": "https://example.com",
        "lifecyclestage": "marketingqualifiedlead"
    })
})

batch_read_model = api.model('BatchRead', {
    'properties': fields.List(fields.String, example=["email", "lifecyclestage", "jobtitle"]),
    'idProperty': fields.String(example="email", description="Property to use for identification (email or custom)"),
    'inputs': fields.List(fields.Raw(example={"id": "1234567"}))
})

batch_update_model = api.model('BatchUpdate', {
    'inputs': fields.List(fields.Raw(example={
        "id": "123456789",
        "properties": {
            "favorite_food": "burger"
        }
    }))
})

batch_upsert_model = api.model('BatchUpsert', {
    'inputs': fields.List(fields.Raw(example={
        "properties": {
            "phone": "5555555555"
        },
        "id": "test@test.com",
        "idProperty": "email"
    }))
})

get_parser = api.parser()
get_parser.add_argument('page', type=int, default=1, help='Page number')
get_parser.add_argument('per_page', type=int, default=10, help='Items per page')

pagination_model = api.model('PaginationResponse', {
    'contacts': fields.List(fields.Nested(contact_response)),
    'total': fields.Integer(description='Total number of contacts'),
    'pages': fields.Integer(description='Total number of pages'),
    'current_page': fields.Integer(description='Current page number')
})

delete_response = api.model('DeleteResponse', {
    'message': fields.String(description="Success message"),
    'contact_id': fields.String(description="Deleted contact ID")
})

batch_result_model = api.model('BatchResult', {
    'id': fields.String(description="Contact ID"),
    'status': fields.String(description="Operation status"),
    'error': fields.String(description="Error message if any")
})

batch_response_model = api.model('BatchResponse', {
    'results': fields.List(fields.Nested(batch_result_model), description="Results of batch operation"),
    'success_count': fields.Integer(description="Number of successful operations"),
    'error_count': fields.Integer(description="Number of failed operations")
})

@contacts_ns.route('/contacts')
class ContactsResource(Resource):
    @api.doc('list_contacts', security='hubspot_token')
    @require_hubspot_auth
    @api.expect(get_parser)
    @api.marshal_with(pagination_model)
    def get(self):
        """List all contacts with pagination"""
        args = get_parser.parse_args()
        contacts, total, pages = contact_service.list_contacts(
            page=args.get('page', 1),
            per_page=args.get('per_page', 10)
        )
        return {
            'contacts': contacts,
            'total': total,
            'pages': pages,
            'current_page': args.get('page', 1)
        }

    @api.doc('create_contact',
        security='hubspot_token',
        responses={
            201: 'Contact created successfully',
            400: 'Invalid request data',
            401: 'No API token provided',
            403: 'Invalid API token',
            409: 'Contact already exists',
            500: 'Server error'
        }
    )
    @require_hubspot_auth
    @api.expect(contact_create_model)
    def post(self):
        """Create a new contact"""
        try:
            contact = contact_service.create_contact(api.payload)
            return contact, 201
        except ValueError as e:
            return {'error': str(e)}, 409 if "already exists" in str(e) else 400
        except Exception as e:
            return {'error': str(e)}, 500

@contacts_ns.route('/contacts/<string:contact_id>')
class ContactResource(Resource):
    @api.doc('get_contact',
        security='hubspot_token',
        responses={
            200: 'Success',
            401: 'No API token provided',
            403: 'Invalid API token',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @require_hubspot_auth
    def get(self, contact_id):
        """Get a contact by ID"""
        try:
            contact = contact_service.get_contact(contact_id)
            return contact
        except Exception as e:
            return {'error': str(e)}, 404 if "not found" in str(e) else 500

    @api.doc('update_contact',
        security='hubspot_token',
        responses={
            200: 'Contact updated successfully',
            400: 'Invalid request data',
            401: 'No API token provided',
            403: 'Invalid API token',
            404: 'Contact not found',
            409: 'Conflict - Email already exists',
            500: 'Server error'
        }
    )
    @require_hubspot_auth
    @api.expect(contact_create_model)
    def put(self, contact_id):
        """Update a contact"""
        try:
            contact = contact_service.update_contact(contact_id, api.payload)
            return contact
        except ValueError as e:
            if "not found" in str(e).lower():
                return {'error': str(e)}, 404
            elif "conflict" in str(e).lower():
                return {'error': str(e)}, 409
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_contact',
        security='hubspot_token',
        responses={
            200: 'Contact deleted successfully',
            401: 'No API token provided',
            403: 'Invalid API token',
            404: 'Contact not found',
            500: 'Server error'
        }
    )
    @require_hubspot_auth
    @api.marshal_with(delete_response, code=200)
    def delete(self, contact_id):
        """Delete a contact"""
        try:
            if contact_service.delete_contact(contact_id):
                return {
                    'message': 'Contact deleted successfully',
                    'contact_id': contact_id
                }, 200
            return {'error': 'Contact not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

@contacts_ns.route('/contacts/search')
class ContactSearchResource(Resource):
    @api.doc('search_contacts',
        security='hubspot_token',
        responses={
            200: 'Search completed successfully',
            400: 'Invalid search parameters',
            401: 'No API token provided',
            403: 'Invalid API token',
            500: 'Server error'
        }
    )
    @require_hubspot_auth
    @api.expect(search_model)
    def post(self):
        """Search contacts with filters"""
        try:
            data = request.get_json()
            page = data.get('page', 1)
            per_page = data.get('per_page', 10)
            
            filters = {
                'email': data.get('email'),
                'name': data.get('name'),
                'company': data.get('company')
            }
            
            filters = {k: v for k, v in filters.items() if v is not None}
            
            contacts, total, pages = contact_service.search_contacts(filters, page, per_page)
            
            return {
                'contacts': contacts,
                'total': total,
                'pages': pages,
                'current_page': page
            }
            
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

@contacts_ns.route('/contacts/batch')
class ContactBatchResource(Resource):
    @api.doc('batch_operations',
        security='hubspot_token',
        responses={
            200: 'Batch operation completed successfully',
            400: 'Invalid request data',
            401: 'No API token provided',
            403: 'Invalid API token',
            500: 'Server error'
        }
    )
    @require_hubspot_auth
    @api.expect(batch_operation_model)
    @api.marshal_with(batch_response_model)
    def post(self):
        """Perform batch operations on contacts"""
        try:
            data = request.get_json()
            if not data or 'operation' not in data or 'contacts' not in data:
                raise ValueError("Missing required fields: operation and contacts")
            
            if data['operation'] not in ['create', 'update', 'delete']:
                raise ValueError(f"Invalid operation: {data['operation']}")
            
            results = contact_service.batch_operation(
                data['operation'],
                data['contacts']
            )
            
            success_count = sum(1 for r in results if not r.get('error', None))
            error_count = len(results) - success_count
            
            return {
                'results': results,
                'success_count': success_count,
                'error_count': error_count
            }
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
