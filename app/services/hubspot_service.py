import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.config import Config
from app.models.unified_lead import UnifiedLead
from app.models.crm_connection import CRMConnection
from app.models.sync_log import SyncLog
from app import db
from config.vault_config import get_secret

class HubspotService:
    """Service class for HubSpot CRM operations"""

    def __init__(self):
        # Try to get API token from Vault first
        self.api_token = None
        try:
            self.api_token = get_secret('HUBSPOT_API_TOKEN')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Could not fetch HubSpot API token from Vault: {e}. Falling back to config.")
            self.api_token = Config.HUBSPOT_API_TOKEN
        self.base_url = Config.HUBSPOT_API_BASE_URL
        if not self.api_token:
            raise ValueError("HubSpot API token not configured in Vault or environment variables")

        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def _handle_response(self, response):
        """Handle API response and raise appropriate exceptions"""
        if response.status_code >= 400:
            if response.status_code == 404:
                raise ValueError("Contact not found")
            elif response.status_code == 409:
                raise ValueError("Contact already exists")
            else:
                raise Exception(f"HubSpot API error: {response.text}")
        return response.json() if response.status_code != 204 else None

    def _map_hubspot_to_unified(self, hubspot_contact: Dict) -> Dict:
        """Map HubSpot contact data to unified lead format"""
        properties = hubspot_contact.get('properties', {})

        return {
            'firstName': properties.get('firstname', ''),
            'lastName': properties.get('lastname', ''),
            'email': properties.get('email', ''),
            'mobilePhone': properties.get('phone', ''),
            'homePhone': properties.get('phone', ''),  # HubSpot doesn't distinguish phone types
            'officePhone': None,
            'addressLine1': properties.get('address', ''),  # HubSpot stores full address
            'addressLine2': None,
            'city': properties.get('city', ''),
            'state': properties.get('state', ''),
            'zip': properties.get('zip', ''),
            'country': properties.get('country', 'USA'),
            'companyName': properties.get('company', ''),
            'title': properties.get('jobtitle', ''),
            'leadStatus': properties.get('lifecyclestage', ''),
            'leadSource': properties.get('hs_lead_status', ''),
            'notes': properties.get('notes', ''),
            'crmSystem': 'hubspot',
            'crmExternalId': str(hubspot_contact.get('id', '')),
            'crmRawData': hubspot_contact
        }

    def _map_unified_to_hubspot(self, lead_data: Dict) -> Dict:
        """Map unified lead data to HubSpot contact properties"""
        properties = {}

        if lead_data.get('firstName'):
            properties['firstname'] = lead_data['firstName']
        if lead_data.get('lastName'):
            properties['lastname'] = lead_data['lastName']
        if lead_data.get('email'):
            properties['email'] = lead_data['email']
        if lead_data.get('mobilePhone'):
            properties['phone'] = lead_data['mobilePhone']
        if lead_data.get('companyName'):
            properties['company'] = lead_data['companyName']
        if lead_data.get('title'):
            properties['jobtitle'] = lead_data['title']

        # Map lead status to valid HubSpot lifecycle stages
        if lead_data.get('leadStatus'):
            status_mapping = {
                'Lead Received': 'lead',
                'Qualified': 'marketingqualifiedlead',
                'Sales Qualified': 'salesqualifiedlead',
                'Opportunity': 'opportunity',
                'Customer': 'customer',
                'Subscriber': 'subscriber',
                'Evangelist': 'evangelist',
                'Other': 'other'
            }
            properties['lifecyclestage'] = status_mapping.get(lead_data['leadStatus'], 'lead')

        # Handle address fields
        address_parts = []
        if lead_data.get('addressLine1'):
            address_parts.append(lead_data['addressLine1'])
        if lead_data.get('addressLine2'):
            address_parts.append(lead_data['addressLine2'])
        if address_parts:
            properties['address'] = ', '.join(address_parts)

        if lead_data.get('city'):
            properties['city'] = lead_data['city']
        if lead_data.get('state'):
            properties['state'] = lead_data['state']
        if lead_data.get('zip'):
            properties['zip'] = lead_data['zip']
        if lead_data.get('country'):
            properties['country'] = lead_data['country']

        # Store notes in a custom property or skip if not available
        # HubSpot doesn't have a default 'notes' property
        if lead_data.get('notes'):
            # You can create a custom property in HubSpot for notes
            # For now, we'll skip it to avoid the error
            pass

        return properties

    def create_lead(self, lead_data: Dict) -> Dict:
        """Create a lead in HubSpot CRM"""
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email']
        for field in required_fields:
            if not lead_data.get(field):
                raise ValueError(f"{field} is required")

        try:
            # Map to HubSpot format
            hubspot_properties = self._map_unified_to_hubspot(lead_data)

            # Create contact in HubSpot
            url = f"{self.base_url}/crm/v3/objects/contacts"
            data = {"properties": hubspot_properties}
            response = requests.post(url, headers=self.headers, json=data)

            hubspot_contact = self._handle_response(response)

            # Create lead in unified database
            unified_lead = UnifiedLead()
            unified_lead.first_name = lead_data['firstName']
            unified_lead.last_name = lead_data['lastName']
            unified_lead.email = lead_data['email']
            unified_lead.mobile_phone = lead_data.get('mobilePhone')
            unified_lead.home_phone = lead_data.get('homePhone')
            unified_lead.office_phone = lead_data.get('officePhone')
            unified_lead.address_line1 = lead_data.get('addressLine1')
            unified_lead.address_line2 = lead_data.get('addressLine2')
            unified_lead.city = lead_data.get('city')
            unified_lead.state = lead_data.get('state')
            unified_lead.zip_code = lead_data.get('zip')
            unified_lead.country = lead_data.get('country', 'USA')
            unified_lead.company_name = lead_data.get('companyName')
            unified_lead.title = lead_data.get('title')
            unified_lead.lead_status = lead_data.get('leadStatus')
            unified_lead.lead_source = lead_data.get('leadSource')
            unified_lead.notes = lead_data.get('notes')
            unified_lead.crm_system = 'hubspot'
            unified_lead.crm_external_id = str(hubspot_contact['id'])
            unified_lead.crm_raw_data = hubspot_contact

            db.session.add(unified_lead)
            db.session.flush()  # Get the ID

            # Log sync operation
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='create',
                status='success',
                lead_id=unified_lead.id,
                external_id=str(hubspot_contact['id']),
                sync_data=hubspot_contact
            )
            db.session.add(sync_log)
            db.session.commit()

            # Return the created lead data
            return {
                'id': hubspot_contact['id'],
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
                'country': unified_lead.country,
                'companyName': unified_lead.company_name,
                'title': unified_lead.title,
                'leadStatus': unified_lead.lead_status,
                'leadSource': unified_lead.lead_source,
                'notes': unified_lead.notes,
                'createdAt': hubspot_contact.get('createdAt'),
                'updatedAt': hubspot_contact.get('updatedAt'),
                'archived': hubspot_contact.get('archived', False)
            }

        except Exception as e:
            db.session.rollback()
            # Log failed sync operation
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='create',
                status='failed',
                error_message=str(e),
                sync_data=lead_data
            )
            db.session.add(sync_log)
            db.session.commit()
            raise Exception(f"Failed to create lead: {str(e)}")

    def update_lead(self, external_id: str, lead_data: Dict) -> Dict:
        """Update a lead in HubSpot CRM"""
        try:
            # Find the lead by external ID
            unified_lead = UnifiedLead.query.filter_by(
                crm_system='hubspot',
                crm_external_id=external_id
            ).first()

            if not unified_lead:
                raise ValueError(f"Lead with external ID {external_id} not found")

            # Map to HubSpot format
            hubspot_properties = self._map_unified_to_hubspot(lead_data)

            # Update contact in HubSpot
            url = f"{self.base_url}/crm/v3/objects/contacts/{external_id}"
            data = {"properties": hubspot_properties}
            response = requests.patch(url, headers=self.headers, json=data)

            hubspot_contact = self._handle_response(response)

            # Update unified lead
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
            if 'country' in lead_data:
                unified_lead.country = lead_data['country']
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

            unified_lead.crm_raw_data = hubspot_contact
            db.session.commit()

            # Log sync operation
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='update',
                status='success',
                lead_id=unified_lead.id,
                external_id=external_id,
                sync_data=hubspot_contact
            )
            db.session.add(sync_log)
            db.session.commit()

            # Return the updated lead data
            return {
                'id': hubspot_contact['id'],
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
                'country': unified_lead.country,
                'companyName': unified_lead.company_name,
                'title': unified_lead.title,
                'leadStatus': unified_lead.lead_status,
                'leadSource': unified_lead.lead_source,
                'notes': unified_lead.notes,
                'createdAt': hubspot_contact.get('createdAt'),
                'updatedAt': hubspot_contact.get('updatedAt'),
                'archived': hubspot_contact.get('archived', False)
            }

        except Exception as e:
            db.session.rollback()
            # Log failed sync operation
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='update',
                status='failed',
                external_id=external_id,
                error_message=str(e),
                sync_data=lead_data
            )
            db.session.add(sync_log)
            db.session.commit()
            raise Exception(f"Failed to update lead: {str(e)}")

    def delete_lead(self, external_id: str) -> bool:
        """Delete a lead from HubSpot CRM"""
        try:
            # Find the lead by external ID
            unified_lead = UnifiedLead.query.filter_by(
                crm_system='hubspot',
                crm_external_id=external_id
            ).first()

            if not unified_lead:
                raise ValueError(f"Lead with external ID {external_id} not found")

            # Archive contact in HubSpot (HubSpot doesn't allow permanent deletion)
            url = f"{self.base_url}/crm/v3/objects/contacts/{external_id}"
            response = requests.delete(url, headers=self.headers)

            if response.status_code != 204:
                self._handle_response(response)

            # Log sync operation before deleting
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='delete',
                status='success',
                lead_id=unified_lead.id,
                external_id=external_id
            )
            db.session.add(sync_log)
            db.session.commit()

            # Delete from unified database
            db.session.delete(unified_lead)
            db.session.commit()

            return True

        except Exception as e:
            db.session.rollback()
            # Log failed sync operation
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='delete',
                status='failed',
                external_id=external_id,
                error_message=str(e)
            )
            db.session.add(sync_log)
            db.session.commit()
            raise Exception(f"Failed to delete lead: {str(e)}")

    def get_leads(self, page: int = 1, per_page: int = 10,
                  last_modified_since: Optional[str] = None,
                  lead_status: Optional[str] = None,
                  lead_source: Optional[str] = None) -> Dict:
        """Get leads from HubSpot CRM"""
        try:
            # Build search request
            url = f"{self.base_url}/crm/v3/objects/contacts/search"

            data = {
                "filterGroups": [],
                "properties": ["email", "firstname", "lastname", "company", "phone",
                              "jobtitle", "lifecyclestage", "address", "city", "state", "zip", "country"],
                "limit": per_page,
                "after": (page - 1) * per_page if page > 1 else None
            }

            # Add filters
            filters = []
            if last_modified_since:
                filters.append({
                    "propertyName": "hs_lastmodifieddate",
                    "operator": "GTE",
                    "value": last_modified_since
                })
            if lead_status:
                filters.append({
                    "propertyName": "lifecyclestage",
                    "operator": "EQ",
                    "value": lead_status
                })
            if lead_source:
                filters.append({
                    "propertyName": "hs_lead_status",
                    "operator": "EQ",
                    "value": lead_source
                })

            if filters:
                data["filterGroups"].append({"filters": filters})

            response = requests.post(url, headers=self.headers, json=data)
            hubspot_response = self._handle_response(response)

            # Sync contacts to unified database
            leads = []
            for contact_data in hubspot_response.get('results', []):
                self._sync_contact_from_hubspot(contact_data)
                leads.append(self._map_hubspot_to_unified(contact_data))

            total = hubspot_response.get('total', len(leads))
            pages = -(-total // per_page)  # Ceiling division

            return {
                'leads': leads,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page
            }

        except Exception as e:
            raise Exception(f"Failed to get leads: {str(e)}")

    def _sync_contact_from_hubspot(self, hubspot_contact: Dict) -> UnifiedLead:
        """Sync a contact from HubSpot to unified database"""
        try:
            hubspot_id = str(hubspot_contact['id'])

            # Check if lead already exists
            unified_lead = UnifiedLead.query.filter_by(
                crm_system='hubspot',
                crm_external_id=hubspot_id
            ).first()

            if not unified_lead:
                unified_lead = UnifiedLead()
                unified_lead.crm_system = 'hubspot'
                unified_lead.crm_external_id = hubspot_id
                db.session.add(unified_lead)

            # Map HubSpot data to unified format
            mapped_data = self._map_hubspot_to_unified(hubspot_contact)

            unified_lead.first_name = mapped_data['firstName']
            unified_lead.last_name = mapped_data['lastName']
            unified_lead.email = mapped_data['email']
            unified_lead.mobile_phone = mapped_data['mobilePhone']
            unified_lead.home_phone = mapped_data['homePhone']
            unified_lead.office_phone = mapped_data['officePhone']
            unified_lead.address_line1 = mapped_data['addressLine1']
            unified_lead.address_line2 = mapped_data['addressLine2']
            unified_lead.city = mapped_data['city']
            unified_lead.state = mapped_data['state']
            unified_lead.zip_code = mapped_data['zip']
            unified_lead.country = mapped_data['country']
            unified_lead.company_name = mapped_data['companyName']
            unified_lead.title = mapped_data['title']
            unified_lead.lead_status = mapped_data['leadStatus']
            unified_lead.lead_source = mapped_data['leadSource']
            unified_lead.notes = mapped_data['notes']
            unified_lead.crm_raw_data = hubspot_contact

            db.session.commit()
            return unified_lead

        except Exception as e:
            db.session.rollback()
            print(f"Error syncing contact from HubSpot: {str(e)}")
            return None

    def sync_leads(self) -> Dict:
        """Sync all leads from HubSpot to unified database"""
        try:
            # Get all contacts from HubSpot
            url = f"{self.base_url}/crm/v3/objects/contacts/search"

            data = {
                "filterGroups": [],
                "properties": ["email", "firstname", "lastname", "company", "phone",
                              "jobtitle", "lifecyclestage", "address", "city", "state", "zip", "country"],
                "limit": 100
            }

            all_contacts = []
            after = None

            while True:
                if after:
                    data["after"] = after

                response = requests.post(url, headers=self.headers, json=data)
                hubspot_response = self._handle_response(response)

                contacts = hubspot_response.get('results', [])
                all_contacts.extend(contacts)

                # Check if there are more pages
                paging = hubspot_response.get('paging', {})
                next_page = paging.get('next', {})
                after = next_page.get('after')

                if not after:
                    break

            # Sync all contacts
            synced_count = 0
            for contact_data in all_contacts:
                if self._sync_contact_from_hubspot(contact_data):
                    synced_count += 1

            # Log sync operation
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='sync',
                status='success',
                sync_data={'synced_count': synced_count, 'total_count': len(all_contacts)}
            )
            db.session.add(sync_log)
            db.session.commit()

            return {
                'message': f'Successfully synced {synced_count} leads from HubSpot',
                'synced_count': synced_count,
                'total_count': len(all_contacts)
            }

        except Exception as e:
            db.session.rollback()
            # Log failed sync operation
            sync_log = SyncLog(
                crm_system='hubspot',
                operation='sync',
                status='failed',
                error_message=str(e)
            )
            db.session.add(sync_log)
            db.session.commit()
            raise Exception(f"Failed to sync leads: {str(e)}")