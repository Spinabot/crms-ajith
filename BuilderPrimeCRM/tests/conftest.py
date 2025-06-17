import pytest
from app import create_app, db
from app.config import Config
import os

os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
    API_KEY = 'test_api_key_123'
    SECRET_KEY = 'test_secret_key_123'
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Authentication headers for API requests."""
    return {
        'Content-Type': 'application/json',
        'x-api-key': TestConfig.API_KEY
    }

@pytest.fixture
def db_session(app):
    """Creates a new database session for a test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        
        db.session = session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove() 