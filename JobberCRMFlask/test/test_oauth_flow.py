#!/usr/bin/env python3
"""
Test script to simulate and debug the complete OAuth flow.
"""

import requests
import json
import sys
import os
import time

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

def test_authorization_url():
    """Test the authorization URL generation."""
    print("Testing authorization URL generation...")
    try:
        response = requests.get(f"{BASE_URL}/auth/jobber?userid=1", allow_redirects=False)
        print(f"Status: {response.status_code}")

        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"Redirect URL: {redirect_url}")

            # Parse the redirect URL to check parameters
            if 'api.getjobber.com' in redirect_url:
                print("✓ Redirect URL contains Jobber domain")

                # Check for required parameters
                required_params = ['response_type=code', 'client_id=', 'redirect_uri=', 'state=']
                missing_params = []

                for param in required_params:
                    if param not in redirect_url:
                        missing_params.append(param)

                if missing_params:
                    print(f"✗ Missing parameters: {missing_params}")
                    return False
                else:
                    print("✓ All required OAuth parameters present")
                    return True
            else:
                print("✗ Redirect URL does not contain Jobber domain")
                return False
        else:
            print(f"✗ Expected 302 redirect, got {response.status_code}")
            if response.status_code == 400:
                print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_callback_without_code():
    """Test callback endpoint without proper OAuth code."""
    print("\nTesting callback without OAuth code...")
    try:
        response = requests.get(f"{BASE_URL}/auth/callback")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Should return 400 for missing code/state
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_callback_with_invalid_code():
    """Test callback endpoint with invalid OAuth code."""
    print("\nTesting callback with invalid OAuth code...")
    try:
        response = requests.get(f"{BASE_URL}/auth/callback?code=invalid_code&state=1")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Should return 400 or 401 for invalid code
        return response.status_code in [400, 401]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_application_health():
    """Test if the application is running and healthy."""
    print("\nTesting application health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Application is healthy")
            return True
        else:
            print("✗ Application health check failed")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to application: {e}")
        return False

def test_environment_config():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    try:
        from config import Config

        required_vars = ['Remodel_ID', 'Remodel_SECRET']
        missing_vars = []

        for var in required_vars:
            value = getattr(Config, var, None)
            if not value:
                missing_vars.append(var)
            else:
                print(f"✓ {var}: {'*' * len(value)} (length: {len(value)})")

        if missing_vars:
            print(f"✗ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✓ All required environment variables are set")
            return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def simulate_oauth_flow():
    """Simulate the complete OAuth flow."""
    print("\nSimulating OAuth flow...")
    print("=" * 50)
    print("Step 1: Authorization Request")
    print("Visit this URL in your browser:")
    print(f"{BASE_URL}/auth/jobber?userid=1")
    print()
    print("Step 2: Complete Authorization")
    print("1. You'll be redirected to Jobber's authorization page")
    print("2. Log in with your Jobber credentials")
    print("3. Authorize the application")
    print("4. You'll be redirected back to the callback URL")
    print()
    print("Step 3: Check Results")
    print("After completing the OAuth flow, run:")
    print("python test/test_database_debug.py")
    print()
    print("Expected Results:")
    print("- You should see tokens stored in the database")
    print("- The client creation API should work")
    print()
    print("If you see errors:")
    print("1. Check the application logs: docker-compose logs flask_app")
    print("2. Verify your Jobber credentials in .env file")
    print("3. Make sure the redirect URI matches your Jobber app settings")

def main():
    """Run all OAuth flow tests."""
    print("OAuth Flow Debug Tests")
    print("=" * 40)

    tests = [
        test_application_health,
        test_environment_config,
        test_authorization_url,
        test_callback_without_code,
        test_callback_with_invalid_code
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 40)
    print("OAuth Flow Test Results:")
    print(f"Application Health: {'✓' if results[0] else '✗'}")
    print(f"Environment Config: {'✓' if results[1] else '✗'}")
    print(f"Authorization URL: {'✓' if results[2] else '✗'}")
    print(f"Callback (no code): {'✓' if results[3] else '✗'}")
    print(f"Callback (invalid): {'✓' if results[4] else '✗'}")

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\n✓ All OAuth flow tests passed!")
        print("\nNext steps:")
        simulate_oauth_flow()
    else:
        print("\n✗ Some OAuth flow tests failed.")
        print("Check the issues above before proceeding with OAuth.")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())