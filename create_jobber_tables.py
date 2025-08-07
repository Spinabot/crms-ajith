#!/usr/bin/env python3
"""
Script to create jobber_tokens table
"""

from app import app
from models import db, JobberToken

def create_jobber_tables():
    """Create jobber_tokens table"""
    with app.app_context():
        print("Creating jobber_tokens table...")
        db.create_all()
        
        # Check if table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'jobber_tokens' in tables:
            print("✅ jobber_tokens table created successfully!")
        else:
            print("❌ Failed to create jobber_tokens table!")
            print(f"Available tables: {tables}")

if __name__ == "__main__":
    create_jobber_tables() 