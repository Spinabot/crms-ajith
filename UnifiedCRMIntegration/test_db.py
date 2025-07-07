#!/usr/bin/env python3
"""
Simple database test script
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def test_database():
    """Test database connection and table existence"""
    app = create_app()
    with app.app_context():
        try:
            # Test database connection
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                print("✓ Database connection successful")

            # Check if jobber_auth table exists
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'jobber_auth')"))
                exists = result.scalar()
                if exists:
                    print("✓ jobber_auth table exists")
                else:
                    print("✗ jobber_auth table does not exist")
                    print("Creating tables...")
                    db.create_all()
                    print("✓ Tables created")

            # List all tables
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                tables = [row[0] for row in result.fetchall()]
                print(f"✓ Available tables: {tables}")

            return True
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False

if __name__ == "__main__":
    print("Testing database connection...")
    success = test_database()
    if success:
        print("Database test completed successfully!")
    else:
        print("Database test failed!")
        sys.exit(1)