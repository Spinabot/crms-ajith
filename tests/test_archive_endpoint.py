#!/usr/bin/env python3
"""
Test script for the JobNimbus archive endpoint
"""

import requests
import json
from app import create_app, db
from app.models import UnifiedLead

def test_archive_endpoint():
    """Test the archive endpoint with local database"""
    app = create_app()
    
    with app.app_context():
        # Create a test contact in the local database
        test_contact = UnifiedLead(
            first_name="Test",
            last_name="Contact",
            email="test@example.com",
            crm_system="jobnimbus",
            crm_external_id="test_jnid_123",
            crm_raw_data={
                "is_active": True,
                "is_archived": False
            }
        )
        
        try:
            db.session.add(test_contact)
            db.session.commit()
            print("✅ Created test contact in local database")
            
            # Test the archive endpoint
            url = "http://localhost:5001/jobnimbus/contacts/test_jnid_123"
            data = {
                "is_active": False,
                "is_archived": True
            }
            
            response = requests.delete(url, json=data)
            print(f"📡 Archive endpoint response status: {response.status_code}")
            print(f"📡 Archive endpoint response: {response.text}")
            
            # Check if local database was updated
            updated_contact = db.session.query(UnifiedLead).filter_by(
                crm_system='jobnimbus', 
                crm_external_id='test_jnid_123'
            ).first()
            
            if updated_contact:
                print(f"✅ Local database updated - is_active: {updated_contact.crm_raw_data.get('is_active')}")
                print(f"✅ Local database updated - is_archived: {updated_contact.crm_raw_data.get('is_archived')}")
            else:
                print("❌ Contact not found in local database")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
        finally:
            # Clean up test data
            try:
                db.session.query(UnifiedLead).filter_by(
                    crm_system='jobnimbus', 
                    crm_external_id='test_jnid_123'
                ).delete()
                db.session.commit()
                print("🧹 Cleaned up test data")
            except Exception as e:
                print(f"⚠️  Error cleaning up: {e}")

if __name__ == "__main__":
    test_archive_endpoint() 