#!/usr/bin/env python3
"""
Debug script to check Jobber database connectivity and token access
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import JobberAuth
from app.services.jobber_service import JobberService
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def debug_database_connection():
    """Debug database connection and token access"""
    app = create_app()

    with app.app_context():
        print("=== Database Connection Debug ===")

        # 1. Check database connection
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT current_database()"))
                db_name = result.scalar()
                print(f"✓ Connected to database: {db_name}")
        except Exception as e:
            print(f"✗ Database connection error: {e}")
            return False

        # 2. Check if jobber_auth table exists
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'jobber_auth')"))
                exists = result.scalar()
                if exists:
                    print("✓ jobber_auth table exists")
                else:
                    print("✗ jobber_auth table does not exist")
                    return False
        except Exception as e:
            print(f"✗ Error checking table: {e}")
            return False

        # 3. Check all records in jobber_auth table
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT user_id, expiration_time, created_at, updated_at FROM jobber_auth"))
                records = result.fetchall()
                print(f"✓ Found {len(records)} records in jobber_auth table:")
                for record in records:
                    print(f"  - User ID: {record[0]}, Expiration: {record[1]}, Updated: {record[3]}")
        except Exception as e:
            print(f"✗ Error querying records: {e}")
            return False

        # 4. Test SQLAlchemy ORM access
        try:
            auth_records = JobberAuth.query.all()
            print(f"✓ SQLAlchemy found {len(auth_records)} records:")
            for record in auth_records:
                print(f"  - User ID: {record.user_id}, Has Valid Token: {record.has_valid_token()}")
        except Exception as e:
            print(f"✗ SQLAlchemy query error: {e}")
            return False

        # 5. Test JobberService.get_user_tokens
        try:
            user_id = "123"
            tokens = JobberService.get_user_tokens(user_id)
            if tokens:
                print(f"✓ JobberService.get_user_tokens('{user_id}') returned tokens")
                print(f"  - Access token length: {len(tokens['access_token'])}")
                print(f"  - Expiration time: {tokens['expiration_time']}")
            else:
                print(f"✗ JobberService.get_user_tokens('{user_id}') returned None")
        except Exception as e:
            print(f"✗ JobberService.get_user_tokens error: {e}")
            return False

        return True

def debug_direct_psycopg2():
    """Debug using direct psycopg2 connection"""
    print("\n=== Direct psycopg2 Connection Debug ===")

    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'leads_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }

    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Check database name
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]
        print(f"✓ Direct connection to database: {db_name}")

        # Check jobber_auth table
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'jobber_auth')")
        exists = cursor.fetchone()[0]
        if exists:
            print("✓ jobber_auth table exists (direct connection)")
        else:
            print("✗ jobber_auth table does not exist (direct connection)")

        # Check records
        cursor.execute("SELECT user_id, expiration_time, created_at, updated_at FROM jobber_auth")
        records = cursor.fetchall()
        print(f"✓ Direct query found {len(records)} records:")
        for record in records:
            print(f"  - User ID: {record[0]}, Expiration: {record[1]}, Updated: {record[3]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"✗ Direct psycopg2 error: {e}")

if __name__ == "__main__":
    print("Jobber Database Debug")
    print("=" * 50)

    # Test direct psycopg2 connection
    debug_direct_psycopg2()

    # Test Flask-SQLAlchemy connection
    success = debug_database_connection()

    if success:
        print("\n✅ Database connectivity is working correctly!")
    else:
        print("\n❌ Database connectivity issues found!")