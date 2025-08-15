#!/usr/bin/env python3
"""
Test script for Merge Unified API (New Implementation)
"""

import os
import sys
import requests
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_merge_unified_api():
    """Test Merge Unified API endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Merge Unified API (New Implementation)...")
    print(f"Base URL: {base_url}")
    print()
    
    print("📋 Environment Setup Required:")
    print("export MERGE_PROD_KEY='your_production_access_key'")
    print("export MERGE_ACCOUNT_TOKEN='your_linked_account_token'")
    print()
    
    print("🎯 CRM Endpoints Test Commands:")
    print()
    
    print("# Accounts")
    print(f"curl '{base_url}/api/merge/crm/accounts'")
    print(f"curl -X POST '{base_url}/api/merge/crm/accounts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"name\": \"Acme Corp\", \"description\": \"Test company\"}'")
    print()
    
    print("# Contacts")
    print(f"curl '{base_url}/api/merge/crm/contacts'")
    print(f"curl -X POST '{base_url}/api/merge/crm/contacts' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"first_name\": \"Ada\", \"last_name\": \"Lovelace\", \"email_addresses\": [{\"email_address\": \"ada@example.com\"}]}'")
    print()
    
    print("# Leads")
    print(f"curl '{base_url}/api/merge/crm/leads'")
    print(f"curl -X POST '{base_url}/api/merge/crm/leads' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"first_name\": \"John\", \"last_name\": \"Doe\", \"company\": \"Test Corp\"}'")
    print()
    
    print("# Opportunities")
    print(f"curl '{base_url}/api/merge/crm/opportunities'")
    print(f"curl -X POST '{base_url}/api/merge/crm/opportunities' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"name\": \"New Deal\", \"amount\": 50000, \"stage\": \"Qualified\"}'")
    print()
    
    print("# Tasks")
    print(f"curl '{base_url}/api/merge/crm/tasks'")
    print(f"curl -X POST '{base_url}/api/merge/crm/tasks' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"subject\": \"Follow up call\", \"due_date\": \"2025-08-25T17:00:00Z\"}'")
    print()
    
    print("# Notes")
    print(f"curl '{base_url}/api/merge/crm/notes'")
    print(f"curl -X POST '{base_url}/api/merge/crm/notes' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"content\": \"Customer interested in premium plan\", \"content_type\": \"text\"}'")
    print()
    
    print("# Engagements")
    print(f"curl '{base_url}/api/merge/crm/engagements'")
    print(f"curl -X POST '{base_url}/api/merge/crm/engagements' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"subject\": \"Sales call\", \"content\": \"Discussed pricing options\"}'")
    print()
    
    print("# Users")
    print(f"curl '{base_url}/api/merge/crm/users'")
    print()
    
    print("# Passthrough (for DELETE operations)")
    print(f"curl -X POST '{base_url}/api/merge/crm/passthrough' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "method": "DELETE",')
    print('    "path": "/crm/v3/objects/contacts/12345",')
    print('    "request_format": "JSON",')
    print('    "data": {"archived": true}')
    print("  }'")
    print()
    
    print("🎯 HRIS Endpoints Test Commands:")
    print()
    
    print("# Employees")
    print(f"curl '{base_url}/api/merge/hris/employees'")
    print()
    
    print("# Time Off")
    print(f"curl '{base_url}/api/merge/hris/time-off'")
    print(f"curl -X POST '{base_url}/api/merge/hris/time-off' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",')
    print('    "amount": 8,')
    print('    "units": "HOURS",')
    print('    "request_type": "VACATION",')
    print('    "start_time": "2025-08-20T09:00:00Z",')
    print('    "end_time": "2025-08-20T17:00:00Z",')
    print('    "status": "REQUESTED"')
    print("  }'")
    print()
    
    print("# Timesheet Entries")
    print(f"curl '{base_url}/api/merge/hris/timesheet-entries'")
    print(f"curl -X POST '{base_url}/api/merge/hris/timesheet-entries' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",')
    print('    "hours_worked": 4,')
    print('    "start_time": "2025-08-20T09:00:00Z",')
    print('    "end_time": "2025-08-20T13:00:00Z"')
    print("  }'")
    print()
    
    print("# Companies, Groups, Locations")
    print(f"curl '{base_url}/api/merge/hris/companies'")
    print(f"curl '{base_url}/api/merge/hris/groups'")
    print(f"curl '{base_url}/api/merge/hris/locations'")
    print()
    
    print("# HRIS Passthrough")
    print(f"curl -X POST '{base_url}/api/merge/hris/passthrough' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "method": "PATCH",')
    print('    "path": "/employees/12345",')
    print('    "data": {"work_email": "new@ex.com"},')
    print('    "request_format": "JSON"')
    print("  }'")
    print()
    
    print("🔧 Key Features:")
    print("✅ Full CRUD operations on supported models")
    print("✅ Ignore endpoints for soft deletion")
    print("✅ Passthrough for vendor-specific operations")
    print("✅ Delete linked account endpoints")
    print("✅ Unified error handling")
    print("✅ Automatic header management")
    print()
    
    print("💡 Pro Tips:")
    print("• Use /meta endpoints to see available fields: /contacts/meta/post, /time-off/meta/post")
    print("• Set run_async=true for long-running operations")
    print("• Use passthrough for DELETE operations not supported by unified API")
    print("• Check Merge docs for field support by integration")
    print()
    
    print("🎯 Ready to test! Set your environment variables and start testing.")

if __name__ == "__main__":
    test_merge_unified_api() 