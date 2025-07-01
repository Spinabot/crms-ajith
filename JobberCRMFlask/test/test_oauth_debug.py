#!/usr/bin/env python3
"""
Debug script to help troubleshoot OAuth flow issues.
"""

import requests
import json
import sys
import os

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

def test_authorization_url():
    """Test the authorization URL generation."""
    print("Testing authorization URL generation...")
    try:
        response = requests.get(f"{BASE_URL}/auth/jobber?userid=123", allow_redirects=False)
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

def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")
    try:
        from utils.db_conn import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # Test a simple query
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result and result[0] == 1:
            print("✓ Database connection successful")
            return True
        else:
            print("✗ Database query failed")
            return False
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    """Run all debug tests."""
    print("OAuth Flow Debug Tests")
    print("=" * 40)

    tests = [
        test_application_health,
        test_environment_config,
        test_database_connection,
        test_authorization_url
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 40)
    print("Debug Test Results:")
    print(f"Application Health: {'✓' if results[0] else '✗'}")
    print(f"Environment Config: {'✓' if results[1] else '✗'}")
    print(f"Database Connection: {'✓' if results[2] else '✗'}")
    print(f"Authorization URL: {'✓' if results[3] else '✗'}")

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\nAll tests passed! The OAuth flow should work correctly.")
        print("\nTo test the full OAuth flow:")
        print("1. Visit: http://localhost:5000/auth/jobber?userid=123")
        print("2. Complete the Jobber authorization")
        print("3. Check the callback response")
    else:
        print("\nSome tests failed. Check the issues above.")
        if not results[0]:
            print("- Make sure the application is running: docker-compose up --build")
        if not results[1]:
            print("- Check your .env file has Remodel_ID and Remodel_SECRET")
        if not results[2]:
            print("- Make sure PostgreSQL is running and accessible")
        if not results[3]:
            print("- Check the authorization endpoint logs for errors")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())