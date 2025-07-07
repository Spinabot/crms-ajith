"""
Validation schemas for Jobber CRM data
"""
from datetime import datetime
from typing import Dict, List, Optional

class JobberClientSchema:
    """Schema for validating Jobber client data"""

    @staticmethod
    def validate_client_data(client_data: Dict) -> Dict:
        """Validate and clean client data"""
        if not isinstance(client_data, dict):
            raise ValueError("Client data must be a dictionary")

        # Required fields
        required_fields = ['id']
        for field in required_fields:
            if field not in client_data:
                raise ValueError(f"Missing required field: {field}")

        # Clean and validate data
        cleaned_data = {
            'id': str(client_data.get('id', '')),
            'firstName': client_data.get('firstName', ''),
            'lastName': client_data.get('lastName', ''),
            'companyName': client_data.get('companyName', ''),
            'isLead': client_data.get('isLead', False),
            'isCompany': client_data.get('isCompany', False),
            'jobberWebUri': client_data.get('jobberWebUri', ''),
            'balance': client_data.get('balance', 0),
            'emails': JobberClientSchema._validate_emails(client_data.get('emails', [])),
            'phones': JobberClientSchema._validate_phones(client_data.get('phones', [])),
            'clientProperties': client_data.get('clientProperties', {}),
            'sourceAttribution': client_data.get('sourceAttribution', {})
        }

        return cleaned_data

    @staticmethod
    def _validate_emails(emails: List) -> List:
        """Validate email data"""
        if not isinstance(emails, list):
            return []

        validated_emails = []
        for email in emails:
            if isinstance(email, dict) and 'address' in email:
                validated_emails.append({
                    'id': email.get('id', ''),
                    'address': email.get('address', '')
                })

        return validated_emails

    @staticmethod
    def _validate_phones(phones: List) -> List:
        """Validate phone data"""
        if not isinstance(phones, list):
            return []

        validated_phones = []
        for phone in phones:
            if isinstance(phone, dict) and 'number' in phone:
                validated_phones.append({
                    'id': phone.get('id', ''),
                    'description': phone.get('description', ''),
                    'smsAllowed': phone.get('smsAllowed', False),
                    'number': phone.get('number', '')
                })

        return validated_phones

class JobberLeadSchema:
    """Schema for validating Jobber lead data in unified format"""

    @staticmethod
    def validate_lead_data(lead_data: Dict) -> Dict:
        """Validate and clean lead data for unified format"""
        if not isinstance(lead_data, dict):
            raise ValueError("Lead data must be a dictionary")

        # Validate required fields
        if not lead_data.get('firstName') and not lead_data.get('lastName') and not lead_data.get('companyName'):
            raise ValueError("At least one of firstName, lastName, or companyName must be provided")

        # Clean and validate data
        cleaned_data = {
            'firstName': lead_data.get('firstName', ''),
            'lastName': lead_data.get('lastName', ''),
            'email': lead_data.get('email', ''),
            'mobilePhone': lead_data.get('mobilePhone', ''),
            'homePhone': lead_data.get('homePhone', ''),
            'officePhone': lead_data.get('officePhone', ''),
            'companyName': lead_data.get('companyName', ''),
            'title': lead_data.get('title', ''),
            'addressLine1': lead_data.get('addressLine1', ''),
            'addressLine2': lead_data.get('addressLine2', ''),
            'city': lead_data.get('city', ''),
            'state': lead_data.get('state', ''),
            'zip': lead_data.get('zip', ''),
            'country': lead_data.get('country', 'USA'),
            'leadStatus': lead_data.get('leadStatus', ''),
            'leadSource': lead_data.get('leadSource', ''),
            'notes': lead_data.get('notes', ''),
            'crmSystem': 'jobber',
            'crmExternalId': lead_data.get('crmExternalId', ''),
            'crmRawData': lead_data.get('crmRawData', {})
        }

        return cleaned_data

# Helper functions for validation
def validate_client_create_data(data: Dict) -> Dict:
    """Validate client create data"""
    return JobberClientSchema.validate_client_data(data)

def validate_lead_data(data: Dict) -> Dict:
    """Validate lead data for unified format"""
    return JobberLeadSchema.validate_lead_data(data)