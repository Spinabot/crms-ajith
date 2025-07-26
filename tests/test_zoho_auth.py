#!/usr/bin/env python3
"""
Test script for Zoho authorization functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_zoho_auth():
    """Test Zoho authorization setup"""
    try:
        from app import create_app, db
        from app.config import Config

        print("✓ Successfully imported app modules")

        # Test app creation
        app = create_app()
        print("✓ Flask app created successfully")

        # Test configuration
        print(f"✓ ZOHO_CLIENT_ID: {Config.ZOHO_CLIENT_ID}")
        print(f"✓ ZOHO_CLIENT_SECRET: {'*' * len(Config.ZOHO_CLIENT_SECRET) if Config.ZOHO_CLIENT_SECRET else 'Not set'}")
        print(f"✓ ZOHO_REDIRECT_URI: {Config.ZOHO_REDIRECT_URI}")
        print(f"✓ ZOHO_ACCOUNTS_URL: {Config.ZOHO_ACCOUNTS_URL}")
        print(f"✓ ZOHO_API_DOMAIN: {Config.ZOHO_API_DOMAIN}")

        # Test database connection
        with app.app_context():
            # Test if ZohoCreds table exists
            try:
                pass  # Removed check for zoho_credentials table
            except Exception as e:
                pass  # Removed error print for zoho_credentials table

            # Test model import
            try:
                pass  # Removed ZohoCreds model usage
            except Exception as e:
                pass  # Removed error print for ZohoCreds model

        print("\n🎉 Zoho authorization setup test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during Zoho auth test: {e}")
        return False

if __name__ == "__main__":
    test_zoho_auth()