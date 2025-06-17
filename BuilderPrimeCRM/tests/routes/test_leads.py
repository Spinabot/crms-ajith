import pytest
import json
from app import create_app, db
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

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

class TestLeadsAPI:
    def test_create_lead(self, client, valid_lead_data):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        response = client.post('/api/clients/v1', 
                             data=json.dumps(valid_lead_data),
                             headers=headers)
        assert response.status_code == 201
        assert 'id' in response.json

    def test_create_lead_without_api_key(self, client, valid_lead_data):
        headers = {'Content-Type': 'application/json'}
        response = client.post('/api/clients/v1', 
                             data=json.dumps(valid_lead_data),
                             headers=headers)
        assert response.status_code == 401

    def test_get_leads(self, client, valid_lead_data):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        for i in range(3):
            data = valid_lead_data.copy()
            data['email'] = f'test{i}@example.com'
            client.post('/api/clients/v1', 
                       data=json.dumps(data),
                       headers=headers)

        response = client.get('/api/clients',
                            headers={'x-api-key': TestConfig.API_KEY})
        assert response.status_code == 200
        assert response.json['total'] == 3
        assert len(response.json['leads']) == 3

    def test_get_leads_pagination(self, client, valid_lead_data):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        for i in range(15):
            data = valid_lead_data.copy()
            data['email'] = f'test{i}@example.com'
            client.post('/api/clients/v1', 
                       data=json.dumps(data),
                       headers=headers)

        response = client.get('/api/clients?page=1&per_page=10',
                            headers={'x-api-key': TestConfig.API_KEY})
        assert response.status_code == 200
        assert response.json['total'] == 15
        assert len(response.json['leads']) == 10

        response = client.get('/api/clients?page=2&per_page=10',
                            headers={'x-api-key': TestConfig.API_KEY})
        assert response.status_code == 200
        assert len(response.json['leads']) == 5

    def test_update_lead(self, client, valid_lead_data):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        response = client.post('/api/clients/v1', 
                             data=json.dumps(valid_lead_data),
                             headers=headers)
        lead_id = response.json['id']

        update_data = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane.doe@example.com',
            'mobilePhone': valid_lead_data['mobilePhone'],
            'addressLine1': valid_lead_data['addressLine1'],
            'city': valid_lead_data['city'],
            'state': valid_lead_data['state'],
            'zip': valid_lead_data['zip']
        }
        response = client.put(f'/api/clients/v1/{lead_id}',
                            data=json.dumps(update_data),
                            headers=headers)
        assert response.status_code == 200
        assert response.json['firstName'] == 'Jane'

    def test_delete_lead(self, client, valid_lead_data):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        response = client.post('/api/clients/v1', 
                             data=json.dumps(valid_lead_data),
                             headers=headers)
        lead_id = response.json['id']

        response = client.delete(f'/api/clients/v1/{lead_id}',
                               headers={'x-api-key': TestConfig.API_KEY})
        assert response.status_code == 200

        response = client.get('/api/clients',
                            headers={'x-api-key': TestConfig.API_KEY})
        assert response.status_code == 200
        assert response.json['total'] == 0

    def test_create_lead_invalid_data(self, client):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        invalid_data = {}  
        response = client.post('/api/clients/v1', 
                             data=json.dumps(invalid_data),
                             headers=headers)
        assert response.status_code == 400

    def test_update_lead_not_found(self, client, valid_lead_data):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        response = client.put('/api/clients/v1/99999',
                            data=json.dumps(valid_lead_data),
                            headers=headers)
        assert response.status_code == 404

    def test_delete_lead_not_found(self, client):
        response = client.delete('/api/clients/v1/99999',
                               headers={'x-api-key': TestConfig.API_KEY})
        assert response.status_code == 404

    def test_get_leads_with_filters(self, client, valid_lead_data):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': TestConfig.API_KEY
        }
        valid_lead_data['leadStatusName'] = 'New'
        client.post('/api/clients/v1', 
                   data=json.dumps(valid_lead_data),
                   headers=headers)

        response = client.get('/api/clients?lead-status=New',
                            headers={'x-api-key': TestConfig.API_KEY})
        assert response.status_code == 200
        assert response.json['total'] == 1
        assert response.json['leads'][0]['leadStatusName'] == 'New'
