from flask import Blueprint, request, jsonify
from app.services.lead_service import LeadService
from app.utils.auth import require_api_key
from flask_restx import Resource
from app.swagger import leads_ns, api, lead_model, get_parser, pagination_model

leads_bp = Blueprint('leads', __name__)

def check_auth():
    """Check authentication before processing request"""
    api_key = request.headers.get('x-api-key')
    if not api_key and request.is_json:
        api_key = request.get_json().get('secretKey')
    if not api_key or api_key != api.app.config['API_KEY']:
        return {'error': 'Unauthorized', 'message': 'Invalid or missing API key'}, 401
    return None

@leads_ns.route('/clients/v1')
class LeadsResource(Resource):
    @api.doc('create_lead', 
        description='Create a new lead',
        responses={201: 'Lead created successfully'})
    @api.expect(lead_model)
    def post(self):
        """Create a new lead"""
        auth_error = check_auth()
        if auth_error:
            return auth_error

        if not request.is_json:
            return {'error': 'Unsupported Media Type', 
                   'message': 'Content-Type must be application/json'}, 415

        data = request.get_json()
        
        if not data.get('firstName') or not data.get('lastName'):
            return {'error': 'First name and last name are required'}, 400

        try:
            lead = LeadService.create_lead(data)
            return {
                'message': f'Client Successfully Created. Opportunity: {lead.id}',
                'id': lead.id
            }, 201
        except Exception as e:
            return {'error': str(e)}, 500

@leads_ns.route('/clients')
class LeadsListResource(Resource):
    @api.doc('get_leads',
        responses={
            200: 'Success',
            401: 'Unauthorized'
        })
    @api.expect(get_parser)
    def get(self):
        """Get a list of leads"""
        auth_error = check_auth()
        if auth_error:
            return auth_error

        args = get_parser.parse_args()
        try:
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            
            leads, total_count = LeadService.get_leads(
                last_modified_since=args.get('last-modified-since'),
                lead_status=args.get('lead-status'),
                lead_source=args.get('lead-source'),
                dialer_status=args.get('dialer-status'),
                phone=args.get('phone'),
                page=page,
                per_page=per_page
            )
            
            result = {
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'leads': [lead.to_dict() for lead in leads]
            }
            return result, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

@leads_ns.route('/clients/v1/<int:lead_id>')
@api.doc(params={'lead_id': 'The lead identifier'})
class LeadResource(Resource):
    @api.doc('update_lead',
        description='Update an existing lead',
        responses={
            200: 'Lead updated successfully',
            404: 'Lead not found',
            415: 'Unsupported Media Type'
        })
    @api.expect(lead_model)
    def put(self, lead_id):
        """Update a lead"""
        auth_error = check_auth()
        if auth_error:
            return auth_error

        if not request.is_json:
            return {'error': 'Unsupported Media Type', 
                   'message': 'Content-Type must be application/json'}, 415

        data = request.get_json()
        lead = LeadService.update_lead(lead_id, data)
        if not lead:
            return {'error': 'Lead not found'}, 404
        return lead.to_dict()

    @api.doc('delete_lead',
        description='Delete a lead',
        responses={
            200: 'Lead deleted successfully',
            404: 'Lead not found'
        })
    def delete(self, lead_id):
        """Delete a lead"""
        auth_error = check_auth()
        if auth_error:
            return auth_error

        if LeadService.delete_lead(lead_id):
            return {'message': 'Lead deleted successfully'}, 200
        return {'error': 'Lead not found'}, 404
