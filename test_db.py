#!/usr/bin/env python3
"""
Test script to check database status and create missing tables
"""

import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, CapsuleToken

def test_database():
    """Test database connection and create tables"""
    with app.app_context():
        print("Testing database connection...")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"Existing tables: {existing_tables}")
        
        if 'capsule_tokens' not in existing_tables:
            print("Creating missing capsule_tokens table...")
            db.create_all()
            
            # Check again
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"Tables after creation: {existing_tables}")
            
            if 'capsule_tokens' in existing_tables:
                print("✅ capsule_tokens table created successfully!")
            else:
                print("❌ Failed to create capsule_tokens table!")
        else:
            print("✅ capsule_tokens table already exists!")

if __name__ == "__main__":
    test_database() 