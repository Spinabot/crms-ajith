import requests
import json
from models import db, Clients, ClientCRMAuth, CRMs, BuilderPrimeClientData
from datetime import datetime

class BuilderPrimeService:
    """Service class for BuilderPrime API integration"""

    @staticmethod
    def create_lead(client_id, lead_data):
        """
        Create a new lead/opportunity in BuilderPrime

        Args:
            client_id (int): Client ID
            lead_data (dict): Lead data including contact info, address, etc.

        Returns:
            dict: API response or error message
        """
        try:
            # Get client and their BuilderPrime authentication
            client = Clients.query.get(client_id)
            if not client:
                return {
                    'success': False,
                    'message': f'Client with ID {client_id} not found',
                    'data': None
                }

            # Get BuilderPrime CRM authentication for this client
            builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
            if not builderprime_crm:
                return {
                    'success': False,
                    'message': 'BuilderPrime CRM not configured in system',
                    'data': None
                }

            client_auth = ClientCRMAuth.query.filter_by(
                client_id=client_id,
                crm_id=builderprime_crm.id
            ).first()

            if not client_auth:
                return {
                    'success': False,
                    'message': f'BuilderPrime authentication not found for client {client_id}',
                    'data': None
                }

            api_key = (client_auth.credentials or {}).get('api_key')
            if not api_key:
                return {
                    'success': False,
                    'message': f'BuilderPrime API key not configured for client {client_id}',
                    'data': None
                }

            # Build the API URL
            domain = (client_auth.credentials or {}).get('domain')
            if not domain:
                return {
                    'success': False,
                    'message': f'BuilderPrime domain not configured for client {client_id}',
                    'data': None
                }
            api_url = f"https://{domain}.builderprime.com/api/clients/v1"

            # Debug information
            print(f"🔍 Debug: Making request to BuilderPrime API")
            print(f"   URL: {api_url}")
            print(f"   Domain: {domain}")
            print(f"   Has API Key: {bool(api_key)}")

            # Prepare the request payload
            payload = {
                "secretKey": api_key
            }

            # Add lead data fields if provided
            field_mapping = {
                'first_name': 'firstName',
                'last_name': 'lastName',
                'email': 'email',
                'mobile_phone': 'mobilePhone',
                'mobile_phone_extension': 'mobilePhoneExtension',
                'home_phone': 'homePhone',
                'home_phone_extension': 'homePhoneExtension',
                'office_phone': 'officePhone',
                'office_phone_extension': 'officePhoneExtension',
                'fax': 'fax',
                'address_line1': 'addressLine1',
                'address_line2': 'addressLine2',
                'city': 'city',
                'state': 'state',
                'zip': 'zip',
                'company_name': 'companyName',
                'title': 'title',
                'notes': 'notes',
                'lead_status_name': 'leadStatusName',
                'lead_source_name': 'leadSourceName',
                'sales_person_first_name': 'salesPersonFirstName',
                'sales_person_last_name': 'salesPersonLastName',
                'lead_setter_first_name': 'leadSetterFirstName',
                'lead_setter_last_name': 'leadSetterLastName',
                'class_name': 'className',
                'project_type_name': 'projectTypeName',
                'external_id': 'externalId',
                'dialer_status': 'dialerStatus'
            }

            # Map lead_data to BuilderPrime API format
            for our_field, bp_field in field_mapping.items():
                if our_field in lead_data and lead_data[our_field]:
                    payload[bp_field] = lead_data[our_field]

            # Handle custom fields if provided
            if 'custom_fields' in lead_data and lead_data['custom_fields']:
                payload['customFields'] = []
                for custom_field in lead_data['custom_fields']:
                    if 'name' in custom_field and 'value' in custom_field:
                        payload['customFields'].append({
                            'customFieldName': custom_field['name'],
                            'customFieldValue': custom_field['value']
                        })

            # Make the API request
            headers = {
                'Content-Type': 'application/json'
            }

            # Check if we're in mock mode (for testing)
            if api_key == 'mock_mode' or 'test' in domain.lower():
                print("🔧 Mock Mode: Simulating BuilderPrime API response")

                # Store data in BuilderPrimeClientData table even in mock mode
                stored_data = BuilderPrimeService._store_builderprime_data(
                    client_id, builderprime_crm.id, lead_data,
                    {'id': 12345, 'status': 'success', 'message': 'Lead created in mock mode'},
                    '12345'
                )

                return {
                    'success': True,
                    'message': 'Lead created successfully in BuilderPrime (Mock Mode)',
                    'data': {
                        'builderprime_response': {
                            'id': 12345,
                            'status': 'success',
                            'message': 'Lead created in mock mode'
                        },
                        'client_id': client_id,
                        'domain': domain,
                        'external_id': lead_data.get('external_id'),
                        'mock_mode': True,
                        'stored_data_id': stored_data.get('id') if stored_data else None
                    }
                }

            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            # Handle response
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()

                # Handle plain text responses (BuilderPrime sometimes returns text instead of JSON)
                if 'text/plain' in content_type or not response.text.strip().startswith('{'):
                    # Parse plain text response for opportunity ID
                    response_text = response.text.strip()
                    opportunity_id = None

                    # Try to extract opportunity ID from text like "Client Successfully Created. Opportunity: 3793445"
                    if 'Opportunity:' in response_text:
                        try:
                            opportunity_id = response_text.split('Opportunity:')[-1].strip()
                        except:
                            pass

                    # Store data in BuilderPrimeClientData table
                    stored_data = BuilderPrimeService._store_builderprime_data(
                        client_id, builderprime_crm.id, lead_data,
                        {'message': response_text, 'opportunity_id': opportunity_id},
                        opportunity_id
                    )

                    return {
                        'success': True,
                        'message': 'Lead created successfully in BuilderPrime',
                        'data': {
                            'builderprime_response': {
                                'message': response_text,
                                'opportunity_id': opportunity_id,
                                'content_type': content_type
                            },
                            'client_id': client_id,
                            'domain': domain,
                            'external_id': lead_data.get('external_id'),
                            'stored_data_id': stored_data.get('id') if stored_data else None
                        }
                    }
                else:
                    # Handle JSON responses
                    try:
                        response_data = response.json()

                        # Store data in BuilderPrimeClientData table
                        stored_data = BuilderPrimeService._store_builderprime_data(
                            client_id, builderprime_crm.id, lead_data, response_data, None
                        )

                        return {
                            'success': True,
                            'message': 'Lead created successfully in BuilderPrime',
                            'data': {
                                'builderprime_response': response_data,
                                'client_id': client_id,
                                'domain': domain,
                                'external_id': lead_data.get('external_id'),
                                'stored_data_id': stored_data.get('id') if stored_data else None
                            }
                        }
                    except Exception as json_error:
                        # Handle case where response is not valid JSON
                        return {
                            'success': False,
                            'message': f'BuilderPrime API returned invalid JSON: {str(json_error)}',
                            'data': {
                                'status_code': response.status_code,
                                'response_text': response.text[:500],  # Limit response text
                                'content_type': response.headers.get('content-type', 'unknown'),
                                'api_url': api_url
                            }
                        }
            else:
                error_message = f"BuilderPrime API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_message += f" - {error_data.get('message', 'Unknown error')}"
                except:
                    # Handle non-JSON error responses
                    response_text = response.text[:500] if response.text else "Empty response"
                    error_message += f" - {response_text}"

                return {
                    'success': False,
                    'message': error_message,
                    'data': {
                        'status_code': response.status_code,
                        'response_text': response.text[:500] if response.text else "Empty response",
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'api_url': api_url
                    }
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Network error connecting to BuilderPrime: {str(e)}',
                'data': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating lead in BuilderPrime: {str(e)}',
                'data': None
            }

    @staticmethod
    def _store_builderprime_data(client_id, crm_id, lead_data, api_response, opportunity_id):
        """
        Store BuilderPrime lead data in the database

        Args:
            client_id (int): Our client ID
            crm_id (int): BuilderPrime CRM ID
            lead_data (dict): Original lead data sent to API
            api_response (dict): Response from BuilderPrime API
            opportunity_id (str): Opportunity ID from BuilderPrime

        Returns:
            dict: Stored data record or None if error
        """
        try:
            # Create name from first and last name
            first_name = lead_data.get('first_name', '')
            last_name = lead_data.get('last_name', '')
            name = f"{first_name} {last_name}".strip()

            # Get phone number (prioritize mobile, then home, then office)
            phone_number = (
                lead_data.get('mobile_phone') or
                lead_data.get('home_phone') or
                lead_data.get('office_phone')
            )

            # Prepare metadata with all lead data and API response
            metadata = {
                'lead_data': lead_data,
                'api_response': api_response,
                'opportunity_id': opportunity_id,
                'stored_at': datetime.utcnow().isoformat()
            }

            # Create BuilderPrimeClientData record
            builderprime_data = BuilderPrimeClientData()
            builderprime_data.crm_id = crm_id
            builderprime_data.source_client_id = str(client_id)
            builderprime_data.crm_client_id = opportunity_id or api_response.get('id')
            builderprime_data.name = name
            builderprime_data.email = lead_data.get('email')
            builderprime_data.phone_number = phone_number
            builderprime_data.crm_metadata = metadata

            db.session.add(builderprime_data)
            db.session.commit()

            print(f"✅ Stored BuilderPrime data: ID={builderprime_data.id}, Name={name}, Opportunity={opportunity_id}")

            return {
                'id': builderprime_data.id,
                'name': name,
                'opportunity_id': opportunity_id,
                'email': lead_data.get('email')
            }

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error storing BuilderPrime data: {str(e)}")
            return None

    @staticmethod
    def get_builderprime_leads(client_id=None, limit=50):
        """
        Get BuilderPrime leads from the database

        Args:
            client_id (int, optional): Filter by specific client ID
            limit (int): Maximum number of records to return

        Returns:
            dict: List of BuilderPrime leads or error message
        """
        try:
            # Get BuilderPrime CRM ID
            builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
            if not builderprime_crm:
                return {
                    'success': False,
                    'message': 'BuilderPrime CRM not configured in system',
                    'data': None
                }

            # Build query
            query = BuilderPrimeClientData.query.filter_by(crm_id=builderprime_crm.id)

            if client_id:
                query = query.filter_by(source_client_id=str(client_id))

            # Get leads ordered by creation date (newest first)
            leads = query.order_by(BuilderPrimeClientData.created_at.desc()).limit(limit).all()

            leads_data = []
            for lead in leads:
                leads_data.append({
                    'id': lead.id,
                    'source_client_id': lead.source_client_id,
                    'crm_client_id': lead.crm_client_id,
                    'name': lead.name,
                    'email': lead.email,
                    'phone_number': lead.phone_number,
                    'opportunity_id': lead.crm_metadata.get('opportunity_id') if lead.crm_metadata else None,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None,
                    'updated_at': lead.updated_at.isoformat() if lead.updated_at else None
                })

            return {
                'success': True,
                'message': f'Found {len(leads_data)} BuilderPrime leads',
                'data': leads_data
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving BuilderPrime leads: {str(e)}',
                'data': None
            }

    @staticmethod
    def fetch_builderprime_data(client_id, **params):
        """
        Fetch data from BuilderPrime API using GET request

        Args:
            client_id (int): Client ID
            **params: Query parameters for the API request

        Returns:
            dict: API response or error message
        """
        try:
            # Get client and their BuilderPrime authentication
            client = Clients.query.get(client_id)
            if not client:
                return {
                    'success': False,
                    'message': f'Client with ID {client_id} not found',
                    'data': None
                }

            # Get BuilderPrime CRM authentication for this client
            builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
            if not builderprime_crm:
                return {
                    'success': False,
                    'message': 'BuilderPrime CRM not configured in system',
                    'data': None
                }

            client_auth = ClientCRMAuth.query.filter_by(
                client_id=client_id,
                crm_id=builderprime_crm.id
            ).first()

            if not client_auth:
                return {
                    'success': False,
                    'message': f'BuilderPrime authentication not found for client {client_id}',
                    'data': None
                }

            api_key = (client_auth.credentials or {}).get('api_key')
            if not api_key:
                return {
                    'success': False,
                    'message': f'BuilderPrime API key not configured for client {client_id}',
                    'data': None
                }

            domain = (client_auth.credentials or {}).get('domain')
            if not domain:
                return {
                    'success': False,
                    'message': f'BuilderPrime domain not configured for client {client_id}',
                    'data': None
                }

            # Build the API URL
            api_url = f"https://{domain}.builderprime.com/api/clients"

            # Debug information
            print(f"🔍 Debug: Making GET request to BuilderPrime API")
            print(f"   URL: {api_url}")
            print(f"   Domain: {domain}")
            print(f"   Has API Key: {bool(api_key)}")
            print(f"   Parameters: {params}")

            # Prepare headers with API key
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }

            # Check if we're in mock mode (for testing)
            if api_key == 'mock_mode' or 'test' in domain.lower():
                print("🔧 Mock Mode: Simulating BuilderPrime API response")

                # Return mock data
                mock_data = [
                    {
                        "id": 1035,
                        "firstName": "Eli",
                        "lastName": "Manning",
                        "phoneNumber": "+12125551234",
                        "homePhoneNumber": "+12125551234",
                        "officePhoneNumber": "+12125551234",
                        "emailAddress": "eli@giants.com",
                        "type": "NEW",
                        "addressLine1": "1 MetLife Stadium Dr",
                        "addressLine2": None,
                        "city": "East Rutherford",
                        "state": "NJ",
                        "zip": "07073",
                        "companyName": "New York Giants",
                        "doNotContact": False,
                        "dialerStatus": "At Dialer",
                        "clientId": 21596,
                        "leadStatusName": "Job Paid",
                        "leadSourceDescription": "Direct Mail",
                        "salesPersonFirstName": "Alice",
                        "salesPersonLastName": "Thompson",
                        "leadSetterFirstName": "Bob",
                        "leadSetterLastName": "Roberts",
                        "projectTypeDescription": "Window replacement",
                        "locationName": "Residential",
                        "buildingTypeDescription": "Single Family",
                        "bestContactTime": "Evening",
                        "bestContactMethod": "Mobile Phone",
                        "estimatedValue": 10000,
                        "closeProbability": 50,
                        "createdDate": 1503670680313,
                        "lastModifiedDate": 1560687583714
                    }
                ]

                return {
                    'success': True,
                    'message': 'Data fetched successfully from BuilderPrime (Mock Mode)',
                    'data': {
                        'builderprime_data': mock_data,
                        'client_id': client_id,
                        'domain': domain,
                        'mock_mode': True,
                        'parameters': params
                    }
                }

            # Make the GET request
            response = requests.get(
                api_url,
                headers=headers,
                params=params,
                timeout=30
            )

            # Handle response
            if response.status_code == 200:
                try:
                    response_data = response.json()

                    return {
                        'success': True,
                        'message': 'Data fetched successfully from BuilderPrime',
                        'data': {
                            'builderprime_data': response_data,
                            'client_id': client_id,
                            'domain': domain,
                            'parameters': params,
                            'total_records': len(response_data) if isinstance(response_data, list) else 1
                        }
                    }
                except Exception as json_error:
                    return {
                        'success': False,
                        'message': f'BuilderPrime API returned invalid JSON: {str(json_error)}',
                        'data': {
                            'status_code': response.status_code,
                            'response_text': response.text[:500],  # Limit response text
                            'content_type': response.headers.get('content-type', 'unknown'),
                            'api_url': api_url
                        }
                    }
            else:
                error_message = f"BuilderPrime API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_message += f" - {error_data.get('message', 'Unknown error')}"
                except:
                    # Handle non-JSON error responses
                    response_text = response.text[:500] if response.text else "Empty response"
                    error_message += f" - {response_text}"

                return {
                    'success': False,
                    'message': error_message,
                    'data': {
                        'status_code': response.status_code,
                        'response_text': response.text[:500] if response.text else "Empty response",
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'api_url': api_url
                    }
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Network error connecting to BuilderPrime: {str(e)}',
                'data': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching data from BuilderPrime: {str(e)}',
                'data': None
            }

    @staticmethod
    def update_lead(client_id, opportunity_id, lead_data):
        """
        Update a lead/opportunity in BuilderPrime

        Args:
            client_id (int): Client ID
            opportunity_id (str): BuilderPrime opportunity ID
            lead_data (dict): Lead data to update

        Returns:
            dict: API response or error message
        """
        try:
            # Get client and their BuilderPrime authentication
            client = Clients.query.get(client_id)
            if not client:
                return {
                    'success': False,
                    'message': f'Client with ID {client_id} not found',
                    'data': None
                }

            # Get BuilderPrime CRM authentication for this client
            builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
            if not builderprime_crm:
                return {
                    'success': False,
                    'message': 'BuilderPrime CRM not configured in system',
                    'data': None
                }

            client_auth = ClientCRMAuth.query.filter_by(
                client_id=client_id,
                crm_id=builderprime_crm.id
            ).first()

            if not client_auth:
                return {
                    'success': False,
                    'message': f'BuilderPrime authentication not found for client {client_id}',
                    'data': None
                }

            api_key = (client_auth.credentials or {}).get('api_key')
            if not api_key:
                return {
                    'success': False,
                    'message': f'BuilderPrime API key not configured for client {client_id}',
                    'data': None
                }

            domain = (client_auth.credentials or {}).get('domain')
            if not domain:
                return {
                    'success': False,
                    'message': f'BuilderPrime domain not configured for client {client_id}',
                    'data': None
                }

            # Build the API URL
            api_url = f"https://{domain}.builderprime.com/api/clients/v1/{opportunity_id}"

            # Debug information
            print(f"🔍 Debug: Making POST request to BuilderPrime API")
            print(f"   URL: {api_url}")
            print(f"   Domain: {domain}")
            print(f"   Has API Key: {bool(api_key)}")
            print(f"   Opportunity ID: {opportunity_id}")

            # Prepare the request payload
            payload = {
                "secretKey": api_key
            }

            # Add lead data fields if provided
            field_mapping = {
                'first_name': 'firstName',
                'last_name': 'lastName',
                'email': 'email',
                'mobile_phone': 'mobilePhone',
                'home_phone': 'homePhone',
                'office_phone': 'officePhone',
                'fax': 'fax',
                'do_not_contact': 'doNotContact',
                'dialer_status': 'dialerStatus',
                'address_line1': 'addressLine1',
                'address_line2': 'addressLine2',
                'city': 'city',
                'state': 'state',
                'zip': 'zip',
                'company_name': 'companyName',
                'title': 'title',
                'notes': 'notes',
                'lead_status_name': 'leadStatusName',
                'lead_source_name': 'leadSourceName',
                'sales_person_first_name': 'salesPersonFirstName',
                'sales_person_last_name': 'salesPersonLastName',
                'lead_setter_first_name': 'leadSetterFirstName',
                'lead_setter_last_name': 'leadSetterLastName',
                'class_name': 'className',
                'project_type_name': 'projectTypeName'
            }

            # Map lead_data to BuilderPrime API format
            for our_field, bp_field in field_mapping.items():
                if our_field in lead_data and lead_data[our_field] is not None:
                    payload[bp_field] = lead_data[our_field]

            # Handle custom fields if provided
            if 'custom_fields' in lead_data and lead_data['custom_fields']:
                payload['customFields'] = []
                for custom_field in lead_data['custom_fields']:
                    if 'name' in custom_field and 'value' in custom_field:
                        payload['customFields'].append({
                            'customFieldName': custom_field['name'],
                            'customFieldValue': custom_field['value']
                        })

            # Make the API request
            headers = {
                'Content-Type': 'application/json'
            }

            # Check if we're in mock mode (for testing)
            if api_key == 'mock_mode' or 'test' in domain.lower():
                print("🔧 Mock Mode: Simulating BuilderPrime API update response")

                # Update data in BuilderPrimeClientData table
                stored_data = BuilderPrimeService._update_builderprime_data(
                    client_id, builderprime_crm.id, opportunity_id, lead_data,
                    {'id': opportunity_id, 'status': 'success', 'message': 'Lead updated in mock mode'},
                    'mock_mode'
                )

                return {
                    'success': True,
                    'message': 'Lead updated successfully in BuilderPrime (Mock Mode)',
                    'data': {
                        'builderprime_response': {
                            'id': opportunity_id,
                            'status': 'success',
                            'message': 'Lead updated in mock mode'
                        },
                        'client_id': client_id,
                        'domain': domain,
                        'opportunity_id': opportunity_id,
                        'mock_mode': True,
                        'stored_data_id': stored_data.get('id') if stored_data else None
                    }
                }

            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            # Handle response
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()

                # Handle plain text responses (BuilderPrime sometimes returns text instead of JSON)
                if 'text/plain' in content_type or not response.text.strip().startswith('{'):
                    # Parse plain text response
                    response_text = response.text.strip()

                    # Update data in BuilderPrimeClientData table
                    stored_data = BuilderPrimeService._update_builderprime_data(
                        client_id, builderprime_crm.id, opportunity_id, lead_data,
                        {'message': response_text, 'opportunity_id': opportunity_id},
                        opportunity_id
                    )

                    return {
                        'success': True,
                        'message': 'Lead updated successfully in BuilderPrime',
                        'data': {
                            'builderprime_response': {
                                'message': response_text,
                                'opportunity_id': opportunity_id,
                                'content_type': content_type
                            },
                            'client_id': client_id,
                            'domain': domain,
                            'opportunity_id': opportunity_id,
                            'stored_data_id': stored_data.get('id') if stored_data else None
                        }
                    }
                else:
                    # Handle JSON responses
                    try:
                        response_data = response.json()

                        # Update data in BuilderPrimeClientData table
                        stored_data = BuilderPrimeService._update_builderprime_data(
                            client_id, builderprime_crm.id, opportunity_id, lead_data, response_data, opportunity_id
                        )

                        return {
                            'success': True,
                            'message': 'Lead updated successfully in BuilderPrime',
                            'data': {
                                'builderprime_response': response_data,
                                'client_id': client_id,
                                'domain': domain,
                                'opportunity_id': opportunity_id,
                                'stored_data_id': stored_data.get('id') if stored_data else None
                            }
                        }
                    except Exception as json_error:
                        # Handle case where response is not valid JSON
                        return {
                            'success': False,
                            'message': f'BuilderPrime API returned invalid JSON: {str(json_error)}',
                            'data': {
                                'status_code': response.status_code,
                                'response_text': response.text[:500],  # Limit response text
                                'content_type': response.headers.get('content-type', 'unknown'),
                                'api_url': api_url
                            }
                        }
            else:
                error_message = f"BuilderPrime API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_message += f" - {error_data.get('message', 'Unknown error')}"

                    # Check for specific BuilderPrime validation errors
                    if 'lead status could not be found' in error_data.get('message', '').lower():
                        error_message += " (Tip: The lead status name must match exactly with what's configured in BuilderPrime. Common values include: 'Lead Received', 'Qualified', 'Proposal Sent', 'Closed Won', 'Closed Lost')"
                    elif 'lead source could not be found' in error_data.get('message', '').lower():
                        error_message += " (Tip: The lead source name must match exactly with what's configured in BuilderPrime. Common values include: 'Website', 'Phone', 'Referral', 'Social Media')"
                    elif 'dialer status could not be found' in error_data.get('message', '').lower():
                        error_message += " (Tip: The dialer status must match exactly with what's configured in BuilderPrime. Common values include: 'Not Started', 'In Progress', 'Completed')"
                    elif 'project type could not be found' in error_data.get('message', '').lower():
                        error_message += " (Tip: The project type name must match exactly with what's configured in BuilderPrime. Common values include: 'Kitchen Renovation', 'Bathroom Remodel', 'Roofing', 'Windows')"
                    elif 'class could not be found' in error_data.get('message', '').lower():
                        error_message += " (Tip: The class name must match exactly with what's configured in BuilderPrime. Common values include: 'Residential', 'Commercial')"

                except:
                    # Handle non-JSON error responses
                    response_text = response.text[:500] if response.text else "Empty response"
                    error_message += f" - {response_text}"

                return {
                    'success': False,
                    'message': error_message,
                    'data': {
                        'status_code': response.status_code,
                        'response_text': response.text[:500] if response.text else "Empty response",
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'api_url': api_url
                    }
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Network error connecting to BuilderPrime: {str(e)}',
                'data': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating lead in BuilderPrime: {str(e)}',
                'data': None
            }

    @staticmethod
    def _update_builderprime_data(client_id, crm_id, opportunity_id, lead_data, api_response, updated_opportunity_id):
        """
        Update BuilderPrime lead data in the database

        Args:
            client_id (int): Our client ID
            crm_id (int): BuilderPrime CRM ID
            opportunity_id (str): Original opportunity ID
            lead_data (dict): Updated lead data sent to API
            api_response (dict): Response from BuilderPrime API
            updated_opportunity_id (str): Updated opportunity ID from BuilderPrime

        Returns:
            dict: Updated data record or None if error
        """
        try:
            # Find existing record by opportunity ID
            existing_data = BuilderPrimeClientData.query.filter_by(
                crm_id=crm_id,
                crm_client_id=opportunity_id
            ).first()

            if not existing_data:
                print(f"⚠️ Warning: No existing BuilderPrime data found for opportunity {opportunity_id}")
                return None

            # Create name from first and last name
            first_name = lead_data.get('first_name', '')
            last_name = lead_data.get('last_name', '')
            name = f"{first_name} {last_name}".strip()

            # Get phone number (prioritize mobile, then home, then office)
            phone_number = (
                lead_data.get('mobile_phone') or
                lead_data.get('home_phone') or
                lead_data.get('office_phone')
            )

            # Update existing record
            existing_data.name = name if name else existing_data.name
            existing_data.email = lead_data.get('email', existing_data.email)
            existing_data.phone_number = phone_number if phone_number else existing_data.phone_number
            existing_data.crm_client_id = updated_opportunity_id

            # Update metadata with new lead data and API response
            metadata = existing_data.crm_metadata or {}
            metadata.update({
                'lead_data': lead_data,
                'api_response': api_response,
                'opportunity_id': updated_opportunity_id,
                'updated_at': datetime.utcnow().isoformat()
            })
            existing_data.crm_metadata = metadata

            db.session.commit()

            print(f"✅ Updated BuilderPrime data: ID={existing_data.id}, Name={name}, Opportunity={updated_opportunity_id}")

            return {
                'id': existing_data.id,
                'name': name,
                'opportunity_id': updated_opportunity_id,
                'email': lead_data.get('email')
            }

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating BuilderPrime data: {str(e)}")
            return None