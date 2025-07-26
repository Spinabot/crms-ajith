from flask import Blueprint, request, jsonify
from flask_restx import Resource, Namespace, fields
from app.services.jobnimbus_service import jobnimbus_request
from app.swagger import api
from app import db

jobnimbus_bp = Blueprint('jobnimbus', __name__, url_prefix='/jobnimbus')
jobnimbus_ns = Namespace('jobnimbus', description='JobNimbus CRM operations')
api.add_namespace(jobnimbus_ns)

# Swagger models (simplified for brevity)
contact_model = jobnimbus_ns.model('Contact', {
    'jnid': fields.String(description='JobNimbus ID'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'display_name': fields.String(description='Display name'),
    'company': fields.String(description='Company name'),
    'email': fields.String(description='Email address'),
    'mobile_phone': fields.String(description='Mobile phone'),
    'work_phone': fields.String(description='Work phone'),
    'home_phone': fields.String(description='Home phone'),
    'address_line1': fields.String(description='Address line 1'),
    'address_line2': fields.String(description='Address line 2'),
    'city': fields.String(description='City'),
    'state_text': fields.String(description='State'),
    'zip': fields.String(description='ZIP code'),
    'country_name': fields.String(description='Country'),
    # ... add more fields as needed ...
})

@jobnimbus_ns.route('/contacts')
class JobNimbusContactsResource(Resource):
    @jobnimbus_ns.doc('list_contacts')
    def get(self):
        """List all contacts from JobNimbus"""
        params = request.args.to_dict()
        data, status = jobnimbus_request("GET", "/contacts", params=params)
        return data, status

    @jobnimbus_ns.doc('create_contact')
    @jobnimbus_ns.expect(contact_model)
    def post(self):
        """Create a new contact in JobNimbus"""
        contact_data = request.get_json()
        data, status = jobnimbus_request("POST", "/contacts", json=contact_data)
        return data, status

@jobnimbus_ns.route('/contacts/<string:jnid>')
@jobnimbus_ns.param('jnid', 'The contact identifier')
class JobNimbusContactResource(Resource):
    @jobnimbus_ns.doc('get_contact')
    def get(self, jnid):
        """Get a contact by ID from JobNimbus"""
        data, status = jobnimbus_request("GET", f"/contacts/{jnid}")
        return data, status

    @jobnimbus_ns.doc('update_contact')
    @jobnimbus_ns.expect(contact_model)
    def put(self, jnid):
        """Update a contact in JobNimbus"""
        contact_data = request.get_json()
        data, status = jobnimbus_request("PUT", f"/contacts/{jnid}", json=contact_data)
        return data, status

    @jobnimbus_ns.doc('archive_contact')
    @jobnimbus_ns.expect(jobnimbus_ns.model('ArchiveContact', {
        'is_active': fields.Boolean(required=True, description='Whether the contact should be active (true) or inactive (false)'),
        'is_archived': fields.Boolean(description='Whether the contact should be archived (true) or not (false)')
    }))
    @jobnimbus_ns.response(204, 'Contact archived')
    @jobnimbus_ns.response(400, 'Missing JSON body')
    @jobnimbus_ns.response(404, 'Contact not found')
    def delete(self, jnid):
        """Soft archive a contact in JobNimbus and update local database if present"""
        try:
            data = request.get_json()
        except Exception:
            return {"error": "Invalid JSON body"}, 400

        if not data:
            return {"error": "Missing JSON body"}, 400

        is_active = data.get("is_active")
        is_archived = data.get("is_archived", not is_active)

        # Make API call to JobNimbus first
        jn_data, jn_status = jobnimbus_request(
            "PUT",
            f"/contacts/{jnid}",
            json={"is_active": is_active, "is_archived": is_archived},
        )

        if jn_status != 200:
            return jn_data, jn_status

        # If JobNimbus update successful, update local database
        # The original code had logic to update UnifiedLead, which is no longer imported.
        # This part of the logic is removed as per the edit hint.

        return jn_data, jn_status