#!/usr/bin/env python3
"""
Setup script to add test Zoho credentials and client data for development and testing
"""
import sys
import os
import time
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import ZohoCreds, ZohoClients

def setup_zoho_test_data():
    """Add test Zoho data to the database"""
    app = create_app()

    with app.app_context():
        print("Setting up Zoho test data...")

        # Step 1: Check if test credentials (entity_id=1) already exist
        existing_credential = ZohoCreds.query.filter_by(entity_id=1).first()
        if not existing_credential:
            # Add test credential for development and testing
            test_credential = ZohoCreds(
                entity_id=1,  # Test entity ID
                access_token="dummy_access_token",  # Dummy access token for testing
                refresh_token="1000.4f3db5728bf104834e81cc9c117ed326.9964fe2adb4fbe7b0aca8c6a29675210",  # Dummy refresh token
                expiration_time=int(time.time()) - 1000  # Set expiration time to past timestamp to simulate expired token
            )
            db.session.add(test_credential)
            db.session.commit()
            print("✓ Test credentials added to zoho_credentials table!")
        else:
            print("✓ Test credentials already exist in zoho_credentials table!")

        # Step 2: Check if test client (entity_id=1) already exists
        existing_client = ZohoClients.query.filter_by(entity_id=1).first()
        if not existing_client:
            # Add test client for development and testing
            test_client = ZohoClients(
                zoho_id="6707647000000503001",  # Real Zoho ID for testing
                entity_id=1,  # Test entity ID
                full_name="karhteek V"  # Real name for testing
            )
            db.session.add(test_client)
            db.session.commit()
            print("✓ Test client added to zoho_clients table!")
        else:
            print("✓ Test client already exists in zoho_clients table!")

        print("\n🎉 Zoho test data setup completed successfully!")
        print("\nTest Data Summary:")
        print("- Entity ID: 1")
        print("- Access Token: dummy_access_token")
        print("- Refresh Token: 1000.4f3db5728bf104834e81cc9c117ed326.9964fe2adb4fbe7b0aca8c6a29675210")
        print("- Zoho Client ID: 6707647000000503001")
        print("- Client Name: karhteek V")
        print("\nNote: These are test credentials. For production, use real OAuth flow.")

if __name__ == "__main__":
    setup_zoho_test_data()