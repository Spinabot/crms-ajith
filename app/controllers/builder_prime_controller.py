from flask import request
from flask_restx import Resource
from app import db
from app.models.crm_db_models import Clients, ClientCRMAuth, CRMs
from app.services.builder_prime_service import BuilderPrimeService
from app.swagger import api, lead_model, lead_response_model, leads_list_model, success_model, sync_result_model, get_parser, builder_prime_ns

# Helper to fetch BuilderPrime API key for a client from DB
def get_builder_prime_api_key(client_id):
    builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
    if not builderprime_crm:
        return None
    auth = ClientCRMAuth.query.filter_by(client_id=client_id, crm_id=builderprime_crm.id).first()
    if auth and auth.api_key:
        return auth.api_key
    return None

@builder_prime_ns.route('/<int:client_id>/leads')
class BuilderPrimeLeadsResource(Resource):
    @api.doc('create_builder_prime_lead',
        description='Create a new lead in BuilderPrime CRM for a specific client')
    @api.expect(lead_model)
    @api.response(201, 'Lead created successfully', success_model)
    @api.response(400, 'Bad Request - Missing required fields')
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(415, 'Unsupported Media Type - Content-Type must be application/json')
    @api.response(500, 'Internal Server Error')
    def post(self, client_id):
        """Create a new lead in BuilderPrime CRM for a specific client"""
        api_key = get_builder_prime_api_key(client_id)
        if not api_key:
            return {'error': 'Unauthorized', 'message': 'BuilderPrime CRM not configured for this client'}, 401

        if not request.is_json:
            return {'error': 'Unsupported Media Type',
                   'message': 'Content-Type must be application/json'}, 415

        data = request.get_json()

        if not data.get('firstName') or not data.get('lastName'):
            return {'error': 'First name and last name are required'}, 400

        try:
            builder_prime_service = BuilderPrimeService(api_key=api_key, client_id=client_id)
            created_lead = builder_prime_service.create_lead(data)
            return {
                'message': f'Lead Successfully Created in BuilderPrime. ID: {created_lead["id"]}',
                'id': created_lead['id'],
                'externalId': created_lead['id']
            }, 201
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('get_builder_prime_leads',
        description='Get leads from BuilderPrime CRM for a specific client with optional filtering')
    @api.expect(get_parser)
    @api.response(200, 'Success', leads_list_model)
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(500, 'Internal Server Error')
    def get(self, client_id):
        """Get leads from BuilderPrime CRM for a specific client"""
        api_key = get_builder_prime_api_key(client_id)
        if not api_key:
            return {'error': 'Unauthorized', 'message': 'BuilderPrime CRM not configured for this client'}, 401

        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            builder_prime_service = BuilderPrimeService(api_key=api_key, client_id=client_id)
            leads_data = builder_prime_service.get_leads(
                page=page,
                per_page=per_page,
                last_modified_since=request.args.get('last-modified-since'),
                lead_status=request.args.get('lead-status'),
                lead_source=request.args.get('lead-source')
            )
            return leads_data, 200
        except Exception as e:
            return {'error': str(e)}, 500

@builder_prime_ns.route('/<int:client_id>/leads/<int:lead_id>')
@api.doc(params={'client_id': 'The client identifier', 'lead_id': 'The lead identifier'})
class BuilderPrimeLeadResource(Resource):
    @api.doc('update_builder_prime_lead',
        description='Update an existing lead in BuilderPrime CRM for a specific client')
    @api.expect(lead_model)
    @api.response(200, 'Lead updated successfully', lead_response_model)
    @api.response(400, 'Bad Request - Invalid data')
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(404, 'Lead not found')
    @api.response(415, 'Unsupported Media Type - Content-Type must be application/json')
    @api.response(500, 'Internal Server Error')
    def put(self, client_id, lead_id):
        """Update a lead in BuilderPrime CRM for a specific client"""
        api_key = get_builder_prime_api_key(client_id)
        if not api_key:
            return {'error': 'Unauthorized', 'message': 'BuilderPrime CRM not configured for this client'}, 401

        if not request.is_json:
            return {'error': 'Unsupported Media Type',
                   'message': 'Content-Type must be application/json'}, 415

        data = request.get_json()

        try:
            builder_prime_service = BuilderPrimeService(api_key=api_key, client_id=client_id)
            updated_lead = builder_prime_service.update_lead(data)
            return updated_lead
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_builder_prime_lead',
        description='Delete a lead from BuilderPrime CRM for a specific client')
    @api.response(200, 'Lead deleted successfully')
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(404, 'Lead not found')
    @api.response(500, 'Internal Server Error')
    def delete(self, client_id, lead_id):
        """Delete a lead from BuilderPrime CRM for a specific client"""
        api_key = get_builder_prime_api_key(client_id)
        if not api_key:
            return {'error': 'Unauthorized', 'message': 'BuilderPrime CRM not configured for this client'}, 401
        try:
            # Simulate deletion (no real DB logic here)
            return {'message': 'Lead deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@builder_prime_ns.route('/<int:client_id>/sync')
class BuilderPrimeSyncResource(Resource):
    @api.doc('sync_builder_prime_leads',
        description='Sync leads from BuilderPrime CRM to unified database for a specific client')
    @api.response(200, 'Sync completed successfully', sync_result_model)
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(500, 'Internal Server Error')
    def post(self, client_id):
        """Sync leads from BuilderPrime CRM for a specific client"""
        api_key = get_builder_prime_api_key(client_id)
        if not api_key:
            return {'error': 'Unauthorized', 'message': 'BuilderPrime CRM not configured for this client'}, 401
        try:
            builder_prime_service = BuilderPrimeService(api_key=api_key, client_id=client_id)
            sync_result = builder_prime_service.sync_leads()
            return sync_result, 200
        except Exception as e:
            return {'error': str(e)}, 500