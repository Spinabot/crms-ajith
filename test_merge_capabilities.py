#!/usr/bin/env python3
"""
Test script for Merge CRM Capabilities Discovery & Meta-Driven Writes
"""

import os
import sys
import requests
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_merge_capabilities():
    """Test the new CRM capabilities discovery and meta-driven writes"""
    base_url = "http://localhost:5001"

    print("🧪 Testing Merge CRM Capabilities Discovery & Meta-Driven Writes...")
    print(f"Base URL: {base_url}")
    print()

    print("📋 Environment Setup Required:")
    print("export MERGE_PROD_KEY='your_production_access_key'")
    print("export MERGE_ACCOUNT_TOKEN='your_linked_account_token'")
    print("export MERGE_CRM_ALLOWED_SLUGS='salesforce,pipedrive,zoho_crm'")
    print()

    print("🎯 New Capabilities Discovery Endpoints:")
    print()

    print("# 1. List all available integrations (names, slugs, logos)")
    print(f"curl '{base_url}/api/merge/crm/integrations'")
    print()

    print("# 2. List linked accounts & their capabilities")
    print(f"curl '{base_url}/api/merge/crm/capabilities'")
    print()

    print("# 3. Get writable fields for creating a new contact")
    print(f"curl '{base_url}/api/merge/crm/meta/contacts/post?account_token=YOUR_TOKEN'")
    print()

    print("# 4. Get writable fields for updating an existing contact")
    print(f"curl '{base_url}/api/merge/crm/meta/contacts/CONTACT_ID/patch?account_token=YOUR_TOKEN'")
    print()

    print("🎯 Meta-Driven Contact Creation (with validation):")
    print()

    print("# Create contact with meta validation")
    print(f"curl -X POST '{base_url}/api/merge/clients/1/crm/contacts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "account_token": "YOUR_TOKEN",')
    print('    "contact": {')
    print('      "first_name": "Ada",')
    print('      "last_name": "Lovelace",')
    print('      "email_addresses": [{"email_address": "ada@example.com"}]')
    print('    }')
    print("  }'")
    print()

    print("🎯 Allowlist Enforcement:")
    print()

    print("# Try to save a linked account with non-allowed integration")
    print(f"curl -X POST '{base_url}/api/merge/clients/1/linked-accounts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "account_token": "test_token",')
    print('    "integration_slug": "unsupported_crm",')
    print('    "end_user_email": "test@example.com",')
    print('    "end_user_org_name": "Test Org"')
    print("  }'")
    print()

    print("🎯 Meta Validation Examples:")
    print()

    print("# Get meta for different CRM models")
    models = ["accounts", "contacts", "leads", "opportunities", "tasks", "notes", "engagements"]
    for model in models:
        print(f"curl '{base_url}/api/merge/crm/meta/{model}/post?account_token=YOUR_TOKEN'")
    print()

    print("🎯 Complete Workflow Example:")
    print()

    print("# Step 1: Check what integrations are available")
    print(f"curl '{base_url}/api/merge/crm/integrations'")
    print()

    print("# Step 2: Check what's currently linked")
    print(f"curl '{base_url}/api/merge/crm/capabilities'")
    print()

    print("# Step 3: Get writable fields for contacts")
    print(f"curl '{base_url}/api/merge/crm/meta/contacts/post?account_token=YOUR_TOKEN'")
    print()

    print("# Step 4: Create contact using only supported fields")
    print(f"curl -X POST '{base_url}/api/merge/clients/1/crm/contacts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "account_token": "YOUR_TOKEN",')
    print('    "contact": {')
    print('      "first_name": "John",')
    print('      "last_name": "Doe",')
    print('      "email_addresses": [{"email_address": "john@example.com"}]')
    print('    }')
    print("  }'")
    print()

    print("🎯 Error Handling Examples:")
    print()

    print("# Missing account_token")
    print(f"curl '{base_url}/api/merge/crm/meta/contacts/post'")
    print()

    print("# Invalid model")
    print(f"curl '{base_url}/api/merge/crm/meta/invalid_model/post?account_token=YOUR_TOKEN'")
    print()

    print("🎯 Ready to test! Set your environment variables and start testing.")
    print()
    print("💡 Tips:")
    print("- Start with /integrations to see available CRMs")
    print("- Use /capabilities to see what's currently linked")
    print("- Always call /meta before POST/PATCH to validate fields")
    print("- The allowlist prevents unauthorized integrations")
    print("- Meta validation ensures you only send supported fields")

if __name__ == "__main__":
    test_merge_capabilities() 