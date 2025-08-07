#!/usr/bin/env python3
"""
Test script to verify Jobber logging functionality
"""

import logging
from app import app
from services.jobber_service import get_jobber_token, logger

def test_jobber_logging():
    """Test the Jobber logging functionality"""
    with app.app_context():
        print("🔍 Testing Jobber logging functionality...")
        
        # Test token retrieval (should log warning if no token)
        try:
            token = get_jobber_token()
            if token:
                print("✅ Token found in database")
                print(f"   Access token: {token['access_token'][:20]}...")
                print(f"   Expires at: {token['expires_at']}")
            else:
                print("⚠️  No token found (expected if not authenticated)")
        except Exception as e:
            print(f"❌ Error retrieving token: {e}")
        
        print("\n📝 Check 'jobber.log' file for detailed logging information")
        print("🎯 To complete OAuth flow, visit: http://127.0.0.1:5001/api/jobber/auth")

if __name__ == "__main__":
    test_jobber_logging() 