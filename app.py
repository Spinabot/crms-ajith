import os
import sys
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# Import configurations
from config.database import DatabaseConfig
from config.flask_config import FlaskConfig

def ensure_database_exists():
    """Create the PostgreSQL database if it doesn't exist"""
    try:
        # Get database connection parameters
        db_params = DatabaseConfig.get_connection_params()

        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port'],
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_params['database'],))
        exists = cursor.fetchone()

        if not exists:
            print(f"📦 Creating database '{db_params['database']}'...")
            cursor.execute(f'CREATE DATABASE "{db_params["database"]}"')
            print(f"✅ Database '{db_params['database']}' created successfully!")
        else:
            print(f"✅ Database '{db_params['database']}' already exists.")

        cursor.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("\n🔧 To fix this issue:")
        print("1. Make sure PostgreSQL is installed and running")
        print("2. Check if the credentials are correct (default: postgres/postgres)")
        print("3. Or set environment variables: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT")
        print("\n💡 Quick setup on macOS:")
        print("   brew install postgresql")
        print("   brew services start postgresql")
        print("   createdb spinabot_crm")
        return False
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

# Ensure the database exists before anything else
database_available = ensure_database_exists()

# Initialize Flask app
app = Flask(__name__)

# Configure database only if available
if database_available:
    app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.get_database_url()
else:
    # Use SQLite as fallback for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temp.db'
    print("⚠️  Using SQLite as fallback database for development")

# Apply Flask configuration
flask_config = FlaskConfig.get_config_dict()
for key, value in flask_config.items():
    app.config[key] = value

# Import db from models to avoid circular imports
from models import db

# Initialize SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)

def initialize_database(app, db):
    """Initialize database tables and add sample data"""
    try:
        with app.app_context():
            # Import models after db is initialized
            from models import (
                CRMs, Clients, ClientCRMAuth, CapsuleToken, JobberToken,
                JobNimbusCredentials, BuilderPrimeClientData, ZohoClientData, HubspotClientData,
                JobberClientData, JobNimbusClientData, MergeLinkedAccount
            )

            # Check if tables exist by using SQLAlchemy's inspect
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            # Check if CRMs table exists and has data
            if 'crms' not in existing_tables:
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
                    ('Capsule', 'Capsule CRM for business management', 'https://api.capsulecrm.com'),
                ]

                for name, desc, url in crm_names:
                    crm = CRMs()
                    crm.name = name
                    crm.description = desc
                    crm.base_url = url
                    db.session.add(crm)
                    db.session.commit()
                    print(f"✅ Added CRM system: {name}")

                print("\n🎉 Database initialized successfully!")
                print("\nTables created:")
                print("- crms")
                print("- clients")
                print("- client_crm_auth")
                print("- capsule_tokens")
                print("- builder_prime_client_data")
                print("- zoho_client_data")
                print("- hubspot_client_data")
                print("- jobber_client_data")
                print("- jobnimbus_client_data")
                print("- merge_linked_accounts")
                print("\nSample data added:")
                print("- 6 CRM systems (Zoho, Jobber, BuilderPrime, HubSpot, JobNimbus, Capsule)")
            else:
                print("✅ Database already initialized. Skipping table creation and sample data.")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("The app will continue running without database functionality.")

# Register blueprints
from routes.client_routes import client_bp
from routes.builderprime_routes import builderprime_bp
from config.swagger_config import swagger_bp
from controllers.jobber_controller import jobber_bp
from controllers.capsule_controller import capsule_bp
from controllers.jobnimbus_controller import jobnimbus_bp
from routes.merge_routes import register_merge_routes
from routes.merge_hris_routes import register_merge_hris_routes
from routes.bitrix24_routes import register_bitrix24_routes
from routes.merge_crm import crm_bp
from routes.merge_hris import hris_bp

app.register_blueprint(capsule_bp)
app.register_blueprint(jobnimbus_bp)
app.register_blueprint(jobber_bp)
app.register_blueprint(client_bp)
app.register_blueprint(builderprime_bp)
app.register_blueprint(swagger_bp)

# Register Merge routes
register_merge_routes(app)
register_merge_hris_routes(app)

# Register Bitrix24 routes
register_bitrix24_routes(app)

# Register new unified Merge blueprints
app.register_blueprint(crm_bp)
app.register_blueprint(hris_bp)

@app.route('/')
def home():
    return """
    <h1>🚀 CRM Integration API is Running!</h1>
    
    <h2>Available Endpoints:</h2>
    
    <h3>Capsule CRM Integration (People/Contacts):</h3>
    <ul>
        <li><a href="/api/capsule/auth">GET /api/capsule/auth</a> - Start OAuth authorization</li>
        <li><a href="/api/capsule/people">GET /api/capsule/people</a> - Get all people/contacts</li>
        <li>POST /api/capsule/people - Create new person/contact</li>
        <li>GET /api/capsule/people/{id} - Get person by ID</li>
        <li>PUT /api/capsule/people/{id} - Update person</li>
        <li>DELETE /api/capsule/people/{id} - Delete person</li>
    </ul>
    
    <h3>Jobber Integration:</h3>
    <ul>
        <li><a href="/api/jobber/clients">GET /api/jobber/clients</a> - Get Jobber clients</li>
        <li><a href="/api/jobber/jobs">GET /api/jobber/jobs</a> - Get Jobber jobs</li>
        <li>POST /api/jobber/clients - Create new Jobber client</li>
    </ul>
    
    <h3>Client Management:</h3>
    <ul>
        <li>GET /api/clients/ - Get all clients</li>
        <li>POST /api/clients/ - Create new client</li>
        <li>GET /api/clients/{id} - Get client by ID</li>
        <li>PUT /api/clients/{id} - Update client</li>
    </ul>
    
    <h3>BuilderPrime Integration:</h3>
    <ul>
        <li>GET /api/builderprime/leads - Get all leads</li>
        <li>POST /api/builderprime/clients/{id}/leads - Create lead</li>
        <li>GET /api/builderprime/clients/{id}/leads - Get client leads</li>
        <li>PUT /api/builderprime/clients/{id}/leads/{opportunity_id} - Update lead</li>
    </ul>
    
               <h3>Merge CRM Integration:</h3>
           <ul>
               <li>POST /api/merge/clients/{id}/link-token - Create Merge Link token</li>
               <li>POST /api/merge/clients/{id}/linked-accounts - Save linked account</li>
               <li>GET /api/merge/clients/{id}/crm/contacts - List contacts</li>
               <li>POST /api/merge/clients/{id}/crm/contacts - Create contact (meta-validated)</li>
               <li>GET /api/merge/linked-accounts - Admin: list all linked accounts</li>
               <li>GET /api/merge/crm/capabilities - List linked accounts & capabilities</li>
               <li>GET /api/merge/crm/integrations - All available integrations (with allowlist status)</li>
               <li>GET /api/merge/crm/allowlist/status - Check allowlist validation & resolved slugs</li>
               <li>GET /api/merge/crm/meta/{model}/post - Get writable fields for POST</li>
               <li>GET /api/merge/crm/meta/{model}/{id}/patch - Get writable fields for PATCH</li>
               <li>POST /api/merge/webhook - Merge webhook endpoint</li>
               <li>GET /api/merge/webhook/debug - Debug webhook configuration</li>
           </ul>
    
    <h3>Merge HRIS Integration:</h3>
    <ul>
        <li>GET /api/merge/hris/clients/{id}/employees - List employees</li>
        <li>GET /api/merge/hris/clients/{id}/employees/{id} - Get employee details</li>
        <li>GET /api/merge/hris/clients/{id}/employments - List employments</li>
        <li>GET /api/merge/hris/clients/{id}/locations - List locations</li>
        <li>GET /api/merge/hris/clients/{id}/groups - List groups</li>
        <li>GET/POST /api/merge/hris/clients/{id}/time-off - List/create time off</li>
        <li>GET/POST /api/merge/hris/clients/{id}/timesheet-entries - List/create timesheet entries</li>
        <li>POST /api/merge/hris/clients/{id}/passthrough - Vendor-specific CRUD operations</li>
    </ul>
    
    <h3>Bitrix24 CRM Integration:</h3>
    <ul>
        <li>POST /api/bitrix/clients/{id}/config - Save Bitrix24 webhook configuration</li>
        <li>GET /api/bitrix/clients/{id}/config/debug - Debug Bitrix24 configuration</li>
        <li>GET/POST /api/bitrix/clients/{id}/contacts - List/create contacts</li>
        <li>GET/PATCH/DELETE /api/bitrix/clients/{id}/contacts/{id} - Full CRUD on contacts</li>
        <li>GET/POST /api/bitrix/clients/{id}/deals - List/create deals</li>
        <li>GET/PATCH/DELETE /api/bitrix/clients/{id}/deals/{id} - Full CRUD on deals</li>
        <li>GET/POST /api/bitrix/clients/{id}/leads - List/create leads</li>
        <li>GET/PATCH/DELETE /api/bitrix/clients/{id}/leads/{id} - Full CRUD on leads</li>
        <li>POST /api/bitrix/webhook - Bitrix24 outbound webhook receiver</li>
    </ul>
    
    <h3>Merge Unified API (New Implementation):</h3>
    <ul>
        <li><strong>CRM Operations:</strong></li>
        <li>GET/POST /api/merge/crm/accounts - List/create accounts</li>
        <li>GET/POST/PATCH /api/merge/crm/contacts - Full CRUD on contacts</li>
        <li>GET/POST /api/merge/crm/leads - List/create leads</li>
        <li>GET/POST/PATCH /api/merge/crm/opportunities - Full CRUD on opportunities</li>
        <li>GET/POST/PATCH /api/merge/crm/tasks - Full CRUD on tasks</li>
        <li>GET/POST /api/merge/crm/notes - List/create notes</li>
        <li>GET/POST/PATCH /api/merge/crm/engagements - Full CRUD on engagements</li>
        <li>GET /api/merge/crm/users - List users</li>
        <li>POST /api/merge/crm/delete-account - Delete linked account</li>
        <li>POST /api/merge/crm/passthrough - Vendor-specific operations</li>
        <li><strong>HRIS Operations:</strong></li>
        <li>GET /api/merge/hris/employees - List employees</li>
        <li>GET/POST /api/merge/hris/time-off - List/create time off</li>
        <li>GET/POST /api/merge/hris/timesheet-entries - List/create timesheets</li>
        <li>POST /api/merge/hris/delete-account - Delete linked account</li>
        <li>POST /api/merge/hris/passthrough - Vendor-specific operations</li>
    </ul>
    
    <h3>API Documentation:</h3>
    <ul>
        <li><a href="/swagger">Swagger UI</a> - Interactive API documentation</li>
    </ul>
    
    <p><strong>Status:</strong> ✅ API is running and ready to use!</p>
    """

# Initialize the database only once
if __name__ == '__main__':
    # Get host and port from configuration
    FLASK_HOST = FlaskConfig.HOST
    FLASK_PORT = FlaskConfig.PORT

    # Initialize database only in main process
    initialize_database(app, db)

    # Run the Flask app
    app.run(debug=FlaskConfig.DEBUG, host=FLASK_HOST, port=FLASK_PORT)