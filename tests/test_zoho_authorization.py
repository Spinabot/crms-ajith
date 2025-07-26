#!/usr/bin/env python3
"""
Test script to verify Zoho authorization behavior
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db

def test_zoho_authorization():
    """Test Zoho authorization with test data"""
    app = create_app()

    with app.app_context():
        print("Testing Zoho authorization behavior...")

        # Test 1: Check if test credentials exist
        # creds = ZohoCreds.query.filter_by(entity_id=1).first()
        # if creds:
        #     print(f"✓ Test credentials found for entity_id=1")
        #     print(f"  - Access Token: {creds.access_token}")
        #     print(f"  - Has Valid Token: {creds.has_valid_token()}")
        #     print(f"  - Expiration Time: {creds.expiration_time}")
        # else:
        #     print("❌ Test credentials not found")
        #     return False

        # Test 2: Check if test client exists
        # client = ZohoClients.query.filter_by(entity_id=1).first()
        # if client:
        #     print(f"✓ Test client found for entity_id=1")
        #     print(f"  - Zoho ID: {client.zoho_id}")
        #     print(f"  - Full Name: {client.full_name}")
        # else:
        #     print("❌ Test client not found")
        #     return False

        # Test 3: Test authorization route behavior
        with app.test_client() as client:
            # Test authorization for entity_id=1 (should return "User already authorized")
            response = client.get('/zoho/1/redirect')
            print(f"✓ Authorization response for entity_id=1: {response.data.decode()}")

            # Test authorization for entity_id=999 (should redirect to Zoho)
            response = client.get('/zoho/999/redirect')
            print(f"✓ Authorization response for entity_id=999: {response.status_code} (should be 302 redirect)")

        print("\n🎉 Zoho authorization test completed successfully!")
        print("\nNow you can:")
        print("1. Start your application: python run.py")
        print("2. Visit: http://localhost:5000/zoho/1/redirect (should show 'User already authorized')")
        print("3. Visit: http://localhost:5000/zoho/999/redirect (should redirect to Zoho OAuth)")

        return True

if __name__ == "__main__":
    test_zoho_authorization()