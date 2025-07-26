#!/usr/bin/env python3
"""
Database initialization script for Unified CRM Integration
"""

from app import create_app, db
from app.config import Config

def init_database():
    """Initialize the database with basic setup"""
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()

        # Configure BuilderPrime if API key is available
        if Config.BUILDER_PRIME_API_KEY:
            print(f"✅ Configured BuilderPrime connection with API key: {Config.BUILDER_PRIME_API_KEY[:10]}...")
        else:
            print("⚠️  BuilderPrime API key not found in environment variables")

        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()