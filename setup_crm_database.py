#!/usr/bin/env python3
"""
Database setup script for CRM_db
This script will create the CRM_db database if it doesn't exist and initialize it with the new schema.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_crm_database():
    """Create the CRM_db database if it doesn't exist"""
    # Get database configuration
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = 'crm_db'  # New database name

    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def main():
    """Main function to set up the CRM_db database"""
    print("Setting up CRM_db database...")

    # Create database
    if create_crm_database():
        print("CRM_db database setup completed successfully!")
        print("Now you can run: python init_crm_db.py")
    else:
        print("CRM_db database setup failed. Please check your PostgreSQL connection.")
        print("Make sure PostgreSQL is running and your credentials are correct.")

if __name__ == '__main__':
    main()