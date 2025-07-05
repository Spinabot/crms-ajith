#!/usr/bin/env python3
"""
Database initialization script for HubSpot CRM
"""
import os
from app import create_app
from app.extensions import db, migrate

def init_database():
    """Initialize the database with migrations"""
    app = create_app()

    with app.app_context():
        # Initialize migrations
        print("Initializing database migrations...")
        migrate.init_app(app, db)

                # Check if migrations directory exists
        import os
        migrations_dir = os.path.join(os.getcwd(), 'migrations')

        if not os.path.exists(migrations_dir):
            # Create migration directory and initial migration
            try:
                from flask_migrate import init, migrate as flask_migrate
                init()
                print("Migration directory created successfully!")

                try:
                    flask_migrate(message="Initial migration")
                    print("Initial migration created successfully!")
                except Exception as e:
                    print(f"Migration creation error: {e}")
            except Exception as e:
                print(f"Migration directory creation error: {e}")
        else:
            print("Migration directory already exists, skipping initialization.")

        # Always try to upgrade the database
        try:
            from flask_migrate import upgrade
            upgrade()
            print("Database upgraded successfully!")
        except Exception as e:
            print(f"Database upgrade error: {e}")

if __name__ == '__main__':
    init_database()