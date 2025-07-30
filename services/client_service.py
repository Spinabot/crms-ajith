from models import db, Clients, ClientCRMAuth, CRMs
from datetime import datetime

class ClientService:
    """Service class for client-related business logic"""

    @staticmethod
    def create_client(company_name, email, other_contact_info=None, builderprime=None, hubspot_api_key=None):
        """
        Create a new client with CRM authentication

        Args:
            company_name (str): Client company name
            email (str): Client email
            other_contact_info (str, optional): Additional contact information
            builderprime (dict, optional): BuilderPrime credentials with api_key and domain
            hubspot_api_key (str, optional): HubSpot API key

        Returns:
            dict: Created client data or error message
        """
        try:
            # Check if client with same email already exists
            existing_client = Clients.query.filter_by(email=email).first()
            if existing_client:
                return {
                    'success': False,
                    'message': f'Client with email {email} already exists',
                    'data': None
                }

            # Create new client
            new_client = Clients()
            new_client.company_name = company_name
            new_client.email = email
            new_client.other_contact_info = other_contact_info

            db.session.add(new_client)
            db.session.commit()

            # Create CRM authentication records if API keys are provided
            crm_auths = []

            # Get CRM IDs
            builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
            hubspot_crm = CRMs.query.filter_by(name='HubSpot').first()

            # Create BuilderPrime authentication if credentials provided
            if builderprime and builderprime_crm:
                builderprime_auth = ClientCRMAuth()
                builderprime_auth.client_id = new_client.id
                builderprime_auth.crm_id = builderprime_crm.id
                builderprime_auth.credentials = {
                    "api_key": builderprime.get('api_key'),
                    "domain": builderprime.get('domain')
                }
                db.session.add(builderprime_auth)
                crm_auths.append('BuilderPrime')

            # Create HubSpot authentication if API key provided
            if hubspot_api_key and hubspot_crm:
                hubspot_auth = ClientCRMAuth()
                hubspot_auth.client_id = new_client.id
                hubspot_auth.crm_id = hubspot_crm.id
                hubspot_auth.credentials = {"api_key": hubspot_api_key}
                db.session.add(hubspot_auth)
                crm_auths.append('HubSpot')

            db.session.commit()

            return {
                'success': True,
                'message': 'Client created successfully',
                'data': {
                    'id': new_client.id,
                    'company_name': new_client.company_name,
                    'email': new_client.email,
                    'other_contact_info': new_client.other_contact_info,
                    'domain': builderprime.get('domain') if builderprime else None,
                    'crm_integrations': crm_auths
                }
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating client: {str(e)}',
                'data': None
            }

    @staticmethod
    def update_client(client_id, company_name=None, email=None, other_contact_info=None, builderprime=None, hubspot_api_key=None):
        """
        Update an existing client

        Args:
            client_id (int): Client ID
            company_name (str, optional): New company name
            email (str, optional): New email
            other_contact_info (str, optional): New contact info
            builderprime (dict, optional): BuilderPrime credentials with api_key and domain
            hubspot_api_key (str, optional): New HubSpot API key

        Returns:
            dict: Updated client data or error message
        """
        try:
            # Get existing client
            client = Clients.query.get(client_id)
            if not client:
                return {
                    'success': False,
                    'message': f'Client with ID {client_id} not found',
                    'data': None
                }

            # Check if email is being changed and if new email already exists
            if email and email != client.email:
                existing_client = Clients.query.filter_by(email=email).first()
                if existing_client:
                    return {
                        'success': False,
                        'message': f'Client with email {email} already exists',
                        'data': None
                    }

            # Track updated fields
            updated_fields = []

            # Update client fields if provided
            if company_name is not None:
                client.company_name = company_name
                updated_fields.append('company_name')
            if email is not None:
                client.email = email
                updated_fields.append('email')
            if other_contact_info is not None:
                client.other_contact_info = other_contact_info
                updated_fields.append('other_contact_info')

            # Update CRM authentication records
            updated_crm_auths = []

            # Get CRM IDs
            builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
            hubspot_crm = CRMs.query.filter_by(name='HubSpot').first()

            # Update BuilderPrime authentication if provided
            if builderprime_crm and builderprime:
                builderprime_auth = ClientCRMAuth.query.filter_by(
                    client_id=client_id,
                    crm_id=builderprime_crm.id
                ).first()

                if not builderprime_auth:
                    # Create new BuilderPrime auth record
                    builderprime_auth = ClientCRMAuth()
                    builderprime_auth.client_id = client_id
                    builderprime_auth.crm_id = builderprime_crm.id
                    db.session.add(builderprime_auth)

                # Update credentials
                if builderprime_auth.credentials is None:
                    builderprime_auth.credentials = {}

                if 'api_key' in builderprime:
                    builderprime_auth.credentials["api_key"] = builderprime['api_key']
                if 'domain' in builderprime:
                    builderprime_auth.credentials["domain"] = builderprime['domain']

                updated_crm_auths.append('BuilderPrime')

            # Update HubSpot authentication if provided
            if hubspot_crm and hubspot_api_key is not None:
                hubspot_auth = ClientCRMAuth.query.filter_by(
                    client_id=client_id,
                    crm_id=hubspot_crm.id
                ).first()

                if not hubspot_auth:
                    # Create new HubSpot auth record
                    hubspot_auth = ClientCRMAuth()
                    hubspot_auth.client_id = client_id
                    hubspot_auth.crm_id = hubspot_crm.id
                    db.session.add(hubspot_auth)

                # Update credentials
                if hubspot_auth.credentials is None:
                    hubspot_auth.credentials = {}
                hubspot_auth.credentials["api_key"] = hubspot_api_key

                updated_crm_auths.append('HubSpot')

            db.session.commit()

            # Get updated client data with CRM integrations
            crm_integrations = []
            for auth in client.crm_auths:
                crm = auth.crm
                crm_integrations.append({
                    'crm_name': crm.name,
                    'has_api_key': bool(auth.credentials) and "api_key" in auth.credentials
                })

            return {
                'success': True,
                'message': 'Client updated successfully',
                'data': {
                    'id': client.id,
                    'company_name': client.company_name,
                    'email': client.email,
                    'other_contact_info': client.other_contact_info,
                    'domain': builderprime.get('domain') if builderprime else None,
                    'crm_integrations': crm_integrations,
                    'updated_fields': updated_fields,
                    'updated_crm_auths': updated_crm_auths
                }
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating client: {str(e)}',
                'data': None
            }

    @staticmethod
    def get_all_clients():
        """
        Get all clients

        Returns:
            dict: List of all clients or error message
        """
        try:
            clients = Clients.query.all()

            clients_data = []
            for client in clients:
                # Get CRM authentications for this client
                crm_auths = ClientCRMAuth.query.filter_by(client_id=client.id).all()
                crm_integrations = []

                for auth in crm_auths:
                    crm = CRMs.query.get(auth.crm_id)
                    if crm:
                        # Get domain from credentials JSON for BuilderPrime
                        domain = None
                        api_key = None
                        if auth.credentials:
                            domain = auth.credentials.get('domain')
                            api_key = auth.credentials.get('api_key')

                        crm_integrations.append({
                            'crm_name': crm.name,
                            'crm_id': auth.crm_id,
                            'domain': domain,
                            'has_api_key': bool(api_key),
                            'credentials': auth.credentials,
                            'created_at': auth.created_at.isoformat() if auth.created_at else None,
                            'updated_at': auth.updated_at.isoformat() if auth.updated_at else None
                        })

                clients_data.append({
                    'id': client.id,
                    'company_name': client.company_name,
                    'email': client.email,
                    'other_contact_info': client.other_contact_info,
                    'created_at': client.created_at.isoformat() if hasattr(client, 'created_at') and client.created_at else None,
                    'updated_at': client.updated_at.isoformat() if hasattr(client, 'updated_at') and client.updated_at else None,
                    'crm_integrations': crm_integrations,
                    'total_crm_integrations': len(crm_integrations)
                })

            return {
                'success': True,
                'message': f'Found {len(clients_data)} clients',
                'data': clients_data
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving clients: {str(e)}',
                'data': None
            }

    @staticmethod
    def get_client_by_id(client_id):
        """
        Get client by ID

        Args:
            client_id (int): Client ID

        Returns:
            dict: Client data or error message
        """
        try:
            client = Clients.query.get(client_id)

            if not client:
                return {
                    'success': False,
                    'message': f'Client with ID {client_id} not found',
                    'data': None
                }

            # Get CRM authentications for this client
            crm_auths = ClientCRMAuth.query.filter_by(client_id=client.id).all()
            crm_integrations = []

            for auth in crm_auths:
                crm = CRMs.query.get(auth.crm_id)
                if crm:
                    # Get domain from credentials JSON for BuilderPrime
                    domain = None
                    api_key = None
                    if auth.credentials:
                        domain = auth.credentials.get('domain')
                        api_key = auth.credentials.get('api_key')

                    crm_integrations.append({
                        'crm_name': crm.name,
                        'crm_id': auth.crm_id,
                        'domain': domain,
                        'has_api_key': bool(api_key),
                        'credentials': auth.credentials,
                        'created_at': auth.created_at.isoformat() if auth.created_at else None,
                        'updated_at': auth.updated_at.isoformat() if auth.updated_at else None
                    })

            return {
                'success': True,
                'message': 'Client retrieved successfully',
                'data': {
                    'id': client.id,
                    'company_name': client.company_name,
                    'email': client.email,
                    'other_contact_info': client.other_contact_info,
                    'created_at': client.created_at.isoformat() if hasattr(client, 'created_at') and client.created_at else None,
                    'updated_at': client.updated_at.isoformat() if hasattr(client, 'updated_at') and client.updated_at else None,
                    'crm_integrations': crm_integrations,
                    'total_crm_integrations': len(crm_integrations)
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving client: {str(e)}',
                'data': None
            }