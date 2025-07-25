from app import db
from app.models.crm_db_models import Clients, ClientCRMAuth, CRMs
from sqlalchemy.exc import SQLAlchemyError

class ClientService:
    @staticmethod
    def register_client(data):
        name = data.get('name')
        email = data.get('email')
        other_contact_info = data.get('otherContactInfo')
        builderprime_api_key = data.get('builderPrimeApiKey')
        hubspot_api_token = data.get('hubspotApiToken')

        if not name or not email:
            raise ValueError('Name and email are required')

        try:
            # Create client
            client = Clients(name=name, email=email, other_contact_info=other_contact_info)
            db.session.add(client)
            db.session.flush()  # Get client.id

            crm_auths = []

            # Store BuilderPrime API key if provided
            if builderprime_api_key:
                builderprime_crm = CRMs.query.filter_by(name='BuilderPrime').first()
                if builderprime_crm:
                    auth = ClientCRMAuth(client_id=client.id, crm_id=builderprime_crm.id, api_key=builderprime_api_key)
                    db.session.add(auth)
                    crm_auths.append(auth)

            # Store HubSpot API token if provided
            if hubspot_api_token:
                hubspot_crm = CRMs.query.filter_by(name='HubSpot').first()
                if hubspot_crm:
                    auth = ClientCRMAuth(client_id=client.id, crm_id=hubspot_crm.id, api_key=hubspot_api_token)
                    db.session.add(auth)
                    crm_auths.append(auth)

            db.session.commit()
            return client, crm_auths
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f'Failed to register client: {str(e)}')

    @staticmethod
    def get_client_by_id(client_id):
        client = Clients.query.get(client_id)
        if not client:
            return None, []
        crm_auths = ClientCRMAuth.query.filter_by(client_id=client.id).all()
        return client, crm_auths