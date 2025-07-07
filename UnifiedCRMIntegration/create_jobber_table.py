#!/usr/bin/env python3
"""
Simple script to create the JobberAuth table
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import JobberAuth

def create_jobber_auth_table():
    """Create the JobberAuth table"""
    app = create_app()
    with app.app_context():
        try:
            # Create all tables (this will create the JobberAuth table)
            db.create_all()
            print("✓ JobberAuth table created successfully")

            # Verify the table exists
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'jobber_auth')"))
                exists = result.scalar()
                if exists:
                    print("✓ JobberAuth table verified in database")
                else:
                    print("✗ JobberAuth table not found in database")
                    return False

            return True
        except Exception as e:
            print(f"✗ Error creating JobberAuth table: {e}")
            return False

if __name__ == "__main__":
    print("Creating JobberAuth table...")
    success = create_jobber_auth_table()
    if success:
        print("JobberAuth table setup completed successfully!")
    else:
        print("Failed to create JobberAuth table. Please check your database connection.")
        sys.exit(1)