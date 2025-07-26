from flask import Blueprint, request, jsonify
from flask_restx import Resource, Namespace
from app.services.hubspot_service import HubspotService
from app import db
from app.utils.auth import require_api_key
from app.swagger import api, lead_model, lead_response_model, pagination_model, get_parser

hubspot_bp = Blueprint('hubspot', __name__)
hubspot_ns = Namespace('hubspot', description='HubSpot CRM operations')

# Add namespace to API
api.add_namespace(hubspot_ns)

@hubspot_ns.route('/leads')
class HubSpotLeadsResource(Resource):
    @api.doc('list_hubspot_leads',
        description='List leads from HubSpot CRM with pagination',
        responses={200: 'Success', 500: 'Internal Server Error'})
    @api.expect(get_parser)
    @api.marshal_with(pagination_model)
    def get(self):
        """List leads from HubSpot CRM with pagination"""
        try:
            args = get_parser.parse_args()
            hubspot_service = HubspotService()

            result = hubspot_service.get_leads(
                page=args.page,
                per_page=args.per_page,
                last_modified_since=request.args.get('last_modified_since'),
                lead_status=request.args.get('lead_status'),
                lead_source=request.args.get('lead_source')
            )

            return result

        except Exception as e:
            api.abort(500, f'Failed to get HubSpot leads: {str(e)}')

    @api.doc('create_hubspot_lead',
        description='Create a new lead in HubSpot CRM',
        responses={201: 'Lead Created', 400: 'Bad Request', 500: 'Internal Server Error'})
    @api.expect(lead_model)
    @api.marshal_with(lead_response_model, code=201)
    def post(self):
        """Create a new lead in HubSpot CRM"""
        try:
            hubspot_service = HubspotService()
            lead_data = api.payload

            result = hubspot_service.create_lead(lead_data)
            return result, 201

        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, f'Failed to create HubSpot lead: {str(e)}')

@hubspot_ns.route('/leads/<string:external_id>')
class HubSpotLeadResource(Resource):
    @api.doc('get_hubspot_lead',
        description='Get a specific lead from HubSpot CRM by external ID',
        responses={200: 'Success', 404: 'Lead Not Found', 500: 'Internal Server Error'})
    @api.marshal_with(lead_response_model)
    def get(self, external_id):
        """Get a specific lead from HubSpot CRM by external ID"""
        try:
            # Find the lead in unified database
            # unified_lead = UnifiedLead.query.filter_by(
            #     crm_system='hubspot',
            #     crm_external_id=external_id
            # ).first()

            # if not unified_lead:
            #     api.abort(404, 'Lead not found')

            # At this point unified_lead is guaranteed to be not None
            # return unified_lead.to_dict()
            api.abort(404, 'Lead not found')

        except Exception as e:
            api.abort(500, f'Failed to get HubSpot lead: {str(e)}')

    @api.doc('update_hubspot_lead',
        description='Update a lead in HubSpot CRM',
        responses={200: 'Success', 404: 'Lead Not Found', 400: 'Bad Request', 500: 'Internal Server Error'})
    @api.expect(lead_model)
    @api.marshal_with(lead_response_model)
    def put(self, external_id):
        """Update a lead in HubSpot CRM"""
        try:
            hubspot_service = HubspotService()
            lead_data = api.payload

            result = hubspot_service.update_lead(external_id, lead_data)
            return result

        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, f'Failed to update HubSpot lead: {str(e)}')

    @api.doc('delete_hubspot_lead',
        description='Delete a lead from HubSpot CRM',
        responses={204: 'Lead Deleted', 404: 'Lead Not Found', 500: 'Internal Server Error'})
    @api.response(204, 'Lead deleted successfully')
    def delete(self, external_id):
        """Delete a lead from HubSpot CRM"""
        try:
            hubspot_service = HubspotService()

            success = hubspot_service.delete_lead(external_id)
            if success:
                return '', 204
            else:
                api.abort(404, 'Lead not found')

        except ValueError as e:
            api.abort(404, str(e))
        except Exception as e:
            api.abort(500, f'Failed to delete HubSpot lead: {str(e)}')

@hubspot_ns.route('/leads/sync')
class HubSpotSyncResource(Resource):
    @api.doc('sync_hubspot_leads',
        description='Sync all leads from HubSpot CRM to unified database',
        responses={200: 'Sync Completed', 500: 'Internal Server Error'})
    def post(self):
        """Sync all leads from HubSpot CRM to unified database"""
        try:
            hubspot_service = HubspotService()

            result = hubspot_service.sync_leads()
            return result

        except Exception as e:
            api.abort(500, f'Failed to sync HubSpot leads: {str(e)}')