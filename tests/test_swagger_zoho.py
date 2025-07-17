#!/usr/bin/env python3
"""
Test script to verify Zoho API Swagger documentation
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.swagger import api

def test_swagger_zoho():
    """Test Zoho API Swagger documentation"""
    app = create_app()

    with app.app_context():
        print("Testing Zoho API Swagger documentation...")

        # Check if Zoho namespace exists
        zoho_ns = None
        for namespace in api.namespaces:
            if namespace.name == 'zoho':
                zoho_ns = namespace
                break

        if zoho_ns:
            print(f"✓ Zoho namespace found: {zoho_ns.name}")
            print(f"  Description: {zoho_ns.description}")
            print(f"  Resources count: {len(zoho_ns.resources)}")

            if len(zoho_ns.resources) >= 3:
                print(f"✓ Found {len(zoho_ns.resources)} Zoho API resources")
            else:
                print(f"⚠ Expected at least 3 resources, found {len(zoho_ns.resources)}")
        else:
            print("❌ Zoho namespace not found")
            return False

        # Check if Zoho models are defined
        zoho_models = [
            'ZohoLead', 'ZohoLeadsResponse', 'ZohoUser',
            'ZohoUsersResponse', 'ZohoMetadataResponse',
            'ZohoAuthSuccess', 'ZohoAuthError'
        ]

        print("\nChecking Zoho models...")
        for model_name in zoho_models:
            if model_name in api.models:
                print(f"✓ Model found: {model_name}")
            else:
                print(f"⚠ Model missing: {model_name}")

        print("\n🎉 Zoho Swagger documentation test completed!")
        print("\nTo view the Swagger documentation:")
        print("1. Start your application: python run.py")
        print("2. Visit: http://localhost:5000/swagger")
        print("3. Look for the 'zoho' section in the API documentation")

        return True

if __name__ == "__main__":
    test_swagger_zoho()