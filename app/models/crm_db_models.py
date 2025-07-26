from app import db
from datetime import datetime

class CRMs(db.Model):
    """Model to store information about different CRM systems"""
    __tablename__ = 'crm_systems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    base_url = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'baseUrl': self.base_url
        }

class Clients(db.Model):
    """Model to store information about internal clients/users"""
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    other_contact_info = db.Column(db.String(255))
    domain = db.Column(db.String(255))  # New column for client domain URL

    # Relationships
    crm_auths = db.relationship("ClientCRMAuth", backref="client", cascade="all, delete-orphan")
    unified_leads = db.relationship("UnifiedLead", backref="client", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'otherContactInfo': self.other_contact_info,
            'domain': self.domain
        }

class ClientCRMAuth(db.Model):
    """Model to store authentication credentials for clients to access CRM systems"""
    __tablename__ = 'client_crm_auth'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    crm_id = db.Column(db.Integer, db.ForeignKey('crm_systems.id', ondelete='CASCADE'), nullable=False)
    api_key = db.Column(db.String(255))
    client_secret = db.Column(db.String(255))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'clientId': self.client_id,
            'crmId': self.crm_id,
            'hasApiKey': bool(self.api_key),
            'hasClientSecret': bool(self.client_secret),
            'hasAccessToken': bool(self.access_token),
            'hasRefreshToken': bool(self.refresh_token),
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

class UnifiedLead(db.Model):
    """Unified model to store all leads for all clients and CRMs"""
    __tablename__ = 'unified_leads'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    crm_system = db.Column(db.String(50), nullable=False)  # e.g., 'builder_prime'
    crm_external_id = db.Column(db.String(100))  # ID in the external CRM, if any
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    mobile_phone = db.Column(db.String(20))
    home_phone = db.Column(db.String(20))
    office_phone = db.Column(db.String(20))
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    company_name = db.Column(db.String(255))
    title = db.Column(db.String(100))
    lead_status = db.Column(db.String(100))
    lead_source = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'clientId': self.client_id,
            'crmSystem': self.crm_system,
            'crmExternalId': self.crm_external_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'mobilePhone': self.mobile_phone,
            'homePhone': self.home_phone,
            'officePhone': self.office_phone,
            'addressLine1': self.address_line1,
            'addressLine2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip_code,
            'companyName': self.company_name,
            'title': self.title,
            'leadStatus': self.lead_status,
            'leadSource': self.lead_source,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }