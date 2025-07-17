from datetime import datetime
from app import db

class UnifiedLead(db.Model):
    """Unified lead model that can store data from any CRM system"""
    __tablename__ = 'unified_leads'

    id = db.Column(db.Integer, primary_key=True)

    # Basic contact information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mobile_phone = db.Column(db.String(20))
    home_phone = db.Column(db.String(20))
    office_phone = db.Column(db.String(20))

    # Address information
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(50), default='USA')

    # Company information
    company_name = db.Column(db.String(200))
    title = db.Column(db.String(100))

    # Lead information
    lead_status = db.Column(db.String(50))
    lead_source = db.Column(db.String(50))
    notes = db.Column(db.Text)

    # CRM system tracking
    crm_system = db.Column(db.String(50), nullable=False)  # builder_prime, hubspot, jobber, jobnimbus, zoho
    crm_external_id = db.Column(db.String(100))  # ID from the original CRM system
    crm_raw_data = db.Column(db.JSON)  # Store original CRM data as JSON

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
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
            'country': self.country,
            'companyName': self.company_name,
            'title': self.title,
            'leadStatus': self.lead_status,
            'leadSource': self.lead_source,
            'notes': self.notes,
            'crmSystem': self.crm_system,
            'crmExternalId': self.crm_external_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }