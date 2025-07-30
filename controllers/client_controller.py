from flask import request, jsonify
from services.client_service import ClientService

class ClientController:
    """Controller class for handling client-related HTTP requests"""

    @staticmethod
    def create_client():
        """
        Create a new client

        Expected JSON payload:
        {
            "company_name": "Company Name",
            "email": "client@example.com",
            "other_contact_info": "Additional info (optional)",
            "builderprime": {
                "api_key": "bp_api_key_here",
                "domain": "subdomain"
            },
            "hubspot_api_key": "hs_api_key_here (optional)"
        }
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'data': None
                }), 400

            # Validate required fields
            company_name = data.get('company_name')
            email = data.get('email')

            if not company_name or not email:
                return jsonify({
                    'success': False,
                    'message': 'Company name and email are required',
                    'data': None
                }), 400

            # Get optional fields
            other_contact_info = data.get('other_contact_info')
            builderprime = data.get('builderprime')
            hubspot_api_key = data.get('hubspot_api_key')

            # Call service to create client
            result = ClientService.create_client(
                company_name=company_name,
                email=email,
                other_contact_info=other_contact_info,
                builderprime=builderprime,
                hubspot_api_key=hubspot_api_key
            )

            if result['success']:
                return jsonify(result), 201
            else:
                return jsonify(result), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'data': None
            }), 500

    @staticmethod
    def update_client(client_id):
        """
        Update an existing client

        Expected JSON payload (all fields optional):
        {
            "company_name": "Updated Company Name",
            "email": "updated@example.com",
            "other_contact_info": "Updated contact info",
            "builderprime": {
                "api_key": "new_bp_api_key",
                "domain": "new_subdomain"
            },
            "hubspot_api_key": "new_hs_api_key"
        }
        """
        try:
            # Validate client_id
            try:
                client_id = int(client_id)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid client ID. Must be a number.',
                    'data': None
                }), 400

            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided for update',
                    'data': None
                }), 400

            # Get all optional fields
            company_name = data.get('company_name')
            email = data.get('email')
            other_contact_info = data.get('other_contact_info')
            builderprime = data.get('builderprime')
            hubspot_api_key = data.get('hubspot_api_key')

            # Check if at least one field is provided
            if all(field is None for field in [company_name, email, other_contact_info, builderprime, hubspot_api_key]):
                return jsonify({
                    'success': False,
                    'message': 'At least one field must be provided for update',
                    'data': None
                }), 400

            # Call service to update client
            result = ClientService.update_client(
                client_id=client_id,
                company_name=company_name,
                email=email,
                other_contact_info=other_contact_info,
                builderprime=builderprime,
                hubspot_api_key=hubspot_api_key
            )

            if result['success']:
                return jsonify(result), 200
            else:
                # Determine appropriate status code based on error type
                error_message = result['message'].lower()
                if 'not found' in error_message:
                    status_code = 404
                elif 'already exists' in error_message:
                    status_code = 409
                else:
                    status_code = 400

                return jsonify(result), status_code

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'data': None
            }), 500

    @staticmethod
    def get_all_clients():
        """
        Get all clients

        Returns:
            JSON response with list of all clients
        """
        try:
            result = ClientService.get_all_clients()

            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'data': None
            }), 500

    @staticmethod
    def get_client_by_id(client_id):
        """
        Get client by ID

        Args:
            client_id (int): Client ID from URL parameter

        Returns:
            JSON response with client data
        """
        try:
            # Validate client_id
            try:
                client_id = int(client_id)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid client ID. Must be a number.',
                    'data': None
                }), 400

            result = ClientService.get_client_by_id(client_id)

            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 404

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'data': None
            }), 500