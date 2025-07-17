#!/usr/bin/env python3
"""
Fix Jobber database table issue
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_jobber_table():
    """Create the jobber_auth table directly using psycopg2"""

    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'leads_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }

    print(f"Connecting to database: {db_params['host']}:{db_params['port']}/{db_params['database']}")

    try:
        # Connect to database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        print("✓ Connected to database successfully")

        # Create the jobber_auth table
        create_table_sql = """
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

        cursor.execute(create_table_sql)
        conn.commit()
        print("✓ jobber_auth table created successfully")

        # Verify table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'jobber_auth')")
        exists = cursor.fetchone()[0]

        if exists:
            print("✓ jobber_auth table verified in database")

            # List all tables
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✓ Available tables: {tables}")
        else:
            print("✗ jobber_auth table not found after creation")
            return False

        cursor.close()
        conn.close()
        print("✓ Database connection closed")
        return True

    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

if __name__ == "__main__":
    print("Creating JobberAuth table...")
    success = create_jobber_table()
    if success:
        print("\n🎉 JobberAuth table setup completed successfully!")
        print("You can now test the OAuth flow again.")
    else:
        print("\n❌ Failed to create JobberAuth table.")
        print("Please check your database connection and try again.")