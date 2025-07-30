import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig:
    """Database configuration settings"""

    # Database configuration using environment variables
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'spinabot_crm')
    DB_PORT = os.getenv('DB_PORT', '5432')

    @classmethod
    def get_database_url(cls):
        """Get the complete database URL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def get_connection_params(cls):
        """Get database connection parameters"""
        return {
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME
        }