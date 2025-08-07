#!/usr/bin/env python3
"""
Script to insert Jobber CRM access token into the database
"""

from app import app
from models import db, JobberToken
import time

def insert_jobber_token():
    """Insert the Jobber access token into the database"""
    with app.app_context():
        # Check if jobber_tokens table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"Available tables: {tables}")
        
        if 'jobber_tokens' not in tables:
            print("Creating jobber_tokens table...")
            db.create_all()
            print("✅ jobber_tokens table created!")
        
        # Check if token already exists
        existing_token = JobberToken.query.first()
        if existing_token:
            print("✅ Token already exists in database!")
            print(f"Access token: {existing_token.access_token[:20]}...")
            return
        
        # Get token from user input
        print("🔑 Please provide your Jobber access token:")
        access_token = input("Access Token: ").strip()
        
        if not access_token:
            print("❌ No access token provided. Exiting.")
            return
        
        refresh_token = input("Refresh Token (optional, press Enter to skip): ").strip()
        
        # Insert the token
        print("Inserting Jobber access token...")
        token = JobberToken()
        token.access_token = access_token
        token.refresh_token = refresh_token or ""
        token.expires_at = int(time.time()) + (365 * 24 * 60 * 60)  # 1 year from now
        
        db.session.add(token)
        db.session.commit()
        
        print("✅ Jobber access token inserted successfully!")
        print(f"Access token: {token.access_token[:20]}...")
        print(f"Expires at: {token.expires_at}")

if __name__ == "__main__":
    insert_jobber_token() 