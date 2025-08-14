#!/usr/bin/env python3
"""
Script to create Merge CRM integration tables
"""

import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, MergeLinkedAccount

def create_merge_tables():
    """Create Merge CRM integration tables"""
    with app.app_context():
        print("Creating Merge CRM integration tables...")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"Existing tables: {existing_tables}")
        
        if 'merge_linked_accounts' not in existing_tables:
            print("Creating merge_linked_accounts table...")
            db.create_all()
            
            # Check again
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"Tables after creation: {existing_tables}")
            
            if 'merge_linked_accounts' in existing_tables:
                print("✅ merge_linked_accounts table created successfully!")
            else:
                print("❌ Failed to create merge_linked_accounts table!")
        else:
            print("✅ merge_linked_accounts table already exists!")

if __name__ == "__main__":
    create_merge_tables() 