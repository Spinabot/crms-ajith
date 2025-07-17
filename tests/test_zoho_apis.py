#!/usr/bin/env python3
"""
Test script to verify Zoho API endpoints (leads, users, metadata)
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import ZohoCreds, ZohoClients

def test_zoho_apis():
    """Test Zoho API endpoints"""
    app = create_app()

    with app.app_context():
        print("Testing Zoho API endpoints...")

        # Test 1: Check if test credentials exist
        creds = ZohoCreds.query.filter_by(entity_id=1).first()
        if not creds:
            print("❌ Test credentials not found. Run setup_zoho_test_data.py first.")
            return False

        print("✓ Test credentials found")

        # Test 2: Test API endpoints with test client
        with app.test_client() as client:
            print("\n--- Testing API Endpoints ---")

            # Test leads endpoint
            print("Testing /zoho/1/leads...")
            response = client.get('/zoho/1/leads')
            print(f"  Status: {response.status_code}")
            if response.status_code == 401:
                print("  ✓ Expected 401 (dummy token is expired)")
            else:
                print(f"  Response: {response.data.decode()[:100]}...")

            # Test users endpoint
            print("Testing /zoho/1/users...")
            response = client.get('/zoho/1/users')
            print(f"  Status: {response.status_code}")
            if response.status_code == 401:
                print("  ✓ Expected 401 (dummy token is expired)")
            else:
                print(f"  Response: {response.data.decode()[:100]}...")

            # Test metadata endpoint
            print("Testing /zoho/1/leads/meta...")
            response = client.get('/zoho/1/leads/meta')
            print(f"  Status: {response.status_code}")
            if response.status_code == 401:
                print("  ✓ Expected 401 (dummy token is expired)")
            else:
                print(f"  Response: {response.data.decode()[:100]}...")

            # Test with non-existent entity
            print("Testing /zoho/999/leads (non-existent entity)...")
            response = client.get('/zoho/999/leads')
            print(f"  Status: {response.status_code}")
            if response.status_code == 401:
                print("  ✓ Expected 401 (entity not authenticated)")
            else:
                print(f"  Response: {response.data.decode()[:100]}...")

        print("\n🎉 Zoho API endpoints test completed!")
        print("\nNote: The 401 responses are expected because:")
        print("1. Test credentials use dummy/expired tokens")
        print("2. For real testing, you need valid OAuth tokens")
        print("\nTo test with real data:")
        print("1. Complete OAuth flow for entity_id=1")
        print("2. Or use a different entity_id with valid credentials")

        return True

if __name__ == "__main__":
    test_zoho_apis()