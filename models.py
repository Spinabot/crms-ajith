from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a db instance that will be initialized later
db = SQLAlchemy()

class CRMs(db.Model):
    """CRM systems table"""
    __tablename__ = 'crms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_url = db.Column(db.String(255), nullable=False)

    # Relationships
    client_auths = db.relationship('ClientCRMAuth', backref='crm', lazy=True)
    builder_prime_clients = db.relationship('BuilderPrimeClientData', backref='crm', lazy=True)
    zoho_clients = db.relationship('ZohoClientData', backref='crm', lazy=True)
    hubspot_clients = db.relationship('HubspotClientData', backref='crm', lazy=True)
    jobber_clients = db.relationship('JobberClientData', backref='crm', lazy=True)
    jobnimbus_clients = db.relationship('JobNimbusClientData', backref='crm', lazy=True)

class Clients(db.Model):
    """Clients table"""
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    other_contact_info = db.Column(db.Text)

    # Relationships
    crm_auths = db.relationship('ClientCRMAuth', backref='client', lazy=True)

class ClientCRMAuth(db.Model):
    """Client CRM Authentication table"""
    __tablename__ = 'client_crm_auth'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    crm_id = db.Column(db.Integer, db.ForeignKey('crms.id'), nullable=False)
    credentials = db.Column(db.JSON, nullable=True)  # New flexible JSON field for all credentials
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CapsuleToken(db.Model):
    """Capsule CRM OAuth tokens table"""
    __tablename__ = 'capsule_tokens'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=True)
    expires_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobberToken(db.Model):
    """Jobber CRM OAuth tokens table"""
    __tablename__ = 'jobber_tokens'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=True)
    expires_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobNimbusCredentials(db.Model):
    """JobNimbus CRM API credentials table"""
    __tablename__ = 'jobnimbus_credentials'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(500), nullable=False)
    base_url = db.Column(db.String(255), default='https://api.jobnimbus.com')
    api_prefix = db.Column(db.String(10), default='v1')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BuilderPrimeClientData(db.Model):
    """BuilderPrime CRM client data table"""
    __tablename__ = 'builder_prime_client_data'

    id = db.Column(db.Integer, primary_key=True)
    crm_id = db.Column(db.Integer, db.ForeignKey('crms.id'), nullable=False)
    source_client_id = db.Column(db.String(100), nullable=False)
    crm_client_id = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    crm_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ZohoClientData(db.Model):
    """Zoho CRM client data table"""
    __tablename__ = 'zoho_client_data'

    id = db.Column(db.Integer, primary_key=True)
    crm_id = db.Column(db.Integer, db.ForeignKey('crms.id'), nullable=False)
    source_client_id = db.Column(db.String(100), nullable=False)
    crm_client_id = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    crm_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HubspotClientData(db.Model):
    """HubSpot CRM client data table"""
    __tablename__ = 'hubspot_client_data'

    id = db.Column(db.Integer, primary_key=True)
    crm_id = db.Column(db.Integer, db.ForeignKey('crms.id'), nullable=False)
    source_client_id = db.Column(db.String(100), nullable=False)
    crm_client_id = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    crm_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JobberClientData(db.Model):
    """Jobber CRM client data table"""
    __tablename__ = 'jobber_client_data'

    id = db.Column(db.Integer, primary_key=True)
    crm_id = db.Column(db.Integer, db.ForeignKey('crms.id'), nullable=False)
    source_client_id = db.Column(db.String(100), nullable=False)
    crm_client_id = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    crm_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JobNimbusClientData(db.Model):
    """JobNimbus CRM client data table"""
    __tablename__ = 'jobnimbus_client_data'

    id = db.Column(db.Integer, primary_key=True)
    crm_id = db.Column(db.Integer, db.ForeignKey('crms.id'), nullable=False)
    source_client_id = db.Column(db.String(100), nullable=False)
    crm_client_id = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    crm_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)