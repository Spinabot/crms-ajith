import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.config import Config
from app.models import UnifiedLead, CRMConnection, SyncLog
from app import db

class BuilderPrimeService:
    """Service class for BuilderPrime CRM operations"""

    def __init__(self):
        # Use API key from environment variables
        self.api_key = Config.BUILDER_PRIME_API_KEY
        if not self.api_key:
            raise ValueError("BuilderPrime API key not configured in environment variables")

    def create_lead(self, lead_data: Dict) -> Dict:
        """Create a lead in BuilderPrime CRM (local database)"""
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'mobilePhone',
                          'addressLine1', 'city', 'state', 'zip']

        for field in required_fields:
            if not lead_data.get(field):
                raise ValueError(f"{field} is required")

        try:
            # Create lead in unified database
            unified_lead = UnifiedLead()
            unified_lead.first_name = lead_data['firstName']
            unified_lead.last_name = lead_data['lastName']
            unified_lead.email = lead_data['email']
            unified_lead.mobile_phone = lead_data['mobilePhone']
            unified_lead.home_phone = lead_data.get('homePhone')
            unified_lead.office_phone = lead_data.get('officePhone')
            unified_lead.address_line1 = lead_data['addressLine1']
            unified_lead.address_line2 = lead_data.get('addressLine2')
            unified_lead.city = lead_data['city']
            unified_lead.state = lead_data['state']
            unified_lead.zip_code = lead_data['zip']
            unified_lead.company_name = lead_data.get('companyName')
            unified_lead.title = lead_data.get('title')
            unified_lead.lead_status = lead_data.get('leadStatus')
            unified_lead.lead_source = lead_data.get('leadSource')
            unified_lead.notes = lead_data.get('notes')
            unified_lead.crm_system = 'builder_prime'
            unified_lead.crm_external_id = str(datetime.utcnow().timestamp())  # Generate unique ID
            unified_lead.crm_raw_data = lead_data

            db.session.add(unified_lead)
            db.session.flush()  # Get the ID

            # Return the created lead data
            return {
                'id': unified_lead.id,
                'firstName': unified_lead.first_name,
                'lastName': unified_lead.last_name,
                'email': unified_lead.email,
                'mobilePhone': unified_lead.mobile_phone,
                'homePhone': unified_lead.home_phone,
                'officePhone': unified_lead.office_phone,
                'addressLine1': unified_lead.address_line1,
                'addressLine2': unified_lead.address_line2,
                'city': unified_lead.city,
                'state': unified_lead.state,
                'zip': unified_lead.zip_code,
                'companyName': unified_lead.company_name,
                'title': unified_lead.title,
                'leadStatus': unified_lead.lead_status,
                'leadSource': unified_lead.lead_source,
                'notes': unified_lead.notes,
                'createdAt': unified_lead.created_at.isoformat() if unified_lead.created_at else None,
                'updatedAt': unified_lead.updated_at.isoformat() if unified_lead.updated_at else None
            }

        except Exception as e:
            raise Exception(f"Failed to create lead: {str(e)}")

    def update_lead(self, external_id: str, lead_data: Dict) -> Dict:
        """Update a lead in BuilderPrime CRM (local database)"""
        try:
            # Find the lead by external ID
            unified_lead = UnifiedLead.query.filter_by(
                crm_system='builder_prime',
                crm_external_id=external_id
            ).first()

            if not unified_lead:
                raise ValueError(f"Lead with external ID {external_id} not found")

            # Update fields
            if 'firstName' in lead_data:
                unified_lead.first_name = lead_data['firstName']
            if 'lastName' in lead_data:
                unified_lead.last_name = lead_data['lastName']
            if 'email' in lead_data:
                unified_lead.email = lead_data['email']
            if 'mobilePhone' in lead_data:
                unified_lead.mobile_phone = lead_data['mobilePhone']
            if 'homePhone' in lead_data:
                unified_lead.home_phone = lead_data['homePhone']
            if 'officePhone' in lead_data:
                unified_lead.office_phone = lead_data['officePhone']
            if 'addressLine1' in lead_data:
                unified_lead.address_line1 = lead_data['addressLine1']
            if 'addressLine2' in lead_data:
                unified_lead.address_line2 = lead_data['addressLine2']
            if 'city' in lead_data:
                unified_lead.city = lead_data['city']
            if 'state' in lead_data:
                unified_lead.state = lead_data['state']
            if 'zip' in lead_data:
                unified_lead.zip_code = lead_data['zip']
            if 'companyName' in lead_data:
                unified_lead.company_name = lead_data['companyName']
            if 'title' in lead_data:
                unified_lead.title = lead_data['title']
            if 'leadStatus' in lead_data:
                unified_lead.lead_status = lead_data['leadStatus']
            if 'leadSource' in lead_data:
                unified_lead.lead_source = lead_data['leadSource']
            if 'notes' in lead_data:
                unified_lead.notes = lead_data['notes']

            unified_lead.crm_raw_data = lead_data
            db.session.commit()

            # Return the updated lead data
            return {
                'id': unified_lead.id,
                'firstName': unified_lead.first_name,
                'lastName': unified_lead.last_name,
                'email': unified_lead.email,
                'mobilePhone': unified_lead.mobile_phone,
                'homePhone': unified_lead.home_phone,
                'officePhone': unified_lead.office_phone,
                'addressLine1': unified_lead.address_line1,
                'addressLine2': unified_lead.address_line2,
                'city': unified_lead.city,
                'state': unified_lead.state,
                'zip': unified_lead.zip_code,
                'companyName': unified_lead.company_name,
                'title': unified_lead.title,
                'leadStatus': unified_lead.lead_status,
                'leadSource': unified_lead.lead_source,
                'notes': unified_lead.notes,
                'createdAt': unified_lead.created_at.isoformat() if unified_lead.created_at else None,
                'updatedAt': unified_lead.updated_at.isoformat() if unified_lead.updated_at else None
            }

        except Exception as e:
            raise Exception(f"Failed to update lead: {str(e)}")

    def delete_lead(self, external_id: str) -> bool:
        """Delete a lead from BuilderPrime CRM (local database)"""
        try:
            # Find the lead by external ID
            unified_lead = UnifiedLead.query.filter_by(
                crm_system='builder_prime',
                crm_external_id=external_id
            ).first()

            if not unified_lead:
                raise ValueError(f"Lead with external ID {external_id} not found")

            db.session.delete(unified_lead)
            db.session.commit()

            return True

        except Exception as e:
            raise Exception(f"Failed to delete lead: {str(e)}")

    def get_leads(self, page: int = 1, per_page: int = 10,
                  last_modified_since: Optional[str] = None,
                  lead_status: Optional[str] = None,
                  lead_source: Optional[str] = None) -> Dict:
        """Get leads from BuilderPrime CRM (local database)"""
        try:
            query = UnifiedLead.query.filter_by(crm_system='builder_prime')

            # Apply filters
            if last_modified_since:
                query = query.filter(UnifiedLead.updated_at >= last_modified_since)
            if lead_status:
                query = query.filter(UnifiedLead.lead_status == lead_status)
            if lead_source:
                query = query.filter(UnifiedLead.lead_source == lead_source)

            # Get total count
            total_count = query.count()

            # Apply pagination
            leads = query.order_by(UnifiedLead.created_at.desc()) \
                        .offset((page - 1) * per_page) \
                        .limit(per_page) \
                        .all()

            # Convert to list of dictionaries
            leads_list = []
            for lead in leads:
                leads_list.append({
                    'id': lead.id,
                    'firstName': lead.first_name,
                    'lastName': lead.last_name,
                    'email': lead.email,
                    'mobilePhone': lead.mobile_phone,
                    'homePhone': lead.home_phone,
                    'officePhone': lead.office_phone,
                    'addressLine1': lead.address_line1,
                    'addressLine2': lead.address_line2,
                    'city': lead.city,
                    'state': lead.state,
                    'zip': lead.zip_code,
                    'companyName': lead.company_name,
                    'title': lead.title,
                    'leadStatus': lead.lead_status,
                    'leadSource': lead.lead_source,
                    'notes': lead.notes,
                    'createdAt': lead.created_at.isoformat() if lead.created_at else None,
                    'updatedAt': lead.updated_at.isoformat() if lead.updated_at else None
                })

            return {
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'leads': leads_list
            }

        except Exception as e:
            raise Exception(f"Failed to get leads: {str(e)}")

    def sync_leads(self) -> Dict:
        """Sync leads from BuilderPrime to unified database (already synced since it's local)"""
        try:
            # Since BuilderPrime is local, just return current stats
            total_leads = UnifiedLead.query.filter_by(crm_system='builder_prime').count()

            return {
                'synced': total_leads,
                'errors': 0,
                'message': 'BuilderPrime leads are already synced (local database)'
            }

        except Exception as e:
            raise Exception(f"Failed to sync leads: {str(e)}")