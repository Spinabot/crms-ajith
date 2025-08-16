#!/usr/bin/env python3
"""
Setup script to properly configure Bitrix24 CRM in your database.
This script will:
1. Add Bitrix24 to the CRMs table
2. Update the integration files to use the proper CRM ID
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, CRMs
from config.database import DatabaseConfig
from config.flask_config import FlaskConfig

def setup_bitrix24_crm():
    """Setup Bitrix24 CRM entry in the database"""
    
    # Create a minimal Flask app for database operations
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if Bitrix24 already exists
            existing = CRMs.query.filter_by(name='bitrix24').first()
            if existing:
                print(f"✅ Bitrix24 CRM already exists with ID: {existing.id}")
                crm_id = existing.id
            else:
                # Create new Bitrix24 CRM entry
                bitrix_crm = CRMs(
                    name='bitrix24',
                    description='Bitrix24 CRM Integration',
                    base_url='https://bitrix24.com'
                )
                db.session.add(bitrix_crm)
                db.session.commit()
                crm_id = bitrix_crm.id
                print(f"✅ Created Bitrix24 CRM with ID: {crm_id}")
            
            # Now update the integration files to use the proper CRM ID
            update_integration_files(crm_id)
            
        except Exception as e:
            print(f"❌ Error setting up Bitrix24 CRM: {e}")
            return False
    
    return True

def update_integration_files(crm_id):
    """Update the integration files to use the proper CRM ID"""
    
    print(f"\n🔄 Updating integration files to use CRM ID: {crm_id}")
    
    # Update service file
    service_file = "services/bitrix24_service.py"
    if os.path.exists(service_file):
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Replace temporary ID with proper CRM ID
        content = content.replace("crm_id=999", f"crm_id={crm_id}")
        
        with open(service_file, 'w') as f:
            f.write(content)
        print(f"✅ Updated {service_file}")
    
    # Update controller file
    controller_file = "controllers/bitrix24_controller.py"
    if os.path.exists(controller_file):
        with open(controller_file, 'r') as f:
            content = f.read()
        
        # Replace temporary ID with proper CRM ID
        content = content.replace("crm_id=999", f"crm_id={crm_id}")
        
        with open(controller_file, 'w') as f:
            f.write(content)
        print(f"✅ Updated {controller_file}")
    
    print(f"\n🎯 Integration files updated to use CRM ID: {crm_id}")
    print("You can now use the Bitrix24 integration with proper database relationships!")

if __name__ == "__main__":
    print("🚀 Setting up Bitrix24 CRM integration...")
    success = setup_bitrix24_crm()
    
    if success:
        print("\n🎉 Bitrix24 CRM setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set your environment variables:")
        print("   export BITRIX_WEBHOOK_BASE='https://b24-...bitrix24.com/rest/1/<token>/'")
        print("   export BITRIX_OUTBOUND_TOKEN='your_outbound_token'")
        print("\n2. Test the integration:")
        print("   python test_bitrix24_integration.py")
        print("\n3. Or test manually with cURL:")
        print("   curl -X POST http://localhost:5001/api/bitrix/clients/1/config \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"webhook_base\": \"your_webhook_url\"}'")
    else:
        print("\n❌ Bitrix24 CRM setup failed. Check the error messages above.")
        sys.exit(1) 