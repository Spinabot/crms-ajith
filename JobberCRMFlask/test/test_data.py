#!/usr/bin/env python3
"""
Test script for the data retrieval API.
"""

import requests
import json
import sys
import os

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

def test_get_data_without_auth():
    """Test getting data without authorization."""
    print("Testing data retrieval without authorization...")

    try:
        response = requests.post(f"{BASE_URL}/data/jobber/1")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Should return 401 (unauthorized) since no token is available
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_data_with_invalid_userid():
    """Test getting data with invalid userid."""
    print("\nTesting data retrieval with invalid userid...")

    try:
        response = requests.post(f"{BASE_URL}/data/jobber/999999")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Should return 401 (unauthorized) since no token is available for this user
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_data_with_string_userid():
    """Test getting data with string userid (should fail)."""
    print("\nTesting data retrieval with string userid...")

    try:
        response = requests.post(f"{BASE_URL}/data/jobber/abc")
        print(f"Status: {response.status_code}")

        # Should return 404 (not found) for invalid userid format
        return response.status_code == 404
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting on the data retrieval endpoint."""
    print("\nTesting rate limiting...")

    try:
        # Make multiple requests quickly to trigger rate limiting
        responses = []
        for i in range(6):  # More than the limit of 5
            response = requests.post(f"{BASE_URL}/data/jobber/1")
            responses.append(response.status_code)

        print(f"Response status codes: {responses}")

        # The 6th request should be rate limited (429)
        return 429 in responses
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

def simulate_data_retrieval():
    """Simulate the data retrieval flow."""
    print("\nSimulating data retrieval flow...")
    print("=" * 50)
    print("Step 1: Authorization Required")
    print("First, authorize a user:")
    print(f"{BASE_URL}/auth/jobber?userid=1")
    print()
    print("Step 2: Retrieve Data")
    print("After authorization, retrieve client data:")
    print("curl -X POST http://localhost:5000/data/jobber/1")
    print()
    print("Expected Results:")
    print("- If authorized: Returns client data from Jobber")
    print("- If not authorized: Returns 401 error")
    print()
    print("Note: This endpoint uses pagination to fetch all clients")
    print("and includes rate limiting (3-second sleep every 5 requests)")

def main():
    """Run all data retrieval tests."""
    print("Data Retrieval API Tests")
    print("=" * 40)

    tests = [
        test_application_health,
        test_get_data_without_auth,
        test_get_data_with_invalid_userid,
        test_get_data_with_string_userid,
        test_rate_limiting
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 40)
    print("Data Retrieval Test Results:")
    print(f"Application Health: {'✓' if results[0] else '✗'}")
    print(f"Without Auth: {'✓' if results[1] else '✗'}")
    print(f"Invalid UserID: {'✓' if results[2] else '✗'}")
    print(f"String UserID: {'✓' if results[3] else '✗'}")
    print(f"Rate Limiting: {'✓' if results[4] else '✗'}")

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\n✓ All data retrieval tests passed!")
        print("\nNext steps:")
        simulate_data_retrieval()
    else:
        print("\n✗ Some data retrieval tests failed.")
        print("Check the issues above before proceeding.")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())