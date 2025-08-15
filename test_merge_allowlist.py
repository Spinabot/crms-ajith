#!/usr/bin/env python3
"""
Test script for Merge CRM Allowlist Validation & Slug Resolution
"""

import os
import sys
import requests
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_merge_allowlist():
    """Test the new allowlist validation and slug resolution system"""
    base_url = "http://localhost:5001"

    print("🧪 Testing Merge CRM Allowlist Validation & Slug Resolution...")
    print(f"Base URL: {base_url}")
    print()

    print("📋 Environment Setup Required:")
    print("export MERGE_PROD_KEY='your_production_access_key'")
    print("export MERGE_ACCOUNT_TOKEN='your_linked_account_token'")
    print("export MERGE_CRM_ALLOWED_SLUGS='accelo,activecampaign,affinity,capsule,close,teamwork_crm,vtiger,zendesk_sell,zoho_crm'")
    print()

    print("🎯 New Allowlist Management Endpoints:")
    print()

    print("# 1. Check allowlist status and validation results")
    print(f"curl '{base_url}/api/merge/crm/allowlist/status'")
    print()

    print("# 2. Get integrations catalog with allowlist status")
    print(f"curl '{base_url}/api/merge/crm/integrations'")
    print()

    print("# 3. Test allowlist enforcement with valid integration")
    print(f"curl -X POST '{base_url}/api/merge/clients/1/linked-accounts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "account_token": "test_token",')
    print('    "integration_slug": "salesforce",')
    print('    "end_user_email": "test@example.com",')
    print('    "end_user_org_name": "Test Org"')
    print("  }'")
    print()

    print("# 4. Test allowlist enforcement with invalid integration")
    print(f"curl -X POST '{base_url}/api/merge/clients/1/linked-accounts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "account_token": "test_token",')
    print('    "integration_slug": "unsupported_crm",')
    print('    "end_user_email": "test@example.com",')
    print('    "end_user_org_name": "Test Org"')
    print("  }'")
    print()

    print("🎯 Allowlist Validation Examples:")
    print()

    print("# Check status with different allowlist configurations")
    allowlist_examples = [
        "salesforce,pipedrive,zoho_crm",
        "accelo,activecampaign,affinity,capsule,close,teamwork_crm,vtiger,zendesk_sell,zoho_crm",
        "invalid_vendor,another_invalid"
    ]
    
    for i, allowlist in enumerate(allowlist_examples, 1):
        print(f"# Example {i}: {allowlist}")
        print(f"export MERGE_CRM_ALLOWED_SLUGS='{allowlist}'")
        print(f"curl '{base_url}/api/merge/crm/allowlist/status'")
        print()

    print("🎯 Complete Workflow Example:")
    print()

    print("# Step 1: Set your allowlist")
    print("export MERGE_CRM_ALLOWED_SLUGS='accelo,activecampaign,affinity,capsule,close,teamwork_crm,vtiger,zendesk_sell,zoho_crm'")
    print()

    print("# Step 2: Check allowlist validation")
    print(f"curl '{base_url}/api/merge/crm/allowlist/status'")
    print()

    print("# Step 3: See integrations with allowlist status")
    print(f"curl '{base_url}/api/merge/crm/integrations'")
    print()

    print("# Step 4: Try to link an allowed integration")
    print(f"curl -X POST '{base_url}/api/merge/clients/1/linked-accounts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "account_token": "YOUR_TOKEN",')
    print('    "integration_slug": "salesforce",')
    print('    "end_user_email": "user@example.com",')
    print('    "end_user_org_name": "Example Corp"')
    print("  }'")
    print()

    print("🎯 Troubleshooting:")
    print()

    print("# If you get unresolved vendors, check the exact slugs:")
    print(f"curl '{base_url}/api/merge/crm/allowlist/status' | jq '.allowlist_status.unresolved_names'")
    print()

    print("# Compare with available integrations:")
    print(f"curl '{base_url}/api/merge/crm/integrations' | jq '.data[] | {name: .name, slug: .slug}'")
    print()

    print("🎯 Ready to test! Set your environment variables and start testing.")
    print()
    print("💡 Tips:")
    print("- Start with /allowlist/status to see validation results")
    print("- Use /integrations to see which vendors are in your allowlist")
    print("- The system automatically resolves vendor names to slugs")
    print("- Unresolved vendors will be listed for manual correction")
    print("- Allowlist enforcement happens at linked account creation")

if __name__ == "__main__":
    test_merge_allowlist() 