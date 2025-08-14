#!/usr/bin/env python3
"""
Test script for Merge HRIS integration
"""

import os
import sys
import requests
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_merge_hris_integration():
    """Test Merge HRIS integration endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Merge HRIS Integration...")
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: List Employees
    print("1️⃣ Testing List Employees...")
    print("   Note: This requires a valid account_token from a linked HRIS account.")
    print()
    
    # Test 2: List Employments
    print("2️⃣ Testing List Employments...")
    print("   Note: This requires a valid account_token from a linked HRIS account.")
    print()
    
    # Test 3: List Locations
    print("3️⃣ Testing List Locations...")
    print("   Note: This requires a valid account_token from a linked HRIS account.")
    print()
    
    # Test 4: List Groups
    print("4️⃣ Testing List Groups...")
    print("   Note: This requires a valid account_token from a linked HRIS account.")
    print()
    
    # Test 5: Time Off Operations
    print("5️⃣ Testing Time Off Operations...")
    print("   Note: This requires a valid account_token from a linked HRIS account.")
    print()
    
    # Test 6: Timesheet Entries
    print("6️⃣ Testing Timesheet Entries...")
    print("   Note: This requires a valid account_token from a linked HRIS account.")
    print()
    
    # Test 7: Passthrough
    print("7️⃣ Testing Passthrough...")
    print("   Note: This requires a valid account_token from a linked HRIS account.")
    print()
    
    print("📋 Manual Testing Steps:")
    print("1. Set MERGE_API_KEY environment variable")
    print("2. Complete Merge Link for HRIS (not just CRM)")
    print("3. Get the account_token from Merge dashboard or webhook")
    print("4. Test the HRIS endpoints with the real account_token")
    print()
    
    print("🔧 Environment Setup:")
    print("export MERGE_API_KEY='your_production_access_key'")
    print("export MERGE_BASE_URL='https://api.merge.dev'  # optional, defaults to US")
    print()
    
    print("🎯 Quick Test Commands:")
    print()
    
    print("# List employees")
    print(f"curl '{base_url}/api/merge/hris/clients/1/employees?page_size=25'")
    print()
    
    print("# Create time off")
    print(f"curl -X POST '{base_url}/api/merge/hris/clients/1/time-off' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "model": {')
    print('      "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",')
    print('      "request_type": "VACATION",')
    print('      "units": "DAYS",')
    print('      "amount": 1,')
    print('      "start_time": "2025-08-20T09:00:00Z",')
    print('      "end_time": "2025-08-20T17:00:00Z"')
    print('    }')
    print("  }'")
    print()
    
    print("# Create timesheet entry")
    print(f"curl -X POST '{base_url}/api/merge/hris/clients/1/timesheet-entries' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "model": {')
    print('      "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",')
    print('      "hours_worked": 8,')
    print('      "start_time": "2025-08-13T09:00:00Z",')
    print('      "end_time": "2025-08-13T17:00:00Z"')
    print('    }')
    print("  }'")
    print()
    
    print("# Passthrough example (PATCH employee)")
    print(f"curl -X POST '{base_url}/api/merge/hris/clients/1/passthrough' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "method": "PATCH",')
    print('    "path": "/employees/123",')
    print('    "data": {"first_name": "Jane"},')
    print('    "request_format": "JSON"')
    print("  }'")
    print()
    
    print("🎯 Ready to test! Complete the Merge Link for HRIS first to get your account_token.")
    print()
    print("💡 Note: HRIS integration requires linking to HRIS systems (BambooHR, Personio, etc.)")
    print("   not just CRM systems. Use the same Merge Link flow but select HRIS category.")

if __name__ == "__main__":
    test_merge_hris_integration() 