#!/usr/bin/env python3
"""
Database initialization script for CRM_db
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Temporarily change the database name for this script
os.environ['DB_NAME'] = 'crm_db'

from app import create_app, db
from app.models.crm_db_models import CRMs, Clients, ClientCRMAuth, ClientCustomerData

def init_crm_database():
    """Initialize the CRM_db database with the new schema"""
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ All tables created successfully!")

        # Add required CRM systems
        crm_names = [
            ('Zoho', 'Zoho CRM for business management', 'https://www.zohoapis.com'),
            ('Jobber', 'Jobber CRM for service businesses', 'https://api.getjobber.com'),
            ('BuilderPrime', 'BuilderPrime CRM system for construction management', 'https://api.builderprime.com'),
            ('HubSpot', 'HubSpot CRM for marketing and sales', 'https://api.hubapi.com'),
            ('JobNimbus', 'JobNimbus CRM for field service management', 'https://api.jobnimbus.com'),
        ]
        crm_objs = {}
        for name, desc, url in crm_names:
            crm = CRMs.query.filter_by(name=name).first()
            if not crm:
                crm = CRMs(name=name, description=desc, base_url=url)
                db.session.add(crm)
                db.session.commit()
                print(f"✅ Added CRM system: {name}")
            crm_objs[name] = crm

        # Add a sample client
        sample_client = Clients.query.filter_by(email='admin@example.com').first()
        if not sample_client:
            sample_client = Clients(
                name='Admin User',
                email='admin@example.com',
                other_contact_info='System Administrator'
            )
            db.session.add(sample_client)
            db.session.commit()
            print("✅ Added sample client: Admin User")

        # Add a sample external client data (using HubSpot as example)
        existing_client_data = ClientCustomerData.query.filter_by(crm_client_id='ext_123').first()
        if not existing_client_data:
            customer_data = ClientCustomerData(
                crm_id=crm_objs['HubSpot'].id,
                source_client_id=sample_client.id,
                crm_client_id='ext_123',
                name='John Doe',
                email='john@example.com',
                phone_number='123-456-7890',
                custom_metadata={'source': 'hubspot', 'lead_score': 85}
            )
            db.session.add(customer_data)
            print("✅ Added sample external client data: John Doe")
        else:
            print("⚠️  Sample external client data already exists.")

        db.session.commit()
        print("\n🎉 CRM_db database initialized successfully!")
        print("\nTables created:")
        print("- crm_systems")
        print("- clients")
        print("- client_crm_auth")
        print("- client_customer_data")
        print("\nSample data added:")
        print("- 5 CRM systems (Zoho, Jobber, BuilderPrime, HubSpot, JobNimbus)")
        print("- 1 sample client (Admin User)")
        print("- 1 sample external client data (John Doe)")

if __name__ == '__main__':
    init_crm_database()