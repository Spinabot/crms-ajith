#!/usr/bin/env python3
"""
Test script to verify database connection and operations.
"""

import sys
import os
import psycopg2
from datetime import datetime

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.db_conn import get_db_connection, insert_jobber

def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Test a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")

        cursor.close()
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_table_creation():
    """Test table creation."""
    print("\nTesting table creation...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'jobber_auth'
            );
        """)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("✓ jobber_auth table already exists")
        else:
            print("Creating jobber_auth table...")
            # This will be created by insert_jobber function

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Table creation test failed: {e}")
        return False

def test_insert_operation():
    """Test insert operation."""
    print("\nTesting insert operation...")
    try:
        # Test data
        test_user_id = "test_user_123"
        test_access_token = "test_access_token_123"
        test_refresh_token = "test_refresh_token_123"
        test_expiration_time = int(datetime.now().timestamp()) + 3600  # 1 hour from now

        # Insert test data
        insert_jobber(test_user_id, test_access_token, test_refresh_token, test_expiration_time)
        print("✓ Insert operation successful")

        # Verify the data was inserted
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jobber_auth WHERE user_id = %s", (test_user_id,))
        result = cursor.fetchone()

        if result:
            print(f"✓ Data verification successful: {result[1]}")  # user_id
        else:
            print("✗ Data verification failed: record not found")
            return False

        # Clean up test data
        cursor.execute("DELETE FROM jobber_auth WHERE user_id = %s", (test_user_id,))
        conn.commit()
        print("✓ Test data cleaned up")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Insert operation test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variables configuration."""
    print("\nTesting environment variables...")
    try:
        required_vars = [
            'POSTGRES_DB',
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'POSTGRES_HOST',
            'POSTGRES_PORT',
            'Remodel_ID',
            'Remodel_SECRET'
        ]

        missing_vars = []
        for var in required_vars:
            if not getattr(Config, var, None):
                missing_vars.append(var)

        if missing_vars:
            print(f"✗ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✓ All required environment variables are set")
            return True
    except Exception as e:
        print(f"✗ Environment variables test failed: {e}")
        return False

def main():
    """Run all database tests."""
    print("Testing Database Operations")
    print("=" * 40)

    tests = [
        test_environment_variables,
        test_database_connection,
        test_table_creation,
        test_insert_operation
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 40)
    print("Database Test Results:")
    print(f"Environment Variables: {'✓' if results[0] else '✗'}")
    print(f"Database Connection: {'✓' if results[1] else '✗'}")
    print(f"Table Creation: {'✓' if results[2] else '✗'}")
    print(f"Insert Operation: {'✓' if results[3] else '✗'}")

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} tests")

    if passed == total:
        print("\nAll database tests passed!")
    else:
        print("\nSome database tests failed.")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())