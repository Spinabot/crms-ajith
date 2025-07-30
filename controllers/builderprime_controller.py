from flask import request, jsonify
from services.builderprime_service import BuilderPrimeService

class BuilderPrimeController:
    """Controller class for handling BuilderPrime-related HTTP requests"""

    @staticmethod
    def create_lead(client_id):
        """
        Create a new lead/opportunity in BuilderPrime for a specific client

        Expected JSON payload:
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "johnsmith3@gmail.com",
            "mobile_phone": "+18005554444",
            "mobile_phone_extension": "1",
            "home_phone": "+18005554444",
            "home_phone_extension": "2",
            "office_phone": "+18005554444",
            "office_phone_extension": "3",
            "fax": "+18005554444",
            "address_line1": "123 Main Street",
            "address_line2": "Suite 2",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "12345",
            "company_name": "Widgets Galore",
            "title": "President",
            "notes": "Some notes",
            "lead_status_name": "Lead Received",
            "lead_source_name": "Facebook",
            "sales_person_first_name": "Alice",
            "sales_person_last_name": "Thompson",
            "lead_setter_first_name": "Bob",
            "lead_setter_last_name": "Roberts",
            "class_name": "Residential",
            "project_type_name": "Kitchen Renovation",
            "external_id": "AB-4617",
            "dialer_status": "1st Attempt",
            "custom_fields": [
                {
                    "name": "Budget",
                    "value": "5000"
                },
                {
                    "name": "Referred By",
                    "value": "Axl Rose"
                }
            ]
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

            # Get request data
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'data': None
                }), 400

            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email']
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}',
                    'data': None
                }), 400

            # Call service to create lead
            result = BuilderPrimeService.create_lead(client_id, data)

            if result['success']:
                return jsonify(result), 201
            else:
                # Determine appropriate status code based on error type
                error_message = result['message'].lower()
                if 'not found' in error_message:
                    status_code = 404
                elif 'not configured' in error_message or 'not found' in error_message:
                    status_code = 400
                elif 'network error' in error_message or 'timeout' in error_message:
                    status_code = 503
                else:
                    status_code = 500

                return jsonify(result), status_code

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'data': None
            }), 500

    @staticmethod
    def get_leads(client_id=None):
        """
        Get BuilderPrime leads from the database

        Args:
            client_id (int, optional): Client ID from URL parameter

        Returns:
            JSON response with list of BuilderPrime leads
        """
        try:
            # Validate client_id if provided
            if client_id:
                try:
                    client_id = int(client_id)
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid client ID. Must be a number.',
                        'data': None
                    }), 400

            # Get limit from query parameters (default 50)
            limit = request.args.get('limit', 50, type=int)
            if limit > 100:  # Cap at 100 for performance
                limit = 100

            result = BuilderPrimeService.get_builderprime_leads(client_id, limit)

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
    def fetch_builderprime_data(client_id):
        """
        Fetch data from BuilderPrime API using GET request

        Args:
            client_id (int): Client ID from URL parameter

        Returns:
            JSON response with BuilderPrime API data
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

            # Get query parameters from request
            params = {}

            # last-modified-since: Optional. Number in milliseconds since epoch
            last_modified_since = request.args.get('last-modified-since', type=int)
            if last_modified_since:
                params['last-modified-since'] = last_modified_since

            # lead-status: Optional. String for lead status name
            lead_status = request.args.get('lead-status')
            if lead_status:
                params['lead-status'] = lead_status

            # lead-source: Optional. String for lead source name
            lead_source = request.args.get('lead-source')
            if lead_source:
                params['lead-source'] = lead_source

            # dialer-status: Optional. String for dialer status
            dialer_status = request.args.get('dialer-status')
            if dialer_status:
                params['dialer-status'] = dialer_status

            # phone: Optional. String for phone number (E.164 format recommended)
            phone = request.args.get('phone')
            if phone:
                params['phone'] = phone

            # limit: Optional. Number (max 500)
            limit = request.args.get('limit', type=int)
            if limit:
                if limit > 500:
                    return jsonify({
                        'success': False,
                        'message': 'Limit cannot exceed 500 records',
                        'data': None
                    }), 400
                params['limit'] = limit

            # page: Optional. Number (starts with 0)
            page = request.args.get('page', type=int)
            if page is not None:
                if page < 0:
                    return jsonify({
                        'success': False,
                        'message': 'Page number must be 0 or greater',
                        'data': None
                    }), 400
                params['page'] = page

            # Call service to fetch data from BuilderPrime API
            result = BuilderPrimeService.fetch_builderprime_data(client_id, **params)

            if result['success']:
                return jsonify(result), 200
            else:
                # Determine appropriate status code based on error type
                error_message = result['message'].lower()
                if 'not found' in error_message:
                    status_code = 404
                elif 'not configured' in error_message:
                    status_code = 400
                elif 'network error' in error_message or 'timeout' in error_message:
                    status_code = 503
                else:
                    status_code = 500

                return jsonify(result), status_code

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'data': None
            }), 500

    @staticmethod
    def update_lead(client_id, opportunity_id):
        """
        Update a lead/opportunity in BuilderPrime

        Args:
            client_id (int): Client ID from URL parameter
            opportunity_id (str): BuilderPrime opportunity ID from URL parameter

        Returns:
            JSON response with update result
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

            # Validate opportunity_id
            if not opportunity_id:
                return jsonify({
                    'success': False,
                    'message': 'Opportunity ID is required',
                    'data': None
                }), 400

            # Get request data
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided for update',
                    'data': None
                }), 400

            # Call service to update lead
            result = BuilderPrimeService.update_lead(client_id, opportunity_id, data)

            if result['success']:
                return jsonify(result), 200
            else:
                # Determine appropriate status code based on error type
                error_message = result['message'].lower()
                if 'not found' in error_message:
                    status_code = 404
                elif 'not configured' in error_message:
                    status_code = 400
                elif 'network error' in error_message or 'timeout' in error_message:
                    status_code = 503
                else:
                    status_code = 500

                return jsonify(result), status_code

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'data': None
            }), 500