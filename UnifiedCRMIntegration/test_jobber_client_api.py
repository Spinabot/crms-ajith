#!/usr/bin/env python3
"""
Test script for Jobber client data API
"""
import requests
import json
import sys

def test_jobber_client_api():
    """Test the Jobber client data API endpoints"""

    base_url = "http://localhost:5000"
    user_id = "123"  # Use the same user ID you used for authentication

    print("Testing Jobber Client Data API")
    print("=" * 50)

    # Test 1: Check authentication status
    print("\n1. Testing authentication status...")
    try:
        response = requests.get(f"{base_url}/auth/jobber/status/{user_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            auth_data = response.json()
            if auth_data.get('hasValidToken'):
                print("✓ User is authenticated")
            else:
                print("✗ User token is expired or invalid")
                return False
        else:
            print("✗ User is not authenticated")
            return False

    except Exception as e:
        print(f"✗ Error checking authentication: {e}")
        return False

    # Test 2: Get client data (raw Jobber format)
    print("\n2. Testing client data retrieval...")
    try:
        response = requests.get(f"{base_url}/api/jobber/clients/{user_id}")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Client data retrieved successfully")
            print(f"  - Count: {data.get('count', 0)} clients")
            print(f"  - Message: {data.get('message', '')}")

            # Show first client if available
            if data.get('data') and len(data['data']) > 0:
                first_client = data['data'][0]
                print(f"  - First client: {first_client.get('firstName', '')} {first_client.get('lastName', '')}")
                print(f"  - Client ID: {first_client.get('id', '')}")
                print(f"  - Is Lead: {first_client.get('isLead', False)}")
        else:
            print(f"✗ Failed to get client data: {response.json()}")
            return False

    except Exception as e:
        print(f"✗ Error getting client data: {e}")
        return False

    # Test 3: Get leads (unified format)
    print("\n3. Testing leads retrieval (unified format)...")
    try:
        response = requests.get(f"{base_url}/api/jobber/leads?user_id={user_id}")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Leads retrieved successfully")
            print(f"  - Count: {data.get('count', 0)} leads")
            print(f"  - Message: {data.get('message', '')}")

            # Show first lead if available
            if data.get('leads') and len(data['leads']) > 0:
                first_lead = data['leads'][0]
                print(f"  - First lead: {first_lead.get('firstName', '')} {first_lead.get('lastName', '')}")
                print(f"  - Email: {first_lead.get('email', '')}")
                print(f"  - Phone: {first_lead.get('mobilePhone', '')}")
                print(f"  - CRM System: {first_lead.get('crmSystem', '')}")
        else:
            print(f"✗ Failed to get leads: {response.json()}")
            return False

    except Exception as e:
        print(f"✗ Error getting leads: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 All tests passed! Jobber client data API is working correctly.")
    return True

def test_error_scenarios():
    """Test error scenarios"""

    base_url = "http://localhost:5000"

    print("\nTesting Error Scenarios")
    print("=" * 50)

    # Test 1: Unauthenticated user
    print("\n1. Testing unauthenticated user...")
    try:
        response = requests.get(f"{base_url}/api/jobber/clients/999")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 401:
            print("✓ Correctly rejected unauthenticated user")
        else:
            print("✗ Should have rejected unauthenticated user")

    except Exception as e:
        print(f"✗ Error testing unauthenticated user: {e}")

    # Test 2: Missing user_id parameter
    print("\n2. Testing missing user_id parameter...")
    try:
        response = requests.get(f"{base_url}/api/jobber/leads")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 400:
            print("✓ Correctly rejected missing user_id parameter")
        else:
            print("✗ Should have rejected missing user_id parameter")

    except Exception as e:
        print(f"✗ Error testing missing parameter: {e}")

if __name__ == "__main__":
    print("Jobber Client Data API Test")
    print("=" * 50)

    # Test main functionality
    success = test_jobber_client_api()

    if success:
        # Test error scenarios
        test_error_scenarios()
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Please check your setup.")
        sys.exit(1)