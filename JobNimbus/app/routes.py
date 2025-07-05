import json
from flask import Blueprint, current_app
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

# Pagination response model
pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='Current page number'),
    'limit': fields.Integer(description='Number of items per page'),
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages'),
    'has_next': fields.Boolean(description='Whether there is a next page'),
    'has_prev': fields.Boolean(description='Whether there is a previous page'),
    'sort_by': fields.String(description='Current sort field'),
    'sort_order': fields.String(description='Current sort order (asc/desc)'),
    'search': fields.String(description='Current search term (if any)'),
    'is_active': fields.String(description='Filter by active status (true/false)'),
    'is_archived': fields.String(description='Filter by archived status (true/false)')
})

# Paginated contacts response model
paginated_contacts_model = api.model('PaginatedContacts', {
    'contacts': fields.List(fields.Nested(contact_model), description='List of contacts'),
    'pagination': fields.Nested(pagination_model, description='Pagination information')
})

# Delete request model
delete_request_model = api.model('DeleteRequest', {
    'is_active': fields.Boolean(description='Whether the contact should be active (true) or inactive (false)'),
    'is_archived': fields.Boolean(description='Whether the contact should be archived (true) or not (false)')
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
    @ns.doc('list_contacts', params={
        'page': 'Page number (default: 1)',
        'limit': 'Number of items per page (default: 10, max: 100)',
        'sort_by': 'Sort field (default: jnid)',
        'sort_order': 'Sort order: asc or desc (default: asc)',
        'search': 'Search term for first_name, last_name, or company',
        'is_active': 'Filter by active status (true/false)',
        'is_archived': 'Filter by archived status (true/false)'
    })
    def get(self):
        """List all contacts with pagination, sorting, filtering, and archive filters"""
        # Get pagination and filter parameters from query string
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'jnid')
        sort_order = request.args.get('sort_order', 'asc').lower()
        search = request.args.get('search', '').strip()
        is_active = request.args.get('is_active')
        is_archived = request.args.get('is_archived')
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
        if limit > 100:
            limit = 100
        
        # Validate sort order
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get contacts from JobNimbus API
        # Try to include archived contacts by adding query parameters
        url = CONTACTS_ENDPOINT
        params = {}
        
        # Add parameters to include archived contacts if not specifically filtering
        if is_archived is None and is_active is None:
            # Try to get all contacts including archived ones
            params = {"include_archived": "true", "include_inactive": "true"}
        
        data, status = jobnimbus_request("GET", url, params=params)
        print(f"JobNimbus API Response - Data: {data}, Status: {status}")
        
        if status != 200:
            return {"error": "Failed to fetch contacts from JobNimbus"}, status
        
        # Extract contacts from response
        all_contacts = data.get("results", [])
        
        # Apply archive filters if provided
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            all_contacts = [c for c in all_contacts if c.get('is_active', True) == is_active_bool]
        if is_archived is not None:
            is_archived_bool = is_archived.lower() == 'true'
            all_contacts = [c for c in all_contacts if c.get('is_archived', False) == is_archived_bool]
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            all_contacts = [
                contact for contact in all_contacts
                if (contact.get('first_name', '').lower().find(search_lower) != -1 or
                    contact.get('last_name', '').lower().find(search_lower) != -1 or
                    contact.get('company', '').lower().find(search_lower) != -1 or
                    contact.get('display_name', '').lower().find(search_lower) != -1)
            ]
        
        # Apply sorting
        if sort_by in ['first_name', 'last_name', 'company', 'display_name', 'jnid', 'status_name', 'record_type_name']:
            reverse = sort_order == 'desc'
            all_contacts.sort(
                key=lambda x: (x.get(sort_by, '') or '').lower(),
                reverse=reverse
            )
        
        total_contacts = len(all_contacts)
        
        # Apply pagination
        start_index = offset
        end_index = start_index + limit
        paginated_contacts = all_contacts[start_index:end_index]
        
        # Calculate pagination metadata
        total_pages = (total_contacts + limit - 1) // limit  # Ceiling division
        has_next = page < total_pages
        has_prev = page > 1
        
        # Create pagination info
        pagination_info = {
            'page': page,
            'limit': limit,
            'total': total_contacts,
            'pages': total_pages,
            'has_next': has_next,
            'has_prev': has_prev,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'search': search if search else None,
            'is_active': is_active,
            'is_archived': is_archived
        }
        
        # Return paginated response
        response = {
            'contacts': paginated_contacts,
            'pagination': pagination_info
        }
        
        return response, 200

    @ns.doc('create_contact')
    @ns.expect(contact_model)
    @ns.marshal_with(contact_model, code=201)
    def post(self):
        """Create a new contact"""
        contact_data = request.get_json()
        if not contact_data:
            return {"error": "Missing JSON body"}, 400

        print(f"Creating contact with data: {contact_data}")
        print(f"JobNimbus API Key: {current_app.config.get('JOBNIMBUS_API_KEY', 'Not set')}")
        
        # Call JobNimbus API to create contact
        data, status = jobnimbus_request("POST", CONTACTS_ENDPOINT, json=contact_data)
        print(f"JobNimbus API Response - Data: {data}, Status: {status}")  # Debugging line
        
        # Check if the API call was successful (2xx status codes)
        if 200 <= status < 300:
            # Extract contact data from response
            contact_response = data if isinstance(data, dict) else {}
            
            # Create contact object with data from both request and response
            contact = Contact(
                jnid=contact_response.get("jnid") or contact_data.get("jnid"),
                first_name=contact_response.get("first_name") or contact_data.get("first_name", ""),
                last_name=contact_response.get("last_name") or contact_data.get("last_name", ""),
                display_name=contact_response.get("display_name") or contact_data.get("display_name", ""),
                company=contact_response.get("company") or contact_data.get("company", ""),
                status=contact_response.get("status") or contact_data.get("status"),
                status_name=contact_response.get("status_name") or contact_data.get("status_name", "Unknown"),
                record_type=contact_response.get("record_type") or contact_data.get("record_type"),
                record_type_name=contact_response.get("record_type_name") or contact_data.get("record_type_name", "Unknown"),
                address_line1=contact_response.get("address_line1") or contact_data.get("address_line1", ""),
                address_line2=contact_response.get("address_line2") or contact_data.get("address_line2", ""),
                city=contact_response.get("city") or contact_data.get("city", ""),
                state_text=contact_response.get("state_text") or contact_data.get("state_text", ""),
                zip=contact_response.get("zip") or contact_data.get("zip", ""),
                country_name=contact_response.get("country_name") or contact_data.get("country_name", ""),
                created_by_name=contact_response.get("created_by_name") or contact_data.get("created_by_name", ""),
                email=contact_response.get("email") or contact_data.get("email", ""),
                home_phone=contact_response.get("home_phone") or contact_data.get("home_phone", ""),
                mobile_phone=contact_response.get("mobile_phone") or contact_data.get("mobile_phone", ""),
                work_phone=contact_response.get("work_phone") or contact_data.get("work_phone", ""),
                fax_number=contact_response.get("fax_number") or contact_data.get("fax_number", ""),
                website=contact_response.get("website") or contact_data.get("website", ""),
                geo=json.dumps(contact_response.get("geo")) if contact_response.get("geo") else (json.dumps(contact_data.get("geo")) if contact_data.get("geo") else None),
            )
            
            try:
                db.session.add(contact)
                db.session.commit()
                print(f"Contact saved to database with jnid: {contact.jnid}")
            except Exception as e:
                db.session.rollback()
                print(f"Database error: {e}")
                # Still return the API response even if database save fails
                return data, status
            
            # Return the contact data from the database
            return contact.to_dict(), 201
        else:
            # If API call failed, return the error response
            print(f"JobNimbus API call failed with status {status}: {data}")
            return data, status

@ns.route('/<string:jnid>')
@ns.param('jnid', 'The contact identifier')
@ns.response(404, 'Contact not found')
class ContactResource(Resource):
    @ns.doc('get_contact')
    @ns.marshal_with(contact_model)
    def get(self, jnid):
        """Get a contact by ID from JobNimbus API"""
        # Get contact from JobNimbus API
        data, status = jobnimbus_request("GET", f"{CONTACTS_ENDPOINT}/{jnid}")
        
        if status != 200:
            return {"error": "Contact not found"}, 404
        
        # Extract contact data from JobNimbus response
        # JobNimbus returns {"count": 1, "results": [contact_data]}
        if isinstance(data, dict) and "results" in data and data["results"]:
            contact_data = data["results"][0]
        else:
            contact_data = data  # Fallback for direct contact response
            
        return contact_data, 200

    @ns.doc('update_contact')
    @ns.expect(contact_model)
    @ns.marshal_with(contact_model)
    def put(self, jnid):
        """Update a contact"""
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing JSON body"}, 400

            # Make API call to JobNimbus first
            jn_data, jn_status = jobnimbus_request("PUT", f"{CONTACTS_ENDPOINT}/{jnid}", json=data)
                
            if jn_status != 200:
                print(f"JobNimbus API error: {jn_data}")
                return jn_data, jn_status

            # If JobNimbus update successful, update local database
            contact = db.session.get(Contact, jnid)
            
            if contact:
                # Update existing contact in local DB
                print("Updating contact in local database:", jnid)
                for key, value in data.items():
                    if hasattr(contact, key):
                        if key in ['geo', 'location', 'owners', 'subcontractors', 'tags', 'related', 'rules'] and value:
                            # Serialize complex objects to JSON string
                            setattr(contact, key, json.dumps(value))
                        else:
                            setattr(contact, key, value)
                    else:
                        print(f"Warning: Field '{key}' not found in Contact model")

                try:
                    db.session.commit()
                    print("Local database update successful")
                except Exception as db_error:
                    db.session.rollback()
                    print(f"Local database error: {db_error}")
                    # Still return the JobNimbus response even if local DB update fails
                    return jn_data, jn_status
            else:
                print(f"Contact {jnid} not found in local database - will be synced later")
                
            return jn_data, jn_status
                
        except Exception as e:
            print(f"Unexpected error in PUT method: {e}")
            return {"error": "Internal server error", "details": str(e)}, 500

    @ns.doc('delete_contact')
    @ns.expect(delete_request_model)
    @ns.response(204, 'Contact deleted')
    @ns.response(400, 'Missing JSON body')
    @ns.response(404, 'Contact not found')
    def delete(self, jnid):
        """Soft delete a contact"""
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
            f"{CONTACTS_ENDPOINT}/{jnid}",
            json={"is_active": is_active, "is_archived": is_archived},
        )

        if jn_status != 200:
            return jn_data, jn_status

        # If JobNimbus update successful, update local database
        contact = db.session.get(Contact, jnid)
        if contact:
            contact.is_active = is_active
            contact.is_archived = is_archived
            try:
                db.session.commit()
                print(f"Contact {jnid} archived in local database")
            except Exception as db_error:
                db.session.rollback()
                print(f"Local database error: {db_error}")
                # Still return the JobNimbus response even if local DB update fails
                return jn_data, jn_status
        else:
            print(f"Contact {jnid} not found in local database - will be synced later")

        return jn_data, jn_status


