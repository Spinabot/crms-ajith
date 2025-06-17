import requests
from app.config import Config

class HubspotClient:
    def __init__(self):
        self.base_url = Config.HUBSPOT_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {Config.HUBSPOT_API_TOKEN}',
            'Content-Type': 'application/json'
        }

    def _handle_response(self, response):
        if response.status_code >= 400:
            raise Exception(f"HubSpot API error: {response.text}")
        return response.json() if response.status_code != 204 else None

    def create_contact(self, properties):
        """Create a contact in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts"
            data = {"properties": properties}
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 409:
                error_data = response.json()
                error_message = error_data.get('message', 'Contact already exists')
                raise ValueError(f"Contact already exists: {error_message}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error creating contact in HubSpot: {str(e)}")
            if e.response.status_code == 409:
                raise ValueError("Contact with this email already exists")
            raise Exception(f"Failed to create contact: {str(e)}")
        except Exception as e:
            print(f"Error creating contact in HubSpot: {str(e)}")
            raise

    def get_contact(self, contact_id, properties=None, properties_with_history=None):
        """Get a contact by ID"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
            params = {}
            
            if properties:
                params['properties'] = ','.join(properties)
            if properties_with_history:
                params['propertiesWithHistory'] = ','.join(properties_with_history)
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting contact from HubSpot: {str(e)}")
            raise Exception(f"Failed to get contact: {str(e)}")

    def list_contacts(self, limit=None, after=None, properties=None, filters=None):
        """List contacts with optional filters"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/search"
            
            data = {
                "filterGroups": [],
                "properties": properties or ["email", "firstname", "lastname", "company"],
                "limit": limit or 100
            }
            
            if after:
                data["after"] = after
            
            if filters:
                filter_group = {"filters": []}
                
                if filters.get('email'):
                    filter_group["filters"].append({
                        "propertyName": "email",
                        "operator": "CONTAINS_TOKEN",
                        "value": filters['email']
                    })
                
                if filters.get('name'):
                    name_filter_group = {
                        "filters": [
                            {
                                "propertyName": "firstname",
                                "operator": "CONTAINS_TOKEN",
                                "value": filters['name']
                            },
                            {
                                "propertyName": "lastname",
                                "operator": "CONTAINS_TOKEN",
                                "value": filters['name']
                            }
                        ]
                    }
                    data["filterGroups"].append(name_filter_group)
                
                if filters.get('company'):
                    filter_group["filters"].append({
                        "propertyName": "company",
                        "operator": "CONTAINS_TOKEN",
                        "value": filters['company']
                    })
                
                if filter_group["filters"]:
                    data["filterGroups"].append(filter_group)
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error listing contacts: {str(e)}")
            raise Exception(f"Failed to list contacts: {str(e)}")
        except Exception as e:
            print(f"Error in list_contacts: {str(e)}")
            raise

    def update_contact(self, contact_id, properties):
        """Update a contact in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
            data = {"properties": properties}
            response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code == 404:
                raise ValueError(f"Contact {contact_id} not found")
            elif response.status_code == 409:
                error_data = response.json()
                error_message = error_data.get('message', 'Email already exists')
                raise ValueError(f"Conflict updating contact: {error_message}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error updating contact in HubSpot: {str(e)}")
            if e.response.status_code == 404:
                raise ValueError(f"Contact {contact_id} not found")
            elif e.response.status_code == 409:
                raise ValueError("Email address already exists for another contact")
            raise Exception(f"Failed to update contact: {str(e)}")
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error updating contact in HubSpot: {str(e)}")
            raise

    def batch_create_contacts(self, contacts):
        """Create multiple contacts in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/batch/create"
            inputs = []
            for contact in contacts:
                inputs.append({
                    "properties": contact.get("properties", {})
                })
            
            data = {"inputs": inputs}
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error in batch create contacts: {str(e)}")
            raise Exception(f"Failed to create contacts: {str(e)}")

    def batch_update_contacts(self, contacts):
        """Update multiple contacts in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/batch/update"
            inputs = []
            for contact in contacts:
                inputs.append({
                    "id": contact["id"],
                    "properties": contact.get("properties", {})
                })
            
            data = {"inputs": inputs}
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error in batch update contacts: {str(e)}")
            raise Exception(f"Failed to update contacts: {str(e)}")

    def batch_delete_contacts(self, contact_ids):
        """Delete multiple contacts in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/batch/archive"
            inputs = [{"id": str(id)} for id in contact_ids]
            data = {"inputs": inputs}
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            print(f"Error in batch delete contacts: {str(e)}")
            raise Exception(f"Failed to delete contacts: {str(e)}")

    def batch_read_contacts(self, contact_ids, properties=None):
        """Read multiple contacts from HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/batch/read"
            inputs = [{"id": str(id)} for id in contact_ids]
            data = {
                "inputs": inputs,
                "properties": properties if properties else ["email", "firstname", "lastname", "company"]
            }
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error in batch read contacts: {str(e)}")
            raise Exception(f"Failed to read contacts: {str(e)}")

    def create_association(self, contact_id, to_object_type, to_object_id, association_type_id):
        """Create an association between objects"""
        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}/associations/{to_object_type}/{to_object_id}/{association_type_id}"
        response = requests.put(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def delete_association(self, contact_id, to_object_type, to_object_id, association_type_id):
        """Delete an association between objects"""
        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}/associations/{to_object_type}/{to_object_id}/{association_type_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.status_code == 204

    def batch_upsert_contacts(self, inputs):
        """Batch upsert contacts"""
        url = f"{self.base_url}/crm/v3/objects/contacts/batch/upsert"
        response = requests.post(url, headers=self.headers, json={"inputs": inputs})
        response.raise_for_status()
        return response.json()

    def search_contacts(self, filters):
        url = f"{self.base_url}/crm/v3/objects/contacts/search"
        response = requests.post(url, headers=self.headers, json=filters)
        return self._handle_response(response)

    def delete_contact(self, contact_id):
        """Delete a contact in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 404:
                raise ValueError(f"Contact {contact_id} not found")
            
            response.raise_for_status()
            return response.status_code == 204
        
        except requests.exceptions.RequestException as e:
            print(f"Error deleting contact in HubSpot: {str(e)}")
            raise Exception(f"Failed to delete contact: {str(e)}")
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error deleting contact in HubSpot: {str(e)}")
            raise
