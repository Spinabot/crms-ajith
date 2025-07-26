import os
import sys
import psycopg2
from app import create_app
from app.config import Config
from config.vault_config import load_secrets
from app.models.crm_db_models import CRMs, Clients, ClientCRMAuth
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

def ensure_crm_db_exists():
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'crm_db')

    # Connect to the default 'postgres' database
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database='postgres'
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Check if crm_db exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cursor.fetchone()
    if not exists:
        print(f"📦 Creating database '{db_name}'...")
        cursor.execute(f'CREATE DATABASE "{db_name}"')
        print(f"✅ Database '{db_name}' created successfully!")
    else:
        print(f"✅ Database '{db_name}' already exists.")

    cursor.close()
    conn.close()

# Ensure the crm_db database exists before anything else
ensure_crm_db_exists()

def initialize_crm_db(app, db):
    with app.app_context():
        db.create_all()
        from app.models.crm_db_models import Clients, CRMs

        # Only initialize if there are no clients
        if Clients.query.first() is None:
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
                    crm = CRMs()
                    crm.name = name
                    crm.description = desc
                    crm.base_url = url
                    db.session.add(crm)
                    db.session.commit()
                    print(f"✅ Added CRM system: {name}")
                crm_objs[name] = crm

            # Add a sample client
            sample_client = Clients.query.filter_by(email='admin@example.com').first()
            if not sample_client:
                sample_client = Clients()
                sample_client.name = 'Admin User'
                sample_client.email = 'admin@example.com'
                sample_client.other_contact_info = 'System Administrator'
                db.session.add(sample_client)
                db.session.commit()
                print("✅ Added sample client: Admin User")

            db.session.commit()
            print("\n🎉 CRM_db database initialized successfully!")
            print("\nTables created:")
            print("- crm_systems")
            print("- clients")
            print("- client_crm_auth")
            print("- unified_leads")
            print("\nSample data added:")
            print("- 5 CRM systems (Zoho, Jobber, BuilderPrime, HubSpot, JobNimbus)")
            print("- 1 sample client (Admin User)")
        else:
            print("✅ Database already initialized. Skipping table creation and sample data.")

# Load Vault secrets
VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
VAULT_SECRET_PATH = os.getenv("VAULT_SECRET_PATH")
if not all([VAULT_ADDR, VAULT_TOKEN, VAULT_SECRET_PATH]):
    raise RuntimeError("❌ Missing Vault environment variables")
secrets = load_secrets(VAULT_ADDR, VAULT_TOKEN, VAULT_SECRET_PATH)

app = create_app()
from app import db

# Always initialize the CRM database; let it handle sample data checks
initialize_crm_db(app, db)

# Only initialize the CRM database in the main process (not the Flask reloader)
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
    initialize_crm_db(app, db)

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=int(Config.PORT),
        debug=False if Config.FLASK_ENV == "production" else True
    )