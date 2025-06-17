from datetime import datetime
from app.extensions import db

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hubspot_id = db.Column(db.BigInteger, unique=True)
    email = db.Column(db.String(120), unique=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    website = db.Column(db.String(200))
    lifecyclestage = db.Column(db.String(50))
    hs_additional_emails = db.Column(db.String(500))  
    hs_pinned_engagement_id = db.Column(db.BigInteger)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hubspot_id': self.hubspot_id,
            'email': self.email,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'phone': self.phone,
            'company': self.company,
            'website': self.website,
            'lifecyclestage': self.lifecyclestage,
            'hs_additional_emails': self.hs_additional_emails,
            'hs_pinned_engagement_id': self.hs_pinned_engagement_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
