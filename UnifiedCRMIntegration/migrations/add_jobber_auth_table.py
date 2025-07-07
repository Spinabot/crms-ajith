"""
Migration script to add JobberAuth table
"""
from app import create_app, db
from app.models import JobberAuth

def upgrade():
    """Add JobberAuth table"""
    app = create_app()
    with app.app_context():
        # Create the table
        JobberAuth.__table__.create(db.engine, checkfirst=True)
        print("JobberAuth table created successfully")

def downgrade():
    """Remove JobberAuth table"""
    app = create_app()
    with app.app_context():
        # Drop the table
        JobberAuth.__table__.drop(db.engine, checkfirst=True)
        print("JobberAuth table dropped successfully")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()