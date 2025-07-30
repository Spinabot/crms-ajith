import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FlaskConfig:
    """Flask application configuration settings"""

    # Flask configuration from environment variables
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))

    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def get_config_dict(cls):
        """Get Flask configuration as dictionary"""
        return {
            'ENV': cls.ENV,
            'DEBUG': cls.DEBUG,
            'SQLALCHEMY_TRACK_MODIFICATIONS': cls.SQLALCHEMY_TRACK_MODIFICATIONS
        }