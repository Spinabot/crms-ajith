from flask import request
from flask_restx import Resource
from app.services.vault_service import VaultService
from app.swagger import api, vault_ns, vault_secrets_model, vault_status_model, vault_connection_model, vault_secret_model

@vault_ns.route('/status')
class VaultStatusResource(Resource):
    @api.doc('get_vault_status',
        description='Get Vault server status and health information')
    @api.response(200, 'Success', vault_status_model)
    @api.response(500, 'Internal Server Error')
    def get(self):
        """Get Vault server status"""
        try:
            vault_service = VaultService()
            status = vault_service.get_vault_status()
            return status, 200
        except Exception as e:
            return {'error': str(e)}, 500

@vault_ns.route('/connection')
class VaultConnectionResource(Resource):
    @api.doc('test_vault_connection',
        description='Test the Vault connection and authentication')
    @api.response(200, 'Success', vault_connection_model)
    @api.response(500, 'Internal Server Error')
    def get(self):
        """Test Vault connection"""
        try:
            vault_service = VaultService()
            connection_status = vault_service.test_connection()
            return connection_status, 200
        except Exception as e:
            return {'error': str(e)}, 500

@vault_ns.route('/secrets')
class VaultSecretsResource(Resource):
    @api.doc('get_all_crm_secrets',
        description='Get all CRM-related secrets from Vault')
    @api.response(200, 'Success', vault_secrets_model)
    @api.response(500, 'Internal Server Error')
    def get(self):
        """Get all CRM secrets from Vault"""
        try:
            vault_service = VaultService()
            secrets = vault_service.get_all_crm_secrets()
            return {
                'secrets': secrets,
                'count': len(secrets),
                'message': 'Secrets retrieved successfully'
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

@vault_ns.route('/secrets/<path:secret_path>')
class VaultSecretResource(Resource):
    @api.doc('get_secret',
        description='Get a specific secret from Vault by path')
    @api.response(200, 'Success', vault_secret_model)
    @api.response(404, 'Secret not found')
    @api.response(500, 'Internal Server Error')
    def get(self, secret_path):
        """Get a specific secret from Vault"""
        try:
            vault_service = VaultService()
            secret_data = vault_service.get_secret(secret_path)
            return {
                'path': secret_path,
                'data': secret_data,
                'message': 'Secret retrieved successfully'
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('create_or_update_secret',
        description='Create or update a secret in Vault')
    @api.expect(vault_secret_model)
    @api.response(200, 'Secret created/updated successfully')
    @api.response(500, 'Internal Server Error')
    def post(self, secret_path):
        """Create or update a secret in Vault"""
        try:
            if not request.is_json:
                return {'error': 'Content-Type must be application/json'}, 415

            secret_data = request.get_json()
            vault_service = VaultService()
            success = vault_service.create_or_update_secret(secret_path, secret_data)

            if success:
                return {
                    'message': f'Secret at {secret_path} created/updated successfully',
                    'path': secret_path
                }, 200
            else:
                return {'error': 'Failed to create/update secret'}, 500

        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_secret',
        description='Delete a secret from Vault')
    @api.response(200, 'Secret deleted successfully')
    @api.response(500, 'Internal Server Error')
    def delete(self, secret_path):
        """Delete a secret from Vault"""
        try:
            vault_service = VaultService()
            success = vault_service.delete_secret(secret_path)

            if success:
                return {
                    'message': f'Secret at {secret_path} deleted successfully',
                    'path': secret_path
                }, 200
            else:
                return {'error': 'Failed to delete secret'}, 500

        except Exception as e:
            return {'error': str(e)}, 500

@vault_ns.route('/list')
class VaultListResource(Resource):
    @api.doc('list_secrets',
        description='List all secrets at a given path')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    def get(self):
        """List secrets in Vault"""
        try:
            path = request.args.get('path', '')
            vault_service = VaultService()
            secrets = vault_service.list_secrets(path)

            return {
                'path': path,
                'secrets': secrets,
                'count': len(secrets),
                'message': 'Secrets listed successfully'
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500