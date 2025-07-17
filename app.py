import os
import sys
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app import create_app
from app.config import Config
from config.vault_config import load_secrets

def wait_for_database(max_retries=30, retry_interval=2):
    """Wait for database to be ready"""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'postgres'  # Connect to default postgres database first
    }

    print("🔄 Waiting for database to be ready...")

    for attempt in range(max_retries):
        try:
            # Try to connect to the default postgres database
            conn = psycopg2.connect(**db_config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Check if our target database exists
            db_name = os.getenv('DB_NAME', 'leads_db')
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()

            if not exists:
                print(f"📦 Creating database '{db_name}'...")
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                print(f"✅ Database '{db_name}' created successfully!")

            cursor.close()
            conn.close()

            # Now try to connect to our target database
            db_config['database'] = db_name
            conn = psycopg2.connect(**db_config)
            conn.close()

            print("✅ Database is ready!")
            return True

        except psycopg2.OperationalError as e:
            print(f"⏳ Database not ready yet (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("❌ Failed to connect to database after maximum retries")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    return False

flask_env = os.getenv("FLASK_ENV", "local")

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
VAULT_SECRET_PATH = os.getenv("VAULT_SECRET_PATH")

if not all([VAULT_ADDR, VAULT_TOKEN, VAULT_SECRET_PATH]):
    raise RuntimeError("❌ Missing Vault environment variables")

secrets = load_secrets(VAULT_ADDR, VAULT_TOKEN, VAULT_SECRET_PATH)

def init_database():
    """Initialize the database with basic setup"""
    # Import the existing init_db function
    from init_db import init_database as init_db_function
    init_db_function()

## Wait for database to be ready before initializing
print("🔄 Checking database connection...")
if not wait_for_database():
    print("❌ Failed to connect to database. Exiting...")
    sys.exit(1)

## initiate the database
print("🔄 Initializing database...")
try:
    init_database()
    print("✅ Database initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize database: {e}")
    sys.exit(1)

app = create_app()

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=int(Config.PORT),
        debug=False if Config.FLASK_ENV == "production" else True
    )