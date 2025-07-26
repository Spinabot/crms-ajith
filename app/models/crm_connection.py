from datetime import datetime
from app import db

class CRMConnection(db.Model):
    """Model to store CRM connection credentials and tokens"""
    __tablename__ = 'crm_connections'

    id = db.Column(db.Integer, primary_key=True)
    crm_system = db.Column(db.String(50), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)

    # OAuth tokens
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)

    # API keys and credentials
    api_key = db.Column(db.String(255))
    client_id = db.Column(db.String(255))
    client_secret = db.Column(db.String(255))

    # Configuration
    config_data = db.Column(db.JSON)  # Store additional configuration

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'crmSystem': self.crm_system,
            'isActive': self.is_active,
            'hasValidToken': self.has_valid_token(),
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def has_valid_token(self):
        if not self.token_expires_at:
            return False
        return datetime.utcnow() < self.token_expires_at