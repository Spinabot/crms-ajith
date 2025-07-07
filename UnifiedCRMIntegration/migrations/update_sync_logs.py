"""
Migration script to update sync_logs table to make lead_id nullable
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def run_migration():
    app = create_app()

    with app.app_context():
        try:
            # Update the sync_logs table to make lead_id nullable
            db.session.execute(text("""
                ALTER TABLE sync_logs
                ALTER COLUMN lead_id DROP NOT NULL;
            """))

            db.session.commit()
            print("Successfully updated sync_logs table to make lead_id nullable")

        except Exception as e:
            db.session.rollback()
            print(f"Error updating sync_logs table: {e}")
            raise

if __name__ == "__main__":
    run_migration()