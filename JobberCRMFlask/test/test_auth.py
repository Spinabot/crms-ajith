#!/usr/bin/env python3
"""
Simple test script to verify the Jobber OAuth authentication endpoints.
"""

import requests
import json
import sys
import os

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

def test_auth_endpoint():
    """Test the authorization endpoint (will redirect to Jobber)."""
    print("\nTesting authorization endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/auth/jobber?userid=123", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Redirect URL: {response.headers.get('Location', 'No redirect')}")
        return response.status_code == 302
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_auth_endpoint_missing_userid():
    """Test the authorization endpoint without userid parameter."""
    print("\nTesting authorization endpoint without userid...")
    try:
        response = requests.get(f"{BASE_URL}/auth/jobber", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Flask Jobber CRM Application")
    print("=" * 40)

    tests = [
        test_health_endpoint,
        test_hello_endpoint,
        test_auth_endpoint,
        test_auth_endpoint_missing_userid
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Health Endpoint: {'✓' if results[0] else '✗'}")
    print(f"Hello Endpoint: {'✓' if results[1] else '✗'}")
    print(f"Auth Endpoint: {'✓' if results[2] else '✗'}")
    print(f"Auth Endpoint (no userid): {'✓' if results[3] else '✗'}")

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\nAll tests passed! The application is running correctly.")
    else:
        print("\nSome tests failed. Check the application logs.")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())