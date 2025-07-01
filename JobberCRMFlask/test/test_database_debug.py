#!/usr/bin/env python3
"""
Database debug script to check if jobber_auth table exists and has data.
"""

import sys
import os
import psycopg2

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        conn = psycopg2.connect(
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
            database=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD
        )
        print("✓ Database connection successful")
        return conn
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return None

def check_table_exists(conn):
    """Check if jobber_auth table exists."""
    print("\nChecking if jobber_auth table exists...")
    try:
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'jobber_auth'
            );
        """)

        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("✓ jobber_auth table exists")

            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'jobber_auth'
                ORDER BY ordinal_position;
            """)

            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")

            return True
        else:
            print("✗ jobber_auth table does not exist")
            return False

    except Exception as e:
        print(f"✗ Error checking table: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()

def check_table_data(conn):
    """Check if there's any data in the jobber_auth table."""
    print("\nChecking jobber_auth table data...")
    try:
        cursor = conn.cursor()

        # Count rows
        cursor.execute("SELECT COUNT(*) FROM jobber_auth;")
        count = cursor.fetchone()[0]

        print(f"Total rows in jobber_auth table: {count}")

        if count > 0:
            # Show sample data
            cursor.execute("""
                SELECT user_id,
                       LEFT(access_token, 20) || '...' as access_token_preview,
                       LEFT(refresh_token, 20) || '...' as refresh_token_preview,
                       expiration_time,
                       created_at,
                       updated_at
                FROM jobber_auth
                ORDER BY created_at DESC
                LIMIT 5;
            """)

            rows = cursor.fetchall()
            print("\nSample data:")
            for row in rows:
                print(f"  User ID: {row[0]}")
                print(f"  Access Token: {row[1]}")
                print(f"  Refresh Token: {row[2]}")
                print(f"  Expiration: {row[3]}")
                print(f"  Created: {row[4]}")
                print(f"  Updated: {row[5]}")
                print("  ---")
        else:
            print("No data found in jobber_auth table")

        return count

    except Exception as e:
        print(f"✗ Error checking table data: {e}")
        return 0
    finally:
        if 'cursor' in locals():
            cursor.close()

def create_table_manually(conn):
    """Create the jobber_auth table manually if it doesn't exist."""
    print("\nCreating jobber_auth table manually...")
    try:
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS jobber_auth (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL UNIQUE,
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            expiration_time BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor.execute(create_table_query)
        conn.commit()

        print("✓ jobber_auth table created successfully")
        return True

    except Exception as e:
        print(f"✗ Error creating table: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()

def insert_test_data(conn):
    """Insert test data to verify the table works."""
    print("\nInserting test data...")
    try:
        cursor = conn.cursor()

        # Insert test data
        test_data = {
            'user_id': 'test_user_999',
            'access_token': 'test_access_token_999',
            'refresh_token': 'test_refresh_token_999',
            'expiration_time': 9999999999  # Far future
        }

        insert_query = """
        INSERT INTO jobber_auth (user_id, access_token, refresh_token, expiration_time)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET
            access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            expiration_time = EXCLUDED.expiration_time,
            updated_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(insert_query, (
            test_data['user_id'],
            test_data['access_token'],
            test_data['refresh_token'],
            test_data['expiration_time']
        ))
        conn.commit()

        print("✓ Test data inserted successfully")

        # Verify the data was inserted
        cursor.execute("SELECT COUNT(*) FROM jobber_auth WHERE user_id = %s", (test_data['user_id'],))
        count = cursor.fetchone()[0]

        if count > 0:
            print("✓ Test data verified in database")

            # Clean up test data
            cursor.execute("DELETE FROM jobber_auth WHERE user_id = %s", (test_data['user_id'],))
            conn.commit()
            print("✓ Test data cleaned up")

            return True
        else:
            print("✗ Test data not found after insertion")
            return False

    except Exception as e:
        print(f"✗ Error with test data: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()

def main():
    """Run all database debug tests."""
    print("Database Debug Tests")
    print("=" * 40)

    # Test connection
    conn = test_database_connection()
    if not conn:
        return 1

    try:
        # Check if table exists
        table_exists = check_table_exists(conn)

        if not table_exists:
            # Try to create table
            created = create_table_manually(conn)
            if created:
                table_exists = check_table_exists(conn)

        if table_exists:
            # Check data
            data_count = check_table_data(conn)

            # Test insert functionality
            insert_success = insert_test_data(conn)

            print("\n" + "=" * 40)
            print("Database Debug Results:")
            print(f"Table Exists: {'✓' if table_exists else '✗'}")
            print(f"Data Count: {data_count}")
            print(f"Insert Test: {'✓' if insert_success else '✗'}")

            if data_count == 0:
                print("\n⚠️  No tokens found in database!")
                print("This means:")
                print("1. The OAuth flow hasn't been completed yet, OR")
                print("2. There was an error during token storage")
                print("\nTo fix this:")
                print("1. Complete the OAuth flow: http://localhost:5000/auth/jobber?userid=1")
                print("2. Check the application logs for errors")
                print("3. Verify your Jobber credentials are correct")

            return 0 if table_exists and insert_success else 1
        else:
            print("\n✗ Could not create or verify jobber_auth table")
            return 1

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    exit(main())