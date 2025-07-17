import pytest
from app import create_app, db
from app.models import UnifiedLead, CRMConnection, SyncLog

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_app_creation(app):
    """Test that the app can be created"""
    assert app is not None
    assert app.config['TESTING'] is True

def test_database_models(app):
    """Test database model creation"""
    with app.app_context():
        # Test UnifiedLead model
        lead = UnifiedLead(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            crm_system='builder_prime'
        )
        db.session.add(lead)
        db.session.commit()

        assert lead.id is not None
        assert lead.first_name == 'John'
        assert lead.crm_system == 'builder_prime'

        # Test CRMConnection model
        connection = CRMConnection(
            crm_system='builder_prime',
            api_key='test_api_key',
            is_active=True
        )
        db.session.add(connection)
        db.session.commit()

        assert connection.id is not None
        assert connection.crm_system == 'builder_prime'
        assert connection.is_active is True

def test_api_endpoints(client):
    """Test basic API endpoints"""
    # Test root endpoint redirects to swagger
    response = client.get('/')
    assert response.status_code == 302  # Redirect

    # Test BuilderPrime endpoints return 401 without auth
    response = client.get('/builder-prime/leads')
    assert response.status_code == 401

    response = client.post('/builder-prime/leads',
                          json={'firstName': 'John', 'lastName': 'Doe'})
    assert response.status_code == 401

def test_placeholder_endpoints(client):
    """Test placeholder endpoints for unimplemented CRMs"""
    # Test HubSpot placeholder
    response = client.get('/hubspot/leads')
    assert response.status_code == 501
    assert b'coming soon' in response.data

    # Test Jobber placeholder
    response = client.get('/jobber/leads')
    assert response.status_code == 501
    assert b'coming soon' in response.data

    # Test JobNimbus placeholder
    response = client.get('/jobnimbus/leads')
    assert response.status_code == 501
    assert b'coming soon' in response.data

    # Test Zoho placeholder
    response = client.get('/zoho/leads')
    assert response.status_code == 501
    assert b'coming soon' in response.data