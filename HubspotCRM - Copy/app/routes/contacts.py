from flask import Blueprint
from flask_restx import Resource
from app.swagger import api, contacts_ns, contact_model, contact_response, pagination_model, search_model, batch_operation_model, get_parser
from app.services.contact_service import ContactService
from flask import request

contacts = Blueprint('contacts', __name__)

contact_service = ContactService()

@contacts_ns.route('/contacts')
class ContactsResource(Resource):
    @api.doc('list_contacts')
    @api.expect(get_parser)
    @api.marshal_with(pagination_model)
    def get(self):
        """List all contacts with pagination"""
        args = get_parser.parse_args()
        contacts, total, pages = contact_service.list_contacts(args.page, args.per_page)
        return {
            'contacts': contacts,
            'total': total,
            'pages': pages,
            'current_page': args.page
        }

    @api.doc('create_contact')
    @api.expect(contact_model)
    @api.marshal_with(contact_response, code=201)
    def post(self):
        """Create a new contact"""
        return contact_service.create_contact(api.payload), 201

@contacts_ns.route('/contacts/<string:contact_id>')
class ContactResource(Resource):
    @api.doc('get_contact')
    @api.marshal_with(contact_response)
    def get(self, contact_id):
        """Get a contact by ID"""
        contact = contact_service.get_contact(contact_id)
        if not contact:
            api.abort(404, 'Contact not found')
        return contact

    @api.doc('update_contact')
    @api.expect(contact_model)
    @api.marshal_with(contact_response)
    def patch(self, contact_id):
        """Update a contact"""
        contact = contact_service.update_contact(contact_id, api.payload)
        if not contact:
            api.abort(404, 'Contact not found')
        return contact

    @api.doc('delete_contact')
    @api.response(204, 'Contact deleted')
    def delete(self, contact_id):
        """Delete a contact"""
        if contact_service.delete_contact(contact_id):
            return '', 204
        api.abort(404, 'Contact not found')

@contacts_ns.route('/contacts/search')
class ContactSearchResource(Resource):
    @api.doc('search_contacts')
    @api.expect(search_model)
    @api.marshal_with(pagination_model)
    def post(self):
        """Search contacts with filters"""
        data = request.get_json()
        page = data.pop('page', 1)
        per_page = data.pop('per_page', 10)
        contacts, total, pages = contact_service.search_contacts(data, page, per_page)
        return {
            'contacts': contacts,
            'total': total,
            'pages': pages,
            'current_page': page
        }

@contacts_ns.route('/contacts/batch')
class ContactBatchResource(Resource):
    @api.doc('batch_operations')
    @api.expect(batch_operation_model)
    def post(self):
        """Perform batch operations on contacts"""
        data = request.get_json()
        operation = data.get('operation')
        contacts_data = data.get('contacts', [])
        
        if operation not in ['create', 'update', 'delete']:
            api.abort(400, 'Invalid operation')
            
        try:
            result = contact_service.batch_operation(operation, contacts_data)
            return result
        except Exception as e:
            api.abort(500, str(e))
