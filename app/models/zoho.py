from app import db
from datetime import datetime

class ZohoCreds(db.Model):
    """Model to store Zoho CRM credentials and tokens"""
    __tablename__ = 'zoho_credentials'

    entity_id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    expiration_time = db.Column(db.BigInteger)

    # Relationship to clients (one-to-many)
    clients = db.relationship("ZohoClients", backref="credentials", cascade="all, delete-orphan")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'entityId': self.entity_id,
            'hasValidToken': self.has_valid_token(),
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def has_valid_token(self):
        """Check if the access token is still valid"""
        if not self.expiration_time:
            return False
        current_time = int(datetime.utcnow().timestamp())
        return current_time < self.expiration_time

class ZohoClients(db.Model):
    """Model to store Zoho CRM clients"""
    __tablename__ = 'zoho_clients'

    zoho_id = db.Column(db.String(100), primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('zoho_credentials.entity_id', ondelete='CASCADE'), nullable=False)
    full_name = db.Column(db.String(200))

    # Relationship to audit logs
    audit_logs = db.relationship("ZohoAudit", backref="client", cascade="all, delete-orphan")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'zohoId': self.zoho_id,
            'entityId': self.entity_id,
            'fullName': self.full_name,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

class ZohoAudit(db.Model):
    """Model to store Zoho CRM audit logs"""
    __tablename__ = 'zoho_audit'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.String(100))
    entity_id = db.Column(db.Integer)
    zoho_id = db.Column(db.String(100), db.ForeignKey('zoho_clients.zoho_id', ondelete='CASCADE'))
    name = db.Column(db.String(200))
    message = db.Column(db.String(500))
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'leadId': self.lead_id,
            'entityId': self.entity_id,
            'zohoId': self.zoho_id,
            'name': self.name,
            'message': self.message,
            'time': self.time.isoformat() if self.time else None
        }