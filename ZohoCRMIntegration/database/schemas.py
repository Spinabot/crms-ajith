# schemas.py
from sqlalchemy import Column
from database import db  # Import db from the database module
from sqlalchemy import Integer, String,DateTime,ForeignKey
from sqlalchemy.orm import relationship


class ZohoCreds(db.Model):
    __tablename__ = 'credentials'
    # Remodel ID as a primary
    entity_id = Column(Integer, primary_key=True)  # Unique constraint for entity_id
    access_token = Column(String)
    refresh_token = Column(String)
    expiration_time = Column(Integer)
    
    # Relationship to clients (one-to-many)
    clients = relationship("Clients", backref="credentials", cascade="all, delete-orphan")


class Clients(db.Model):
    __tablename__ = "clients"
    zoho_id = Column(String, primary_key=True)
    entity_id = Column(Integer, ForeignKey("credentials.entity_id", ondelete="CASCADE"))
    full_name = Column(String)

class ZohoAudit(db.Model):
    __tablename__ = "audit"
    id = Column(Integer, primary_key=True,autoincrement=True)
    lead_id = Column(String)
    entity_id = Column(Integer)
    zoho_id = Column(String, ForeignKey("clients.zoho_id", ondelete="CASCADE"))
    name = Column(String)
    message = Column(String)
    time = Column(DateTime)




# Function to create tables
def create_tables():
    db.create_all() 