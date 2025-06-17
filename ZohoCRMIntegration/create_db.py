# create_db.py
# Import necessary modules and components
from main import app  # Import the Flask app to use its context
from database.schemas import create_tables  # Function to create database tables
import time  # Used to set expiration time for tokens
from main import db  # Import the database instance
from database.schemas import ZohoCreds, Clients  # Import database models

# Use the Flask app context to perform database operations
with app.app_context():
    # Step 1: Create database tables
    create_tables()
    print("Database tables created!")

    # Step 2: Check if test credentials (entity_id=1) already exist in the ZohoCreds table
    existing_credential = ZohoCreds.query.filter_by(entity_id=1).first()
    if not existing_credential:
        # If no credentials exist, add a test credential for development and testing
        TEST_CREDENTIAL = ZohoCreds(
            entity_id=1,  # Test entity ID
            access_token="dummy_access_token",  # Dummy access token for testing
            refresh_token="1000.4f3db5728bf104834e81cc9c117ed326.9964fe2adb4fbe7b0aca8c6a29675210",  # Dummy refresh token
            expiration_time=int(time.time()) - 1000  # Set expiration time to a past timestamp to simulate an expired token
        )
        db.session.add(TEST_CREDENTIAL)  # Add the test credential to the session
        db.session.commit()  # Commit the changes to the database
        print("TEST data added to credentials table!")
    else:
        # If credentials already exist, print a message
        print("Data with entity_id=1 already exists in the credentials table!")

    # Step 3: Check if test client (entity_id=1) already exists in the Clients table
    existing_CRM_user = Clients.query.filter_by(entity_id=1).first()
    if not existing_CRM_user:
        # If no client exists, add a test client for development and testing
        TEST_CLIENT = Clients(
            zoho_id="6707647000000503001",  # This is real zoho ID for testing
            entity_id=1,  # Test entity ID
            full_name="karhteek V"  # real name for testing
        )
        db.session.add(TEST_CLIENT)  # Add the test client to the session
        db.session.commit()  # Commit the changes to the database
        print("TEST data added to clients table!")
    else:
        # If client already exists, print a message
        print("Data with entity_id=1 already exists in the clients table!")


#the reason for adding test data is that before we spin up the service, 
# most likely we will need to test the service using pytest or other testing frameworks.
# if the database is empty, the tests will fail.
# This script ensures that the database is set up with necessary tables and test data
# so that the tests can run successfully.