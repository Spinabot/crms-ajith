#!/usr/bin/env python3
"""
Test script for the client creation API.
"""

import requests
import json
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from app import app

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestClientCreate:
    def test_create_client_success(self, client):
        """Test successful client creation."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "clientCreate": {
                        "client": {
                            "id": "test_id",
                            "firstName": "John",
                            "lastName": "Doe"
                        },
                        "userErrors": []
                    }
                }
            }
            mock_post.return_value = mock_response

            # Test data
            test_data = {
                "firstName": "John",
                "lastName": "Doe",
                "companyName": "Test Company"
            }

            response = client.post('/client/create/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "data" in data

    def test_create_client_no_token(self, client):
        """Test client creation with no available token."""
        with patch('client.routes.get_token') as mock_get_token:
            mock_get_token.return_value = None

            test_data = {"firstName": "John", "lastName": "Doe"}

            response = client.post('/client/create/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "No token available" in data["error"]

    def test_create_client_invalid_data(self, client):
        """Test client creation with invalid data."""
        with patch('client.routes.get_token') as mock_get_token:
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Missing required fields
            test_data = {}

            response = client.post('/client/create/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 200  # Schema allows None values

class TestClientUpdate:
    def test_update_client_success(self, client):
        """Test successful client update."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "clientEdit": {
                        "client": {
                            "id": "test_id",
                            "firstName": "John",
                            "lastName": "Smith"
                        },
                        "userErrors": []
                    }
                }
            }
            mock_post.return_value = mock_response

            # Test data
            test_data = {
                "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA=",
                "firstName": "John",
                "lastName": "Smith"
            }

            response = client.post('/client/update/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "data" in data

    def test_update_client_no_token(self, client):
        """Test client update with no available token."""
        with patch('client.routes.get_token') as mock_get_token:
            mock_get_token.return_value = None

            test_data = {
                "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA=",
                "firstName": "John"
            }

            response = client.post('/client/update/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "No token available" in data["error"]

    def test_update_client_missing_client_id(self, client):
        """Test client update with missing client ID."""
        with patch('client.routes.get_token') as mock_get_token:
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Missing required clientId
            test_data = {
                "firstName": "John",
                "lastName": "Smith"
            }

            response = client.post('/client/update/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "Validation error" in data["error"]

    def test_update_client_user_errors(self, client):
        """Test client update with user errors from Jobber."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response with user errors
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "clientEdit": {
                        "client": None,
                        "userErrors": [
                            {
                                "message": "Client not found",
                                "path": ["clientId"]
                            }
                        ]
                    }
                }
            }
            mock_post.return_value = mock_response

            test_data = {
                "clientId": "invalid_id",
                "firstName": "John"
            }

            response = client.post('/client/update/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "Client update failed" in data["error"]
            assert "userErrors" in data

    def test_update_client_graphql_errors(self, client):
        """Test client update with GraphQL errors."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response with GraphQL errors
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "errors": [
                    {
                        "message": "GraphQL error",
                        "locations": [{"line": 1, "column": 1}]
                    }
                ]
            }
            mock_post.return_value = mock_response

            test_data = {
                "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA=",
                "firstName": "John"
            }

            response = client.post('/client/update/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "GraphQL errors" in data["error"]

    def test_update_client_complex_data(self, client):
        """Test client update with complex data including emails and phones."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "clientEdit": {
                        "client": {
                            "id": "test_id",
                            "firstName": "John",
                            "lastName": "Smith",
                            "emails": [{"id": "email1", "address": "john@example.com"}],
                            "phones": [{"id": "phone1", "number": "+1234567890"}]
                        },
                        "userErrors": []
                    }
                }
            }
            mock_post.return_value = mock_response

            # Test complex data
            test_data = {
                "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA=",
                "firstName": "John",
                "lastName": "Smith",
                "emailsToAdd": [
                    {"address": "john@example.com", "description": "Primary"}
                ],
                "phonesToAdd": [
                    {"number": "+1234567890", "description": "Mobile"}
                ],
                "billingAddress": {
                    "city": "New York",
                    "country": "US",
                    "postalCode": "10001"
                }
            }

            response = client.post('/client/update/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "data" in data

class TestClientArchive:
    def test_archive_client_success(self, client):
        """Test successful client archive."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "clientArchive": {
                        "client": {
                            "id": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA=",
                            "firstName": "Allen",
                            "lastName": "Works",
                            "companyName": "WonderTech Inc"
                        },
                        "userErrors": []
                    }
                }
            }
            mock_post.return_value = mock_response

            # Test data
            test_data = {
                "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA="
            }

            response = client.post('/client/archive/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "data" in data
            assert "clientArchive" in data["data"]

    def test_archive_client_no_token(self, client):
        """Test client archive with no available token."""
        with patch('client.routes.get_token') as mock_get_token:
            mock_get_token.return_value = None

            test_data = {
                "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA="
            }

            response = client.post('/client/archive/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "No token available" in data["error"]

    def test_archive_client_missing_client_id(self, client):
        """Test client archive with missing client ID."""
        with patch('client.routes.get_token') as mock_get_token:
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Missing required clientId
            test_data = {}

            response = client.post('/client/archive/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "Validation error" in data["error"]

    def test_archive_client_user_errors(self, client):
        """Test client archive with user errors from Jobber."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response with user errors
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "clientArchive": {
                        "client": None,
                        "userErrors": [
                            {
                                "message": "Client not found",
                                "path": ["clientId"]
                            }
                        ]
                    }
                }
            }
            mock_post.return_value = mock_response

            test_data = {
                "clientId": "invalid_id"
            }

            response = client.post('/client/archive/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "Client archive failed" in data["error"]
            assert "userErrors" in data

    def test_archive_client_graphql_errors(self, client):
        """Test client archive with GraphQL errors."""
        with patch('client.routes.get_token') as mock_get_token, \
             patch('client.routes.requests.post') as mock_post:

            # Mock token response
            mock_get_token.return_value = [{"access_token": "test_token"}]

            # Mock Jobber API response with GraphQL errors
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "errors": [
                    {
                        "message": "GraphQL error",
                        "locations": [{"line": 1, "column": 1}]
                    }
                ]
            }
            mock_post.return_value = mock_response

            test_data = {
                "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA="
            }

            response = client.post('/client/archive/1',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "GraphQL errors" in data["error"]

def test_create_client_without_auth():
    """Test creating a client without authorization."""
    response = requests.post(f"{BASE_URL}/client/create/123",
                           json={"firstName": "Test", "lastName": "User"})
    assert response.status_code == 401

def test_update_client_without_auth():
    """Test updating a client without authorization."""
    response = requests.post(f"{BASE_URL}/client/update/123",
                           json={"clientId": "test_id", "firstName": "Test"})
    assert response.status_code == 401

def test_archive_client_without_auth():
    """Test archiving a client without authorization."""
    response = requests.post(f"{BASE_URL}/client/archive/123",
                           json={"clientId": "test_id"})
    assert response.status_code == 401

def test_create_client_invalid_data():
    """Test creating a client with invalid data."""
    print("\nTesting client creation with invalid data...")

    invalid_data = {
        "invalidField": "invalid value"
    }

    try:
        response = requests.post(f"{BASE_URL}/client/create/123", json=invalid_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Should return 400 (bad request) for invalid data
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_client_missing_data():
    """Test creating a client with missing JSON data."""
    print("\nTesting client creation with missing data...")

    try:
        response = requests.post(f"{BASE_URL}/client/create/123")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Should return 400 (bad request) for missing data
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_client_valid_data():
    """Test creating a client with valid data (will fail due to no auth)."""
    print("\nTesting client creation with valid data...")

    valid_data = {
        "firstName": "Jane",
        "lastName": "Smith",
        "companyName": "Smith Corp",
        "emails": [{"address": "jane@smithcorp.com", "primary": True}],
        "phones": [{"number": "555-5678", "primary": True}],
        "billingAddress": {
            "street1": "123 Main St",
            "city": "Anytown",
            "province": "CA",
            "country": "US",
            "postalCode": "12345"
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/client/create/123", json=valid_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Should return 401 (unauthorized) since no token is available
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting on the client creation endpoint."""
    print("\nTesting rate limiting...")

    test_data = {"firstName": "Test"}

    try:
        # Make multiple requests quickly to trigger rate limiting
        responses = []
        for i in range(6):  # More than the limit of 5
            response = requests.post(f"{BASE_URL}/client/create/123", json=test_data)
            responses.append(response.status_code)

        print(f"Response status codes: {responses}")

        # The 6th request should be rate limited (429)
        return 429 in responses
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all client tests."""
    print("Testing Client Creation API")
    print("=" * 40)

    tests = [
        test_create_client_without_auth,
        test_create_client_invalid_data,
        test_create_client_missing_data,
        test_create_client_valid_data,
        test_rate_limiting
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 40)
    print("Client Test Results:")
    print(f"Without Auth: {'✓' if results[0] else '✗'}")
    print(f"Invalid Data: {'✓' if results[1] else '✗'}")
    print(f"Missing Data: {'✓' if results[2] else '✗'}")
    print(f"Valid Data: {'✓' if results[3] else '✗'}")
    print(f"Rate Limiting: {'✓' if results[4] else '✗'}")

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\nAll client tests passed!")
        print("\nNote: These tests expect 401 errors because no authorization token is available.")
        print("To test successful client creation, you need to:")
        print("1. First authorize a user: http://localhost:5000/auth/jobber?userid=123")
        print("2. Then create a client with the same userid")
    else:
        print("\nSome client tests failed.")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())