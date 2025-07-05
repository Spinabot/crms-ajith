#!/usr/bin/env python3
"""
Test script to verify HubSpot CRM API connectivity
"""
import requests
import time
import sys

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint is working!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

def test_swagger_endpoint():
    """Test the Swagger documentation endpoint"""
    try:
        response = requests.get('http://localhost:5000/swagger', timeout=5)
        if response.status_code == 200:
            print("✅ Swagger documentation is accessible!")
            return True
        else:
            print(f"❌ Swagger endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Swagger on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing Swagger endpoint: {e}")
        return False

def main():
    print("Testing HubSpot CRM API connectivity...")
    print("=" * 50)

    # Wait a bit for the app to start
    print("Waiting for application to start...")
    time.sleep(5)

    health_ok = test_health_endpoint()
    swagger_ok = test_swagger_endpoint()

    print("=" * 50)
    if health_ok and swagger_ok:
        print("🎉 All tests passed! The application is running correctly.")
        print("\nYou can now access:")
        print("- API: http://localhost:5000")
        print("- Swagger Docs: http://localhost:5000/swagger")
        print("- pgAdmin (dev): http://localhost:8080")
    else:
        print("❌ Some tests failed. Check the container logs:")
        print("docker-compose logs web")
        sys.exit(1)

if __name__ == '__main__':
    main()