from sqlalchemy import or_
from app.utils.api_client import HubspotClient
from app.models import Contact
from app.extensions import db

class ContactService:
    def __init__(self):
        self.hubspot_client = HubspotClient()

    def _format_hubspot_properties(self, data):
        return {
            "properties": {
                k: str(v) for k, v in data.items() if v is not None
            }
        }

    def create_contact(self, contact_data):
        """Create a contact"""
        try:
            properties = contact_data.get('properties', {})
            
            if not properties.get('email'):
                raise ValueError("Email is required")
            
            try:
                hubspot_contact = self.hubspot_client.create_contact(properties)
            except ValueError as e:
                raise e
            except Exception as e:
                print(f"Error creating contact in HubSpot: {str(e)}")
                raise Exception("Failed to create contact in HubSpot")
            
            contact = Contact(
                hubspot_id=hubspot_contact['id'],
                email=hubspot_contact['properties'].get('email'),
                firstname=hubspot_contact['properties'].get('firstname'),
                lastname=hubspot_contact['properties'].get('lastname'),
                phone=hubspot_contact['properties'].get('phone'),
                company=hubspot_contact['properties'].get('company'),
                website=hubspot_contact['properties'].get('website'),
                lifecyclestage=hubspot_contact['properties'].get('lifecyclestage')
            )
            
            db.session.add(contact)
            db.session.commit()
            
            return {
                'id': hubspot_contact['id'],
                'properties': hubspot_contact['properties'],
                'createdAt': hubspot_contact.get('createdAt'),
                'updatedAt': hubspot_contact.get('updatedAt'),
                'archived': hubspot_contact.get('archived', False)
            }
            
        except ValueError as e:
            print(f"Validation error in create_contact: {str(e)}")
            db.session.rollback()
            raise
        except Exception as e:
            print(f"Error in create_contact: {str(e)}")
            db.session.rollback()
            raise

    def get_contact(self, contact_id):
        """Get a contact by HubSpot ID"""
        try:
            hubspot_contact = self.hubspot_client.get_contact(contact_id)
            
            self._sync_contact_from_hubspot(hubspot_contact)
            
            return {
                'id': hubspot_contact['id'],
                'properties': hubspot_contact['properties'],
                'createdAt': hubspot_contact.get('createdAt'),
                'updatedAt': hubspot_contact.get('updatedAt'),
                'archived': hubspot_contact.get('archived', False)
            }
        except Exception as e:
            print(f"Error in get_contact: {str(e)}")
            raise ValueError(f"Contact {contact_id} not found")

    def update_contact(self, contact_id, data):
        """Update a contact"""
        try:
            if not contact_id:
                raise ValueError("Contact ID is required")

            updated_contact = self.hubspot_client.update_contact(contact_id, data.get('properties', {}))
            
            return updated_contact
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            print(f"Error updating contact {contact_id}: {str(e)}")
            raise Exception(f"Failed to update contact {contact_id}: {str(e)}")

    def delete_contact(self, contact_id):
        """Delete a contact by HubSpot ID"""
        try:
            success = self.hubspot_client.delete_contact(contact_id)
            
            if success:
                contact = Contact.query.filter_by(hubspot_id=contact_id).first()
                if contact:
                    db.session.delete(contact)
                    db.session.commit()
                return True
            return False
        except ValueError as e:
            print(f"Error in delete_contact: {str(e)}")
            raise ValueError(f"Contact {contact_id} not found")
        except Exception as e:
            print(f"Error in delete_contact: {str(e)}")
            raise Exception(f"Failed to delete contact {contact_id}: {str(e)}")

    def list_contacts(self, page, per_page):
        """List contacts with pagination"""
        try:
            hubspot_response = self.hubspot_client.list_contacts(limit=per_page)
            
            contacts = []
            if hubspot_response and 'results' in hubspot_response:
                for contact_data in hubspot_response['results']:
                    self._sync_contact_from_hubspot(contact_data)
                    
                    contacts.append({
                        'id': contact_data['id'],
                        'properties': contact_data['properties'],
                        'createdAt': contact_data.get('createdAt'),
                        'updatedAt': contact_data.get('updatedAt'),
                        'archived': contact_data.get('archived', False)
                    })
            
            total = hubspot_response.get('total', len(contacts))
            pages = -(-total // per_page)
            
            return contacts, total, pages
            
        except Exception as e:
            print(f"Error in list_contacts: {str(e)}")
            return [], 0, 0

    def _sync_contact_from_hubspot(self, hubspot_contact):
        """Sync a contact from HubSpot to local database"""
        try:
            props = hubspot_contact.get('properties', {})
            hubspot_id = int(hubspot_contact['id'])
            
            contact = Contact.query.filter_by(hubspot_id=hubspot_id).first()
            
            if not contact:
                contact = Contact(hubspot_id=hubspot_id)
                db.session.add(contact)
            
            contact.email = props.get('email')
            contact.firstname = props.get('firstname')
            contact.lastname = props.get('lastname')
            contact.phone = props.get('phone')
            contact.company = props.get('company')
            contact.website = props.get('website')
            contact.lifecyclestage = props.get('lifecyclestage')
            
            db.session.commit()
            return contact
            
        except Exception as e:
            print(f"Error in _sync_contact_from_hubspot: {str(e)}")
            db.session.rollback()
            return None

    def search_contacts(self, filters, page, per_page):
        """Search contacts using HubSpot's search"""
        try:
            after = (page - 1) * per_page if page > 1 else None
            
            hubspot_response = self.hubspot_client.list_contacts(
                limit=per_page,
                after=after,
                filters=filters
            )
            
            contacts = []
            if hubspot_response and 'results' in hubspot_response:
                contacts = hubspot_response['results']
                for contact_data in contacts:
                    self._sync_contact_from_hubspot(contact_data)
            
            total = hubspot_response.get('total', len(contacts))
            pages = -(-total // per_page)
            
            return contacts, total, pages
            
        except Exception as e:
            print(f"Error in search_contacts: {str(e)}")
            return [], 0, 0

    def batch_operation(self, operation, contacts_data):
        """Perform batch operations on contacts"""
        try:
            results = []
            
            if operation == "create":
                response = self.hubspot_client.batch_create_contacts(contacts_data)
                if response and 'results' in response:
                    for result in response['results']:
                        self._sync_contact_from_hubspot(result)
                        results.append({
                            'id': result['id'],
                            'status': 'success',
                            'error': None
                        })
            
            elif operation == "update":
                response = self.hubspot_client.batch_update_contacts(contacts_data)
                if response and 'results' in response:
                    for result in response['results']:
                        self._sync_contact_from_hubspot(result)
                        results.append({
                            'id': result['id'],
                            'status': 'success',
                            'error': None
                        })
            
            elif operation == "delete":
                try:
                    success = self.hubspot_client.batch_delete_contacts(contacts_data)
                    if success:
                        for contact_id in contacts_data:
                            contact = Contact.query.filter_by(hubspot_id=contact_id).first()
                            if contact:
                                db.session.delete(contact)
                        db.session.commit()
                        
                        results = [{
                            'id': contact_id,
                            'status': 'success',
                            'error': None
                        } for contact_id in contacts_data]
                except Exception as e:
                    results = [{
                        'id': contact_id,
                        'status': 'error',
                        'error': str(e)
                    } for contact_id in contacts_data]
            
            else:
                raise ValueError(f"Invalid operation: {operation}")
            
            return results
            
        except Exception as e:
            print(f"Error in batch operation: {str(e)}")
            if not results:
                results = [{
                    'id': contact.get('id', 'unknown') if isinstance(contact, dict) else str(contact),
                    'status': 'error',
                    'error': str(e)
                } for contact in contacts_data]
            return results
