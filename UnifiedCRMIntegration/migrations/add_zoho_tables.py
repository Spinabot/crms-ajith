"""
Migration script to add Zoho CRM tables
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("[DEBUG] Script started")

try:
    from app import create_app, db
    print("[DEBUG] Imported create_app and db")
except Exception as e:
    print(f"[DEBUG] Error importing create_app or db: {e}")
    raise

try:
    from app.models import ZohoCreds, ZohoClients, ZohoAudit
    print("[DEBUG] Imported Zoho models")
except Exception as e:
    print(f"[DEBUG] Error importing Zoho models: {e}")
    raise


def upgrade():
    """Add Zoho CRM tables"""
    print("Starting Zoho CRM table creation...")
    try:
        app = create_app()
        print("[DEBUG] App created")
    except Exception as e:
        print(f"[DEBUG] Error creating app: {e}")
        raise
    with app.app_context():
        try:
            print("Creating ZohoCreds table...")
            ZohoCreds.__table__.create(db.engine, checkfirst=True)
            print("Creating ZohoClients table...")
            ZohoClients.__table__.create(db.engine, checkfirst=True)
            print("Creating ZohoAudit table...")
            ZohoAudit.__table__.create(db.engine, checkfirst=True)
            print("Zoho CRM tables created successfully")
        except Exception as e:
            print(f"Error creating Zoho CRM tables: {e}")

def downgrade():
    """Remove Zoho CRM tables"""
    print("Starting Zoho CRM table drop...")
    try:
        app = create_app()
        print("[DEBUG] App created")
    except Exception as e:
        print(f"[DEBUG] Error creating app: {e}")
        raise
    with app.app_context():
        try:
            print("Dropping ZohoAudit table...")
            ZohoAudit.__table__.drop(db.engine, checkfirst=True)
            print("Dropping ZohoClients table...")
            ZohoClients.__table__.drop(db.engine, checkfirst=True)
            print("Dropping ZohoCreds table...")
            ZohoCreds.__table__.drop(db.engine, checkfirst=True)
            print("Zoho CRM tables dropped successfully")
        except Exception as e:
            print(f"Error dropping Zoho CRM tables: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()