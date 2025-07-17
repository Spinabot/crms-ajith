from flask import request
from flask_restx import Resource
from app.models.unified_lead import UnifiedLead
from app.models.crm_connection import CRMConnection
from app.models.sync_log import SyncLog
from app import db
from app.utils.auth import require_api_key
from app.services.builder_prime_service import BuilderPrimeService
from config.vault_config import get_secret
from app.swagger import api, lead_model, lead_response_model, leads_list_model, success_model, sync_result_model, get_parser, builder_prime_ns
from app.config import Config

def check_builder_prime_auth():
    """Check BuilderPrime authentication using Vault first, then Config as fallback"""
    api_key = None
    try:
        api_key = get_secret('BUILDER_PRIME_API_KEY')
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not fetch BuilderPrime API key from Vault: {e}. Falling back to config.")
        api_key = Config.BUILDER_PRIME_API_KEY
    if not api_key:
        return {'error': 'Unauthorized', 'message': 'BuilderPrime CRM not configured'}, 401
    return None

@builder_prime_ns.route('/leads')
class BuilderPrimeLeadsResource(Resource):
    @api.doc('create_builder_prime_lead',
        description='Create a new lead in BuilderPrime CRM')
    @api.expect(lead_model)
    @api.response(201, 'Lead created successfully', success_model)
    @api.response(400, 'Bad Request - Missing required fields')
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(415, 'Unsupported Media Type - Content-Type must be application/json')
    @api.response(500, 'Internal Server Error')
    def post(self):
        """Create a new lead in BuilderPrime CRM"""
        auth_error = check_builder_prime_auth()
        if auth_error:
            return auth_error

        if not request.is_json:
            return {'error': 'Unsupported Media Type',
                   'message': 'Content-Type must be application/json'}, 415

        data = request.get_json()

        if not data.get('firstName') or not data.get('lastName'):
            return {'error': 'First name and last name are required'}, 400

        try:
            # Create lead using BuilderPrime service
            builder_prime_service = BuilderPrimeService()
            created_lead = builder_prime_service.create_lead(data)

            # Log sync
            sync_log = SyncLog()
            sync_log.crm_system = 'builder_prime'
            sync_log.operation = 'create'
            sync_log.status = 'success'
            sync_log.lead_id = created_lead['id']
            sync_log.external_id = created_lead.get('id')
            sync_log.sync_data = created_lead
            db.session.add(sync_log)
            db.session.commit()

            return {
                'message': f'Lead Successfully Created in BuilderPrime. ID: {created_lead["id"]}',
                'id': created_lead['id'],
                'externalId': created_lead['id']
            }, 201

        except Exception as e:
            # Log error
            sync_log = SyncLog()
            sync_log.crm_system = 'builder_prime'
            sync_log.operation = 'create'
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.sync_data = data
            db.session.add(sync_log)
            db.session.commit()

            return {'error': str(e)}, 500

    @api.doc('get_builder_prime_leads',
        description='Get leads from BuilderPrime CRM with optional filtering')
    @api.expect(get_parser)
    @api.response(200, 'Success', leads_list_model)
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(500, 'Internal Server Error')
    def get(self):
        """Get leads from BuilderPrime CRM"""
        auth_error = check_builder_prime_auth()
        if auth_error:
            return auth_error

        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            builder_prime_service = BuilderPrimeService()
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

@builder_prime_ns.route('/leads/<int:lead_id>')
@api.doc(params={'lead_id': 'The lead identifier'})
class BuilderPrimeLeadResource(Resource):
    @api.doc('update_builder_prime_lead',
        description='Update an existing lead in BuilderPrime CRM')
    @api.expect(lead_model)
    @api.response(200, 'Lead updated successfully', lead_response_model)
    @api.response(400, 'Bad Request - Invalid data')
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(404, 'Lead not found')
    @api.response(415, 'Unsupported Media Type - Content-Type must be application/json')
    @api.response(500, 'Internal Server Error')
    def put(self, lead_id):
        """Update a lead in BuilderPrime CRM"""
        auth_error = check_builder_prime_auth()
        if auth_error:
            return auth_error

        if not request.is_json:
            return {'error': 'Unsupported Media Type',
                   'message': 'Content-Type must be application/json'}, 415

        data = request.get_json()

        try:
            # Find the unified lead
            unified_lead = UnifiedLead.query.filter_by(
                id=lead_id,
                crm_system='builder_prime'
            ).first()

            if not unified_lead:
                return {'error': 'Lead not found'}, 404

            # Update using BuilderPrime service
            builder_prime_service = BuilderPrimeService()
            updated_lead = builder_prime_service.update_lead(
                unified_lead.crm_external_id,
                data
            )

            # Log sync
            sync_log = SyncLog()
            sync_log.crm_system = 'builder_prime'
            sync_log.operation = 'update'
            sync_log.status = 'success'
            sync_log.lead_id = unified_lead.id
            sync_log.external_id = unified_lead.crm_external_id
            sync_log.sync_data = updated_lead
            db.session.add(sync_log)
            db.session.commit()

            return updated_lead

        except Exception as e:
            # Log error
            sync_log = SyncLog()
            sync_log.crm_system = 'builder_prime'
            sync_log.operation = 'update'
            sync_log.status = 'failed'
            sync_log.lead_id = lead_id
            sync_log.error_message = str(e)
            sync_log.sync_data = data
            db.session.add(sync_log)
            db.session.commit()

            return {'error': str(e)}, 500

    @api.doc('delete_builder_prime_lead',
        description='Delete a lead from BuilderPrime CRM')
    @api.response(200, 'Lead deleted successfully')
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(404, 'Lead not found')
    @api.response(500, 'Internal Server Error')
    def delete(self, lead_id):
        """Delete a lead from BuilderPrime CRM"""
        auth_error = check_builder_prime_auth()
        if auth_error:
            return auth_error

        try:
            # Find the unified lead
            unified_lead = UnifiedLead.query.filter_by(
                id=lead_id,
                crm_system='builder_prime'
            ).first()

            if not unified_lead:
                return {'error': 'Lead not found'}, 404

            # Log sync BEFORE deleting the lead
            sync_log = SyncLog()
            sync_log.crm_system = 'builder_prime'
            sync_log.operation = 'delete'
            sync_log.status = 'success'
            sync_log.lead_id = unified_lead.id  # Still exists at this point
            sync_log.external_id = unified_lead.crm_external_id
            db.session.add(sync_log)

            # Now delete the lead (foreign key constraint will automatically set lead_id to NULL in sync_logs)
            db.session.delete(unified_lead)
            db.session.commit()

            return {'message': 'Lead deleted successfully'}, 200

        except Exception as e:
            # Log error
            try:
                sync_log = SyncLog()
                sync_log.crm_system = 'builder_prime'
                sync_log.operation = 'delete'
                sync_log.status = 'failed'
                sync_log.lead_id = lead_id
                sync_log.error_message = str(e)
                db.session.add(sync_log)
                db.session.commit()
            except:
                # If logging fails, just rollback and continue
                db.session.rollback()

            return {'error': str(e)}, 500

@builder_prime_ns.route('/sync')
class BuilderPrimeSyncResource(Resource):
    @api.doc('sync_builder_prime_leads',
        description='Sync leads from BuilderPrime CRM to unified database')
    @api.response(200, 'Sync completed successfully', sync_result_model)
    @api.response(401, 'Unauthorized - BuilderPrime CRM not configured')
    @api.response(500, 'Internal Server Error')
    def post(self):
        """Sync leads from BuilderPrime CRM"""
        auth_error = check_builder_prime_auth()
        if auth_error:
            return auth_error

        try:
            builder_prime_service = BuilderPrimeService()
            sync_result = builder_prime_service.sync_leads()

            return sync_result, 200

        except Exception as e:
            return {'error': str(e)}, 500