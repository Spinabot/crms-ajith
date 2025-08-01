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
                CRMs, Clients, ClientCRMAuth,
                BuilderPrimeClientData, ZohoClientData, HubspotClientData,
                JobberClientData, JobNimbusClientData
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
                print("- builder_prime_client_data")
                print("- zoho_client_data")
                print("- hubspot_client_data")
                print("- jobber_client_data")
                print("- jobnimbus_client_data")
                print("\nSample data added:")
                print("- 5 CRM systems (Zoho, Jobber, BuilderPrime, HubSpot, JobNimbus)")
            else:
                print("✅ Database already initialized. Skipping table creation and sample data.")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("The app will continue running without database functionality.")

# Register blueprints
from routes.client_routes import client_bp
from routes.builderprime_routes import builderprime_bp
from config.swagger_config import swagger_bp

app.register_blueprint(client_bp)
app.register_blueprint(builderprime_bp)
app.register_blueprint(swagger_bp)

@app.route('/')
def home():
    return """
    <h1>🚀 CRM Integration API is Running!</h1>
    
    <h2>Available Endpoints:</h2>
    
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