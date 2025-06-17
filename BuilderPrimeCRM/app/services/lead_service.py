from app.models import Lead
from app import db
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class LeadService:
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 500

    @staticmethod
    def validate_required_fields(lead_data: Dict) -> tuple[bool, str]:
        required_fields = {
            'firstName': 'First name',
            'lastName': 'Last name',
            'email': 'Email address',
            'mobilePhone': 'Mobile phone number',
            'addressLine1': 'Address line 1',
            'city': 'City',
            'state': 'State',
            'zip': 'ZIP code'
        }
        
        for field, name in required_fields.items():
            if not lead_data.get(field):
                return False, f"{name} is required"
        return True, ""

    @staticmethod
    def create_lead(lead_data: Dict) -> Lead:
        is_valid, error_message = LeadService.validate_required_fields(lead_data)
        if not is_valid:
            raise ValueError(error_message)

        lead = Lead(
            first_name=lead_data['firstName'],
            last_name=lead_data['lastName'],
            email=lead_data['email'],
            mobile_phone=lead_data['mobilePhone'],
            mobile_phone_extension=lead_data.get('mobilePhoneExtension'),
            home_phone=lead_data.get('homePhone'),
            home_phone_extension=lead_data.get('homePhoneExtension'),
            office_phone=lead_data.get('officePhone'),
            office_phone_extension=lead_data.get('officePhoneExtension'),
            fax=lead_data.get('fax'),
            address_line1=lead_data['addressLine1'],
            address_line2=lead_data.get('addressLine2'),
            city=lead_data['city'],
            state=lead_data['state'],
            zip_code=lead_data['zip'],
            company_name=lead_data.get('companyName'),
            title=lead_data.get('title'),
            notes=lead_data.get('notes'),
            lead_status=lead_data.get('leadStatusName'),
            lead_source=lead_data.get('leadSourceName'),
            sales_person_first_name=lead_data.get('salesPersonFirstName'),
            sales_person_last_name=lead_data.get('salesPersonLastName'),
            lead_setter_first_name=lead_data.get('leadSetterFirstName'),
            lead_setter_last_name=lead_data.get('leadSetterLastName'),
            class_name=lead_data.get('className'),
            project_type=lead_data.get('projectTypeName'),
            external_id=lead_data.get('externalId'),
            dialer_status=lead_data.get('dialerStatus')
        )
        db.session.add(lead)
        db.session.commit()
        return lead

    @staticmethod
    def update_lead(lead_id: int, lead_data: Dict) -> Optional[Lead]:
        lead = db.session.get(Lead, lead_id)
        if not lead:
            return None

        required_fields = {
            'firstName': 'first_name',
            'lastName': 'last_name',
            'email': 'email',
            'mobilePhone': 'mobile_phone',
            'addressLine1': 'address_line1',
            'city': 'city',
            'state': 'state',
            'zip': 'zip_code'
        }

        for json_key, model_attr in required_fields.items():
            if json_key in lead_data:
                if not lead_data[json_key]:
                    raise ValueError(f"{json_key} cannot be empty")
                setattr(lead, model_attr, lead_data[json_key])

        field_mapping = {
            'mobilePhoneExtension': 'mobile_phone_extension',
            'homePhone': 'home_phone',
            'homePhoneExtension': 'home_phone_extension',
            'officePhone': 'office_phone',
            'officePhoneExtension': 'office_phone_extension',
            'fax': 'fax',
            'addressLine2': 'address_line2',
            'companyName': 'company_name',
            'title': 'title',
            'notes': 'notes',
            'leadStatusName': 'lead_status',
            'leadSourceName': 'lead_source',
            'salesPersonFirstName': 'sales_person_first_name',
            'salesPersonLastName': 'sales_person_last_name',
            'leadSetterFirstName': 'lead_setter_first_name',
            'leadSetterLastName': 'lead_setter_last_name',
            'className': 'class_name',
            'projectTypeName': 'project_type',
            'externalId': 'external_id',
            'dialerStatus': 'dialer_status'
        }

        for json_key, model_attr in field_mapping.items():
            if json_key in lead_data:
                setattr(lead, model_attr, lead_data[json_key])

        lead.updated_at = datetime.utcnow()
        db.session.commit()
        return lead

    @staticmethod
    def get_leads(
        last_modified_since: Optional[str] = None,
        lead_status: Optional[str] = None,
        lead_source: Optional[str] = None,
        dialer_status: Optional[str] = None,
        phone: Optional[str] = None,
        page: Optional[int] = 1,
        per_page: Optional[int] = None
    ) -> Tuple[List[Lead], int]:
        query = Lead.query

        if last_modified_since:
            query = query.filter(Lead.updated_at >= last_modified_since)
        if lead_status:
            query = query.filter(Lead.lead_status == lead_status)
        if lead_source:
            query = query.filter(Lead.lead_source == lead_source)
        if dialer_status:
            query = query.filter(Lead.dialer_status == dialer_status)
        if phone:
            query = query.filter(
                (Lead.mobile_phone == phone) |
                (Lead.home_phone == phone) |
                (Lead.office_phone == phone)
            )

        total_count = query.count()
        
        page = page or 1
        per_page = min(per_page or LeadService.DEFAULT_PAGE_SIZE, LeadService.MAX_PAGE_SIZE)
        query = query.order_by(Lead.created_at.desc())
        leads = query.offset((page - 1) * per_page).limit(per_page).all()

        return leads, total_count

    @staticmethod
    def get_lead(lead_id: int) -> Optional[Lead]:
        return db.session.get(Lead, lead_id)

    @staticmethod
    def delete_lead(lead_id: int) -> bool:
        lead = db.session.get(Lead, lead_id)
        if lead:
            db.session.delete(lead)
            db.session.commit()
            return True
        return False
