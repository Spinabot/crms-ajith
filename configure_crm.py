#!/usr/bin/env python3
"""
CRM Configuration Script for Unified CRM Integration
This script helps configure CRM connections in the database.
"""

from app import create_app, db
from app.models import CRMConnection
import os
from dotenv import load_dotenv

load_dotenv()

def configure_builder_prime():
    """Configure BuilderPrime CRM connection"""
    app = create_app()

    with app.app_context():
        connection = CRMConnection.query.filter_by(crm_system='builder_prime').first()
        if connection:
            # Get API key from environment or prompt user
            api_key = os.getenv('BUILDER_PRIME_API_KEY')
            if not api_key:
                api_key = input("Enter your BuilderPrime API key: ").strip()

            if api_key:
                connection.api_key = api_key
                connection.is_active = True
                db.session.commit()
                print("✅ BuilderPrime connection configured successfully!")
                print(f"   API Key: {api_key[:10]}...")
                print(f"   Status: Active")
            else:
                print("❌ No API key provided. BuilderPrime connection not configured.")
        else:
            print("❌ BuilderPrime connection not found in database. Run init_db.py first.")

def list_connections():
    """List all CRM connections"""
    app = create_app()

    with app.app_context():
        connections = CRMConnection.query.all()
        print("\n📋 Current CRM Connections:")
        print("-" * 50)

        for conn in connections:
            status = "🟢 Active" if conn.is_active else "🔴 Inactive"
            has_key = "✅" if conn.api_key else "❌"
            print(f"{conn.crm_system:15} | {status:10} | API Key: {has_key}")

        print("-" * 50)

def main():
    """Main function"""
    print("🔧 CRM Configuration Tool")
    print("=" * 30)

    while True:
        print("\nOptions:")
        print("1. Configure BuilderPrime CRM")
        print("2. List all connections")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == '1':
            configure_builder_prime()
        elif choice == '2':
            list_connections()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()