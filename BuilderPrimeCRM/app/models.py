from datetime import datetime
from app import db

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mobile_phone = db.Column(db.String(20), nullable=False)
    mobile_phone_extension = db.Column(db.String(10))
    home_phone = db.Column(db.String(20))
    home_phone_extension = db.Column(db.String(10))
    office_phone = db.Column(db.String(20))
    office_phone_extension = db.Column(db.String(10))
    fax = db.Column(db.String(20))
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200))
    title = db.Column(db.String(100))
    notes = db.Column(db.Text)
    lead_status = db.Column(db.String(50))
    lead_source = db.Column(db.String(50))
    sales_person_first_name = db.Column(db.String(100))
    sales_person_last_name = db.Column(db.String(100))
    lead_setter_first_name = db.Column(db.String(100))
    lead_setter_last_name = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    project_type = db.Column(db.String(100))
    external_id = db.Column(db.String(50))
    dialer_status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'mobilePhone': self.mobile_phone,
            'mobilePhoneExtension': self.mobile_phone_extension,
            'homePhone': self.home_phone,
            'homePhoneExtension': self.home_phone_extension,
            'officePhone': self.office_phone,
            'officePhoneExtension': self.office_phone_extension,
            'fax': self.fax,
            'addressLine1': self.address_line1,
            'addressLine2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip_code,
            'companyName': self.company_name,
            'title': self.title,
            'notes': self.notes,
            'leadStatusName': self.lead_status,
            'leadSourceName': self.lead_source,
            'salesPersonFirstName': self.sales_person_first_name,
            'salesPersonLastName': self.sales_person_last_name,
            'leadSetterFirstName': self.lead_setter_first_name,
            'leadSetterLastName': self.lead_setter_last_name,
            'className': self.class_name,
            'projectTypeName': self.project_type,
            'externalId': self.external_id,
            'dialerStatus': self.dialer_status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
