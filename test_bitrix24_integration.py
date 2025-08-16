#!/usr/bin/env python3
"""
Test script for Bitrix24 CRM integration.
Run this to test the endpoints with your actual Bitrix24 credentials.
"""

import os
import requests
import json

# Configuration - update these with your actual values
BASE_URL = "http://localhost:5001"  # Your Flask app URL
CLIENT_ID = 1  # Your internal client ID in the database

# Bitrix24 credentials from your environment
BITRIX_WEBHOOK_BASE = os.getenv("BITRIX_WEBHOOK_BASE", "https://b24-k7mbrm.bitrix24.com/rest/1/bn97b3lpvwpp7dxw/")
BITRIX_OUTBOUND_TOKEN = os.getenv("BITRIX_OUTBOUND_TOKEN", "mkv9w4dxxvbao7gaemm0y7eay4uctbme")

def test_bitrix24_integration():
    """Test all Bitrix24 endpoints"""
    
    print("🚀 Testing Bitrix24 CRM Integration")
    print("=" * 50)
    
    # Test 1: Save configuration
    print("\n1. Testing configuration save...")
    config_data = {
        "webhook_base": BITRIX_WEBHOOK_BASE,
        "outbound_token": BITRIX_OUTBOUND_TOKEN
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/bitrix/clients/{CLIENT_ID}/config",
            json=config_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Configuration saved successfully")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Debug configuration
    print("\n2. Testing configuration debug...")
    try:
        response = requests.get(f"{BASE_URL}/api/bitrix/clients/{CLIENT_ID}/config/debug")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Config debug: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Create a contact
    print("\n3. Testing contact creation...")
    contact_data = {
        "fields": {
            "NAME": "Ada",
            "LAST_NAME": "Lovelace",
            "PHONE": [{"VALUE": "+15551234567", "VALUE_TYPE": "WORK"}],
            "EMAIL": [{"VALUE": "ada@example.com", "VALUE_TYPE": "WORK"}]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/bitrix/clients/{CLIENT_ID}/contacts",
            json=contact_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Contact created: {json.dumps(data, indent=2)}")
            contact_id = data.get("result", {}).get("id")
        else:
            print(f"   ❌ Error: {response.text}")
            contact_id = None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        contact_id = None
    
    # Test 4: List contacts
    print("\n4. Testing contact listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/bitrix/clients/{CLIENT_ID}/contacts")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Contacts listed: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Create a deal
    print("\n5. Testing deal creation...")
    deal_data = {
        "fields": {
            "TITLE": "Test Deal",
            "STAGE_ID": "NEW",
            "CURRENCY_ID": "USD",
            "OPPORTUNITY": 1000.00
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/bitrix/clients/{CLIENT_ID}/deals",
            json=deal_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Deal created: {json.dumps(data, indent=2)}")
            deal_id = data.get("result", {}).get("id")
        else:
            print(f"   ❌ Error: {response.text}")
            deal_id = None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        deal_id = None
    
    # Test 6: List deals
    print("\n6. Testing deal listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/bitrix/clients/{CLIENT_ID}/deals")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Deals listed: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    print("\n📋 Sample cURL commands you can run:")
    print(f"\n# Save configuration:")
    print(f'curl -X POST {BASE_URL}/api/bitrix/clients/{CLIENT_ID}/config \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"webhook_base": "{BITRIX_WEBHOOK_BASE}", "outbound_token": "{BITRIX_OUTBOUND_TOKEN}"}}\'')
    
    print(f"\n# Create contact:")
    print(f'curl -X POST {BASE_URL}/api/bitrix/clients/{CLIENT_ID}/contacts \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"fields": {{"NAME": "Ada", "LAST_NAME": "Lovelace"}}}}\'')
    
    print(f"\n# List contacts:")
    print(f'curl "{BASE_URL}/api/bitrix/clients/{CLIENT_ID}/contacts"')
    
    print(f"\n# Create deal:")
    print(f'curl -X POST {BASE_URL}/api/bitrix/clients/{CLIENT_ID}/deals \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"fields": {{"TITLE": "Test Deal", "STAGE_ID": "NEW"}}}}\'')

if __name__ == "__main__":
    test_bitrix24_integration() 