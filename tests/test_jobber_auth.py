#!/usr/bin/env python3
"""
Test script for Jobber authentication integration
"""
import os
import sys
from app import create_app, db
from app.models import JobberAuth

def test_database_connection():
    """Test database connection and table creation"""
    app = create_app()
    with app.app_context():
        try:
            # Test database connection using newer SQLAlchemy syntax
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("✓ Database connection successful")

            # Test JobberAuth table creation
            db.create_all()
            print("✓ JobberAuth table created/verified successfully")

            return True
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False

def test_config():
    """Test configuration values"""
    app = create_app()
    with app.app_context():
        from app.config import Config

        required_vars = [
            'JOBBER_CLIENT_ID',
            'JOBBER_CLIENT_SECRET',
            'JOBBER_TOKENS_URL',
            'JOBBER_API_URL'
        ]

        missing_vars = []
        for var in required_vars:
            if not getattr(Config, var, None):
                missing_vars.append(var)

        if missing_vars:
            print(f"✗ Missing configuration variables: {', '.join(missing_vars)}")
            print("Please set these environment variables:")
            for var in missing_vars:
                print(f"  - {var}")
            return False
        else:
            print("✓ All required configuration variables are set")
            return True

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import jwt
        import requests
        import redis
        from app.routes.jobber_auth import jobber_auth_bp
        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Jobber Authentication Integration")
    print("=" * 50)

    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Database Connection", test_database_connection),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  Test failed: {test_name}")

    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed! Jobber authentication integration is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())