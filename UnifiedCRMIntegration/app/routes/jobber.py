from flask import Blueprint, request, jsonify
from flask_restx import Resource
from app.models import UnifiedLead, CRMConnection, SyncLog, JobberAuth
from app import db
from app.utils.auth import require_api_key
from app.swagger import jobber_ns
from app.services.jobber_service import JobberService
import logging

logger = logging.getLogger(__name__)

jobber_bp = Blueprint('jobber', __name__)

@jobber_ns.route('/clients/<int:user_id>')
class JobberClientsResource(Resource):
    @jobber_ns.doc('get_jobber_clients',
        description='Get client data from Jobber CRM',
        params={'user_id': 'User ID for authentication'},
        responses={
            200: 'Client data retrieved successfully',
            401: 'Unauthorized - no valid tokens available',
            500: 'Internal server error'
        })
    def get(self, user_id):
        """Get client data from Jobber CRM"""
        try:
            # Check if user is authenticated
            auth_record = JobberAuth.query.filter_by(user_id=str(user_id)).first()
            if not auth_record:
                return {'error': 'User not authenticated with Jobber. Please authorize first.'}, 401

            if not auth_record.has_valid_token():
                return {'error': 'Authentication expired. Please refresh your token.'}, 401

            # Get client data from Jobber
            data, error = JobberService.get_client_data(str(user_id))

            if error:
                return {'error': error}, 500

            if not data:
                return {'message': 'No client data found', 'data': []}, 200

            # Flatten the paginated data
            all_clients = []
            for page in data:
                all_clients.extend(page)

            return {
                'message': 'Client data retrieved successfully',
                'count': len(all_clients),
                'data': all_clients
            }, 200

        except Exception as e:
            logger.error(f"Error getting Jobber client data: {e}")
            return {'error': 'Internal server error'}, 500

@jobber_ns.route('/leads')
class JobberLeadsResource(Resource):
    @jobber_ns.doc('get_jobber_leads',
        description='Get leads from Jobber CRM (converted to unified format)',
        responses={
            200: 'Leads retrieved successfully',
            401: 'Unauthorized - no valid tokens available',
            500: 'Internal server error'
        })
    def get(self):
        """Get leads from Jobber CRM in unified format"""
        try:
            # Get user_id from query parameter
            user_id = request.args.get('user_id')
            if not user_id:
                return {'error': 'user_id parameter is required'}, 400

            # Check if user is authenticated
            auth_record = JobberAuth.query.filter_by(user_id=user_id).first()
            if not auth_record:
                return {'error': 'User not authenticated with Jobber. Please authorize first.'}, 401

            if not auth_record.has_valid_token():
                return {'error': 'Authentication expired. Please refresh your token.'}, 401

            # Get client data from Jobber
            data, error = JobberService.get_client_data(user_id)

            if error:
                return {'error': error}, 500

            if not data:
                return {'message': 'No leads found', 'leads': []}, 200

            # Convert to unified lead format
            unified_leads = []
            for page in data:
                for client in page:
                    unified_lead = JobberService.convert_to_unified_lead(client)
                    if unified_lead:
                        unified_leads.append(unified_lead)

            return {
                'message': 'Leads retrieved successfully',
                'count': len(unified_leads),
                'leads': unified_leads
            }, 200

        except Exception as e:
            logger.error(f"Error getting Jobber leads: {e}")
            return {'error': 'Internal server error'}, 500

    @jobber_ns.doc('create_jobber_lead',
        description='Create a lead in Jobber CRM - Coming Soon',
        responses={501: 'Not Implemented'})
    def post(self):
        """Create a lead in Jobber CRM - Coming Soon"""
        return {'message': 'Jobber CRM lead creation coming soon'}, 501