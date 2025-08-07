#!/usr/bin/env python3
"""
Script to insert Capsule CRM access token into the database
"""

from app import app
from models import db, CapsuleToken
import time

def insert_capsule_token():
    """Insert the Capsule access token into the database"""
    with app.app_context():
        # Check if capsule_tokens table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"Available tables: {tables}")
        
        if 'capsule_tokens' not in tables:
            print("Creating capsule_tokens table...")
            db.create_all()
            print("✅ capsule_tokens table created!")
        
        # Check if token already exists
        existing_token = CapsuleToken.query.first()
        if existing_token:
            print("✅ Token already exists in database!")
            print(f"Access token: {existing_token.access_token[:20]}...")
            return
        
        # Insert the new token
        print("Inserting Capsule access token...")
        token = CapsuleToken()
        token.access_token = "YezfG6OpHLqG8s/n2IPKQ18N9IGnDyvaJEMwK/0RBemETcZo1FNBGcJDTj8nFyU0"
        token.refresh_token = ""  # Empty string for now
        token.expires_at = int(time.time()) + (365 * 24 * 60 * 60)  # 1 year from now
        
        db.session.add(token)
        db.session.commit()
        
        print("✅ Capsule access token inserted successfully!")
        print(f"Access token: {token.access_token[:20]}...")
        print(f"Expires at: {token.expires_at}")

if __name__ == "__main__":
    insert_capsule_token() 