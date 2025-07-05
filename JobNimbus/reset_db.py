#!/usr/bin/env python3
"""
Script to reset the database after schema changes.
This will drop all tables and recreate them with the new schema.
"""

from app import create_app
from app.database import db

def reset_database():
    """Drop all tables and recreate them"""
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Database reset complete!")

if __name__ == "__main__":
    reset_database() 