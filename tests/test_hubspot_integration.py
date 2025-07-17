#!/usr/bin/env python3
"""
Test script for HubSpot CRM integration
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

def test_hubspot_integration():
    """Test HubSpot CRM integration endpoints"""

    print("Testing HubSpot CRM Integration...")
    print("=" * 50)

    # Test data
    test_lead = {
        "firstName": "John",
        "lastName": "Doe",
        "email": f"john.doe.{datetime.now().timestamp()}@example.com",
        "mobilePhone": "+18005554444",
        "homePhone": "+18005554445",
        "addressLine1": "123 Main Street",
        "addressLine2": "Suite 100",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90210",
        "country": "USA",
        "companyName": "Test Company",
        "title": "Manager",
        "leadStatus": "Lead Received",
        "leadSource": "Website",
        "notes": "Test lead from integration"
    }

    try:
        # Test 1: Create a lead
        print("1. Testing lead creation...")
        response = requests.post(
            f"{BASE_URL}/api/hubspot/leads",
            headers=headers,
            json=test_lead
        )

        if response.status_code == 201:
            created_lead = response.json()
            print(f"   ✓ Lead created successfully with ID: {created_lead.get('id')}")
            external_id = created_lead.get('id')
        else:
            print(f"   ✗ Failed to create lead: {response.status_code} - {response.text}")
            return False

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

        # Test 3: Update the lead
        print("3. Testing lead update...")
        update_data = {
            "title": "Senior Manager",
            "notes": "Updated notes from integration test"
        }

        response = requests.put(
            f"{BASE_URL}/api/hubspot/leads/{external_id}",
            headers=headers,
            json=update_data
        )

        if response.status_code == 200:
            updated_lead = response.json()
            print(f"   ✓ Lead updated successfully: {updated_lead.get('title')}")
        else:
            print(f"   ✗ Failed to update lead: {response.status_code} - {response.text}")

        # Test 4: List leads
        print("4. Testing lead listing...")
        response = requests.get(
            f"{BASE_URL}/api/hubspot/leads?page=1&per_page=10",
            headers=headers
        )

        if response.status_code == 200:
            leads_data = response.json()
            print(f"   ✓ Retrieved {len(leads_data.get('leads', []))} leads (Total: {leads_data.get('total', 0)})")
        else:
            print(f"   ✗ Failed to list leads: {response.status_code} - {response.text}")

        # Test 5: Sync leads
        print("5. Testing lead sync...")
        response = requests.post(
            f"{BASE_URL}/api/hubspot/leads/sync",
            headers=headers
        )

        if response.status_code == 200:
            sync_result = response.json()
            print(f"   ✓ Sync completed: {sync_result.get('message', 'Unknown')}")
        else:
            print(f"   ✗ Failed to sync leads: {response.status_code} - {response.text}")

        # Test 6: Delete the test lead
        print("6. Testing lead deletion...")
        response = requests.delete(
            f"{BASE_URL}/api/hubspot/leads/{external_id}",
            headers=headers
        )

        if response.status_code == 204:
            print(f"   ✓ Lead deleted successfully")
        else:
            print(f"   ✗ Failed to delete lead: {response.status_code} - {response.text}")

        print("\n" + "=" * 50)
        print("HubSpot Integration Test Completed!")
        return True

    except requests.exceptions.ConnectionError:
        print("   ✗ Connection error: Make sure the server is running on localhost:5000")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_hubspot_integration()
    exit(0 if success else 1)