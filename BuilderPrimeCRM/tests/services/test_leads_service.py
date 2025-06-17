import pytest
from app.services.lead_service import LeadService
from app.models import Lead
from datetime import datetime
from app import db

@pytest.fixture
def valid_lead_data():
    return {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john.doe@example.com',
        'mobilePhone': '+18005554444',
        'addressLine1': '123 Main St',
        'city': 'Los Angeles',
        'state': 'CA',
        'zip': '90001',
        'companyName': 'Test Company',
        'title': 'Manager',
        'notes': 'Test notes',
        'leadStatusName': 'New',
        'leadSourceName': 'Website'
    }

@pytest.fixture
def sample_lead(app, valid_lead_data):
    with app.app_context():
        lead = LeadService.create_lead(valid_lead_data)
        db.session.refresh(lead)  
        return lead

class TestLeadService:
    def test_create_lead_with_valid_data(self, app, valid_lead_data):
        with app.app_context():
            lead = LeadService.create_lead(valid_lead_data)
            db.session.refresh(lead)  
            assert lead.first_name == valid_lead_data['firstName']
            assert lead.last_name == valid_lead_data['lastName']
            assert lead.email == valid_lead_data['email']
            assert lead.mobile_phone == valid_lead_data['mobilePhone']

    def test_create_lead_with_missing_required_field(self, app):
        with app.app_context():
            invalid_data = {
                'firstName': 'John',
            }
            with pytest.raises(ValueError) as exc_info:
                LeadService.create_lead(invalid_data)
            assert "Last name is required" in str(exc_info.value)

    def test_get_leads_pagination(self, app, valid_lead_data):
        with app.app_context():
            for i in range(15):
                data = valid_lead_data.copy()
                data['email'] = f'test{i}@example.com'
                LeadService.create_lead(data)
            db.session.commit()

            leads, total = LeadService.get_leads(page=1, per_page=10)
            assert len(leads) == 10
            assert total == 15

            leads, total = LeadService.get_leads(page=2, per_page=10)
            assert len(leads) == 5
            assert total == 15

    def test_update_lead(self, app, sample_lead):
        with app.app_context():
            db.session.add(sample_lead)  
            update_data = {
                'firstName': 'Jane',
                'email': 'jane.doe@example.com'
            }
            updated_lead = LeadService.update_lead(sample_lead.id, update_data)
            db.session.refresh(updated_lead)  
            assert updated_lead.first_name == 'Jane'
            assert updated_lead.email == 'jane.doe@example.com'
            assert updated_lead.last_name == sample_lead.last_name

    def test_delete_lead(self, app, sample_lead):
        with app.app_context():
            db.session.add(sample_lead) 
            assert LeadService.delete_lead(sample_lead.id) is True
            assert LeadService.get_lead(sample_lead.id) is None

    def test_get_leads_with_filters(self, app, valid_lead_data):
        with app.app_context():
            data1 = valid_lead_data.copy()
            data1['leadStatusName'] = 'New'
            data1['email'] = 'test1@example.com'
            LeadService.create_lead(data1)

            data2 = valid_lead_data.copy()
            data2['leadStatusName'] = 'In Progress'
            data2['email'] = 'test2@example.com'
            LeadService.create_lead(data2)
            db.session.commit()

            leads, total = LeadService.get_leads(lead_status='New')
            assert total == 1
            assert leads[0].lead_status == 'New'

    def test_get_leads_by_phone(self, app, valid_lead_data):
        with app.app_context():
            phone = '+18005554444'
            data = valid_lead_data.copy()
            data['mobilePhone'] = phone
            LeadService.create_lead(data)
            db.session.commit()

            leads, total = LeadService.get_leads(phone=phone)
            assert total == 1
            assert leads[0].mobile_phone == phone
