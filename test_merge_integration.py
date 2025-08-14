#!/usr/bin/env python3
"""
Test script for Merge CRM integration
"""

import os
import sys
import requests
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_merge_integration():
    """Test Merge CRM integration endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Merge CRM Integration...")
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Create Link Token
    print("1️⃣ Testing Create Link Token...")
    link_token_data = {
        "end_user_email": "owner@example.com",
        "end_user_org_name": "Acme Roofing",
        "end_user_origin_id": "client-1",
        "integration_slug": "hubspot"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/merge/clients/1/link-token",
            json=link_token_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Link token created successfully!")
            print(f"   Link Token: {result.get('link_token', 'N/A')}")
            print(f"   Magic Link URL: {result.get('magic_link_url', 'N/A')}")
            print()
            
            # Store for next test
            link_token = result.get('link_token')
            magic_link_url = result.get('magic_link_url')
            
            if magic_link_url:
                print(f"🌐 Open this URL to complete the Merge Link: {magic_link_url}")
                print("   After completing the link, you'll get an account_token to use in the next test.")
                print()
        else:
            print(f"❌ Failed to create link token: {response.status_code}")
            print(f"   Response: {response.text}")
            print()
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        print()
        return
    
    # Test 2: Save Linked Account (simulated)
    print("2️⃣ Testing Save Linked Account...")
    print("   Note: This requires a real account_token from completing the Merge Link.")
    print("   For testing, you can use a placeholder token.")
    print()
    
    # Test 3: List Contacts
    print("3️⃣ Testing List Contacts...")
    print("   Note: This requires a valid account_token from a linked account.")
    print()
    
    # Test 4: Create Contact
    print("4️⃣ Testing Create Contact...")
    print("   Note: This requires a valid account_token from a linked account.")
    print()
    
    print("📋 Manual Testing Steps:")
    print("1. Set MERGE_API_KEY environment variable")
    print("2. Open the magic_link_url in a browser")
    print("3. Complete the Merge Link process")
    print("4. Get the account_token from Merge dashboard or webhook")
    print("5. Test the remaining endpoints with the real account_token")
    print()
    
    print("🔧 Environment Setup:")
    print("export MERGE_API_KEY='your_production_access_key'")
    print("export MERGE_BASE_URL='https://api.merge.dev'  # optional, defaults to US")
    print()
    
    print("🎯 Ready to test! Complete the Merge Link first to get your account_token.")

if __name__ == "__main__":
    test_merge_integration() 