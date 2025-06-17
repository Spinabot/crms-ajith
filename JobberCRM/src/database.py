import os

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base

from config import Config

DATABASE_URL = f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"


# Create an engine for connecting to PostgreSQL
engine = create_engine(DATABASE_URL)

# Create a base class for defining models
Base = declarative_base()

# Define the Tokens table as a Python class
class Token(Base):
    __tablename__ = "tokens"

    userid = Column(Integer, nullable=False, primary_key=True)
    access_token = Column(String(512), nullable=False)
    refresh_token = Column(String(128), nullable=False)
    expiration_time = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Token(userid={self.userid}, access_token={self.access_token}, refresh_token={self.refresh_token}, expiration_time={self.expiration_time})>"


# Check if the table already exists
inspector = inspect(engine)
if not inspector.has_table("tokens"):
    # Table doesn't exist, so create it
    Base.metadata.create_all(engine)
    # add log token creation success.
# add else token exists log
