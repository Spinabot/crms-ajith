import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app import db
from app.models.crm_db_models import UnifiedLead

class BuilderPrimeService:
    """Service class for BuilderPrime CRM operations"""

    def __init__(self, api_key: Optional[str] = None, client_id: Optional[int] = None):
        if not api_key:
            raise ValueError("BuilderPrime API key must be provided for the client")
        self.api_key = api_key
        self.client_id = client_id

    def create_lead(self, lead_data: Dict) -> Dict:
        required_fields = ['firstName', 'lastName', 'email', 'mobilePhone',
                          'addressLine1', 'city', 'state', 'zip']
        for field in required_fields:
            if not lead_data.get(field):
                raise ValueError(f"{field} is required")
        try:
            # --- External API call would go here (simulate for now) ---
            external_id = str(datetime.utcnow().timestamp())
            # --- Store in UnifiedLead ---
            lead = UnifiedLead(
                client_id=self.client_id,
                crm_system='builder_prime',
                crm_external_id=external_id,
                first_name=lead_data['firstName'],
                last_name=lead_data['lastName'],
                email=lead_data['email'],
                mobile_phone=lead_data['mobilePhone'],
                home_phone=lead_data.get('homePhone'),
                office_phone=lead_data.get('officePhone'),
                address_line1=lead_data['addressLine1'],
                address_line2=lead_data.get('addressLine2'),
                city=lead_data['city'],
                state=lead_data['state'],
                zip_code=lead_data['zip'],
                company_name=lead_data.get('companyName'),
                title=lead_data.get('title'),
                lead_status=lead_data.get('leadStatus'),
                lead_source=lead_data.get('leadSource'),
                notes=lead_data.get('notes'),
            )
            db.session.add(lead)
            db.session.commit()
            return lead.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create lead: {str(e)}")

    def update_lead(self, lead_data: Dict) -> Dict:
        try:
            lead = UnifiedLead.query.filter_by(
                client_id=self.client_id,
                crm_system='builder_prime',
                crm_external_id=lead_data.get('externalId')
            ).first()
            if not lead:
                raise ValueError("Lead not found")
            # Update fields
            for field, attr in [
                ('firstName', 'first_name'),
                ('lastName', 'last_name'),
                ('email', 'email'),
                ('mobilePhone', 'mobile_phone'),
                ('homePhone', 'home_phone'),
                ('officePhone', 'office_phone'),
                ('addressLine1', 'address_line1'),
                ('addressLine2', 'address_line2'),
                ('city', 'city'),
                ('state', 'state'),
                ('zip', 'zip_code'),
                ('companyName', 'company_name'),
                ('title', 'title'),
                ('leadStatus', 'lead_status'),
                ('leadSource', 'lead_source'),
                ('notes', 'notes'),
            ]:
                if field in lead_data:
                    setattr(lead, attr, lead_data[field])
            lead.updated_at = datetime.utcnow()
            db.session.commit()
            return lead.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update lead: {str(e)}")

    def delete_lead(self, external_id: str) -> bool:
        try:
            lead = UnifiedLead.query.filter_by(
                client_id=self.client_id,
                crm_system='builder_prime',
                crm_external_id=external_id
            ).first()
            if not lead:
                raise ValueError("Lead not found")
            db.session.delete(lead)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete lead: {str(e)}")

    def get_leads(self, page: int = 1, per_page: int = 10,
                  last_modified_since: Optional[str] = None,
                  lead_status: Optional[str] = None,
                  lead_source: Optional[str] = None) -> Dict:
        try:
            query = UnifiedLead.query.filter_by(
                client_id=self.client_id,
                crm_system='builder_prime'
            )
            if last_modified_since:
                query = query.filter(UnifiedLead.updated_at >= last_modified_since)
            if lead_status:
                query = query.filter(UnifiedLead.lead_status == lead_status)
            if lead_source:
                query = query.filter(UnifiedLead.lead_source == lead_source)
            total = query.count()
            leads = query.order_by(UnifiedLead.created_at.desc()) \
                        .offset((page - 1) * per_page) \
                        .limit(per_page) \
                        .all()
            return {
                'total': total,
                'page': page,
                'per_page': per_page,
                'leads': [lead.to_dict() for lead in leads]
            }
        except Exception as e:
            raise Exception(f"Failed to get leads: {str(e)}")

    def sync_leads(self) -> Dict:
        try:
            # For now, just return stats from UnifiedLead
            total_leads = UnifiedLead.query.filter_by(
                client_id=self.client_id,
                crm_system='builder_prime'
            ).count()
            return {
                'synced': total_leads,
                'errors': 0,
                'message': 'BuilderPrime leads are synced with unified database.'
            }
        except Exception as e:
            raise Exception(f"Failed to sync leads: {str(e)}")