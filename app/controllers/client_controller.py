from flask_restx import Resource, Namespace, fields
from flask import request
from app.services.client_service import ClientService

client_ns = Namespace('clients', description='Client registration and CRM key management')

# DTO for client registration request
client_registration_model = client_ns.model('ClientRegistration', {
    'name': fields.String(required=True, description='Company name'),
    'email': fields.String(required=True, description='Contact email'),
    'otherContactInfo': fields.String(required=False, description='Other contact info'),
    'domain': fields.String(required=False, description='Domain URL of the client'),  # Added domain field
    'builderPrimeApiKey': fields.String(required=False, description='BuilderPrime API Key'),
    'hubspotApiToken': fields.String(required=False, description='HubSpot API Token'),
})

# DTO for client registration response
client_registration_response_model = client_ns.model('ClientRegistrationResponse', {
    'id': fields.Integer(description='Client ID'),
    'name': fields.String(description='Company name'),
    'email': fields.String(description='Contact email'),
    'otherContactInfo': fields.String(description='Other contact info'),
    'domain': fields.String(description='Domain URL of the client'),  # Added domain field
    'crmAuths': fields.List(fields.Raw, description='List of CRM auths for this client'),
})

@client_ns.route('/')
class ClientRegistrationResource(Resource):
    @client_ns.expect(client_registration_model)
    @client_ns.marshal_with(client_registration_response_model)
    def post(self):
        """Register a new client and store their CRM API keys"""
        data = request.get_json()
        try:
            client, crm_auths = ClientService.register_client(data)
            return {
                'id': client.id,
                'name': client.name,
                'email': client.email,
                'otherContactInfo': client.other_contact_info,
                'domain': client.domain,  # Added domain field to response
                'crmAuths': [auth.to_dict() for auth in crm_auths]
            }, 201
        except Exception as e:
            return {'error': str(e)}, 400

@client_ns.route('/<int:client_id>')
class ClientResource(Resource):
    @client_ns.marshal_with(client_registration_response_model)
    def get(self, client_id):
        """Get a client by client ID"""
        client, crm_auths = ClientService.get_client_by_id(client_id)
        if not client:
            client_ns.abort(404, f"Client with id {client_id} not found")
        return {
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'otherContactInfo': client.other_contact_info,
            'domain': client.domain,
            'crmAuths': [auth.to_dict() for auth in crm_auths]
        }