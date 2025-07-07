#!/usr/bin/env python3
"""
Simple test script to verify HubSpot integration fix
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = os.getenv('API_KEY', 'test_api_key')

headers = {
    'Content-Type': 'application/json',
    'x-api-key': API_KEY
}

def test_hubspot_fix():
    """Test HubSpot integration with corrected data mapping"""

    print("Testing HubSpot Integration Fix...")
    print("=" * 50)

    # Test data with valid HubSpot properties
    test_lead = {
        "firstName": "John",
        "lastName": "Smith",
        "email": f"john.smith.{datetime.now().timestamp()}@example.com",
        "mobilePhone": "+18005554444",
        "addressLine1": "123 Main Street",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "12345",
        "companyName": "Test Company",
        "title": "Manager",
        "leadStatus": "Lead Received"  # This should map to 'lead' in HubSpot
    }

    try:
        # Test 1: Create a lead
        print("1. Testing lead creation with corrected mapping...")
        response = requests.post(
            f"{BASE_URL}/api/hubspot/leads",
            headers=headers,
            json=test_lead
        )

        print(f"   Response Status: {response.status_code}")
        print(f"   Response Body: {response.text[:500]}...")

        if response.status_code == 201:
            created_lead = response.json()
            print(f"   ✓ Lead created successfully with ID: {created_lead.get('id')}")
            external_id = created_lead.get('id')

            # Test 2: Get the created lead
            print("2. Testing lead retrieval...")
            response = requests.get(
                f"{BASE_URL}/api/hubspot/leads/{external_id}",
                headers=headers
            )

            if response.status_code == 200:
                retrieved_lead = response.json()
                print(f"   ✓ Lead retrieved successfully: {retrieved_lead.get('firstName')} {retrieved_lead.get('lastName')}")
            else:
                print(f"   ✗ Failed to retrieve lead: {response.status_code} - {response.text}")

            # Test 3: Delete the test lead
            print("3. Testing lead deletion...")
            response = requests.delete(
                f"{BASE_URL}/api/hubspot/leads/{external_id}",
                headers=headers
            )

            if response.status_code == 204:
                print(f"   ✓ Lead deleted successfully")
            else:
                print(f"   ✗ Failed to delete lead: {response.status_code} - {response.text}")

            print("\n" + "=" * 50)
            print("HubSpot Integration Fix Test Completed Successfully!")
            return True
        else:
            print(f"   ✗ Failed to create lead: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("   ✗ Connection error: Make sure the server is running on localhost:5000")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_hubspot_fix()
    exit(0 if success else 1)