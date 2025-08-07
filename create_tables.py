#!/usr/bin/env python3
"""
Script to create all database tables including capsule_tokens
"""

from app import app
from models import db, CapsuleToken

def create_tables():
    """Create all database tables"""
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        print("✅ All tables created successfully!")
        
        # Verify capsule_tokens table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'capsule_tokens' in tables:
            print("✅ capsule_tokens table created successfully!")
        else:
            print("❌ capsule_tokens table not found!")
            print("Available tables:", tables)

if __name__ == "__main__":
    create_tables() 