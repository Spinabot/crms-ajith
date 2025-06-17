import os
from app.config import Config

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "postgresql://postgres:Vissu@localhost:5432/contacts_test_db"
    )