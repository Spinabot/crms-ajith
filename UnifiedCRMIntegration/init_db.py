#!/usr/bin/env python3
"""
Database initialization script for Unified CRM Integration
"""

from app import create_app, db
from app.models import CRMConnection
from app.config import Config

def init_database():
    """Initialize the database with basic setup"""
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()

        # Create default CRM connections (inactive)
        crm_systems = ['builder_prime', 'hubspot', 'jobber', 'jobnimbus', 'zoho']

        for crm_system in crm_systems:
            # Check if connection already exists
            existing = CRMConnection.query.filter_by(crm_system=crm_system).first()
            if not existing:
                connection = CRMConnection(
                    crm_system=crm_system,
                    is_active=False
                )
                db.session.add(connection)
                print(f"Created inactive connection for {crm_system}")

        # Configure BuilderPrime if API key is available
        if Config.BUILDER_PRIME_API_KEY:
            builder_prime_connection = CRMConnection.query.filter_by(crm_system='builder_prime').first()
            if builder_prime_connection:
                builder_prime_connection.api_key = Config.BUILDER_PRIME_API_KEY
                builder_prime_connection.is_active = True
                print(f"✅ Configured BuilderPrime connection with API key: {Config.BUILDER_PRIME_API_KEY[:10]}...")
            else:
                # Create new BuilderPrime connection
                connection = CRMConnection(
                    crm_system='builder_prime',
                    api_key=Config.BUILDER_PRIME_API_KEY,
                    is_active=True
                )
                db.session.add(connection)
                print(f"✅ Created and configured BuilderPrime connection with API key: {Config.BUILDER_PRIME_API_KEY[:10]}...")
        else:
            print("⚠️  BuilderPrime API key not found in environment variables")

        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()