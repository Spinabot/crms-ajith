#!/usr/bin/env python3
"""
Test script for Zoho CRM CRUD operations in UnifiedCRMIntegration
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
ENTITY_ID = 1  # Use the same entity ID as in previous tests

def test_zoho_create_lead():
    """Test creating a lead in Zoho CRM"""
    print("=== Testing Zoho Create Lead ===")

    url = f"{BASE_URL}/zoho/{ENTITY_ID}/leads/create"

    # Sample lead data based on the reference create.py
    lead_data = {
        "data": [
            {
                "First_Name": "John",
                "Last_Name": "Doe",
                "Company": "Test Company Inc",
                "Email": "john.doe@testcompany.com",
                "Phone": "555-123-4567",
                "Lead_Source": "Website",
                "Lead_Status": "New",
                "Industry": "Technology",
                "Annual_Revenue": 1000000,
                "City": "New York",
                "State": "NY",
                "Country": "United States"
            }
        ]
    }

    try:
        response = requests.post(url, json=lead_data, headers={"Content-Type": "application/json"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code in [200, 201]:
            print("✅ Create lead test PASSED")
            return response.json()
        else:
            print("❌ Create lead test FAILED")
            return None

    except Exception as e:
        print(f"❌ Create lead test ERROR: {e}")
        return None

def test_zoho_update_lead(lead_id):
    """Test updating a lead in Zoho CRM"""
    print(f"\n=== Testing Zoho Update Lead (ID: {lead_id}) ===")

    url = f"{BASE_URL}/zoho/{ENTITY_ID}/leads/update?client_id={lead_id}"

    # Sample update data
    update_data = {
        "data": [
            {
                "First_Name": "John Updated",
                "Last_Name": "Doe Updated",
                "Company": "Test Company Inc Updated",
                "Email": "john.updated@testcompany.com",
                "Phone": "555-987-6543",
                "Lead_Status": "Contacted"
            }
        ]
    }

    try:
        response = requests.put(url, json=update_data, headers={"Content-Type": "application/json"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Update lead test PASSED")
            return response.json()
        else:
            print("❌ Update lead test FAILED")
            return None

    except Exception as e:
        print(f"❌ Update lead test ERROR: {e}")
        return None

def test_zoho_delete_lead(lead_id):
    """Test deleting a lead in Zoho CRM"""
    print(f"\n=== Testing Zoho Delete Lead (ID: {lead_id}) ===")

    url = f"{BASE_URL}/zoho/{ENTITY_ID}/leads/delete?ids={lead_id}"

    try:
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Delete lead test PASSED")
            return response.json()
        else:
            print("❌ Delete lead test FAILED")
            return None

    except Exception as e:
        print(f"❌ Delete lead test ERROR: {e}")
        return None

def test_zoho_get_leads():
    """Test getting leads from Zoho CRM"""
    print("\n=== Testing Zoho Get Leads ===")

    url = f"{BASE_URL}/zoho/{ENTITY_ID}/leads"

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total leads: {len(data.get('data', []))}")
            print("✅ Get leads test PASSED")
            return data
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("❌ Get leads test FAILED")
            return None

    except Exception as e:
        print(f"❌ Get leads test ERROR: {e}")
        return None

def main():
    """Run all Zoho CRUD tests"""
    print("🚀 Starting Zoho CRM CRUD Tests")
    print("=" * 50)

    # Test 1: Get existing leads first
    leads_data = test_zoho_get_leads()

    # Test 2: Create a new lead
    create_result = test_zoho_create_lead()

    if create_result and create_result.get('data'):
        # Extract the created lead ID
        created_lead = create_result['data'][0]
        lead_id = created_lead.get('details', {}).get('id') or created_lead.get('id')

        if lead_id:
            # Test 3: Update the created lead
            test_zoho_update_lead(lead_id)

            # Test 4: Delete the created lead
            test_zoho_delete_lead(lead_id)
        else:
            print("⚠️  Could not extract lead ID from create response")
    else:
        print("⚠️  Create test failed or no lead ID returned")

    print("\n" + "=" * 50)
    print("🏁 Zoho CRM CRUD Tests Completed")

if __name__ == "__main__":
    main()