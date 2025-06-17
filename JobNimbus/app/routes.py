from flask import Blueprint
from flask import jsonify
from flask import render_template_string
from flask import request
from flask_restx import Api, Resource, fields

from app.config import CONTACTS_ENDPOINT
from app.database import db
from app.models import Contact
from app.utils import jobnimbus_request

main = Blueprint("main", __name__)
api = Api(main, version='1.0', title='JobNimbus API',
          description='A RESTful API for managing JobNimbus contacts')

# Define namespaces
ns = api.namespace('contacts', description='Contact operations')

# Define models for Swagger documentation
contact_model = api.model('Contact', {
    'jnid': fields.String(description='JobNimbus ID'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'display_name': fields.String(description='Display name'),
    'company': fields.String(description='Company name'),
    'status': fields.String(description='Status'),
    'status_name': fields.String(description='Status name'),
    'record_type': fields.String(description='Record type'),
    'record_type_name': fields.String(description='Record type name'),
    'address_line1': fields.String(description='Address line 1'),
    'address_line2': fields.String(description='Address line 2'),
    'city': fields.String(description='City'),
    'state_text': fields.String(description='State'),
    'zip': fields.String(description='ZIP code'),
    'country_name': fields.String(description='Country'),
    'created_by_name': fields.String(description='Created by'),
    'email': fields.String(description='Email address'),
    'home_phone': fields.String(description='Home phone'),
    'mobile_phone': fields.String(description='Mobile phone'),
    'work_phone': fields.String(description='Work phone'),
    'fax_number': fields.String(description='Fax number'),
    'website': fields.String(description='Website')
})

@main.route("/")
def home():
    return render_template_string(
        """
    <h1>Welcome to the JobNimbus Contacts API!</h1>
    <p>Please visit <a href="/swagger">/swagger</a> for API documentation.</p>
    """
    )

@ns.route('/')
class ContactList(Resource):
    @ns.doc('list_contacts')
    @ns.marshal_list_with(contact_model)
    def get(self):
        """List all contacts"""
        data, status = jobnimbus_request("GET", CONTACTS_ENDPOINT)
        return data, status

    @ns.doc('create_contact')
    @ns.expect(contact_model)
    @ns.marshal_with(contact_model, code=201)
    def post(self):
        """Create a new contact"""
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

@ns.route('/<string:jnid>')
@ns.param('jnid', 'The contact identifier')
@ns.response(404, 'Contact not found')
class ContactResource(Resource):
    @ns.doc('get_contact')
    @ns.marshal_with(contact_model)
    def get(self, jnid):
        """Get a contact by ID"""
        contact = db.session.get(Contact, jnid)
        if contact:
            return contact.to_dict(), 200
        return {"error": "Contact not found"}, 404

    @ns.doc('update_contact')
    @ns.expect(contact_model)
    @ns.marshal_with(contact_model)
    def put(self, jnid):
        """Update a contact"""
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

    @ns.doc('delete_contact')
    @ns.response(204, 'Contact deleted')
    def delete(self, jnid):
        """Soft delete a contact"""
        contact = db.session.get(Contact, jnid)
        if not contact:
            return {"error": "Contact not found"}, 404

        data = request.get_json()
        if not data:
            return {"error": "Missing JSON body"}, 400

        is_active = data.get("is_active")
        is_archived = data.get("is_archived", not is_active)

        contact.is_active = is_active
        contact.is_archived = is_archived
        db.session.commit()

        jn_data, jn_status = jobnimbus_request(
            "PUT",
            f"{CONTACTS_ENDPOINT}/{jnid}",
            json={"is_active": is_active, "is_archived": is_archived},
        )

        return jn_data, jn_status
