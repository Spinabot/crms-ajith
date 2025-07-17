from app import db
from datetime import datetime

class JobberAuth(db.Model):
    """Model to store Jobber OAuth authentication data"""
    __tablename__ = 'jobber_auth'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False, unique=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expiration_time = db.Column(db.BigInteger, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'hasValidToken': self.has_valid_token(),
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def has_valid_token(self):
        """Check if the access token is still valid"""
        current_time = int(datetime.utcnow().timestamp())
        return current_time < self.expiration_time